from sqlmodel import select, delete
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timedelta, timezone
from app.models.event import Event
from app.mcp_client.calendar_client import calendar_client
import dateutil.parser

class CalendarService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_events(self, days: int = 7):
        """
        Fetch events from MCP, update local cache, and return cached events.
        Implements 'Write-Through' cache policy.
        """
        # 1. Fetch from MCP
        try:
            mcp_events = await calendar_client.list_events(days=days)
        except Exception as e:
            print(f"Error fetching from MCP: {e}")
            mcp_events = []
        
        # Check for error response from MCP
        if mcp_events and isinstance(mcp_events, list) and len(mcp_events) > 0 and "error" in mcp_events[0]:
             print(f"MCP returned error: {mcp_events[0]['error']}")
             mcp_events = []

        # 2. Clean up old events (older than today)
        # We keep events starting from today onwards
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Delete events that end before today
        statement = delete(Event).where(Event.end_time < today_start)
        await self.session.exec(statement)
        
        # 3. Upsert fetched events
        if mcp_events:
            for event_data in mcp_events:
                try:
                    # Parse dates (Google returns ISO strings)
                    start_dt = dateutil.parser.parse(event_data["start"])
                    end_dt = dateutil.parser.parse(event_data["end"])
                    
                    # Convert to naive UTC for Postgres TIMESTAMP WITHOUT TIME ZONE
                    if start_dt.tzinfo:
                        start_dt = start_dt.astimezone(timezone.utc).replace(tzinfo=None)
                    if end_dt.tzinfo:
                        end_dt = end_dt.astimezone(timezone.utc).replace(tzinfo=None)
                    
                    # Check if exists
                    existing = await self.session.get(Event, event_data["id"])
                    if existing:
                        existing.summary = event_data["summary"]
                        existing.description = event_data.get("description")
                        existing.start_time = start_dt
                        existing.end_time = end_dt
                        existing.raw_data = event_data
                        self.session.add(existing)
                    else:
                        event = Event(
                            id=event_data["id"],
                            summary=event_data["summary"],
                            description=event_data.get("description"),
                            start_time=start_dt,
                            end_time=end_dt,
                            raw_data=event_data
                        )
                        self.session.add(event)
                except Exception as e:
                    print(f"Error processing event {event_data.get('id')}: {e}")
        
        await self.session.commit()
        
        # 4. Return from DB (sorted)
        # We want events from now up to days
        # Actually, let's just return all future events we have, or limit by the requested window
        end_window = now + timedelta(days=days)
        
        statement = select(Event).where(Event.start_time >= today_start).where(Event.start_time <= end_window).order_by(Event.start_time)
        results = await self.session.exec(statement)
        return results.all()

    async def create_event(self, summary, start_time, end_time, description=""):
        # 1. Create in MCP
        result = await calendar_client.create_event(summary, start_time, end_time, description)
        
        if "error" in result:
            return result

        # 2. Add to DB
        try:
            start_dt = dateutil.parser.parse(start_time)
            end_dt = dateutil.parser.parse(end_time)
            
            # Convert to naive UTC
            if start_dt.tzinfo:
                start_dt = start_dt.astimezone(timezone.utc).replace(tzinfo=None)
            if end_dt.tzinfo:
                end_dt = end_dt.astimezone(timezone.utc).replace(tzinfo=None)
            
            event = Event(
                id=result["id"],
                summary=result["summary"],
                description=description,
                start_time=start_dt,
                end_time=end_dt,
                status=result.get("status"),
                html_link=result.get("link"),
                raw_data=result
            )
            self.session.add(event)
            await self.session.commit()
            await self.session.refresh(event)
            return event
        except Exception as e:
            print(f"Error saving created event to DB: {e}")
            # Return the MCP result even if DB save fails
            return result

    async def find_free_blocks(self, duration_minutes: int = 60, days: int = 3):
        # For now, just pass through to MCP
        return await calendar_client.find_free_blocks(duration_minutes, days)
