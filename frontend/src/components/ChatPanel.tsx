export default function ChatPanel() {
  return (
    <div className="flex flex-col h-full p-4">
      <div className="flex-1 flex items-center justify-center text-gray-400">
        <p>Chat Interface (Coming in Phase 2)</p>
      </div>
      <div className="mt-4">
        <input
          type="text"
          disabled
          placeholder="Type a message..."
          className="w-full p-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 disabled:opacity-50"
        />
      </div>
    </div>
  );
}
