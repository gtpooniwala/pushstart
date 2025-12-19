"use client";

import { useState, useCallback, useEffect } from "react";
import ChatPanel from "@/components/ChatPanel";
import RightPanel from "@/components/RightPanel";
import HistoryPanel from "@/components/HistoryPanel";

export default function Home() {
  const [rightPanelWidth, setRightPanelWidth] = useState(450);
  const [isResizing, setIsResizing] = useState(false);

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
        <HistoryPanel />
      </div>

      {/* Center Panel - Chat */}
      <div className="flex-1 flex flex-col min-w-0 bg-white dark:bg-gray-950 relative">
        <ChatPanel />
      </div>

      {/* Resize Handle */}
      <div
        className={`w-1 cursor-col-resize hover:bg-blue-500 transition-colors flex-shrink-0 z-10 ${
          isResizing ? "bg-blue-500" : "bg-gray-200 dark:bg-gray-800"
        }`}
        onMouseDown={startResizing}
      />

      {/* Right Panel - Tasks & Context */}
      <div 
        style={{ width: rightPanelWidth }}
        className="flex-shrink-0 bg-gray-50 dark:bg-gray-900 flex flex-col"
      >
        <RightPanel />
      </div>
    </main>
  );
}
