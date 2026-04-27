"""
Pub/Sub Service for Real-time Agent Communication
Enables Critic Agent to monitor workflow progress in real-time via Google Cloud Pub/Sub.
"""

import json
import asyncio
from typing import Dict, Callable, Optional, Any
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class MockPubSubService:
    """
    Mock Pub/Sub for local development.
    In production, replace with google.cloud.pubsub_v1
    """
    
    def __init__(self):
        self.topics: Dict[str, list] = defaultdict(list)
        self.subscribers: Dict[str, list] = defaultdict(list)
    
    async def publish(self, topic: str, message: Dict[str, Any]):
        """
        Publish a message to a topic.
        Asynchronously notifies all subscribers.
        """
        logger.info(f"📢 Publishing to {topic}: {message}")
        
        self.topics[topic].append(message)
        
        # Notify all subscribers
        tasks = []
        for callback, context in self.subscribers[topic]:
            task = asyncio.create_task(callback(message, context))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def subscribe(self, topic: str, callback: Callable, context: Dict = None):
        """
        Subscribe to a topic.
        Callback is called whenever a message is published.
        """
        logger.info(f"📡 Subscribing to {topic}")
        self.subscribers[topic].append((callback, context or {}))
    
    async def get_topic_messages(self, topic: str) -> list:
        """Retrieve all messages published to a topic"""
        return self.topics.get(topic, [])


class GCPPubSubService:
    """
    Real Google Cloud Pub/Sub Service.
    Use this in production with actual GCP credentials.
    """
    
    def __init__(self, project_id: str):
        from google.cloud import pubsub_v1
        
        self.project_id = project_id
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscriptions: Dict[str, Any] = {}
    
    async def publish(self, topic: str, message: Dict[str, Any]):
        """Publish message to GCP Pub/Sub topic"""
        topic_path = self.publisher.topic_path(self.project_id, topic)
        message_json = json.dumps(message)
        
        try:
            future = self.publisher.publish(topic_path, message_json.encode('utf-8'))
            message_id = future.result()
            logger.info(f"Published message {message_id} to {topic}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to publish to GCP topic {topic}. Missing topic? Error: {e}")
    
    async def subscribe(self, topic: str, callback: Callable, context: Dict = None):
        """Subscribe to GCP Pub/Sub topic.

        GCP delivers messages on a background thread, not the event loop thread.
        asyncio.run() would create a *new* loop and raise RuntimeError because
        uvicorn's loop is already running.  We capture the running loop here
        (inside the async subscribe method) and use run_coroutine_threadsafe so
        the callback executes on the correct loop.  ack() is called only after a
        successful callback; nack() lets Pub/Sub redeliver on failure.
        """
        subscription_path = self.subscriber.subscription_path(
            self.project_id, f"{topic}-subscription"
        )
        loop = asyncio.get_event_loop()

        def message_callback(message):
            try:
                data    = json.loads(message.data.decode("utf-8"))
                future  = asyncio.run_coroutine_threadsafe(
                    callback(data, context or {}), loop
                )
                future.result(timeout=30)   # propagate exceptions; let Pub/Sub retry on timeout
                message.ack()
            except Exception as e:
                logger.error(f"Pub/Sub callback failed for topic {topic}: {e}")
                message.nack()

        try:
            streaming_pull_future = self.subscriber.subscribe(
                subscription_path, callback=message_callback
            )
            self.subscriptions[topic] = streaming_pull_future
            logger.info(f"Subscribed to {topic}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to subscribe to GCP topic {topic}. Missing subscription? Error: {e}")


def create_pubsub_service(use_mock: bool = True, project_id: str = None) -> MockPubSubService:
    """Factory function to create appropriate Pub/Sub service"""
    if use_mock:
        return MockPubSubService()
    else:
        if not project_id:
            raise ValueError("GCP project_id required for real Pub/Sub")
        return GCPPubSubService(project_id)
