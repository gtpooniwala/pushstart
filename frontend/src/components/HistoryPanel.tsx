import { useEffect, useState } from "react";

interface Thread {
  id: string;
  title: string;
}

interface HistoryPanelProps {
  onSelectThread: (threadId: string | null) => void;
  currentThreadId: string | null;
}

export default function HistoryPanel({ onSelectThread, currentThreadId }: HistoryPanelProps) {
  const [threads, setThreads] = useState<Thread[]>([]);

  const fetchHistory = async () => {
    try {
      const res = await fetch("http://localhost:8000/chat/history");
      if (res.ok) {
        const data = await res.json();
        setThreads(data.threads);
      }
    } catch (e) {
      console.error("Failed to fetch history", e);
    }
  };

  useEffect(() => {
    fetchHistory();
    // Poll every 5 seconds to update history if new chats are created
    const interval = setInterval(fetchHistory, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-gray-200 dark:border-gray-800 flex justify-between items-center">
        <h2 className="font-semibold text-sm text-gray-500 uppercase tracking-wider">History</h2>
        <button 
          onClick={() => onSelectThread(null)}
          className="text-xs bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded"
        >
          New Chat
        </button>
      </div>
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {threads.length === 0 && (
          <div className="p-4 text-center text-xs text-gray-400">
            No history yet
          </div>
        )}
        {threads.map((thread) => (
          <div 
            key={thread.id}
            onClick={() => onSelectThread(thread.id)}
            className={`p-2 text-sm rounded cursor-pointer truncate ${
              currentThreadId === thread.id 
                ? "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300" 
                : "text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800"
            }`}
          >
            {thread.title}
          </div>
        ))}
      </div>
    </div>
  );
}
