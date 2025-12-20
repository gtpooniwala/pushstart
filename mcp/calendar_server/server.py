from mcp.server.fastmcp import FastMCP
import os
import datetime
from typing import List, Optional
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Load .env
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
load_dotenv(os.path.join(root_dir, ".env"))

mcp = FastMCP("calendar")

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_service():
    """Shows basic usage of the Google Calendar API."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_path = os.path.join(os.path.dirname(__file__), 'token.json')
    creds_path = os.path.join(os.path.dirname(__file__), 'credentials.json')

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists(creds_path):
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            else:
                # If no credentials, return None (mock mode or error)
                return None

    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Error building service: {e}")
        return None

@mcp.tool()
def list_events(days: int = 7) -> List[dict]:
    """List upcoming calendar events."""
    service = get_service()
    if not service:
        return [{"error": "Calendar service not configured. Please add credentials.json."}]

    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    end_time = (datetime.datetime.utcnow() + datetime.timedelta(days=days)).isoformat() + 'Z'
    
    try:
        events_result = service.events().list(
            calendarId='primary', 
            timeMin=now,
            timeMax=end_time,
            maxResults=50, 
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        
        results = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            results.append({
                "id": event['id'],
                "summary": event.get('summary', 'No Title'),
                "start": start,
                "end": event['end'].get('dateTime', event['end'].get('date')),
                "description": event.get('description', '')
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def create_event(summary: str, start_time: str, end_time: str, description: str = "") -> dict:
    """Create a new calendar event. Times must be ISO format strings."""
    service = get_service()
    if not service:
        return {"error": "Calendar service not configured."}

    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'UTC',
        },
    }

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        return {
            "id": event.get('id'),
            "summary": event.get('summary'),
            "status": "created",
            "link": event.get('htmlLink')
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def find_free_blocks(duration_minutes: int = 60, days: int = 3) -> List[dict]:
    """Find free time blocks of a specific duration within working hours (9 AM - 5 PM)."""
    service = get_service()
    if not service:
        return [{"error": "Calendar service not configured."}]
        
    # Get calendar timezone
    try:
        cal_setting = service.calendars().get(calendarId='primary').execute()
        time_zone = cal_setting.get('timeZone', 'UTC')
    except:
        time_zone = 'UTC'

    import pytz
    tz = pytz.timezone(time_zone)
    
    now = datetime.datetime.now(tz)
    free_blocks = []

    # Iterate through days
    for i in range(days):
        current_day = now + datetime.timedelta(days=i)
        
        # Define working hours for this day (9 AM to 5 PM)
        work_start = current_day.replace(hour=9, minute=0, second=0, microsecond=0)
        work_end = current_day.replace(hour=17, minute=0, second=0, microsecond=0)
        
        # Skip if work_end is in the past
        if work_end < now:
            continue
            
        # Adjust work_start if today and already past 9 AM
        if i == 0 and now > work_start:
            work_start = now
            # Round up to next 30 mins
            if work_start.minute < 30:
                work_start = work_start.replace(minute=30, second=0, microsecond=0)
            else:
                work_start = (work_start + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

        if work_start >= work_end:
            continue

        # Fetch events for this day
        day_start_iso = current_day.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        day_end_iso = current_day.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()
        
        events_result = service.events().list(
            calendarId='primary', 
            timeMin=day_start_iso,
            timeMax=day_end_iso,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        # Find gaps
        last_end = work_start
        
        for event in events:
            # Parse event times
            start_str = event['start'].get('dateTime')
            if not start_str: continue # All-day event (skip for now or treat as blocking?)
            
            # Handle 'Z' for UTC
            if start_str.endswith('Z'):
                start_str = start_str[:-1] + '+00:00'
                
            event_start = datetime.datetime.fromisoformat(start_str)
            
            # Normalize timezone
            if event_start.tzinfo is None:
                event_start = tz.localize(event_start)
            else:
                event_start = event_start.astimezone(tz)

            # If event starts after last_end, we have a gap
            if event_start > last_end:
                gap_duration = (event_start - last_end).total_seconds() / 60
                if gap_duration >= duration_minutes:
                    free_blocks.append({
                        "start": last_end.isoformat(),
                        "end": event_start.isoformat(),
                        "duration_minutes": int(gap_duration)
                    })
            
            # Update last_end
            end_str = event['end'].get('dateTime')
            if end_str:
                if end_str.endswith('Z'):
                    end_str = end_str[:-1] + '+00:00'
                event_end = datetime.datetime.fromisoformat(end_str)
                if event_end.tzinfo is None:
                    event_end = tz.localize(event_end)
                else:
                    event_end = event_end.astimezone(tz)
                
                if event_end > last_end:
                    last_end = event_end

        # Check gap after last event until work_end
        if last_end < work_end:
            gap_duration = (work_end - last_end).total_seconds() / 60
            if gap_duration >= duration_minutes:
                free_blocks.append({
                    "start": last_end.isoformat(),
                    "end": work_end.isoformat(),
                    "duration_minutes": int(gap_duration)
                })

    return free_blocks

# Expose the SSE ASGI app for Uvicorn
app = mcp.sse_app()

if __name__ == "__main__":
    mcp.run()
