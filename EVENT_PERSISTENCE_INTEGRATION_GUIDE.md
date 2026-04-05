# Event Persistence Integration Guide

## Overview

The event persistence system logs all system events to Firestore for audit trails, compliance, and debugging.

## Quick Start

### 1. Initialize Event Logger

In your main FastAPI app or orchestrator:

```python
from firestore_adapter import FirestoreAdapter
from event_persistence import initialize_event_logging

# Create Firestore adapter
adapter = FirestoreAdapter(project_id="your-gcp-project", use_mock=False)

# Initialize event logging system
event_logger, event_emitter = initialize_event_logging(adapter)

# Start the background processor
await event_logger.start(flush_interval_seconds=5)
```

### 2. Log Events in MCP Servers

Update each MCP server to log events. Example from `task_mcp_server.py`:

```python
from event_persistence import get_event_logger

class TaskMCPServer(BaseMCPServer):
    async def _create_task(self, title: str, project_id: str, **kwargs):
        event_logger = get_event_logger()
        
        try:
            task = await self.agent.create_task(title=title, project_id=project_id, **kwargs)
            
            # Log successful event
            await event_logger.log_event(
                event_type="task_created",
                source="task_agent",
                action="create",
                resource_id=task.get("id"),
                resource_type="task",
                data={"title": title, "project_id": project_id},
                result=task
            )
            
            return task
            
        except Exception as e:
            # Log error event
            await event_logger.log_event(
                event_type="task_creation_failed",
                source="task_agent",
                action="create",
                resource_type="task",
                data={"title": title},
                error=str(e)
            )
            raise
```

### 3. Log Access Events

For compliance and audit trails:

```python
from event_persistence import get_event_logger

event_logger = get_event_logger()

# Log when a user accesses a resource
await event_logger.log_access(
    user_id="user123",
    resource_id="task_456",
    resource_type="task",
    access_type="read",
    ip_address="192.168.1.1",
    duration_ms=150,
    success=True
)
```

### 4. Query Events

```python
from event_persistence import get_event_logger

event_logger = get_event_logger()

# Get all events from a source
task_events = await event_logger.get_events_by_source("task_agent")

# Get events for a user
user_events = await event_logger.get_events_by_user("user123")

# Get events for a resource
resource_events = await event_logger.get_events_by_resource("task_456")

# Replay events in a time range
past_events = await event_logger.replay_events(
    start_time="2024-01-01T00:00:00",
    end_time="2024-01-02T00:00:00"
)
```

### 5. Analyze Events

```python
from event_persistence import EventAggregator, get_event_logger

event_logger = get_event_logger()
aggregator = EventAggregator(event_logger)

# Get activity summary for last 24 hours
summary = await aggregator.get_activity_summary(hours=24)

# Get user activity
user_activity = await aggregator.get_user_activity("user123", hours=24)

# Get health events (failures) from last hour
health = await aggregator.get_health_events(hours=1)
```

## Event Types

### Task Events
- `task_created` - New task created
- `task_updated` - Task updated
- `task_deleted` - Task deleted
- `task_assigned` - Task assigned to user
- `task_completed` - Task marked complete
- `task_creation_failed` - Error creating task

### Calendar Events
- `event_created` - Calendar event created
- `event_updated` - Calendar event updated
- `event_deleted` - Calendar event deleted
- `attendee_added` - Attendee added to event
- `attendee_removed` - Attendee removed from event

### Note Events
- `note_created` - Note created
- `note_updated` - Note updated
- `note_deleted` - Note deleted
- `note_searched` - Note searched
- `note_linked` - Notes linked together

### Access Events
- `data_read` - Data accessed for reading
- `data_written` - Data modified
- `data_deleted` - Data deleted
- `data_shared` - Data shared with others

## Firestore Collections

### events Collection
Stores all system events for audit trail.

**Fields**:
- `id`: Unique event ID
- `event_type`: Type of event (task_created, etc.)
- `source`: Agent/service generating the event (task_agent, etc.)
- `user_id`: User who triggered the event
- `resource_id`: Resource affected (task_123, etc.)
- `resource_type`: Type of resource (task, note, event, etc.)
- `action`: Action performed (create, update, delete, read)
- `status`: Event status (processed, failed, pending_retry)
- `timestamp`: When the event occurred
- `data`: Input data for the operation
- `result`: Result of the operation
- `error`: Error message if failed
- `metadata`: Additional context
- `retention_days`: How long to keep this event (default 90)

**Indexes**:
- (`timestamp`, `source`) - Query recent events from a source
- (`event_type`, `timestamp`) - Query events by type
- (`user_id`, `timestamp`) - Query events by user
- (`resource_id`) - Query events affecting a resource
- (`status`) - Query failed events

### access_logs Collection
Stores user access log for compliance.

**Fields**:
- `id`: Unique log ID
- `user_id`: User accessing resource
- `resource_id`: Resource being accessed
- `resource_type`: Type of resource
- `access_type`: read, write, delete, share
- `timestamp`: When access occurred
- `ip_address`: User's IP address
- `user_agent`: User's browser/client info
- `duration_ms`: How long access took
- `success`: Whether access was successful
- `error_message`: Error if access failed
- `metadata`: Additional context

## Compliance & Retention

### Audit Trail (events collection)
- **Retention**: 90 days
- **Purpose**: System audit, debugging, investigation
- **Automatic Cleanup**: Runs nightly to delete events older than 90 days

### Access Logs (access_logs collection)
- **Retention**: 30 days
- **Purpose**: User access compliance, security investigation
- **Automatic Cleanup**: Runs nightly to delete logs older than 30 days

## Configuration

### Mock Mode (Development)
```python
adapter = FirestoreAdapter(use_mock=True)
```
- Uses in-memory database
- No GCP credentials needed
- Events stored in memory
- Perfect for local testing and development

### Production Mode (with Real Firestore)
```python
adapter = FirestoreAdapter(project_id="my-gcp-project", use_mock=False)
```
- Requires GCP credentials
- Events stored in Firestore
- Full production support
- Automatic index management

## Background Processor

The event logger runs a background task that periodically flushes queued events to Firestore.

```python
# Start with 5-second flush interval
await event_logger.start(flush_interval_seconds=5)

# Later, stop gracefully
await event_logger.stop()  # Flushes remaining events
```

## Performance Considerations

1. **Batching**: Events are queued and flushed periodically (default 5 seconds)
2. **Async Operations**: All logging is non-blocking
3. **Error Resilience**: Failed events are re-queued for retry
4. **Storage Efficiency**: Old events are automatically cleaned up per retention policy
5. **Index Optimization**: Firestore indexes optimize query performance

## Monitoring & Health

```python
from event_persistence import EventAggregator

aggregator = EventAggregator(event_logger)

# Check system health in last hour
health = await aggregator.get_health_events(hours=1)

if health["success_rate"] < 95:
    print(f"Warning: Success rate is only {health['success_rate']}%")
    print(f"Recent failures: {health['failures']}")
```

## Examples

### Example 1: Complete Task Creation with Event Logging

```python
async def create_task_with_logging(title, project_id, user_id):
    event_logger = get_event_logger()
    
    try:
        # Log the attempt
        await event_logger.log_event(
            event_type="task_creation_started",
            source="task_agent",
            action="create",
            user_id=user_id,
            resource_type="task",
            data={"title": title, "project_id": project_id}
        )
        
        # Create the task
        task = await task_agent.create_task(
            title=title,
            project_id=project_id
        )
        
        # Log success
        await event_logger.log_event(
            event_type="task_created",
            source="task_agent",
            action="create",
            user_id=user_id,
            resource_id=task["id"],
            resource_type="task",
            data={"title": title},
            result=task
        )
        
        # Log access
        await event_logger.log_access(
            user_id=user_id,
            resource_id=task["id"],
            resource_type="task",
            access_type="write",
            success=True
        )
        
        return task
        
    except Exception as e:
        # Log error
        await event_logger.log_event(
            event_type="task_creation_failed",
            source="task_agent",
            action="create",
            user_id=user_id,
            resource_type="task",
            data={"title": title},
            error=str(e)
        )
        raise
```

### Example 2: Compliance Report

```python
async def generate_compliance_report(start_date, end_date):
    event_logger = get_event_logger()
    
    # Get all events in the period
    events = await event_logger.replay_events(
        start_time=start_date,
        end_time=end_date
    )
    
    # Get access logs
    access_logs = await adapter.query_access_logs(limit=1000)
    
    return {
        "period": f"{start_date} to {end_date}",
        "total_events": len(events),
        "total_access_logs": len(access_logs),
        "events_by_type": {
            event_type: len([e for e in events if e["event_type"] == event_type])
            for event_type in set(e["event_type"] for e in events)
        },
        "failed_operations": len([e for e in events if e["status"] == "failed"])
    }
```

## Integration Checklist

- [ ] Create FirestoreAdapter instance
- [ ] Initialize event logging system
- [ ] Start event logger background processor
- [ ] Update all MCP servers to log events
- [ ] Add access logging for compliance
- [ ] Set up monitoring/health checks
- [ ] Configure cleanup routines
- [ ] Test event replay capability
- [ ] Document event types for your organization
- [ ] Set up compliance reporting

## File Location

```
backend/mcp_tools/
├── event_persistence.py         # Event logger, emitter, and aggregator
├── firestore_adapter.py          # Firestore operations
├── firestore_schemas.py          # Collection schemas
└── (updated MCP servers with event logging)
```

## Next Steps

1. Update all 6 MCP servers to log events
2. Integrate event logging into Orchestrator
3. Set up cleanup routines for old events
4. Create compliance reporting endpoints
5. Enable event replay for debugging
6. Monitor system health via events
