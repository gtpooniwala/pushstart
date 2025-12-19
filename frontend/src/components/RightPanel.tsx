import { useState } from "react";
import TaskList from "./TaskList";

interface RightPanelProps {
  proposedAction: any;
  onActionHandled: () => void;
  threadId: string | null;
}

function ProposedActionCard({ action }: { action: any }) {
  const { name, args, task_details } = action;
  
  // Helper to render a field change
  const renderChange = (label: string, oldVal: any, newVal: any) => {
    if (newVal === undefined || newVal === null) return null;
    if (oldVal === newVal) return null;
    
    return (
      <div className="mb-2 text-sm">
        <span className="font-semibold text-gray-600 dark:text-gray-400">{label}:</span>
        <div className="flex items-center gap-2 mt-1 flex-wrap">
          {oldVal !== undefined && (
            <span className="line-through text-red-500 bg-red-50 dark:bg-red-900/20 px-1 rounded">
              {String(oldVal)}
            </span>
          )}
          {oldVal !== undefined && <span className="text-gray-400">→</span>}
          <span className="text-green-600 bg-green-50 dark:bg-green-900/20 px-1 rounded font-medium">
            {String(newVal)}
          </span>
        </div>
      </div>
    );
  };

  let content = null;

  if (name === "update_task" && task_details) {
    content = (
      <div>
        <div className="mb-3 pb-2 border-b border-gray-200 dark:border-gray-700">
          <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Updating Task</div>
          <div className="font-medium">{task_details.content}</div>
        </div>
        {renderChange("Content", task_details.content, args.content)}
        {renderChange("Description", task_details.description, args.description)}
        {renderChange("Due Date", task_details.due_string || task_details.due_date || task_details.due?.string || task_details.due?.date, args.due_string)}
        {renderChange("Priority", task_details.priority, args.priority)}
      </div>
    );
  } else if (name === "delete_task" && task_details) {
    content = (
      <div>
        <div className="text-xs text-red-500 uppercase tracking-wider mb-1">Deleting Task</div>
        <div className="font-medium line-through text-gray-500">{task_details.content}</div>
        {task_details.description && (
           <div className="text-sm text-gray-400 mt-1">{task_details.description}</div>
        )}
      </div>
    );
  } else if (name === "create_task") {
    content = (
      <div>
        <div className="text-xs text-green-500 uppercase tracking-wider mb-1">Creating Task</div>
        <div className="font-medium text-lg mb-2">{args.content}</div>
        {args.description && (
          <div className="text-sm text-gray-600 dark:text-gray-300 mb-2">
            <span className="font-semibold">Desc:</span> {args.description}
          </div>
        )}
        {args.due_string && (
          <div className="text-sm text-gray-600 dark:text-gray-300 mb-2">
            <span className="font-semibold">Due:</span> {args.due_string}
          </div>
        )}
        {args.priority && (
          <div className="text-sm text-gray-600 dark:text-gray-300">
            <span className="font-semibold">Priority:</span> {args.priority}
          </div>
        )}
      </div>
    );
  } else {
    // Fallback
    content = (
      <div className="font-mono text-sm text-gray-700 dark:text-gray-300">
        <span className="font-bold text-purple-600 dark:text-purple-400">
          {name}
        </span>
        <pre className="mt-1 text-xs overflow-x-auto">
          {JSON.stringify(args, null, 2)}
        </pre>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded border border-blue-200 dark:border-blue-800 mb-3 shadow-sm">
      {content}
    </div>
  );
}

export default function RightPanel({ proposedAction, onActionHandled, threadId }: RightPanelProps) {
  const [isProcessing, setIsProcessing] = useState(false);

  const handleApprove = async () => {
    if (!threadId || !proposedAction) return;
    setIsProcessing(true);
    try {
      await fetch("http://localhost:8000/chat/approve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          thread_id: threadId,
          tool_call_id: proposedAction.id
        }),
      });
      onActionHandled();
    } catch (e) {
      console.error("Error approving:", e);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReject = async () => {
    if (!threadId || !proposedAction) return;
    setIsProcessing(true);
    try {
      await fetch("http://localhost:8000/chat/reject", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          thread_id: threadId,
          tool_call_id: proposedAction.id,
          reason: "Rejected via UI"
        }),
      });
      onActionHandled();
    } catch (e) {
      console.error("Error rejecting:", e);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-gray-200 dark:border-gray-800">
        <h2 className="font-semibold text-lg">Tasks</h2>
      </div>
      
      {proposedAction && (
        <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border-b border-blue-100 dark:border-blue-800">
          <h3 className="text-sm font-semibold text-blue-800 dark:text-blue-200 mb-2">
            Proposed Action
          </h3>
          <ProposedActionCard action={proposedAction} />
          <div className="flex gap-2">
            <button
              onClick={handleApprove}
              disabled={isProcessing}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded text-sm font-medium disabled:opacity-50"
            >
              {isProcessing ? "Processing..." : "Approve"}
            </button>
            <button
              onClick={handleReject}
              disabled={isProcessing}
              className="flex-1 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 px-3 py-1.5 rounded text-sm font-medium disabled:opacity-50"
            >
              Reject
            </button>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-4">
        <TaskList />
      </div>
    </div>
  );
}
