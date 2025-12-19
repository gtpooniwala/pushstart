import { useState, useEffect } from "react";
import TaskList from "./TaskList";

interface RightPanelProps {
  proposedActions: any[];
  onActionHandled: () => void;
  threadId: string | null;
}

function ProposedActionCard({ action, isSelected, onToggle }: { action: any, isSelected?: boolean, onToggle?: () => void }) {
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
  } else if (name === "complete_task" && task_details) {
    content = (
      <div>
        <div className="text-xs text-green-600 uppercase tracking-wider mb-1">Completing Task</div>
        <div className="font-medium text-gray-700 dark:text-gray-300">{task_details.content}</div>
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
    <div className={`bg-white dark:bg-gray-800 p-4 rounded border mb-3 shadow-sm transition-colors ${
      isSelected 
        ? "border-blue-500 dark:border-blue-500 ring-1 ring-blue-500" 
        : "border-gray-200 dark:border-gray-700 opacity-60"
    }`}>
      <div className="flex items-start gap-3">
        {onToggle && (
          <div className="pt-1">
            <input 
              type="checkbox" 
              checked={isSelected} 
              onChange={onToggle}
              className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
            />
          </div>
        )}
        <div className="flex-1 min-w-0">
          {content}
        </div>
      </div>
    </div>
  );
}

export default function RightPanel({ proposedActions, onActionHandled, threadId }: RightPanelProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Initialize selection when actions change
  useEffect(() => {
    if (proposedActions && proposedActions.length > 0) {
      setSelectedIds(new Set(proposedActions.map(a => a.id)));
    } else {
      setSelectedIds(new Set());
    }
  }, [proposedActions]);

  const toggleSelection = (id: string) => {
    const newSet = new Set(selectedIds);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setSelectedIds(newSet);
  };

  const handleApprove = async () => {
    if (!threadId || !proposedActions.length) return;
    setIsProcessing(true);
    try {
      await fetch("http://localhost:8000/chat/approve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          thread_id: threadId,
          approved_tool_call_ids: Array.from(selectedIds)
        }),
      });
      setRefreshTrigger(prev => prev + 1);
      onActionHandled();
    } catch (e) {
      console.error("Error approving:", e);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReject = async () => {
    if (!threadId || !proposedActions.length) return;
    setIsProcessing(true);
    try {
      await fetch("http://localhost:8000/chat/reject", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          thread_id: threadId,
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
      
      {proposedActions && proposedActions.length > 0 && (
        <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border-b border-blue-100 dark:border-blue-800">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-blue-800 dark:text-blue-200">
              Proposed Actions ({proposedActions.length})
            </h3>
            <div className="text-xs text-blue-600 dark:text-blue-300">
              {selectedIds.size} selected
            </div>
          </div>
          
          <div className="max-h-[300px] overflow-y-auto mb-3 pr-1">
            {proposedActions.map((action) => (
              <ProposedActionCard 
                key={action.id} 
                action={action} 
                isSelected={selectedIds.has(action.id)}
                onToggle={() => toggleSelection(action.id)}
              />
            ))}
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleApprove}
              disabled={isProcessing || selectedIds.size === 0}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isProcessing ? "Processing..." : `Approve (${selectedIds.size})`}
            </button>
            <button
              onClick={handleReject}
              disabled={isProcessing}
              className="flex-1 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 px-3 py-1.5 rounded text-sm font-medium disabled:opacity-50"
            >
              Cancel All
            </button>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-4">
        <TaskList refreshTrigger={refreshTrigger} />
      </div>
    </div>
  );
}
