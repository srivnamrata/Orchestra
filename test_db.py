import asyncio
from backend.database import get_all_tasks
try:
    print(get_all_tasks(user_id="test"))
except Exception as e:
    print(f"Error: {e}")
