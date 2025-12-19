"use client";

import { useState, useCallback, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import ChatPanel from "@/components/ChatPanel";
import RightPanel from "@/components/RightPanel";
import HistoryPanel from "@/components/HistoryPanel";

export default function Home() {
  const [rightPanelWidth, setRightPanelWidth] = useState(450);
  const [isResizing, setIsResizing] = useState(false);
  
  // Agent State
  const [proposedActions, setProposedActions] = useState<any[]>([]);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [messages, setMessages] = useState<any[]>([]);

  const searchParams = useSearchParams();
  const router = useRouter();

  // Sync from URL on mount/update
  useEffect(() => {
    const tid = searchParams.get("threadId");
    if (tid !== threadId) {
      setThreadId(tid || null);
    }
  }, [searchParams]);

  const handleThreadChange = (newId: string | null) => {
    setThreadId(newId);
    if (newId) {
      router.push(`/?threadId=${newId}`);
    } else {
      router.push("/");
    }
  };

  // Set initial width based on screen size
  useEffect(() => {
    // Default to largest allowed size (800px) as requested, but ensure it fits
    const maxAllowed = 800;
    const sidebarWidth = 256; // w-64
    const minChatWidth = 400; // Ensure chat has decent space
    
    const availableSpace = window.innerWidth - (window.innerWidth >= 768 ? sidebarWidth : 0);
    const width = Math.min(maxAllowed, availableSpace - minChatWidth);
    
    setRightPanelWidth(Math.max(300, width));
  }, []);

  const startResizing = useCallback(() => {
    setIsResizing(true);
  }, []);

  const stopResizing = useCallback(() => {
    setIsResizing(false);
  }, []);

  const resize = useCallback(
    (mouseMoveEvent: MouseEvent) => {
      if (isResizing) {
        const newWidth = window.innerWidth - mouseMoveEvent.clientX;
        // Limit the width between 300px and 800px
        if (newWidth > 300 && newWidth < 800) {
          setRightPanelWidth(newWidth);
        }
      }
    },
    [isResizing]
  );

  useEffect(() => {
    if (isResizing) {
      window.addEventListener("mousemove", resize);
      window.addEventListener("mouseup", stopResizing);
    }
    return () => {
      window.removeEventListener("mousemove", resize);
      window.removeEventListener("mouseup", stopResizing);
    };
  }, [isResizing, resize, stopResizing]);

  return (
    <main className="flex h-screen w-full overflow-hidden bg-white dark:bg-gray-950">
      {/* Left Panel - History */}
      <div className="w-64 flex-shrink-0 border-r border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 hidden md:flex flex-col">
        <HistoryPanel onSelectThread={handleThreadChange} currentThreadId={threadId} />
      </div>

      {/* Center Panel - Chat */}
      <div className="flex-1 min-w-0 bg-white dark:bg-gray-900">
        <ChatPanel 
          threadId={threadId} 
          setThreadId={handleThreadChange}
          setProposedActions={setProposedActions}
          proposedActions={proposedActions}
          messages={messages}
          setMessages={setMessages}
        />
      </div>

      {/* Resizer Handle */}
      <div
        className="w-1 bg-gray-200 dark:bg-gray-800 hover:bg-blue-500 cursor-col-resize transition-colors"
        onMouseDown={startResizing}
      />

      {/* Right Panel - Tasks/Context */}
      <div
        style={{ width: rightPanelWidth }}
        className="flex-shrink-0 bg-gray-50 dark:bg-gray-950 border-l border-gray-200 dark:border-gray-800"
      >
        <RightPanel 
          proposedActions={proposedActions} 
          onActionHandled={(data) => {
            if (data) {
              setMessages(data.messages);
              if (data.proposed_actions && data.proposed_actions.length > 0) {
                setProposedActions(data.proposed_actions);
              } else {
                setProposedActions([]);
              }
            } else {
              setProposedActions([]);
            }
          }}
          threadId={threadId}
        />
      </div>
    </main>
  );
}
