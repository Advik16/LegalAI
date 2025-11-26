// src/components/LegalChamberStreamed.jsx
import React, { useEffect, useRef, useState } from "react";
import { FileText, Gavel, Send } from "lucide-react";

// Inline SVG logo icon – no external image needed
const LogoIcon = () => (
  <svg
    width="32"
    height="32"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className="text-white"
  >
    <path d="M12 3v18" />
    <path d="M6 6h12" />
    <path d="M6 6l-3 7a3 3 0 006 0l-3-7" />
    <path d="M18 6l-3 7a3 3 0 006 0l-3-7" />
  </svg>
);


/**
 * useSSEStream - minimal SSE streaming helper (POST sends JSON `payload`)
 * expects SSE frames like: data: {"token":"..."}
 */
function useSSEStream() {
  const controllerRef = useRef(null);

  useEffect(() => {
    return () => controllerRef.current?.abort();
  }, []);

  async function start({ url, payload = {}, onToken, onDone, onError }) {
    // abort previous
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;

    try {
      const res = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "text/event-stream, */*",
        },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`HTTP ${res.status}: ${txt}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        // SSE events separated by double newline
        let idx;
        while ((idx = buffer.indexOf("\n\n")) !== -1) {
          const raw = buffer.slice(0, idx).trim();
          buffer = buffer.slice(idx + 2);
          const lines = raw.split(/\r?\n/);
          for (const line of lines) {
            if (!line.startsWith("data:")) continue;
            const payloadText = line.replace(/^data:\s*/, "");

            if (payloadText === "[DONE]") {
              onDone?.();
              controller.abort();
              return;
            }

            try {
              const parsed = JSON.parse(payloadText);
              if (parsed && typeof parsed.token !== "undefined") {
                onToken?.(String(parsed.token));
              } else {
                onToken?.(JSON.stringify(parsed));
              }
            } catch {
              onToken?.(payloadText);
            }
          }
        }
      }

      // leftover
      if (buffer.trim()) {
        const lines = buffer.trim().split(/\r?\n/);
        for (const line of lines) {
          if (!line.startsWith("data:")) continue;
          const payloadText = line.replace(/^data:\s*/, "");
          try {
            const parsed = JSON.parse(payloadText);
            if (parsed && typeof parsed.token !== "undefined") {
              onToken?.(String(parsed.token));
            } else {
              onToken?.(JSON.stringify(parsed));
            }
          } catch {
            onToken?.(payloadText);
          }
        }
      }

      onDone?.();
    } catch (err) {
      if (err.name !== "AbortError") onError?.(err);
      onDone?.();
    } finally {
      controllerRef.current = null;
    }
  }

  function stop() {
    controllerRef.current?.abort();
    controllerRef.current = null;
  }

  return { start, stop };
}

/**
 * Chat UI component
 * - uses local image as symbol left of "LegalAI"
 * - input is fixed at bottom
 * - messages area scrolls; assistant response receives tokens as they stream
 * - sample cards hidden after first user message is sent
 */
export default function LegalChamberStreamed() {
  const [messages, setMessages] = useState([
    // conversation messages: { role: 'user'|'assistant'|'system', content: string }
  ]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [conversationStarted, setConversationStarted] = useState(false);

  const stream = useSSEStream();
  const messagesRef = useRef(null);

  // sample questions shown only when conversation not started
  const sampleQuestions = [
    { id: 1, title: "CONTRACTS", text: "What should I include in a rental agreement?" },
    { id: 2, title: "LITIGATION", text: "How do I file a small claims lawsuit?" },
  ];

  // scroll to bottom whenever messages change
  useEffect(() => {
    if (!messagesRef.current) return;
    // small timeout to wait for DOM update
    setTimeout(() => {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }, 20);
  }, [messages, isStreaming]);

  // send a message (user), then start streaming assistant response
  const sendMessage = async (text) => {
    if (!text.trim()) return;
    setError(null);

    // mark conversation started (hides samples)
    setConversationStarted(true);

    // push user message
    setMessages((m) => [...m, { role: "user", content: text }]);
    setInput("");

    // append an empty assistant message which we'll fill as tokens stream
    setMessages((m) => [...m, { role: "assistant", content: "", streaming: true }]);
    setIsStreaming(true);

    const url = "http://127.0.0.1:8080/query/stream"; // or "/query/stream" if you proxy
    const payload = { question: text, top_k: 1 };

    stream.start({
      url,
      payload,
      onToken: (token) => {
        // append token to the last assistant message
        setMessages((prev) => {
          // find last assistant index
          const msgs = prev.slice();
          for (let i = msgs.length - 1; i >= 0; i--) {
            if (msgs[i].role === "assistant") {
              msgs[i] = { ...msgs[i], content: (msgs[i].content || "") + token };
              break;
            }
          }
          return msgs;
        });
      },
      onDone: () => {
        // mark assistant streaming as finished
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
      },
      onError: (err) => {
        setError(err?.message || String(err));
        setIsStreaming(false);
      },
    });
  };

  function handleSubmit(e) {
    e?.preventDefault();
    if (isStreaming) return; // prevent double send
    sendMessage(input);
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  // sample question click
  function handleSampleClick(text) {
    if (isStreaming) return;
    sendMessage(text);
  }

  return (
    <div className="min-h-screen flex flex-col bg-cream-50">
      {/* header with symbol left of title */}
      <header className="bg-[#7c1f24] text-white">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center gap-3">
          {/* law symbol (local uploaded file path) */}
          <LogoIcon/>
          <div>
            <div className="font-semibold text-lg">LegalAI</div>
            <div className="text-sm opacity-90">Iustitia Omnibus • Justice for All</div>
          </div>
          <div className="ml-auto opacity-90 text-sm">⚙️</div>
        </div>
      </header>

      {/* disclaimer */}
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

      {/* main chat area */}
      <main className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 py-6 w-full flex flex-col">
        <h1 className="text-3xl font-serif font-bold text-center text-[#222]">Welcome to the Chamber</h1>
        <p className="text-center text-gray-600 mt-1">Your Virtual Legal Counsel Awaits</p>
        <p className="text-center text-gray-500 mt-1 mb-4">Present your legal inquiry below, or select from common matters of law</p>

        {/* sample questions (hidden when conversationStarted === true) */}
        {!conversationStarted && (
          <div className="mt-4 grid gap-3">
            {sampleQuestions.map((s) => (
              <button
                key={s.id}
                onClick={() => handleSampleClick(s.text)}
                className="text-left bg-white border rounded-lg shadow-sm p-4 flex items-center gap-4 hover:shadow-md"
              >
                <div className="bg-[#fff1f0] border rounded-md p-3">
                  {s.id === 1 ? <FileText className="w-5 h-5 text-[#9e3737]" /> : <Gavel className="w-5 h-5 text-[#9e3737]" />}
                </div>
                <div>
                  <div className="text-xs text-[#9e3737] font-semibold">{s.title}</div>
                  <div className="font-medium text-lg mt-1">{s.text}</div>
                </div>
              </button>
            ))}
          </div>
        )}

        {/* messages container */}
        <div
          ref={messagesRef}
          className="mt-6 flex-1 overflow-auto p-3 space-y-3"
          style={{ scrollbarGutter: "stable" }}
        >
          {messages.length === 0 && (
            <div className="text-center text-gray-400 mt-6">No messages yet — ask a question or pick a sample above.</div>
          )}

          {messages.map((m, idx) => {
            const isUser = m.role === "user";
            const containerClass = isUser ? "justify-end" : "justify-start";
            const bubbleClass = isUser
              ? "bg-[#7c1f24] text-white rounded-lg px-4 py-2 max-w-[75%] text-sm"
              : "bg-white border rounded-lg px-4 py-2 max-w-[75%] text-sm";
            return (
              <div key={idx} className={`flex ${containerClass}`}>
                <div className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}>
                  <div className={bubbleClass} style={{ whiteSpace: "pre-wrap" }}>
                    {m.content || (m.streaming ? "…" : "")}
                  </div>
                  {/* small meta for streaming */}
                  {m.streaming ? <div className="text-xs text-gray-400 mt-1">Streaming...</div> : null}
                </div>
              </div>
            );
          })}
        </div>
      </main>

      {/* bottom fixed input area */}
      <div className="w-full border-t bg-white py-3">
        <div className="max-w-4xl mx-auto px-4 sm:px-6">
          <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} className="flex items-center gap-3">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSubmit(); } }}
              placeholder="State your legal inquiry here..."
              className="flex-1 p-3 rounded-md border resize-none h-14 outline-none"
              disabled={isStreaming}
            />
            <div className="flex items-center gap-2">
              {isStreaming && (
                <button
                  type="button"
                  onClick={() => { stream.stop(); setIsStreaming(false); }}
                  className="px-3 py-2 border rounded"
                >
                  Stop
                </button>
              )}
              <button
                type="button"
                onClick={() => handleSubmit()}
                disabled={isStreaming}
                className="bg-[#7c1f24] text-white px-4 py-2 rounded-md flex items-center gap-2"
              >
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
