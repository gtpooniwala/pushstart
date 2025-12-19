"use client";

import { useState, useEffect } from "react";
import { 
  CheckCircle2, 
  Circle, 
  Calendar, 
  Flag, 
  Plus, 
  Tag,
  AlertCircle
} from "lucide-react";
import { cn } from "@/lib/utils";

interface TaskDue {
  date: string;
  string: string;
  is_recurring: boolean;
}

interface Task {
  id: string;
  content: string;
  description?: string;
  is_completed: boolean;
  priority: number; // 1 (normal) to 4 (urgent)
  due?: TaskDue | null;
  labels: string[];
  project_id: string;
}

export default function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [newTask, setNewTask] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const res = await fetch("http://localhost:8000/tasks/");
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) {
          setTasks(data);
          setError(null);
        } else {
          console.error("Expected array of tasks, got:", data);
          setTasks([]);
          setError("Received invalid data format from server");
        }
      } else {
        setError("Failed to fetch tasks");
      }
    } catch (error) {
      console.error("Failed to fetch tasks", error);
      setError("Network error connecting to backend");
    } finally {
      setLoading(false);
    }
  };

  const addTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTask.trim()) return;

    try {
      const res = await fetch("http://localhost:8000/tasks/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: newTask }),
      });
      if (res.ok) {
        setNewTask("");
        fetchTasks();
      }
    } catch (error) {
      console.error("Failed to add task", error);
    }
  };

  const closeTask = async (id: string) => {
    // Optimistic update
    setTasks(tasks.filter(t => t.id !== id));
    try {
      const res = await fetch(`http://localhost:8000/tasks/${id}/close`, {
        method: "POST",
      });
      if (!res.ok) {
        fetchTasks(); // Revert on failure
      }
    } catch (error) {
      console.error("Failed to close task", error);
      fetchTasks(); // Revert on failure
    }
  };

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 4: return "text-red-600";
      case 3: return "text-orange-500";
      case 2: return "text-blue-500";
      default: return "text-gray-400";
    }
  };

  if (loading && tasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-white mb-2"></div>
        <p>Loading tasks...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-red-500 p-4 text-center">
        <AlertCircle className="w-8 h-8 mb-2" />
        <p>{error}</p>
        <button 
          onClick={fetchTasks}
          className="mt-4 px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-1">
      {/* Add Task Input */}
      <form onSubmit={addTask} className="relative group">
        <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
          <Plus className="h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
        </div>
        <input
          type="text"
          value={newTask}
          onChange={(e) => setNewTask(e.target.value)}
          placeholder="Add a task..."
          className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all shadow-sm text-sm"
        />
      </form>

      {/* Task List */}
      <div className="space-y-2">
        {tasks.length === 0 ? (
          <div className="text-center py-10 text-gray-500">
            <p>No tasks found. Enjoy your day! 🎉</p>
          </div>
        ) : (
          tasks.map((task) => (
            <div
              key={task.id}
              className="group relative p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-700 hover:shadow-sm transition-all duration-200"
            >
              <div className="flex items-start gap-3">
                {/* Checkbox */}
                <button
                  onClick={() => closeTask(task.id)}
                  className="mt-0.5 text-gray-400 hover:text-green-500 transition-colors flex-shrink-0"
                >
                  <Circle className="h-5 w-5" />
                </button>

                {/* Content Container */}
                <div className="flex-1 min-w-0 space-y-1.5">
                  {/* Header Row: Content + Priority */}
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100 leading-tight break-words">
                      {task.content}
                    </p>
                    {/* Priority Flag - Only show if priority > 1 */}
                    {task.priority > 1 && (
                      <Flag className={cn("h-3.5 w-3.5 flex-shrink-0 mt-0.5", getPriorityColor(task.priority))} />
                    )}
                  </div>

                  {/* Description */}
                  {task.description && (
                    <p className="text-xs text-gray-500 line-clamp-2 leading-relaxed">
                      {task.description}
                    </p>
                  )}

                  {/* Metadata Row */}
                  {(task.due || (task.labels && task.labels.length > 0)) && (
                    <div className="flex flex-wrap items-center gap-3 pt-1">
                      {task.due && (
                        <div className={cn(
                          "flex items-center gap-1.5 text-xs",
                          new Date(task.due.date) < new Date() ? "text-red-600 font-medium" : "text-gray-500"
                        )}>
                          <Calendar className="h-3.5 w-3.5" />
                          <span>{task.due.string}</span>
                        </div>
                      )}
                      
                      {task.labels && task.labels.length > 0 && (
                        <div className="flex items-center gap-2">
                          {task.labels.map(label => (
                            <span key={label} className="flex items-center gap-1 px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded-full text-[10px] font-medium text-gray-600 dark:text-gray-300">
                              <Tag className="h-3 w-3 opacity-70" />
                              {label}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
