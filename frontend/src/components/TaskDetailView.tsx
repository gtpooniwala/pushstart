"use client";

import { useState, useEffect, useRef } from "react";
import { 
  ArrowLeft, 
  Calendar, 
  Flag, 
  Tag, 
  CheckCircle2, 
  Circle,
  Clock
} from "lucide-react";
import { cn } from "@/lib/utils";
import LinkifiedText from "./LinkifiedText";

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
  priority: number;
  due?: TaskDue | null;
  due_string?: string | null;
  due_date?: string | null;
  labels: string[];
  project_id: string;
  raw_data?: any;
}

interface TaskDetailViewProps {
  task: Task;
  onBack: () => void;
  onUpdate: (taskId: string, updates: Partial<Task>) => Promise<void>;
  onComplete: (taskId: string) => Promise<void>;
}

export default function TaskDetailView({ task, onBack, onUpdate, onComplete }: TaskDetailViewProps) {
  const [content, setContent] = useState(task.content);
  const [description, setDescription] = useState(task.description || "");
  const [dueString, setDueString] = useState(task.due_string || task.due?.string || task.raw_data?.due?.string || "");
  const [dueDate, setDueDate] = useState(task.due?.date || task.due_date || "");

  useEffect(() => {
    setContent(task.content);
    setDescription(task.description || "");
    setDueString(task.due_string || task.due?.string || task.raw_data?.due?.string || "");
    setDueDate(task.due?.date || task.due_date || "");
  }, [task]);
  
  // Editing states
  const [isEditingContent, setIsEditingContent] = useState(false);
  const [isEditingDescription, setIsEditingDescription] = useState(false);
  const [isEditingDue, setIsEditingDue] = useState(false);

  const contentInputRef = useRef<HTMLInputElement>(null);
  const descInputRef = useRef<HTMLTextAreaElement>(null);
  const dueInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditingContent) contentInputRef.current?.focus();
    if (isEditingDescription) descInputRef.current?.focus();
    if (isEditingDue) dueInputRef.current?.focus();
  }, [isEditingContent, isEditingDescription, isEditingDue]);

  const handleSaveContent = async () => {
    if (content !== task.content) {
      await onUpdate(task.id, { content });
    }
    setIsEditingContent(false);
  };

  const handleSaveDescription = async () => {
    if (description !== task.description) {
      await onUpdate(task.id, { description });
    }
    setIsEditingDescription(false);
  };

  const handleSaveDue = async () => {
    const currentDueDate = task.due?.date || task.due_date;
    if (dueDate !== currentDueDate) {
      // Send due_string update (Todoist accepts YYYY-MM-DD as due_string)
      await onUpdate(task.id, { due_string: dueDate } as any);
    }
    setIsEditingDue(false);
  };

  const handlePriorityChange = async (newPriority: number) => {
    await onUpdate(task.id, { priority: newPriority });
  };

  const getPriorityColor = (p: number) => {
    switch (p) {
      case 4: return "text-red-600 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800";
      case 3: return "text-orange-500 bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800";
      case 2: return "text-blue-500 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800";
      default: return "text-gray-500 bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700";
    }
  };

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="flex items-center gap-3 p-4 border-b border-gray-200 dark:border-gray-800">
        <button 
          onClick={onBack}
          className="p-2 -ml-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div className="flex-1" />
        <button
          onClick={() => onComplete(task.id)}
          className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-green-700 bg-green-50 hover:bg-green-100 dark:text-green-400 dark:bg-green-900/20 dark:hover:bg-green-900/30 rounded-lg transition-colors border border-green-200 dark:border-green-800"
        >
          <CheckCircle2 className="h-4 w-4" />
          Complete
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-8">
        {/* Title Section */}
        <div className="space-y-2">
          {isEditingContent ? (
            <input
              ref={contentInputRef}
              type="text"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              onBlur={handleSaveContent}
              onKeyDown={(e) => e.key === 'Enter' && handleSaveContent()}
              className="w-full text-2xl font-semibold bg-transparent border-b-2 border-blue-500 outline-none px-1 py-0.5"
            />
          ) : (
            <h1 
              onClick={() => setIsEditingContent(true)}
              className="text-2xl font-semibold text-gray-900 dark:text-gray-100 cursor-text hover:bg-gray-50 dark:hover:bg-gray-800/50 rounded px-1 -mx-1 transition-colors break-words whitespace-pre-wrap"
            >
              <LinkifiedText text={content} />
            </h1>
          )}
        </div>

        {/* Properties Grid */}
        <div className="grid grid-cols-2 gap-4">
          {/* Priority */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
              <Flag className="h-3.5 w-3.5" />
              Priority
            </label>
            <div className="flex gap-2">
              {[1, 2, 3, 4].map((p) => (
                <button
                  key={p}
                  onClick={() => handlePriorityChange(p)}
                  className={cn(
                    "h-8 w-8 flex items-center justify-center rounded-full text-sm font-medium transition-all border",
                    task.priority === p 
                      ? getPriorityColor(p)
                      : "text-gray-400 border-transparent hover:bg-gray-100 dark:hover:bg-gray-800"
                  )}
                >
                  P{p}
                </button>
              ))}
            </div>
          </div>

          {/* Due Date */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
              <Calendar className="h-3.5 w-3.5" />
              Due Date
            </label>
            {isEditingDue ? (
              <input
                ref={dueInputRef}
                type="date"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                onBlur={handleSaveDue}
                onKeyDown={(e) => e.key === 'Enter' && handleSaveDue()}
                className="w-full text-sm bg-transparent border-b-2 border-blue-500 outline-none py-1"
              />
            ) : (
              <div 
                onClick={() => setIsEditingDue(true)}
                className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 rounded py-1 px-2 -mx-2 transition-colors"
              >
                <Clock className="h-4 w-4 text-gray-400" />
                {dueString || dueDate || "No due date"}
              </div>
            )}
          </div>
        </div>

        {/* Description Section */}
        <div className="space-y-2">
          <label className="text-xs font-medium text-gray-500 uppercase tracking-wider">
            Description
          </label>
          {isEditingDescription ? (
            <textarea
              ref={descInputRef}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              onBlur={handleSaveDescription}
              rows={6}
              className="w-full text-sm leading-relaxed bg-gray-50 dark:bg-gray-800 rounded-lg p-3 border border-blue-500 outline-none resize-none"
            />
          ) : (
            <div 
              onClick={() => setIsEditingDescription(true)}
              className={cn(
                "text-sm leading-relaxed cursor-text hover:bg-gray-50 dark:hover:bg-gray-800/50 rounded p-2 -m-2 transition-colors min-h-[100px] break-words whitespace-pre-wrap",
                !description && "text-gray-400 italic"
              )}
            >
              {description ? <LinkifiedText text={description} /> : "Add a description..."}
            </div>
          )}
        </div>

        {/* Labels (Read-only for now as per MVP) */}
        {task.labels && task.labels.length > 0 && (
          <div className="space-y-2">
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
              <Tag className="h-3.5 w-3.5" />
              Labels
            </label>
            <div className="flex flex-wrap gap-2">
              {task.labels.map(label => (
                <span key={label} className="px-2.5 py-1 bg-gray-100 dark:bg-gray-800 rounded-full text-xs font-medium text-gray-600 dark:text-gray-300">
                  {label}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
