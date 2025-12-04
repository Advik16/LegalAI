// src/App.jsx
import React, { useState } from "react";
import LegalChamberStreamed from "./components/LegalChamberStreamed";
import ConversationsSidebar from "./components/ConversationsSidebar";

export default function App() {
  const [conversations, setConversations] = useState([]);
  const [selectedConversationId, setSelectedConversationId] = useState(null);

  // create a local placeholder conversation and select it
  const handleNewConversation = () => {
    const tempId = "local-" + Date.now().toString(36);
    const newConv = { conversation_id: tempId, title: "New chat", last_message: "" };
    setConversations((c) => [newConv, ...c]);
    setSelectedConversationId(tempId);
  };

  const handleSelectConversation = (conversation_id) => {
    setSelectedConversationId(conversation_id);
  };

  // Optional: a function you can call later to persist a conversation
  // For now it's a no-op; implement server save when you want to persist.
  const persistConversation = async ({ document_id, chunk_id, initial_query, initial_response, localId }) => {
    // Example placeholder — do nothing by default.
    // You can implement API call here later that calls POST /conversations
    // and then replace the local placeholder with the server-provided conversation_id.
    console.log("persistConversation called (no-op):", { document_id, chunk_id, initial_query, initial_response, localId });
  };

  return (
    <div className="flex">
      <ConversationsSidebar
        conversations={conversations}
        selectedId={selectedConversationId}
        onNewConversation={handleNewConversation}
        onSelectConversation={handleSelectConversation}
      />

      <div className="flex-1">
        <LegalChamberStreamed
          conversationId={selectedConversationId}
          onCreateConversation={persistConversation} // present but does nothing by default
        />
      </div>
    </div>
  );
}
