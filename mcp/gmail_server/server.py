from mcp.server.fastmcp import FastMCP
import os
import base64
from typing import List, Optional
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText

# Load .env
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
load_dotenv(os.path.join(root_dir, ".env"))

mcp = FastMCP("gmail")

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose'
]

def get_service():
    """Shows basic usage of the Gmail API."""
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), 'token.json')
    creds_path = os.path.join(os.path.dirname(__file__), 'credentials.json')

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists(creds_path):
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            else:
                return None

    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f"Error building service: {e}")
        return None

@mcp.tool()
def list_emails(max_results: int = 10, query: str = "") -> List[dict]:
    """List emails matching a query (e.g., 'is:unread')."""
    service = get_service()
    if not service:
        return [{"error": "Gmail service not configured. Please add credentials.json."}]

    try:
        results = service.users().messages().list(userId='me', maxResults=max_results, q=query).execute()
        messages = results.get('messages', [])
        
        email_list = []
        for msg in messages:
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            payload = txt.get('payload', {})
            headers = payload.get('headers', [])
            
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
            
            email_list.append({
                "id": msg['id'],
                "threadId": msg['threadId'],
                "subject": subject,
                "from": sender,
                "date": date,
                "snippet": txt.get('snippet', '')
            })
            
        return email_list
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def create_draft(to: str, subject: str, body: str) -> dict:
    """Create a draft email."""
    service = get_service()
    if not service:
        return {"error": "Gmail service not configured."}

    try:
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body = {'message': {'raw': raw}}
        
        draft = service.users().drafts().create(userId='me', body=body).execute()
        return {
            "id": draft['id'],
            "message": draft['message'],
            "status": "Draft created successfully"
        }
    except Exception as e:
        return {"error": str(e)}

# Expose the SSE app for Uvicorn
app = mcp.sse_app()
