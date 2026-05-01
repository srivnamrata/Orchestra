import asyncio
import json
from typing import Callable, Dict, List, Any

class EventBus:
    """
    An in-memory asynchronous event bus to decouple agents from presentation logic.
    """
    def __init__(self):
        self.subscribers: List[Callable] = []

    def subscribe(self, callback: Callable):
        """Register a listener for all events."""
        self.subscribers.append(callback)

    def unsubscribe(self, callback: Callable):
        """Remove a listener."""
        if callback in self.subscribers:
            self.subscribers.remove(callback)

    async def publish(self, event_type: str, data: Dict[str, Any]):
        """
        Emit an event to all subscribers.
        Agents call this instead of global 'emit_thought'.
        """
        tasks = []
        for callback in self.subscribers:
            if asyncio.iscoroutinefunction(callback):
                tasks.append(callback(event_type, data))
            else:
                callback(event_type, data)
        
        if tasks:
            await asyncio.gather(*tasks)