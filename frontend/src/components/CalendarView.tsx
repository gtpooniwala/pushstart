"use client";

import { useState, useEffect } from "react";
import { RefreshCw, Calendar as CalendarIcon, Clock } from "lucide-react";

interface CalendarEvent {
  id: string;
  summary: string;
  start_time: string; // ISO string
  end_time: string;   // ISO string
  description?: string;
}

interface CalendarViewProps {
  refreshTrigger?: number;
}

export default function CalendarView({ refreshTrigger = 0 }: CalendarViewProps) {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchEvents = async () => {
    setLoading(true);
    setError(null);
    try {
      // We'll need to add this endpoint to the backend
      const res = await fetch("http://localhost:8000/calendar/events?days=7");
      if (res.ok) {
        const data = await res.json();
        setEvents(data);
      } else {
        setError("Failed to fetch calendar events");
      }
    } catch (e) {
      console.error("Error fetching events:", e);
      setError("Failed to connect to server");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [refreshTrigger]);

  // Group events by day
  const eventsByDay = events.reduce((acc, event) => {
    const date = new Date(event.start_time).toLocaleDateString(undefined, { 
      weekday: 'short', 
      month: 'short', 
      day: 'numeric' 
    });
    if (!acc[date]) acc[date] = [];
    acc[date].push(event);
    return acc;
  }, {} as Record<string, CalendarEvent[]>);

  // Sort dates
  const sortedDates = Object.keys(eventsByDay).sort((a, b) => {
    // We need to parse the date string back to a timestamp for sorting
    // Since the key format depends on locale, it's safer to pick the first event's start time
    const eventA = eventsByDay[a][0];
    const eventB = eventsByDay[b][0];
    return new Date(eventA.start_time).getTime() - new Date(eventB.start_time).getTime();
  });

  if (loading && events.length === 0) {
    return (
      <div className="flex justify-center items-center h-64 text-gray-400">
        <RefreshCw className="w-6 h-6 animate-spin mr-2" />
        Loading calendar...
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-center text-red-500">
        <p>{error}</p>
        <button 
          onClick={fetchEvents}
          className="mt-2 text-sm underline hover:text-red-600"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4 p-1">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <CalendarIcon className="w-5 h-5" />
          Next 7 Days
        </h2>
        <button 
          onClick={fetchEvents} 
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors" 
          title="Refresh Calendar"
        >
           <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {events.length === 0 ? (
        <div className="text-center py-10 text-gray-500">
          <p>No upcoming events found.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {sortedDates.map(date => (
            <div key={date}>
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2 sticky top-0 bg-gray-50 dark:bg-gray-950 py-1">
                {date}
              </h3>
              <div className="space-y-2">
                {eventsByDay[date].map(event => (
                  <div 
                    key={event.id}
                    className="bg-white dark:bg-gray-800 p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-700 transition-colors"
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex flex-col items-center min-w-[60px] text-xs text-gray-500 pt-1">
                        <span className="font-medium text-gray-900 dark:text-gray-100">
                          {new Date(event.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                        <span className="h-4 w-px bg-gray-200 dark:bg-gray-700 my-1"></span>
                        <span>
                          {new Date(event.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-900 dark:text-gray-100 truncate">
                          {event.summary}
                        </div>
                        {event.description && (
                          <div className="text-xs text-gray-500 mt-1 line-clamp-2">
                            {event.description}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
