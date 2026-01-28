// src/components/LegalChamberStreamed.jsx
import React, { useEffect, useRef, useState } from "react";
import { FileText, Gavel, Send } from "lucide-react";
import { startQueryStream, startChatStream } from "../api";

const LogoIcon = () => (
  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white">
    <path d="M12 3v18" />
    <path d="M6 6h12" />
    <path d="M6 6l-3 7a3 3 0 006 0l-3-7" />
    <path d="M18 6l-3 7a3 3 0 006 0l-3-7" />
  </svg>
);

export default function LegalChamberStreamed({
  conversationId = null,
  selectedConversation = null,
  onConversationCreated = null,
  onConversationUpdate = null,
}) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [activeConversationId, setActiveConversationId] = useState(null);

  const messagesRef = useRef(null);
  const controllerRef = useRef(null);
  const firstUserMessageRef = useRef(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => controllerRef.current?.abort?.();
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    if (!messagesRef.current) return;
    setTimeout(() => {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }, 20);
  }, [messages, isStreaming]);

  // Load messages when conversation changes
  useEffect(() => {
    console.log("🔄 Conversation changed:", conversationId);
    
    if (!conversationId) {
      // New conversation - clear everything
      console.log("📝 Starting new conversation");
      setMessages([]);
      setActiveConversationId(null);
      setError(null);
      firstUserMessageRef.current = null;
      return;
    }

    // Load existing conversation
    console.log("📂 Loading existing conversation:", conversationId);
    if (selectedConversation?.messages) {
      setMessages(selectedConversation.messages);
      setActiveConversationId(conversationId);
    } else {
      setMessages([]);
      setActiveConversationId(conversationId);
    }
  }, [conversationId, selectedConversation]);

  // Save messages to parent whenever they change (for localStorage persistence)
  useEffect(() => {
    const convId = activeConversationId || conversationId;
    if (convId && onConversationUpdate && messages.length > 0) {
      const lastUserMsg = messages.filter(m => m.role === "user").pop();
      onConversationUpdate(convId, {
        messages: messages,
        last_message: lastUserMsg?.content.slice(0, 100) || "",
        updated_at: new Date().toISOString(),
      });
    }
  }, [messages, activeConversationId, conversationId, onConversationUpdate]);

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    setError(null);

    const userMessage = { role: "user", content: text, timestamp: Date.now() };
    const assistantPlaceholder = { role: "assistant", content: "", streaming: true, timestamp: Date.now() };

    setMessages((m) => [...m, userMessage, assistantPlaceholder]);
    setInput("");
    setIsStreaming(true);

    // Store first user message for conversation title
    if (!firstUserMessageRef.current && !activeConversationId) {
      firstUserMessageRef.current = text;
    }

    const convId = activeConversationId || conversationId;
    const isNewConversation = !convId;

    console.log("📤 Sending message:", {
      text: text.slice(0, 50) + "...",
      convId,
      isNewConversation,
      endpoint: isNewConversation ? "/query/stream" : "/chat/stream",
    });

    if (isNewConversation) {
      // First message - use /query/stream (now returns conversation_id)
      console.log("🆕 Using /query/stream");
      
      const controller = startQueryStream({
        question: text,
        top_k: 1,
        onToken: (data) => handleToken(data, true),
        onDone: () => handleDone(),
        onError: handleError,
      });
      controllerRef.current = controller;
    } else {
      // Follow-up message - use /chat/stream
      console.log("💬 Using /chat/stream with conversation_id:", convId);
      
      const controller = startChatStream({
        conversation_id: convId,
        question: text,
        onToken: (data) => handleToken(data, false),
        onDone: () => handleDone(),
        onError: handleError,
      });
      controllerRef.current = controller;
    }
  };

  const handleToken = (data, isQueryStream) => {
    if (!data) return;

    console.log(`📨 Token from ${isQueryStream ? '/query' : '/chat'}:`, data);

    // Handle streaming tokens
    if (data.token !== undefined) {
      const token = String(data.token);
      setMessages((prev) => {
        const msgs = [...prev];
        for (let i = msgs.length - 1; i >= 0; i--) {
          if (msgs[i].role === "assistant" && msgs[i].streaming) {
            msgs[i] = { ...msgs[i], content: msgs[i].content + token };
            break;
          }
        }
        return msgs;
      });
      return;
    }

    // Handle final_response (includes conversation_id)
    if (data.final_response !== undefined) {
      console.log("✅ Final response received:", {
        hasConversationId: !!data.conversation_id,
        conversationId: data.conversation_id,
        hasResponse: !!data.final_response,
      });

      // Update the assistant message with final content
      setMessages((prev) => {
        const msgs = [...prev];
        for (let i = msgs.length - 1; i >= 0; i--) {
          if (msgs[i].role === "assistant" && msgs[i].streaming) {
            msgs[i] = {
              ...msgs[i],
              content: data.final_response,
              streaming: false,
              metadata: {
                document_id: data.document_id,
                chunk_id: data.chunk_id,
              },
            };
            break;
          }
        }
        return msgs;
      });

      // Handle conversation_id (from either /query or /chat)
      if (data.conversation_id && !activeConversationId) {
        console.log("🎯 Setting new conversation_id:", data.conversation_id);
        setActiveConversationId(data.conversation_id);

        // Create conversation in sidebar
        if (onConversationCreated) {
          const title = firstUserMessageRef.current?.slice(0, 60) || "New conversation";
          const lastMsg = firstUserMessageRef.current?.slice(0, 100) || "";
          
          console.log("📋 Creating conversation in sidebar:", {
            conversation_id: data.conversation_id,
            title,
          });

          onConversationCreated({
            conversation_id: data.conversation_id,
            title: title,
            last_message: lastMsg,
            created_at: new Date().toISOString(),
            messages: [], // Will be updated by the useEffect
          });
        }
      }

      return;
    }

    // Handle other metadata
    if (typeof data === "object") {
      setMessages((prev) => {
        const msgs = [...prev];
        for (let i = msgs.length - 1; i >= 0; i--) {
          if (msgs[i].role === "assistant" && msgs[i].streaming) {
            msgs[i] = {
              ...msgs[i],
              metadata: { ...(msgs[i].metadata || {}), ...data },
            };
            break;
          }
        }
        return msgs;
      });
    }
  };

  const handleDone = () => {
    console.log("✅ Stream completed");
    
    setMessages((prev) => {
      const msgs = [...prev];
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
    console.error("❌ Stream error:", err);
    setError(err?.message || String(err));
    setIsStreaming(false);
    
    setMessages((prev) => {
      const msgs = [...prev];
      for (let i = msgs.length - 1; i >= 0; i--) {
        if (msgs[i].role === "assistant") {
          msgs[i] = {
            ...msgs[i],
            streaming: false,
            content: msgs[i].content || "An error occurred while processing your request.",
          };
          break;
        }
      }
      return msgs;
    });
  };

  function handleSubmit(e) {
    e?.preventDefault();
    if (isStreaming || !input.trim()) return;
    sendMessage(input);
  }

  function handleSampleClick(text) {
    if (isStreaming) return;
    sendMessage(text);
  }

  const showWelcome = messages.length === 0;
  const displayConvId = activeConversationId || conversationId;

  return (
    <div className="h-screen flex flex-col bg-cream-50">
      <header className="bg-[#7c1f24] text-white">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center gap-3">
          <LogoIcon />
          <div>
            <div className="font-semibold text-lg">LegalAI</div>
            <div className="text-sm opacity-90">Satyamev Jayate • Truth Alone Triumphs</div>
          </div>

          <div className="ml-auto opacity-90 text-sm flex items-center gap-2">
            {displayConvId ? (
              <>
                <span className="hidden sm:inline">Session:</span>
                <code className="bg-white/20 px-2 py-0.5 rounded text-xs" title={displayConvId}>
                  {displayConvId.slice(0, 8)}
                </code>
              </>
            ) : (
              <span>New Session</span>
            )}
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

      <main className="flex-1 overflow-hidden flex flex-col max-w-4xl mx-auto px-4 sm:px-6 py-6 w-full">
        {showWelcome && (
          <>
            <h1 className="text-3xl font-serif font-bold text-center text-[#222]">Welcome to the Chamber</h1>
            <p className="text-center text-gray-600 mt-1">Your Virtual Legal Counsel Awaits</p>
            <p className="text-center text-gray-500 mt-1 mb-4">Present your legal inquiry below, or select from common matters of law</p>

            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <button
                onClick={() => handleSampleClick("What should I include in a rental agreement?")}
                className="text-left bg-white border rounded-lg shadow-sm p-4 flex items-start gap-4 hover:shadow-md transition-shadow"
              >
                <div className="bg-[#fff1f0] border rounded-md p-3 flex-shrink-0">
                  <FileText className="w-5 h-5 text-[#9e3737]" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-[#9e3737] font-semibold">CONTRACTS</div>
                  <div className="font-medium text-base sm:text-lg mt-1">What should I include in a rental agreement?</div>
                </div>
              </button>
              
              <button
                onClick={() => handleSampleClick("How do I file a small claims lawsuit?")}
                className="text-left bg-white border rounded-lg shadow-sm p-4 flex items-start gap-4 hover:shadow-md transition-shadow"
              >
                <div className="bg-[#fff1f0] border rounded-md p-3 flex-shrink-0">
                  <Gavel className="w-5 h-5 text-[#9e3737]" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-[#9e3737] font-semibold">LITIGATION</div>
                  <div className="font-medium text-base sm:text-lg mt-1">How do I file a small claims lawsuit?</div>
                </div>
              </button>
            </div>
          </>
        )}

        <div
          ref={messagesRef}
          className={`flex-1 overflow-auto p-3 space-y-3 ${showWelcome ? 'mt-6' : 'mt-0'}`}
          style={{ scrollbarGutter: "stable" }}
        >
          {messages.length === 0 && !showWelcome && (
            <div className="text-center text-gray-400 mt-6">No messages yet</div>
          )}

          {messages.map((m, idx) => {
            const isUser = m.role === "user";
            const containerClass = isUser ? "justify-end" : "justify-start";
            const bubbleClass = isUser
              ? "bg-[#7c1f24] text-white rounded-lg px-4 py-3 max-w-[80%] text-sm shadow-sm"
              : "bg-white border rounded-lg px-4 py-3 max-w-[80%] text-sm shadow-sm";
            
            return (
              <div key={idx} className={`flex ${containerClass}`}>
                <div className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}>
                  <div className={bubbleClass} style={{ whiteSpace: "pre-wrap" }}>
                    {m.content || (m.streaming ? "…" : "")}
                  </div>

                  {m.streaming && (
                    <div className="text-xs text-gray-400 mt-1 flex items-center gap-1">
                      <span className="inline-block w-1 h-1 bg-gray-400 rounded-full animate-pulse"></span>
                      <span className="inline-block w-1 h-1 bg-gray-400 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></span>
                      <span className="inline-block w-1 h-1 bg-gray-400 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></span>
                      <span className="ml-1">Generating response</span>
                    </div>
                  )}

                  {!isUser && m.metadata?.document_id && (
                    <div className="text-xs text-gray-500 mt-1.5 bg-gray-50 px-2 py-1 rounded">
                      📄 Source: {m.metadata.document_id}
                      {m.metadata.chunk_id && ` • Chunk: ${m.metadata.chunk_id}`}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </main>

      <div className="w-full border-t bg-white py-3 shadow-lg">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <form onSubmit={handleSubmit} className="flex items-center gap-3">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
              placeholder="State your legal inquiry here..."
              className="flex-1 p-3 rounded-md border resize-none h-14 outline-none focus:border-[#7c1f24] focus:ring-2 focus:ring-[#7c1f24]/20 transition-all"
              disabled={isStreaming}
            />
            <div className="flex items-center gap-2">
              {isStreaming && (
                <button
                  type="button"
                  onClick={() => {
                    controllerRef.current?.abort?.();
                    setIsStreaming(false);
                  }}
                  className="px-3 py-2 border rounded hover:bg-gray-50 transition-colors text-sm"
                >
                  Stop
                </button>
              )}
              <button
                type="submit"
                disabled={isStreaming || !input.trim()}
                className="bg-[#7c1f24] text-white px-4 py-2 rounded-md flex items-center gap-2 hover:bg-[#6a1a1f] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Send className="w-4 h-4" />
                <span className="hidden sm:inline">{isStreaming ? "Sending..." : "Ask"}</span>
              </button>
            </div>
          </form>

          {error && (
            <div className="text-sm text-red-600 mt-2 p-2 bg-red-50 rounded border border-red-200 flex items-start gap-2">
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}
          
          <div className="text-xs text-gray-400 mt-2">
            Press <kbd className="px-1.5 py-0.5 bg-gray-100 border rounded text-gray-600">Enter</kbd> to submit • 
            <kbd className="px-1.5 py-0.5 bg-gray-100 border rounded text-gray-600 ml-1">Shift + Enter</kbd> for new line
          </div>
        </div>
      </div>
    </div>
  );
}