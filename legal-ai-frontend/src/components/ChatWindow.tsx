import React, { useState, useRef } from "react";
import { streamChatResponse } from "../utils/stream";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const ChatWindow: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSend = async () => {
    if (loading || !input.trim()) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      let aiMessageIndex: number;

setMessages(prev => {
  aiMessageIndex = prev.length;
  return [...prev, { role: "assistant", content: "" }];
});

await streamChatResponse(
  input,
  1,
  (token: string) => {
    setMessages(prev => {
      const updated = [...prev];
      if (updated[aiMessageIndex]) {
        updated[aiMessageIndex].content += token;
      }
      return updated;
    });
    scrollToBottom();
  },
  () => setLoading(false)
);

      await streamChatResponse(
        input,
        1,
        (token: string) => {
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1].content += token;
            return updated;
          });
          scrollToBottom();
        },
        () => setLoading(false)
      );
    } catch (error) {
      console.error("Streaming error:", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "⚠️ Something went wrong. Please try again." },
      ]);
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full max-w-3xl mx-auto border rounded-lg shadow-sm bg-white overflow-hidden">
      {/* Chat Area */}
      <div className="flex-grow overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-xs sm:max-w-md px-4 py-2 rounded-2xl shadow ${
                msg.role === "user"
                  ? "bg-blue-500 text-white rounded-br-none"
                  : "bg-gray-200 text-gray-800 rounded-bl-none"
              }`}
            >
              {msg.content || (msg.role === "assistant" && loading ? "..." : "")}
            </div>
          </div>
        ))}
        <div ref={chatEndRef}></div>
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t flex items-center gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask me a legal question..."
          className="flex-grow border border-gray-300 rounded-full px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
        />
        <button
          onClick={handleSend}
          disabled={loading}
          className="bg-blue-500 hover:bg-blue-600 text-white rounded-full px-5 py-2 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatWindow;
