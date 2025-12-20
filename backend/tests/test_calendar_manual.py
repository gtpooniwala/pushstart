import asyncio
import os
from app.mcp_client.calendar_client import calendar_client

async def test_calendar():
    print("Testing find_free_blocks...")
    blocks = await calendar_client.find_free_blocks(duration_minutes=30, days=2)
    print(f"Free blocks: {blocks}")

    if blocks and isinstance(blocks, list) and "error" not in blocks[0]:
        # Try to create an event in the first free block
        block = blocks[0]
        start = block["start"]
        end = block["end"]
        # Just take 30 mins from start
        # We need to parse ISO string to add time, but for simplicity let's just use the block start
        # and calculate end time manually or just use the block end if it matches duration
        
        print(f"Creating event at {start}...")
        # Note: This will actually create an event in your calendar!
        # Uncomment to test creation
        # result = await calendar_client.create_event(
        #     summary="Test Event from Pushstart",
        #     start_time=start,
        #     end_time=end,
        #     description="Automated test event"
        # )
        # print(f"Creation result: {result}")
    else:
        print("No free blocks found or error occurred.")

if __name__ == "__main__":
    asyncio.run(test_calendar())
