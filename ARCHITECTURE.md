# Architecture: Multi-Agent Productivity Assistant

## System Overview

The Multi-Agent Productivity Assistant is an innovative agentic AI system that demonstrates **autonomous decision-making** through the Critic Agent's "Proactive Goal Anticipation" feature.

### Core Innovation: Proactive Goal Anticipation

**Traditional AI:**
```
User → Plan → Execute → Done
```

**Our Innovation:**
```
User → Plan → Execute
          ↑       ↓
          ← Critic Agent Monitors & Replans Autonomously ←
```

---

## Architecture Layers

### Layer 1: API Gateway (FastAPI)

**Purpose**: Expose system functionality via REST API

**Endpoints:**
- `POST /workflows` - Create and execute new workflow
- `GET /workflows/{id}` - Get workflow status
- `GET /workflows/{id}/audit` - Get Critic Agent audit report
- `GET /knowledge-graph/export` - Export semantic graph
- `POST /demonstrate-critic-agent` - Run demo

**Key Features:**
- Async/await throughout for high concurrency
- Proper error handling and logging
- Structured JSON responses
- WebSocket support for real-time updates (extensible)

---

### Layer 2: Agent Coordination

#### Primary Agent: `OrchestratorAgent`

**Responsibilities:**
1. **Plan Generation**: Parse user requests, generate execution plans via LLM
2. **Knowledge Graph Building**: Create semantic representation of workflow
3. **Sub-Agent Coordination**: Delegate steps to appropriate specialists
4. **Dependency Management**: Ensure proper ordering and parallelization
5. **Replan Handling**: Accept and integrate Critic's autonomous replans

**Workflow Execution Flow:**
```python
1. Parse user request
2. Generate execution plan with LLM
3. Build knowledge graph (semantic context)
4. Start Critic agent monitoring
5. Execute steps (respecting dependencies):
   - Find ready steps (all dependencies completed)
   - Run ready steps in parallel
   - Wait for all to complete
   - Repeat until all steps done
6. Handle Critic replan if issued
7. Return results
```

**Key Methods:**
- `process_user_request()` - Main entry point
- `_generate_execution_plan()` - LLM-based plan generation
- `_build_knowledge_graph()` - Create semantic representation
- `_execute_plan()` - Manage execution with deps
- `_execute_step()` - Run individual step
- `handle_critic_replan()` - Accept autonomous replans

---

#### Sub-Agents

##### 1. SchedulerAgent
- **Specialization**: Calendar and scheduling operations
- **Operations**:
  - Find available time slots
  - Check participant availability
  - Handle conflict resolution
  - Create meetings

##### 2. TaskAgent
- **Specialization**: Task management
- **Operations**:
  - Create tasks
  - Assign to people
  - Track progress
  - Mark complete

##### 3. KnowledgeAgent
- **Specialization**: Information and context management
- **Operations**:
  - Gather context
  - Create notes
  - Find related information
  - Prepare background

---

#### Critic Agent: The Game-Changer ⭐

**Location**: `backend/agents/critic_agent.py`

**Purpose**: Autonomously audit workflows and replan if better paths exist

**How It Works:**

```
1. Subscribe to workflow progress via Pub/Sub
2. On each step completion:
   a. Run 5-dimensional audit
   b. Detect any issues
   c. If critical/high issue: attempt replan
3. For each issue:
   a. Generate alternative plans
   b. Calculate efficiency improvement
   c. Check confidence threshold (>75%)
   d. Check efficiency threshold (>15%)
   e. If both pass: AUTONOMOUSLY APPLY REPLAN
4. Provide transparent reasoning for all decisions
```

**5-Dimensional Audit:**

1. **Deadlock Detection**
   - Detects circular dependencies
   - Uses graph traversal (DFS)
   - Risk: CRITICAL

2. **Bottleneck Detection**
   - Identifies slow steps blocking others
   - Calculates step duration outliers
   - Risk: HIGH or MEDIUM

3. **Goal Drift Detection**
   - Checks if workflow still aligned with objective
   - Uses LLM for semantic comparison
   - Risk: HIGH

4. **Efficiency Analysis**
   - Finds faster alternative paths
   - Uses LLM to suggest improvements
   - Risk: MEDIUM

5. **Dependency Analysis**
   - Ensures prerequisites met
   - Validates task ordering
   - Risk: LOW

**Autonomous Replanning:**

```python
if issue_detected:
    alternative_plans = generate_alternatives()
    for plan in alternative_plans:
        efficiency_gain = calculate_gain(plan)
        confidence = estimate_confidence(plan)
        
        if efficiency_gain > 0.15 and confidence > 0.75:
            # 🎯 AUTONOMOUSLY APPLY
            apply_replan(plan)
            publish_decision(plan, reasoning)
            break
```

**Critical Thresholds:**
- Efficiency Threshold: 15% improvement required
- Confidence Threshold: 75% confidence required
- Only applies when BOTH are met

**Decision Transparency:**
Every decision includes:
- Detailed reasoning
- Efficiency gain percentage
- Confidence score
- Risk mitigation steps
- Timestamp

---

### Layer 3: Knowledge & Semantic Understanding

#### Knowledge Graph Service

**Purpose**: Maintain semantic relationships between all entities

**Entity Types:**
- `goal` - High-level objectives
- `task` - Actionable items
- `schedule` - Calendar events
- `note` - Information artifacts
- `person` - Team members
- `project` - Collections of work

**Relationship Types:**
- `depends_on` - Task ordering
- `achieves` - Contributes to goal
- `blocks` - Can impede other tasks
- `related_to` - Semantic connections
- `assigned_to` - Task assignment

**Graph Algorithms:**

1. **Path Finding (BFS)**
   ```
   find_path(source, target) -> List[node_ids]
   Used to detect dependencies and find critical paths
   ```

2. **Cycle Detection (DFS)**
   ```
   detect_circular_dependencies() -> List[cycles]
   Used by Critic to detect deadlocks
   ```

3. **Relationship Traversal (BFS)**
   ```
   get_related_nodes(node_id, relationship_type, max_depth)
   Used to understand task context
   ```

4. **Critical Path Analysis**
   ```
   get_critical_path(goal_node_id) -> List[task_ids]
   Finds longest path to achieve goal
   ```

---

### Layer 4: Communication & Real-Time Updates

#### Pub/Sub Service

**Purpose**: Real-time asynchronous communication between agents

**Architecture:**
```
Step Completes
     ↓
Publish event to Pub/Sub
     ↓
Critic Agent: subscribes to progress
    ↓
LLM Service: receives progress updates
    ↓
Orchestrator: gets replan decisions
    ↓
Pub/Sub broadcasts results
```

**Topic Structure:**
```
workflow-{id}-progress
  └─ Published when step completes
     
workflow-{id}-replan
  └─ Published when Critic suggests replan
     
workflow-{id}-status
  └─ Published when workflow state changes
     
workflow-{id}-audit
  └─ Published when issues detected (not replanned)
```

**Message Format:**
```json
{
  "workflow_id": "abc123",
  "step_id": 1,
  "step_name": "Check Alice's availability",
  "status": "completed",
  "duration_seconds": 5.2,
  "result_summary": "Available on Friday 2-4 PM"
}
```

**Dual Implementation:**
- **Development**: `MockPubSubService` (in-memory)
- **Production**: `GCPPubSubService` (Google Cloud Pub/Sub)

---

### Layer 5: Language Model Integration

#### LLM Service

**Purpose**: Provide AI understanding and generation capabilities

**Uses:**
1. Plan generation from goals
2. Alternative plan suggestions
3. Goal drift detection
4. Decision reasoning
5. Confidence scoring

**Dual Implementation:**
- **Development**: `MockLLMService` (mock responses)
- **Production**: `VertexAILLMService` (Vertex AI Gemini)

**Model: Google Gemini 1.5 Pro**
- Latest reasoning capabilities
- Structured output support
- Multi-turn conversation
- 1M token context window

---

### Layer 6: Data Persistence

#### Firestore Database

**Purpose**: Persistent storage for workflows, tasks, notes, and knowledge graph

**Collections:**
```
workflows/
├── {workflow_id}/
│   ├── status, goal, plan
│   ├── progress/, tasks/
│   └── results/

knowledge_graph/
├── {node_id} → Node data
└── edges/ → Relationship data

tasks/
├── {task_id} → Task details
└── assignments/

notes/
├── {note_id} → Content

events/
└── audit_trail/
```

**Scalability:**
- Serverless (auto-scaling)
- Global replication
- Strong consistency
- Supports complex queries

---

## Data Flow Diagram

### Request Processing Flow

```
1. API Request (POST /workflows)
   ↓
2. OrchestratorAgent.process_user_request()
   ├─ Generate execution plan (via LLM)
   ├─ Build knowledge graph
   └─ Start Critic agent
   ↓
3. Orchestrator executes plan
   ├─ Find ready steps (all deps completed)
   ├─ Delegate to sub-agents
   ├─ Publish progress to Pub/Sub
   └─ Wait for completion
   ↓
4. Critic Agent monitors (async)
   ├─ Audit workflow
   ├─ Detect issues
   └─ Attempt replan
   ↓
5. If replan approved:
   ├─ Publish replan decision
   └─ Orchestrator accepts & continues
   ↓
6. Return final results
```

### Critic Agent Audit Flow

```
Progress Update Received
   ↓
Async Audit:
   ├─ Deadlock detection
   ├─ Bottleneck detection
   ├─ Goal drift detection
   ├─ Efficiency analysis
   └─ Dependency check
   ↓
Issues Found?
   ├─ YES → Attempt replan
   │        ├─ Generate alternatives (LLM)
   │        ├─ Calculate efficiency
   │        ├─ Check thresholds
   │        └─ Apply if approved
   └─ NO → Continue monitoring
```

---

## Deployment Architecture

### Local Development

```
┌─────────────────────────────┐
│   Your Computer             │
├─────────────────────────────┤
│ Python 3.11+ Environment    │
│ ├─ FastAPI Server           │
│ ├─ Agents (in-process)      │
│ ├─ MockPubSubService        │
│ ├─ MockLLMService           │
│ └─ In-memory Knowledge Graph│
└─────────────────────────────┘
```

### Production on GCP

```
┌────────────────────────────────────────────────────┐
│              Google Cloud Platform                 │
├────────────────────────────────────────────────────┤
│                                                    │
│  ┌──────────────────────────────────────────────┐ │
│  │ Cloud Run (API Gateway)                      │ │
│  │ ├─ Auto-scaling: 1-10 instances             │ │
│  │ ├─ Pay per request                           │ │
│  │ └─ Integrated with Cloud Load Balancer      │ │
│  └──────────────────────────────────────────────┘ │
│           │                                        │
│  ┌────────┴──────┬─────────────┬────────────────┐ │
│  │    Pub/Sub    │   Firestore │   Vertex AI    │ │
│  │               │             │                 │ │
│  │ Real-time     │ Database    │ Gemini Model   │ │
│  │ messaging     │ NoSQL       │ LLM            │ │
│  └───────────────┴─────────────┴────────────────┘ │
│                                                    │
└────────────────────────────────────────────────────┘
```

**Deployment Steps:**
1. Build Docker image
2. Push to Container Registry
3. Deploy to Cloud Run
4. Configure environment variables
5. Set up Firestore database
6. Enable Pub/Sub topics
7. Test endpoints

---

## Scalability Considerations

### Horizontal Scaling

**Cloud Run handles:**
- Automatic instance scaling (1-10+ replicas)
- Load balancing
- Health checks
- Zero-downtime deployments

**Firestore:**
- Unlimited concurrent reads/writes
- Automatic regional replication
- Global consistency

**Pub/Sub:**
- Unlimited topics/subscriptions
- Automatic scaling
- 99.95% availability SLA

### Vertical Optimization

- **Async I/O**: Non-blocking throughout
- **Connection Pooling**: Reuse database connections
- **Caching**: Knowledge graph cache in memory
- **Batching**: Batch Pub/Sub publishes
- **Lazy Loading**: Load knowledge graph on demand

### Performance Targets

- **API Latency**: <100ms for instant response
- **Plan Generation**: 2-5 seconds (LLM dependent)
- **Workflow Execution**: 5-30 seconds (task dependent)
- **Audit & Replan**: <1 second per workflow
- **Throughput**: 50-100+ workflows/second at scale

---

## Security Considerations

### Authentication & Authorization

- (Extensible) API key validation
- GCP service accounts for Pub/Sub/Firestore
- Role-based access control (future)

### Data Protection

- Encryption in transit (HTTPS)
- Encryption at rest (Firestore)
- Least privilege principle
- Audit logging of all decisions

---

## Testing Strategy

### Unit Tests
- Individual agent functionality
- Service methods
- Utility functions

### Integration Tests
- Agent coordination
- Pub/Sub communication
- Knowledge graph operations

### System Tests
- Full workflow execution
- Critic agent decisions
- Error handling

**Run tests:**
```bash
pytest tests/ -v
pytest tests/test_agents.py::test_critic_detects_bottleneck -v
```

---

## Extensibility

### Adding New Sub-Agents

```python
class CustomAgent:
    async def execute(self, step, previous_results):
        # Implement custom logic
        return {"status": "success", ...}

# Register with orchestrator
orchestrator.register_sub_agent("custom", CustomAgent())
```

### Adding New Audit Methods

```python
async def _detect_custom_issue(self, workflow):
    # Implement detection logic
    return WorkflowIssue(...)
```

### Custom MCP Tools

Extend the system with Model Context Protocol (MCP) tools:
- Real calendar integrations (Google Calendar, Outlook)
- Email integration
- Slack notifications
- Jira task management

---

## Conclusion

This architecture demonstrates:

1. **Sophisticated Agent Design**: Primary orchestrator + specialist sub-agents
2. **Real-time Communication**: Async Pub/Sub for loose coupling
3. **Semantic Understanding**: Knowledge graph for intelligent decisions
4. **Autonomous Reasoning**: Critic agent with proactive decision-making
5. **Production Readiness**: Cloud-native, scalable, secure
6. **Transparency**: All decisions explained with reasoning

**The key innovation**: Critic Agent moves beyond reaction to proaction, embodying true agentic AI.
