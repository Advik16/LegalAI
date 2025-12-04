// src/components/ConversationsSidebar.jsx
import React from "react";

export default function ConversationsSidebar({
  conversations = [],
  selectedId = null,
  onSelectConversation,
  onNewConversation,
}) {
  return (
    <aside className="w-64 border-r bg-white min-h-screen p-3">
      <div className="flex items-center justify-between mb-4">
        <div className="font-semibold">Chat History</div>
        <button
          onClick={onNewConversation}
          className="text-xs px-2 py-1 bg-[#7c1f24] text-white rounded"
        >
          New
        </button>
      </div>

      <div className="space-y-2">
        {conversations.length === 0 && (
          <div className="text-sm text-gray-500">No conversations yet</div>
        )}

        {conversations.map((c) => {
          const isActive = c.conversation_id === selectedId;
          return (
            <button
              key={c.conversation_id}
              onClick={() => onSelectConversation(c.conversation_id)}
              className={`w-full text-left p-2 rounded ${isActive ? "bg-[#f7e9e9] border" : "hover:bg-gray-50"}`}
            >
              <div className="font-medium text-sm">{c.title || `Chat ${c.conversation_id.slice(0, 6)}`}</div>
              <div className="text-xs text-gray-500 truncate">{c.last_message || ""}</div>
            </button>
          );
        })}
      </div>
    </aside>
  );
}
