# 🤖 Multi-Agent System - Comprehensive Guide

## Overview

The Multi-Agent Productivity Assistant features **5 specialized sub-agents** coordinated by an **Orchestrator Agent**, with powerful governance tools for **self-governance**, **self-tuning**, **autonomous replanning**, and **failure recovery**.

---

## 📊 Agent Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Orchestrator Agent (Router)                |
│  - Routes requests to appropriate sub-agents           |
│  - Coordinates workflow execution                       |
│  - Manages saga transactions                           |
│  - Enforces governance policies                        |
└──────────────┬────────────────────────────────────────┘
               │
       ┌───────┼───────┬──────────┬────────────┐
       │       │       │          │            │
       ▼       ▼       ▼          ▼            ▼
    Task   Calendar  Notes    Scheduler   Knowledge
    Agent   Agent     Agent     Agent       Agent
    
    + Critic Agent (Monitoring & Replanning)
    + Auditor Agent (Security & Vibe-Checks)
    + Governance Engines (Memory, Consensus, Circuit Breaker, Escalation)
    + Self-Tuning (Saga, Adaptive Policies, Scorecard)
    + Dead-Letter Queue (Failure Recovery)
```

---

## 🎯 Agent Specifications

### 1. Task Agent
**Purpose**: Task creation, assignment, tracking, and completion

**Operations**:
- `create_task` - Create new task with priority and deadline
- `list_tasks` - List tasks with filtering and sorting
- `update_task` - Update task status, priority, or details
- `complete_task` - Mark task as complete
- `assign_task` - Assign task to team members

**Example Usage**:
```python
task_step = {
    "type": "create_task",
    "title": "Prepare Q2 budget",
    "description": "Create detailed budget spreadsheet",
    "priority": "high",
    "deadline": "2024-04-15T17:00:00Z",
    "assignee": "finance_team"
}
```

---

### 2. Calendar Agent
**Purpose**: Schedule events, check availability, find optimal meeting times

**Operations**:
- `create_event` - Schedule new calendar event
- `check_availability` - Check availability for users/times
- `find_meeting_time` - Find optimal time for multiple attendees
- `list_events` - List events with filtering
- `update_event` - Modify event details
- `delete_event` - Remove event from calendar

**Key Features**:
- Timezone support
- Conflict detection
- Multi-attendee availability analysis
- Location management
- Automatic slot recommendation

**Example Usage**:
```python
event_step = {
    "type": "create_event",
    "title": "Sprint Planning",
    "start_time": "2024-04-15T10:00:00Z",
    "end_time": "2024-04-15T11:30:00Z",
    "attendees": ["alice@company.com", "bob@company.com"],
    "location": "Conference Room A",
    "timezone": "America/New_York"
}
```

**Availability Check**:
```python
availability_step = {
    "type": "check_availability",
    "user_ids": ["alice@company.com", "bob@company.com", "charlie@company.com"],
    "start_time": "2024-04-15T14:00:00Z",
    "end_time": "2024-04-15T15:00:00Z"
}
```

**Find Meeting Time**:
```python
find_slot_step = {
    "type": "find_meeting_time",
    "attendees": ["alice@company.com", "bob@company.com", "charlie@company.com"],
    "duration_minutes": 60,
    "start_date": "2024-04-15T00:00:00Z",
    "end_date": "2024-04-19T23:59:59Z"
}
```

---

### 3. Notes Agent
**Purpose**: Knowledge management, note-taking, searching, organizing

**Operations**:
- `create_note` - Create note with metadata
- `search_notes` - Search by keywords, tags, category
- `get_note` - Retrieve specific note
- `list_notes` - List notes with filtering and sorting
- `update_note` - Modify note content/metadata
- `delete_note` - Remove note
- `summarize_note` - Generate summary of note content
- `organize_notes` - Get organization statistics and suggestions

**Key Features**:
- Tag-based indexing
- Category organization
- Full-text search
- Pinned notes priority
- LLM-powered summarization
- Related notes linking

**Example Usage - Create Note**:
```python
note_step = {
    "type": "create_note",
    "title": "Sprint 25 Retrospective",
    "content": "Team feedback: Need better tooling, deployment was smooth, communication could improve...",
    "category": "meeting-notes",
    "tags": ["sprint-25", "retrospective", "feedback", "action-items"],
    "metadata": {
        "meeting_date": "2024-04-10",
        "attendees": 8,
        "duration_minutes": 45
    }
}
```

**Search Notes**:
```python
search_step = {
    "type": "search_notes",
    "query": "deployment",
    "tags": ["sprint-25", "feedback"],
    "category": "meeting-notes",
    "limit": 10
}
```

**Summarize Note**:
```python
summarize_step = {
    "type": "summarize_note",
    "note_id": "note_xyz789",
    "max_sentences": 3
}
```

---

### 4. Scheduler Agent
**Purpose**: Compute optimal scheduling, deadline calculations, resource allocation

**Operations**:
- `compute_critical_path` - Find longest path to goal
- `suggest_schedule` - Recommend execution order
- `calculate_deadlines` - Compute sub-deadlines
- `allocate_resources` - Assign resources to tasks
- `detect_conflicts` - Find schedule conflicts

**Example Usage**:
```python
schedule_step = {
    "type": "compute_critical_path",
    "workflow_id": "workflow_12345",
    "consider_dependencies": true
}
```

---

### 5. Knowledge Agent
**Purpose**: Manage semantic relationships, entity linking, context retrieval

**Operations**:
- `add_entity` - Add person, project, document, or concept
- `add_relationship` - Link entities with relationships
- `query_context` - Get full context around an entity
- `find_related` - Find related entities
- `detect_cycles` - Find circular dependencies
- `suggest_parallel` - Suggest independent tasks

**Example Usage**:
```python
knowledge_step = {
    "type": "add_relationship",
    "source_entity": "task_123",
    "target_entity": "goal_456",
    "relationship_type": "contributes_to"
}
```

---

## 🧠 Orchestrator Features

### Routing Intelligence
The Orchestrator automatically routes requests:
- Task requests → `task_agent`
- Calendar/scheduling → `calendar_agent`
- Note/knowledge → `notes_agent`
- Time/resource optimization → `scheduler_agent`
- Entity relationships → `knowledge_agent`
- Goal monitoring → `critic_agent`
- Security checks → `auditor_agent`

### Saga Pattern (Atomic Transactions)
Multi-step workflows are wrapped in sagas for consistency:

```python
# Orchestrator automatically:
1. Begins saga transaction
2. Registers each step with compensation action
3. Executes steps in order
4. On failure: Rolls back in reverse order
5. On success: Completes saga
```

**Example Saga Flow**:
```
Create Meeting (Step 1)
  ↓ [on failure: delete meeting]
Create Task (Step 2)
  ↓ [on failure: delete task]
Update Calendar Notes (Step 3)
  ↓ [on failure: restore notes]
```

### Circuit Breaker Pattern
Prevents cascading failures by tracking service health:

```python
# Before delegating to agent:
check_circuit_breaker(agent_name)
  → If tripped: Use alternative or escalate
  → If healthy: Delegate

# After delegation:
report_service_result(agent_name, success/failure)
  → Updates circuit health
  → May trip circuit if too many failures
```

---

## 💪 Governance & Decision-Making

### 1. Agent Memory (Learning)
- **Before retry**: `recall_failure_pattern(error_type)`
  - Check if we've seen this before
  - Apply known fix if available
  
- **After failure**: `log_failure_and_resolution(error, resolution)`
  - Build institutional memory of solutions

### 2. Consensus Protocol
When Critic and Auditor disagree:
```
request_consensus(
    critic_recommendation,
    auditor_veto_status,
    context
)
→ Returns: consensus_score, final_decision, reasoning
```

- Auditor safety veto is non-negotiable
- If consensus < 40: Auto-escalate to user

### 3. Adaptive Policies
Self-tuning policy thresholds:
```
observe_rule_effectiveness(
    rule_name,
    decision_outcome  # "correct", "overridden", "false_positive", "false_negative"
)

analyze_and_tune_policies()
→ Auto-adjust thresholds with high confidence (>0.75)
```

### 4. Governance Scorecard
Track Critic and Auditor accuracy:
```
log_governance_decision(critic_decision, auditor_check)
resolve_governance_outcome(outcome)  # When result is known
get_governance_scorecard()  # Precision/Recall/F1 metrics
```

---

## 🛡️ Auditor (Security Vibe-Checks)

### Risk Levels
```
🟩 LOW (list, search, get)
   → Execute directly

🟨 MEDIUM (create)
   → Quick intent check via auditor

🟧 HIGH (updates, schedule changes)
   → Intent + Conflict check

🟥 CRITICAL (delete, external comms)
   → Full vibe-check required
```

### Vibe-Check Questions
1. **Intent**: Is this what the user really wants?
2. **Conflicts**: Does this conflict with other pending actions?
3. **Safety**: Could this cause unintended consequences?
4. **Permissions**: Does user have authority for this action?

---

## 📬 Dead-Letter Queue (DLQ)

### When Messages Go to DLQ:
1. **Event delivery fails** - Pub/Sub subscriber throws
2. **Saga compensation fails** - Rollback step fails
3. **Governance callback fails** - Policy/scorecard update fails

### Recovery Process:
```
Message fails
  ↓
Enqueued in DLQ with retry count
  ↓
Retry with exponential backoff:
  1s → 2s → 4s → 8s → 16s
  ↓
After max retries (default 5)
  → Quarantine as poisoned message
  ↓
Manual intervention or drain_dead_letter_queue()
```

### DLQ Operations:
- `enqueue_dead_letter(category, payload, error)`
- `retry_dead_letter(dlq_item_id)`
- `drain_dead_letter_queue()` - Auto-retry eligible items
- `quarantine_dead_letter(dlq_item_id)` - Stop retrying
- `resolve_dead_letter(dlq_item_id)` - Mark as fixed
- `discard_dead_letter(dlq_item_id)` - Remove stale item
- `get_dlq_dashboard()` - Health monitoring

---

## 📡 Event-Driven Architecture

### Event Emission Rules
Agent lifecycle events emitted via Pub/Sub:

```
BEFORE action:  emit_action_lifecycle("action.started", ...)
AFTER success:  emit_action_lifecycle("action.completed", ...)
ON failure:     emit_action_lifecycle("action.failed", ..., priority="CRITICAL")

GOAL registered: emit_event("goal.registered", ...)
HEALTH changed:  emit_event("goal.health_changed", ...)
REPLAN needed:   emit_event("replan.triggered", ..., priority="CRITICAL")
VIBE-CHECK req:  emit_event("vibe_check.requested", ...)
```

### Event Subscribers
- **Critic Agent**: Monitors all lifecycle events for optimization opportunities
- **Auditor Agent**: Watches for CRITICAL priority events requiring safety checks
- **Orchestrator**: Tracks workflow progress via progress events
- **Dead-Letter Queue**: Captures failed event deliveries

---

## 🚀 Workflow Execution Example

### Scenario: "Schedule team meeting with prep work"

**User Request**:
```
"Schedule a 1-hour team sync for Friday with 5 people. 
Need to finalize agenda from last 3 meetings and prepare background notes."
```

**Orchestrator Plan** (50 steps simplified to key steps):
```
Step 1: Search for last 3 meeting notes
  Agent: notes_agent
  Type: search_notes
  Depends: none
  
Step 2-6: Check availability for 5 team members (parallel)
  Agent: calendar_agent
  Type: check_availability
  Depends: Step 1
  
Step 7: Find optimal meeting time
  Agent: calendar_agent
  Type: find_meeting_time
  Depends: Steps 2-6
  
Step 8: Create calendar event
  Agent: calendar_agent
  Type: create_event
  Depends: Step 7
  
Step 9: Summarize last 3 meetings
  Agent: notes_agent
  Type: summarize_note
  Depends: Step 1
  
Step 10: Create meeting prep document
  Agent: notes_agent
  Type: create_note
  Depends: Step 9
  
Step 11: Create setup task for attendees
  Agent: task_agent
  Type: create_task
  Depends: Step 10
```

**Critic Agent Analysis**:
- Steps 2-6 all wait for Step 1 ❌ **Bottleneck detected**
- But Step 1 is critical dependency ✓
- Notes can be summarized in parallel with availability checks 💡 **Optimization**
- Efficiency improvement: 25% (parallel execution)

**Decision**: Replan to run notes summarization in parallel with availability checks

**Auditor Check**:
- Create event: MEDIUM risk ✓ Intent check OK
- Create task: LOW risk ✓ Execute directly
- Create note: LOW risk ✓ Execute directly

**Execution**:
```
Saga begins: "Schedule meeting with prep"
  
  [Parallel Group 1]
  └─ Notes summarization
  └─ Availability checks (all 5 people)
  
  [Serial]
  └─ Find meeting time (depends on availability)
  
  [Parallel Group 2]
  └─ Create calendar event
  └─ Create prep document
  └─ Create prep task
  
Saga completes: Success ✓
```

**Result**:
- Meeting scheduled ✓
- Prep document created ✓
- Task created ✓
- Governance scorecard updated ✓
- Event stream captured ✓

---

## 💡 Best Practices

### When Using Each Agent:

**Task Agent**:
- ✓ Use for actionable items with deadlines
- ✓ Assign to team members
- ✓ Track progress over time
- ✗ Not for one-off items without accountability

**Calendar Agent**:
- ✓ Use for any scheduling need
- ✓ Always check availability first
- ✓ Use find_meeting_time for groups
- ✓ Add location and description
- ✗ Don't hardcode meeting times without checking availability

**Notes Agent**:
- ✓ Use for capturing decisions and ideas
- ✓ Tag notes immediately for findability
- ✓ Search before creating duplicate notes
- ✓ Summarize long documents
- ✗ Don't use notes for tasks or calendar events

**Orchestrator**:
- ✓ Wrap multi-step workflows in sagas
- ✓ Always let Critic and Auditor review
- ✓ Escalate when consensus < 40
- ✓ Monitor circuit breaker health
- ✗ Don't bypass governance for speed

### Governance Rules:

1. ✅ **Always** use sagas for multi-step workflows
2. ✅ **Always** check circuit breaker before delegating
3. ✅ **Always** recall memory before re-planning
4. ✅ **Always** log governance decisions
5. ✅ **Always** escalate with structured options
6. ❌ **Never** ignore Auditor safety vetoes
7. ❌ **Never** skip Vibe-checks for CRITICAL actions
8. ❌ **Never** retry without Critic approval

---

## 📊 Monitoring & Debugging

### Health Checks:
```bash
# System health
curl http://localhost:8000/health

# Agent status
curl http://localhost:8000/agents/status

# Critic audit
curl http://localhost:8000/workflows/{id}/audit

# DLQ health
curl http://localhost:8000/dlq/dashboard

# Governance metrics
curl http://localhost:8000/governance/scorecard
```

### Logs to Watch:
- `[Orchestrator]` - Request routing decisions
- `[Critic]` - Efficiency analysis and replan decisions
- `[Auditor]` - Security checks and veto decisions
- `[DLQ]` - Failed message retries
- `[Governance]` - Policy adjustments and consensus

---

## 🎓 Next Steps

1. **Read Agent Implementations**: Check `backend/agents/*.py` for detailed code
2. **Review Test Suite**: Look at `tests/test_agents.py` for usage examples
3. **Run Examples**: Execute `python demo.py` to see agents in action
4. **Build Your Workflow**: Create a workflow that combines multiple agents
5. **Monitor & Improve**: Watch governance scorecard to optimize policies

---

**Built with the power of autonomous agents that learn, adapt, and improve over time** 🚀
