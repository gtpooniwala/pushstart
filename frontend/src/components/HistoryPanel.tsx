export default function HistoryPanel() {
  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-gray-200 dark:border-gray-800">
        <h2 className="font-semibold text-sm text-gray-500 uppercase tracking-wider">History</h2>
      </div>
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {/* Placeholder items */}
        <div className="p-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800 rounded cursor-pointer">
          Project Planning
        </div>
        <div className="p-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800 rounded cursor-pointer">
          Task Review
        </div>
        <div className="p-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800 rounded cursor-pointer">
          Weekly Sync
        </div>
      </div>
    </div>
  );
}
