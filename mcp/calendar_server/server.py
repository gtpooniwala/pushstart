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
    """Find free time blocks of a specific duration."""
    service = get_service()
    if not service:
        return [{"error": "Calendar service not configured."}]
        
    # Simple implementation: Get events and find gaps
    # This is a naive implementation for demonstration
    events = list_events(days=days)
    if events and "error" in events[0]:
        return events

    # Logic to find gaps would go here
    # For now, returning a placeholder
    return [{"message": "Free block finding logic to be implemented"}]

# Expose the SSE ASGI app for Uvicorn
app = mcp.sse_app()

if __name__ == "__main__":
    mcp.run()
