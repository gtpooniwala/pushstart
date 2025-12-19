import TaskList from "./TaskList";

export default function RightPanel() {
  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-gray-200 dark:border-gray-800">
        <h2 className="font-semibold text-lg">Tasks</h2>
      </div>
      <div className="flex-1 overflow-y-auto p-4">
        <TaskList />
      </div>
    </div>
  );
}
