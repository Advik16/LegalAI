import React from "react";
import ChatWindow from "./components/ChatWindow";

const App: React.FC = () => {
  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <header className="bg-white shadow-md p-4 text-center text-xl font-semibold text-gray-700">
        LegalAI Assistant ⚖️
      </header>
      <main className="flex-grow overflow-hidden">
        <ChatWindow />
      </main>
      <footer className="bg-white text-center text-gray-500 py-2 text-sm border-t">
        Built with ❤️ using React + FastAPI
      </footer>
    </div>
  );
};

export default App;
