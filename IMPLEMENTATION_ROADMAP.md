# 🛣️ Roadmap to Full Architecture Alignment

## Current State → Target State Journey

### Start: Current Architecture (62% Aligned)
```
FastAPI (monolithic)
└─ Orchestrator Agent
   ├─ Task Agent (in-process)
   ├─ Calendar Agent (in-process)
   ├─ Notes Agent (in-process)
   ├─ Critic Agent (in-process)
   └─ Auditor Agent (in-process)
```

### End: Target Architecture (100% Aligned)
```
FastAPI + MCP Servers (distributed)
└─ Orchestrator Agent
   ├─ Task Agent → Task MCP Server (process 1)
   ├─ Calendar Agent → Calendar MCP Server (process 2)
   ├─ Notes Agent → Notes MCP Server (process 3)
   ├─ Critic Agent → Critic MCP Server (process 4)
   ├─ Auditor Agent → Auditor MCP Server (process 5)
   └─ Event Monitor → Event Monitor MCP Server (process 6)
```

---

## Phase 1: Foundation (Days 1-2)

### Week 1, Day 1: Base MCP Framework

**Goal**: Create the foundation for MCP servers

**What to Build**:
1. Base MCP server class
2. MCP tool registration utilities
3. Example MCP server

**Files to Create**:
```
backend/mcp_tools/
├── __init__.py (empty)
├── base_mcp_server.py (NEW)
│   ├── BaseMCPServer class
│   │   ├── __init__(name, description)
│   │   ├── register_tool()
│   │   ├── register_resource()
│   │   ├── start()
│   │   └── stop()
│   └── Tool definitions
├── mcp_types.py (NEW)
│   ├── Tool protocol
│   ├── Resource protocol
│   ├── TextContent, ImageContent
│   └── ToolUseBlock
└── utils.py (NEW)
    ├── json_serialization()
    └── error_handling()
```

**Implementation Details**:
```python
# base_mcp_server.py structure

class BaseMCPServer:
    """Base class for all MCP servers"""
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.tools = {}
        self.resources = {}
    
    def register_tool(self, name, description, handler, input_schema):
        """Register a tool that clients can call"""
        self.tools[name] = {
            'description': description,
            'handler': handler,
            'inputSchema': input_schema
        }
    
    def register_resource(self, uri, name, description, handler):
        """Register a resource that clients can access"""
        self.resources[uri] = {
            'name': name,
            'description': description,
            'handler': handler
        }
    
    async def handle_tool_call(self, tool_name, arguments):
        """Execute a tool"""
        if tool_name in self.tools:
            handler = self.tools[tool_name]['handler']
            return await handler(**arguments)
    
    async def start(self, port):
        """Start MCP server on given port"""
        # Implementation using http/sse transport
        pass
```

**Effort**: 2-3 hours

---

### Week 1, Day 1-2: Task MCP Server

**Goal**: First complete MCP server wrapping Task Agent

**Files to Create**:
```
backend/mcp_tools/task_mcp_server.py (NEW)
├── TaskMCPServer class
│   ├── Inherits from BaseMCPServer
│   ├── Contains TaskAgent instance
│   ├── Tools:
│   │   ├── create_task (input: title, description, priority, deadline)
│   │   ├── list_tasks (input: status, priority, limit)
│   │   ├── update_task (input: task_id, updates)
│   │   ├── complete_task (input: task_id)
│   │   └── assign_task (input: task_id, assignee)
│   └── Resources:
│       ├── /tasks/{task_id} (task details)
│       └── /tasks (all tasks list)
└── Main block for standalone startup
```

**API Contract**:
```json
GET /tools
Response: {
  "tools": [
    {
      "name": "create_task",
      "description": "Create a new task",
      "inputSchema": {
        "type": "object",
        "properties": {
          "title": {"type": "string"},
          "description": {"type": "string"},
          "priority": {"type": "string", "enum": ["low", "medium", "high"]},
          "deadline": {"type": "string", "format": "date-time"}
        },
        "required": ["title"]
      }
    }
  ]
}

POST /tool/create_task
Request: {
  "title": "Prepare presentation",
  "description": "Create Q2 budget presentation",
  "priority": "high",
  "deadline": "2024-04-15T17:00:00Z"
}
Response: {
  "task_id": "task_12345",
  "status": "created",
  "title": "Prepare presentation"
}
```

**Testing**:
```bash
# Start Task MCP Server
python -m backend.mcp_tools.task_mcp_server --port 8001

# In another terminal, test
curl http://localhost:8001/tools
curl -X POST http://localhost:8001/tool/create_task \
  -d '{"title": "Test"}'
```

**Effort**: 2-3 hours

---

## Phase 2: Complete Agent MCP Servers (Days 3-4)

### Week 1, Day 3: Calendar & Notes MCP Servers

**Pattern**: Same as Task MCP Server

**Files to Create**:
```
backend/mcp_tools/calendar_mcp_server.py (NEW)
├── CalendarMCPServer
│   ├── Tools:
│   │   ├── create_event (title, start_time, end_time, attendees, location)
│   │   ├── check_availability (user_ids, start_time, end_time)
│   │   ├── find_meeting_time (attendees, duration_minutes, date_range)
│   │   ├── update_event (event_id, updates)
│   │   ├── delete_event (event_id)
│   │   └── list_events (filters, limit)
│   └── Resources: /events/{event_id}, /events

backend/mcp_tools/notes_mcp_server.py (NEW)
├── NotesMCPServer
│   ├── Tools:
│   │   ├── create_note (title, content, category, tags)
│   │   ├── search_notes (query, tags, category, limit)
│   │   ├── get_note (note_id)
│   │   ├── update_note (note_id, updates)
│   │   ├── delete_note (note_id)
│   │   ├── summarize_note (note_id, max_sentences)
│   │   ├── list_notes (category, sort_by, limit)
│   │   └── organize_notes ()
│   └── Resources: /notes/{note_id}, /notes
```

**Effort**: 2-3 hours

---

### Week 1, Day 4: Critic & Auditor MCP Servers

**Files to Create**:
```
backend/mcp_tools/critic_mcp_server.py (NEW)
├── CriticMCPServer
│   ├── Tools:
│   │   ├── analyze_workflow (workflow_id)
│   │   ├── detect_bottlenecks (plan)
│   │   ├── suggest_optimization (workflow_id)
│   │   ├── start_monitoring (workflow_id, plan)
│   │   └── get_audit_report (workflow_id)
│   └── Resources: /workflows/{workflow_id}/audit

backend/mcp_tools/auditor_mcp_server.py (NEW)
├── AuditorMCPServer
│   ├── Tools:
│   │   ├── vibe_check (action, risk_level)
│   │   ├── validate_intent (user_request, action)
│   │   ├── detect_conflicts (pending_actions)
│   │   ├── assess_risk (action) -> LOW/MEDIUM/HIGH/CRITICAL
│   │   └── get_audit_trail (limit)
│   └── Resources: /audits/{audit_id}
```

**Effort**: 2-3 hours

---

## Phase 3: Event Monitor & Orchestrator Update (Days 3-4)

### Week 1, Day 3: Event Monitor MCP Server

**Files to Create**:
```
backend/mcp_tools/event_monitor_mcp_server.py (NEW)
├── EventMonitorMCPServer
│   ├── Tools:
│   │   ├── emit_event (topic, event_data, priority)
│   │   ├── emit_action_lifecycle (action_id, status, data)
│   │   ├── query_event_stream (filters, limit)
│   │   ├── get_event_stream_snapshot (time_window)
│   │   └── get_goal_event_timeline (goal_id)
│   ├── Resources:
│   │   ├── /events (event stream)
│   │   ├── /events/{event_id}
│   │   └── /workflows/{workflow_id}/timeline
│   └── Database: Firestore event collection
```

**Topics Managed**:
```
- agent-events: General agent lifecycle events
- vibe-check-req: Auditor vibe-check requests (CRITICAL priority)
- replan-sig: Critic replan signals (CRITICAL priority)
- goal-health: Goal health score changes
- action-lifecycle: Action started/completed/failed
```

**Effort**: 2-3 hours

---

### Week 1, Day 4: Update Orchestrator to Use MCP Servers

**Changes to orchestrator_agent.py**:
```python
# OLD: Direct agent instantiation
self.task_agent = TaskAgent()
self.calendar_agent = CalendarAgent()

# NEW: MCP server connections
self.mcp_clients = {
    'task': MCPClient('localhost:8001'),
    'calendar': MCPClient('localhost:8002'),
    'notes': MCPClient('localhost:8003'),
    'critic': MCPClient('localhost:8004'),
    'auditor': MCPClient('localhost:8005'),
    'event_monitor': MCPClient('localhost:8006'),
}

async def _delegate_to_agent(self, agent_type, step):
    """Call MCP server instead of in-process agent"""
    mcp_client = self.mcp_clients[agent_type]
    tool_name = step.get('type')  # e.g., 'create_task'
    arguments = step.get('input', {})
    
    result = await mcp_client.call_tool(tool_name, arguments)
    return result
```

**Updates Needed**:
- Import MCPClient
- Update register_sub_agent() to register MCP clients
- Update _execute_plan() to call MCP servers
- Update _emit_event() to use Event Monitor MCP
- Add service discovery (localhost:port mapping)

**Effort**: 2-3 hours

---

## Phase 4: Firestore Integration (Days 5-6)

### Week 2, Day 1: Firestore Schema & Collections

**Files to Create**:
```
backend/mcp_tools/schemas.py (NEW)
├── Collection definitions
├── Document models
│   ├── TaskDocument
│   ├── NoteDocument
│   ├── GoalDocument
│   ├── AuditDocument
│   └── EventDocument
└── Indexes to create

backend/mcp_tools/firestore_adapter.py (NEW)
├── FirestoreAdapter class
│   ├── __init__(project_id, database)
│   ├── Collection methods: create, read, update, delete, query
│   │   ├── tasks_collection()
│   │   ├── notes_collection()
│   │   ├── goals_collection()
│   │   ├── audit_collection()
│   │   └── events_collection()
│   └── Batch operations
└── Error handling & retries
```

**Collection Structure**:
```
Firestore Database
├── tasks/                          (Collection)
│   ├── {task_id}/                 (Document)
│   │   ├── title: string
│   │   ├── description: string
│   │   ├── status: string (pending/in_progress/completed)
│   │   ├── priority: string (low/medium/high)
│   │   ├── deadline: timestamp
│   │   ├── assignee: string
│   │   ├── created_at: timestamp
│   │   ├── updated_at: timestamp
│   │   └── metadata: map
│   
├── notes/
│   ├── {note_id}/
│   │   ├── title: string
│   │   ├── content: string
│   │   ├── category: string
│   │   ├── tags: array
│   │   ├── word_count: number
│   │   ├── pinned: boolean
│   │   ├── created_at: timestamp
│   │   ├── updated_at: timestamp
│   │   └── metadata: map
│   
├── goals/
│   ├── {goal_id}/
│   │   ├── title: string
│   │   ├── description: string
│   │   ├── status: string
│   │   ├── health_score: number (0-100)
│   │   ├── deadline: timestamp
│   │   ├── workflow_ids: array
│   │   ├── created_at: timestamp
│   │   └── metadata: map
│   
├── audit/
│   ├── {audit_id}/
│   │   ├── workflow_id: string
│   │   ├── action: string
│   │   ├── agent: string
│   │   ├── status: string (pending/completed/failed)
│   │   ├── details: map
│   │   ├── timestamp: timestamp
│   │   └── metadata: map
│   
└── events/
    ├── {event_id}/
        ├── type: string (action_started/action_completed/action_failed/goal_registered/etc)
        ├── agent: string
        ├── workflow_id: string
        ├── priority: string (low/normal/high/critical)
        ├── data: map
        ├── timestamp: timestamp
        └── metadata: map
```

**Indexes to Create**:
```
indexes:
  - collection: tasks
    fields:
      - status
      - priority
      - deadline
      - created_at
  
  - collection: notes
    fields:
      - category
      - tags
      - created_at
  
  - collection: events
    fields:
      - type
      - workflow_id
      - timestamp
      - priority
```

**Effort**: 2 hours

---

### Week 2, Day 1-2: Wire Firestore to Agents

**Updates Needed**:

**In task_mcp_server.py**:
```python
async def create_task(self, title, description, priority, deadline):
    # Create in Firestore
    task_data = {
        'title': title,
        'description': description,
        'priority': priority,
        'deadline': deadline,
        'status': 'pending',
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    doc_id = await self.firestore.tasks.add(task_data)
    return {'task_id': doc_id, 'status': 'created'}

async def list_tasks(self, status=None, priority=None, limit=20):
    # Query from Firestore
    query = self.firestore.tasks
    if status:
        query = query.where('status', '==', status)
    if priority:
        query = query.where('priority', '==', priority)
    
    docs = await query.limit(limit).get()
    return [{'id': doc.id, **doc.to_dict()} for doc in docs]
```

**In notes_mcp_server.py**:
```python
async def create_note(self, title, content, category, tags):
    note_data = {
        'title': title,
        'content': content,
        'category': category,
        'tags': tags,
        'word_count': len(content.split()),
        'pinned': False,
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    doc_id = await self.firestore.notes.add(note_data)
    return {'note_id': doc_id, 'status': 'created'}

async def search_notes(self, query, tags=None, category=None, limit=10):
    # Full-text would use Elasticsearch in production
    # For now, use Firestore query + in-memory filtering
    qs = self.firestore.notes
    if category:
        qs = qs.where('category', '==', category)
    
    docs = await qs.get()
    results = []
    for doc in docs:
        data = doc.to_dict()
        if query in data['title'] or query in data['content']:
            results.append({'id': doc.id, **data})
    
    return sorted(results, key=lambda x: x['created_at'])[:limit]
```

**In event_monitor_mcp_server.py**:
```python
async def emit_event(self, topic, event_data, priority='normal'):
    event = {
        'topic': topic,
        'data': event_data,
        'priority': priority,
        'timestamp': datetime.now()
    }
    
    # Store in Firestore
    doc_id = await self.firestore.events.add(event)
    
    # Publish to Pub/Sub
    await self.pubsub.publish(topic, event)
    
    return {'event_id': doc_id, 'status': 'published'}

async def query_event_stream(self, filters=None, limit=100):
    query = self.firestore.events
    
    if filters:
        if 'type' in filters:
            query = query.where('type', '==', filters['type'])
        if 'workflow_id' in filters:
            query = query.where('workflow_id', '==', filters['workflow_id'])
    
    docs = await query.order_by('timestamp', direction='DESCENDING').limit(limit).get()
    return [{'id': doc.id, **doc.to_dict()} for doc in docs]
```

**Effort**: 3-4 hours

---

## Phase 5: Testing & Integration (Days 7-8)

### Week 2, Day 3: Integration Testing

**Test Plan**:
```python
# test_mcp_integration.py
import pytest
import asyncio

@pytest.mark.asyncio
async def test_task_agent_mcp():
    """Test Task Agent MCP Server"""
    client = MCPClient('localhost:8001')
    
    # Create task
    result = await client.call_tool('create_task', {
        'title': 'Test Task',
        'priority': 'high'
    })
    assert result['status'] == 'created'
    task_id = result['task_id']
    
    # Verify in Firestore
    task = await firestore.tasks.get(task_id)
    assert task['title'] == 'Test Task'
    assert task['priority'] == 'high'

@pytest.mark.asyncio
async def test_end_to_end_workflow():
    """Test complete workflow through Orchestrator"""
    orchestrator = OrchestratorAgent(...)
    
    request = WorkflowRequest(
        goal="Schedule meeting and create notes",
        description="Full workflow test"
    )
    
    result = await orchestrator.process_user_request(request)
    
    # Verify all components called
    assert result['status'] == 'completed'
    # Verify Firestore has events
    # Verify Pub/Sub events published

@pytest.mark.asyncio
async def test_mcp_server_discovery():
    """Test agent service discovery"""
    # Verify all MCP servers are reachable
    # Verify tools are registered
    # Verify resources are available
```

**Effort**: 2-3 hours

---

### Week 2, Day 4: Deployment Preparation

**Files to Update**:
```
Dockerfile (UPDATE)
├── Multi-stage build
├── Stage 1: Build MCP servers
├── Stage 2: Main FastAPI app
└── Expose ports 8000-8009 (API + 6 MCP servers)

docker-compose.yml (NEW)
├── Main app service (port 8000)
├── Task MCP service (port 8001)
├── Calendar MCP service (port 8002)
├── Notes MCP service (port 8003)
├── Critic MCP service (port 8004)
├── Auditor MCP service (port 8005)
├── Event Monitor MCP service (port 8006)
├── Firestore emulator (dev)
├── Pub/Sub emulator (dev)
└── Network linking

deployment/cloudrun.yaml (UPDATE)
├── Main API Cloud Run service
├── MCP servers as companion services
├── Environment variables
├── Service account setup
└── IAM roles (Firestore, Pub/Sub)

.env.example (UPDATE)
├── MCP_SERVERS_HOST: localhost (dev), cloud-run-service (prod)
├── MCP_TASK_HOST: localhost:8001
├── MCP_CALENDAR_HOST: localhost:8002
├── MCP_NOTES_HOST: localhost:8003
├── MCP_CRITIC_HOST: localhost:8004
├── MCP_AUDITOR_HOST: localhost:8005
├── MCP_EVENT_MONITOR_HOST: localhost:8006
└── FIRESTORE_EMULATOR_HOST: localhost:8235
```

**Effort**: 2-3 hours

---

## Timeline Summary

```
┌─────────────────────────────────────────────────────────┐
│ Phase 1: Foundation (Days 1-2)                         │
│ ├─ Base MCP Framework                  ✅ 2-3 hours   │
│ └─ Task MCP Server (1st complete)      ✅ 2-3 hours   │
│                                  TOTAL: 4-6 hours     │
├─────────────────────────────────────────────────────────┤
│ Phase 2: Complete Agents (Days 3-4)                    │
│ ├─ Calendar MCP Server                 ✅ 2-3 hours   │
│ ├─ Notes MCP Server                    ✅ 2-3 hours   │
│ ├─ Critic MCP Server                   ✅ 2 hours     │
│ ├─ Auditor MCP Server                  ✅ 2 hours     │
│ └─ Event Monitor MCP Server            ✅ 2-3 hours   │
│                                  TOTAL: 10-12 hours   │
├─────────────────────────────────────────────────────────┤
│ Phase 3: Orchestrator (Day 4)                          │
│ └─ Update Orchestrator → MCP routing   ✅ 2-3 hours   │
│                                  TOTAL: 2-3 hours     │
├─────────────────────────────────────────────────────────┤
│ Phase 4: Firestore (Days 5-6)                          │
│ ├─ Schema & Collections                ✅ 2 hours     │
│ └─ Wire Firestore to Agents            ✅ 3-4 hours   │
│                                  TOTAL: 5-6 hours     │
├─────────────────────────────────────────────────────────┤
│ Phase 5: Testing (Days 7-8)                            │
│ ├─ Integration Testing                 ✅ 2-3 hours   │
│ └─ Deployment Preparation              ✅ 2-3 hours   │
│                                  TOTAL: 4-6 hours     │
├─────────────────────────────────────────────────────────┤
│ GRAND TOTAL:                          📊 25-33 hours    │
│ (Approximately 3-5 business days)                     │
└─────────────────────────────────────────────────────────┘
```

---

## Success Criteria

✅ **Phase 1 Complete When**:
- Base MCP server class works
- Task MCP server responds to calls
- Agent logic not affected

✅ **Phase 2 Complete When**:
- All 5 agent MCP servers running
- Event Monitor MCP operational
- All tools registered and functional

✅ **Phase 3 Complete When**:
- Orchestrator routes via MCP
- Agents no longer in-process
- Workflow execution still works

✅ **Phase 4 Complete When**:
- Firestore schema deployed
- All agents reading/writing to Firestore
- Data persistence working

✅ **Phase 5 Complete When**:
- All integration tests passing
- Docker-compose works locally
- Ready for Cloud Run deployment

---

## Risk Mitigation

| Risk | Mitigation | Effort |
|------|-----------|--------|
| MCP protocol complexity | Start simple, use HTTP/REST | Low |
| Service discovery issues | Use localhost:port for now | Low |
| Firestore integration bugs | Firestore emulator for testing | Medium |
| Agent logic changes needed | Keep agents unchanged, wrap in MCP | Low |
| Performance degradation | Monitor latency, optimize async | Medium |

---

## Decision Points

**Decision 1: Service Discovery**
- Option A: Hardcode localhost:port (current recommendation)
- Option B: Use Kubernetes service discovery
- Option C: Use Consul/Eureka
- **Recommended**: Option A for Phase 1, upgrade later

**Decision 2: Authentication**
- Option A: No auth for localhost (dev)
- Option B: Service-to-service auth with mTLS
- Option C: API keys
- **Recommended**: Option A for Phase 1, add in Phase 5

**Decision 3: Firestore vs Alternative**
- Option A: Cloud Firestore (current plan)
- Option B: Cloud Datastore
- Option C: PostgreSQL+Cloud SQL
- **Recommended**: Option A (matches architecture)

---

## Next Steps

1. **Approve the roadmap** ✓
2. **Start Phase 1** - Build base MCP framework
3. **Iterate phases** - Each phase builds on previous
4. **Test continuously** - Don't wait for end
5. **Document as you go** - Keep docs current

**Ready to start implementation?** 🚀
