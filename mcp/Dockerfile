# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the MCP code
COPY todoist_server/ /app/todoist_server/
COPY calendar_server/ /app/calendar_server/
COPY gmail_server/ /app/gmail_server/

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Expose the port
EXPOSE 8000

# Command to run the application
# We assume server.py exposes 'app' which is the SSE ASGI app
CMD ["uvicorn", "todoist_server.server:app", "--host", "0.0.0.0", "--port", "8000"]
