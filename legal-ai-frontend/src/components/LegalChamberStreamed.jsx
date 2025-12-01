// src/components/LegalChamberStreamed.jsx
import React, { useEffect, useRef, useState } from "react";
import { FileText, Gavel, Send } from "lucide-react";
import { startQueryStream, startChatStream } from "../api"; // make sure this exists

// Inline SVG logo icon – unchanged
const LogoIcon = () => (
  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white">
    <path d="M12 3v18" />
    <path d="M6 6h12" />
    <path d="M6 6l-3 7a3 3 0 006 0l-3-7" />
    <path d="M18 6l-3 7a3 3 0 006 0l-3-7" />
  </svg>
);

export default function LegalChamberStreamed({ conversationId = null, onCreateConversation = null }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [conversationStarted, setConversationStarted] = useState(false);

  const messagesRef = useRef(null);
  const controllerRef = useRef(null);

  useEffect(() => {
    return () => controllerRef.current?.abort?.();
  }, []);

  useEffect(() => {
    if (!messagesRef.current) return;
    setTimeout(() => {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }, 20);
  }, [messages, isStreaming]);

  // Helper: detect whether conversationId likely represents a persisted server conversation.
  // Treat local placeholders that begin with "local-" as NOT persisted.
  const isPersistedConversation = conversationId && !String(conversationId).startsWith("local-");

  // DEBUG: helpful logs when troubleshooting
  useEffect(() => {
    console.debug("LegalChamberStreamed: conversationId ->", conversationId, "isPersisted ->", Boolean(isPersistedConversation));
  }, [conversationId, isPersistedConversation]);

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    setError(null);
    setConversationStarted(true);

    // push user message
    setMessages((m) => [...m, { role: "user", content: text }]);
    setInput("");
    // append assistant placeholder
    setMessages((m) => [...m, { role: "assistant", content: "", streaming: true }]);
    setIsStreaming(true);

    // choose query vs chat stream based on persisted status
    console.debug("Sending message. conversationId:", conversationId, "isPersistedConversation:", isPersistedConversation);

    const controller = isPersistedConversation
      ? startChatStream({
          conversation_id: conversationId,
          question: text,
          onToken: handleToken,
          onDone: handleDone,
          onError: handleError,
        })
      : startQueryStream({
          question: text,
          top_k: 1,
          onToken: handleToken,
          onDone: handleDone,
          onError: handleError,
        });

    controllerRef.current = controller;
  };

  const handleToken = (tokenOrObj) => {
    if (typeof tokenOrObj === "object" && tokenOrObj !== null) {
      const payloadObj = tokenOrObj;

      if (payloadObj.source) {
        setMessages((prev) => {
          const msgs = prev.slice();
          for (let i = msgs.length - 1; i >= 0; i--) {
            if (msgs[i].role === "assistant") {
              msgs[i] = { ...msgs[i], metadata: payloadObj.source };
              break;
            }
          }
          return msgs;
        });
        return;
      }

      if (payloadObj.final_response) {
        // update assistant message with final_response and metadata
        setMessages((prev) => {
          const msgs = prev.slice();
          for (let i = msgs.length - 1; i >= 0; i--) {
            if (msgs[i].role === "assistant") {
              msgs[i] = {
                ...msgs[i],
                content: payloadObj.final_response,
                metadata: { ...(msgs[i].metadata || {}), document_id: payloadObj.document_id, chunk_id: payloadObj.chunk_id },
                streaming: false,
              };
              break;
            }
          }
          return msgs;
        });

        // NOTE: we intentionally DO NOT call onCreateConversation automatically here.
        setIsStreaming(false);
        return;
      }

      // other structured payloads
      setMessages((prev) => {
        const msgs = prev.slice();
        for (let i = msgs.length - 1; i >= 0; i--) {
          if (msgs[i].role === "assistant") {
            msgs[i] = { ...msgs[i], metadata: { ...(msgs[i].metadata || {}), extra: payloadObj } };
            break;
          }
        }
        return msgs;
      });
      return;
    }

    // token string
    const token = String(tokenOrObj);
    setMessages((prev) => {
      const msgs = prev.slice();
      for (let i = msgs.length - 1; i >= 0; i--) {
        if (msgs[i].role === "assistant") {
          msgs[i] = { ...msgs[i], content: (msgs[i].content || "") + token };
          break;
        }
      }
      return msgs;
    });
  };

  const handleDone = () => {
    setMessages((prev) => {
      const msgs = prev.slice();
      for (let i = msgs.length - 1; i >= 0; i--) {
        if (msgs[i].role === "assistant") {
          msgs[i] = { ...msgs[i], streaming: false };
          break;
        }
      }
      return msgs;
    });
    setIsStreaming(false);
  };

  const handleError = (err) => {
    setError(err?.message || String(err));
    setIsStreaming(false);
  };

  function handleSubmit(e) {
    e?.preventDefault();
    if (isStreaming) return;
    sendMessage(input);
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  function handleSampleClick(text) {
    if (isStreaming) return;
    sendMessage(text);
  }

  return (
    <div className="min-h-screen flex flex-col bg-cream-50">
      <header className="bg-[#7c1f24] text-white">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center gap-3">
          <LogoIcon />
          <div>
            <div className="font-semibold text-lg">LegalAI</div>
            <div className="text-sm opacity-90">Iustitia Omnibus • Justice for All</div>
          </div>

          {/* Visual hint about local vs persisted conversation */}
          <div className="ml-auto opacity-90 text-sm">
            {conversationId ? (isPersistedConversation ? <span>Persisted</span> : <span>Local (unsaved)</span>) : <span>New query</span>}
          </div>
        </div>
      </header>

      <div className="bg-[#fff6f4] border-t border-b border-[#f0d8d6]">
        <div className="max-w-5xl mx-auto px-6 py-3 text-sm text-[#4b2a2b]">
          <strong>Legal Notice & Disclaimer</strong>
          <div className="mt-1">
            This AI assistant provides general legal information for educational purposes only. Information provided does not
            constitute legal advice and should not be relied upon as such. Always consult a licensed attorney for matters
            requiring professional legal counsel.
          </div>
        </div>
      </div>

      <main className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 py-6 w-full flex flex-col">
        <h1 className="text-3xl font-serif font-bold text-center text-[#222]">Welcome to the Chamber</h1>
        <p className="text-center text-gray-600 mt-1">Your Virtual Legal Counsel Awaits</p>
        <p className="text-center text-gray-500 mt-1 mb-4">Present your legal inquiry below, or select from common matters of law</p>

        {!conversationStarted && (
          <div className="mt-4 grid gap-3">
            <button onClick={() => handleSampleClick("What should I include in a rental agreement?")} className="text-left bg-white border rounded-lg shadow-sm p-4 flex items-center gap-4 hover:shadow-md">
              <div className="bg-[#fff1f0] border rounded-md p-3"><FileText className="w-5 h-5 text-[#9e3737]" /></div>
              <div><div className="text-xs text-[#9e3737] font-semibold">CONTRACTS</div><div className="font-medium text-lg mt-1">What should I include in a rental agreement?</div></div>
            </button>
            <button onClick={() => handleSampleClick("How do I file a small claims lawsuit?")} className="text-left bg-white border rounded-lg shadow-sm p-4 flex items-center gap-4 hover:shadow-md">
              <div className="bg-[#fff1f0] border rounded-md p-3"><Gavel className="w-5 h-5 text-[#9e3737]" /></div>
              <div><div className="text-xs text-[#9e3737] font-semibold">LITIGATION</div><div className="font-medium text-lg mt-1">How do I file a small claims lawsuit?</div></div>
            </button>
          </div>
        )}

        <div ref={messagesRef} className="mt-6 flex-1 overflow-auto p-3 space-y-3" style={{ scrollbarGutter: "stable" }}>
          {messages.length === 0 && <div className="text-center text-gray-400 mt-6">No messages yet — ask a question or pick a sample above.</div>}

          {messages.map((m, idx) => {
            const isUser = m.role === "user";
            const containerClass = isUser ? "justify-end" : "justify-start";
            const bubbleClass = isUser ? "bg-[#7c1f24] text-white rounded-lg px-4 py-2 max-w-[75%] text-sm" : "bg-white border rounded-lg px-4 py-2 max-w-[75%] text-sm";
            return (
              <div key={idx} className={`flex ${containerClass}`}>
                <div className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}>
                  <div className={bubbleClass} style={{ whiteSpace: "pre-wrap" }}>
                    {m.content || (m.streaming ? "…" : "")}
                  </div>

                  {m.streaming ? <div className="text-xs text-gray-400 mt-1">Streaming...</div> : null}

                  {m.metadata?.document_id && (
                    <div className="text-xs text-gray-400 mt-1">
                      Source: {m.metadata.document_id}{m.metadata.chunk_id ? ` • chunk: ${m.metadata.chunk_id}` : m.metadata.chunk_index ? ` • chunk index: ${m.metadata.chunk_index}` : null}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </main>

      <div className="w-full border-t bg-white py-3">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} className="flex items-center gap-3">
            <textarea value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSubmit(); } }} placeholder="State your legal inquiry here..." className="flex-1 p-3 rounded-md border resize-none h-14 outline-none" disabled={isStreaming} />
            <div className="flex items-center gap-2">
              {isStreaming && (<button type="button" onClick={() => { controllerRef.current?.abort?.(); setIsStreaming(false); }} className="px-3 py-2 border rounded">Stop</button>)}
              <button type="button" onClick={() => handleSubmit()} disabled={isStreaming} className="bg-[#7c1f24] text-white px-4 py-2 rounded-md flex items-center gap-2">
                <Send className="w-4 h-4" />
                <span>{isStreaming ? "Streaming..." : "Ask"}</span>
              </button>
            </div>
          </form>

          {error && <div className="text-sm text-red-600 mt-2">{error}</div>}
          <div className="text-xs text-gray-400 mt-2">Press Enter to submit • Shift + Enter for new line</div>
        </div>
      </div>
    </div>
  );
}
