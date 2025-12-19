import { useState, useRef, useEffect } from "react";
import LinkifiedText from "./LinkifiedText";

interface Message {
  role: "user" | "assistant" | "tool";
  content: string;
  tool_calls?: any[];
}

interface ChatPanelProps {
  threadId: string | null;
  setThreadId: (id: string) => void;
  setProposedAction: (action: any) => void;
}

function ToolOutput({ content }: { content: string }) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  // Try to parse JSON to see if it's a list of tasks or something structured
  let summary = "Tool Output";
  try {
    const parsed = JSON.parse(content);
    if (Array.isArray(parsed)) {
      summary = `Result: ${parsed.length} items`;
    } else if (typeof parsed === 'object') {
      summary = "Result: Object";
    }
  } catch (e) {
    // Not JSON, just use a snippet
    summary = content.slice(0, 50) + (content.length > 50 ? "..." : "");
  }

  return (
    <div className="text-xs">
      <button 
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 font-semibold"
      >
        <span>{isExpanded ? "▼" : "▶"}</span>
        <span>{summary}</span>
      </button>
      {isExpanded && (
        <div className="mt-2 whitespace-pre-wrap overflow-x-auto bg-gray-50 dark:bg-gray-900 p-2 rounded border border-gray-200 dark:border-gray-700">
          {content}
        </div>
      )}
    </div>
  );
}

function ToolCallDisplay({ toolCalls }: { toolCalls: any[] }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!toolCalls || toolCalls.length === 0) return null;

  return (
    <div className="mt-2 space-y-2">
      {toolCalls.map((call, idx) => (
        <div key={idx} className="border border-blue-200 dark:border-blue-800 rounded bg-blue-50 dark:bg-blue-900/20 overflow-hidden">
          <button 
            onClick={() => setIsExpanded(!isExpanded)}
            className="w-full flex items-center justify-between p-2 text-xs font-medium text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900/40 transition-colors"
          >
            <div className="flex items-center gap-2">
               <span>🛠️ Using tool: {call.name}</span>
            </div>
            <span>{isExpanded ? "▼" : "▶"}</span>
          </button>
          
          {isExpanded && (
            <div className="p-2 bg-white dark:bg-gray-900 border-t border-blue-200 dark:border-blue-800">
              <pre className="text-xs overflow-x-auto font-mono text-gray-600 dark:text-gray-400">
                {JSON.stringify(call.args, null, 2)}
              </pre>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default function ChatPanel({ threadId, setThreadId, setProposedAction }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input;
    setInput("");
    setIsLoading(true);

    // Optimistic update
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);

    try {
      const response = await fetch("http://localhost:8000/chat/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage,
          thread_id: threadId,
        }),
      });

      if (!response.ok) throw new Error("Failed to send message");

      const data = await response.json();
      
      if (data.thread_id && !threadId) {
        setThreadId(data.thread_id);
      }

      setMessages(data.messages);
      setProposedAction(data.proposed_action);
      
    } catch (error) {
      console.error("Error sending message:", error);
      // TODO: Show error toast
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center text-gray-400">
            <p>How can I help you today?</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white"
                    : msg.role === "tool"
                    ? "bg-gray-100 dark:bg-gray-800 text-gray-500 text-sm font-mono"
                    : "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                }`}
              >
                {msg.role === "tool" ? (
                   <ToolOutput content={msg.content} />
                ) : (
                   <>
                     {msg.content && <LinkifiedText text={msg.content} />}
                     {msg.tool_calls && msg.tool_calls.length > 0 && (
                       <ToolCallDisplay toolCalls={msg.tool_calls} />
                     )}
                   </>
                )}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-3">
              <span className="animate-pulse">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
        <div className="relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message..."
            rows={1}
            className="w-full p-3 pr-12 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            style={{ minHeight: "44px", maxHeight: "120px" }}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            className="absolute right-2 bottom-2 p-1.5 text-blue-600 hover:bg-blue-50 dark:hover:bg-gray-700 rounded-md disabled:opacity-50"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
