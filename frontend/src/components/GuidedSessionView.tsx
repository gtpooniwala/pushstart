"use client";

import { useState } from "react";
import { Play, CheckCircle2, SkipForward, Clock } from "lucide-react";

interface Task {
  id: string;
  content: string;
  description?: string;
  priority: number;
}

interface GuidedSessionState {
  session_id: string;
  current_task: Task | null;
  remaining_tasks: number;
  completed_tasks: number;
}

export default function GuidedSessionView() {
  const [session, setSession] = useState<GuidedSessionState | null>(null);
  const [loading, setLoading] = useState(false);

  const startSession = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/guided/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ duration_minutes: 30, labels: ["admin"] })
      });
      if (res.ok) {
        const data = await res.json();
        setSession(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const completeTask = async () => {
    if (!session) return;
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/guided/${session.session_id}/complete`, {
        method: "POST"
      });
      if (res.ok) {
        const data = await res.json();
        setSession(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const skipTask = async () => {
    if (!session) return;
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/guided/${session.session_id}/skip`, {
        method: "POST"
      });
      if (res.ok) {
        const data = await res.json();
        setSession(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (!session) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <div className="text-center space-y-2">
          <h3 className="text-lg font-semibold">Ready to Focus?</h3>
          <p className="text-sm text-gray-500 max-w-xs">
            Start a guided session to power through your admin tasks one by one.
          </p>
        </div>
        <button
          onClick={startSession}
          disabled={loading}
          className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-full font-medium transition-colors disabled:opacity-50"
        >
          <Play className="w-5 h-5" />
          {loading ? "Starting..." : "Start Session"}
        </button>
      </div>
    );
  }

  if (!session.current_task) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center text-green-600 dark:text-green-400 mb-2">
          <CheckCircle2 className="w-8 h-8" />
        </div>
        <h3 className="text-xl font-bold">Session Complete!</h3>
        <p className="text-gray-500">
          You completed {session.completed_tasks} tasks.
        </p>
        <button
          onClick={() => setSession(null)}
          className="mt-4 text-blue-600 hover:underline"
        >
          Start New Session
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-8 h-full flex flex-col">
      <div className="flex justify-between items-center text-sm text-gray-500">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4" />
          <span>Focus Mode</span>
        </div>
        <div>
          {session.remaining_tasks} remaining
        </div>
      </div>

      <div className="flex-1 flex flex-col justify-center space-y-6">
        <div className="space-y-4">
          <div className="text-sm font-medium text-blue-600 dark:text-blue-400 uppercase tracking-wider">
            Current Task
          </div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 leading-tight">
            {session.current_task.content}
          </h2>
          {session.current_task.description && (
            <p className="text-gray-600 dark:text-gray-400 text-lg">
              {session.current_task.description}
            </p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <button
          onClick={skipTask}
          disabled={loading}
          className="flex items-center justify-center gap-2 px-4 py-4 border-2 border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 rounded-xl font-medium transition-colors disabled:opacity-50"
        >
          <SkipForward className="w-5 h-5" />
          Skip
        </button>
        <button
          onClick={completeTask}
          disabled={loading}
          className="flex items-center justify-center gap-2 px-4 py-4 bg-green-600 hover:bg-green-700 text-white rounded-xl font-medium transition-colors disabled:opacity-50 shadow-lg shadow-green-900/20"
        >
          <CheckCircle2 className="w-5 h-5" />
          Complete
        </button>
      </div>
    </div>
  );
}
