# Quick Start Guide

## 5-Minute Setup

### 1. Prerequisites Check
```bash
python --version  # Should be 3.11+
pip --version
```

### 2. Navigate to Project
```bash
cd D:\MultiAgent-Productivity
```

### 3. Create Virtual Environment
```bash
python -m venv venv
.\venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment
```bash
copy .env.example .env
# Keep defaults for local testing (uses mock services)
```

### 6. Start the API Server
```bash
python -m uvicorn backend.api.main:app --reload
```

### 7. Test the API
Open browser: **http://localhost:8000/docs**

You'll see interactive Swagger documentation with all endpoints!

---

## Key Files to Understand

### Core Innovation
- **`backend/agents/critic_agent.py`** ⭐
  - Proactive goal anticipation
  - Autonomous workflow replanning
  - 5-dimensional issue detection

### System Architecture
- **`backend/agents/orchestrator_agent.py`**
  - Primary agent coordinator
  - Plan generation and execution
  
- **`backend/services/knowledge_graph_service.py`**
  - Semantic understanding
  - Task relationships
  
- **`backend/services/pubsub_service.py`**
  - Real-time agent communication

### API & Deployment
- **`backend/api/main.py`**
  - REST endpoints
  - Request routing
  
- **`Dockerfile`**
  - Container image definition
  
- **`deployment/cloudrun.yaml`**
  - Cloud Run configuration

---

## First Demo: Run the Demonstration

```bash
python demo.py
```

This shows:
- Bottleneck detection and optimization
- Goal drift detection
- Knowledge graph relationships
- Transparent decision making

---

## API Examples

### 1. Create a Workflow

```bash
curl -X POST http://localhost:8000/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Schedule weekly team sync on Friday",
    "description": "Find time for team meeting",
    "priority": "high",
    "context": {"participants": 5}
  }'
```

Response:
```json
{
  "workflow_id": "a1b2c3d4",
  "status": "created",
  "goal": "Schedule weekly team sync on Friday"
}
```

### 2. Check Workflow Status

```bash
curl http://localhost:8000/workflows/a1b2c3d4
```

### 3. Get Critic Agent Audit

```bash
curl http://localhost:8000/workflows/a1b2c3d4/audit
```

Shows all issues detected and autonomous replans executed!

### 4. View Knowledge Graph

```bash
curl http://localhost:8000/knowledge-graph/export
```

---

## Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test
pytest tests/test_agents.py::test_critic_detects_bottleneck -v

# With coverage
pytest tests/ --cov=backend
```

---

## Project Structure

```
D:\MultiAgent-Productivity/
├── README.md          ← Start here!
├── ARCHITECTURE.md    ← Deep dive
├── QUICKSTART.md      ← This file
├── demo.py           ← See it in action
├── requirements.txt   ← Dependencies
├── .env.example      ← Configuration
│
├── backend/
│   ├── agents/       ← All agents
│   │   ├── critic_agent.py         ⭐ THE INNOVATION
│   │   ├── orchestrator_agent.py
│   │   ├── scheduler_agent.py
│   │   ├── task_agent.py
│   │   └── knowledge_agent.py
│   │
│   ├── services/     ← Core services
│   │   ├── llm_service.py
│   │   ├── knowledge_graph_service.py
│   │   └── pubsub_service.py
│   │
│   ├── api/
│   │   └── main.py   ← FastAPI endpoints
│   │
│   └── config.py     ← Configuration
│
├── tests/
│   └── test_agents.py  ← Test suite
│
├── deployment/
│   └── cloudrun.yaml   ← GCP deployment
│
└── Dockerfile        ← Container image
```

---

## Environment Variables

Key settings in `.env`:

```bash
# LLM Service
USE_MOCK_LLM=true              # Set to false for real Vertex AI
LLM_MODEL=gemini-1.5-pro

# Pub/Sub
USE_MOCK_PUBSUB=true           # Set to false for real Cloud Pub/Sub

# Critic Agent
CRITIC_AGENT_ENABLED=true
CRITIC_EFFICIENCY_THRESHOLD=0.15  # Trigger replan if >15% improvement
CRITIC_CONFIDENCE_THRESHOLD=0.75  # Only replan if >75% confident

# API
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
```

---

## Deployment to GCP

### Step 1: Build Docker Image
```bash
docker build -t gcr.io/YOUR-PROJECT-ID/multi-agent-productivity .
```

### Step 2: Push to Container Registry
```bash
docker push gcr.io/YOUR-PROJECT-ID/multi-agent-productivity
```

### Step 3: Deploy to Cloud Run
```bash
gcloud run deploy multi-agent-productivity \
  --image gcr.io/YOUR-PROJECT-ID/multi-agent-productivity \
  --platform managed \
  --region us-central1 \
  --set-env-vars="ENVIRONMENT=production"
```

### Step 4: Enable APIs
```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable pubsub.googleapis.com
```

---

## Important Concepts

### Critic Agent - The Innovation

The **Critic Agent** represents leap forward in agentic AI:

1. **Monitors** workflow execution in real-time
2. **Audits** workflow health (5-dimensional analysis)
3. **Detects** problems (bottlenecks, goal drift, inefficiency)
4. **Generates** alternative plans
5. **Decides** autonomously whether to replan
6. **Explains** every decision transparently

This is what makes your system **stand out** from other automation tools.

### Knowledge Graph

Maintains **semantic relationships** between all entities:
- Tasks and goals
- Dependencies
- Parallel execution opportunities
- Critical paths

Used by Critic to understand context and make smart decisions.

### Pub/Sub Communication

**Asynchronous messaging** enables:
- Real-time progress monitoring
- Loose coupling between components
- Scalability (agents can scale independently)
- Extensibility (add consumers without changing publishers)

---

## Debugging

### View Logs

```bash
# Real-time logs while server is running
# Check terminal where you started the server

# API responses in browser
http://localhost:8000/docs
```

### Check Specific Workflow

```bash
# Get workflow status
curl http://localhost:8000/workflows/WORKFLOW_ID

# Get Critic audit report
curl http://localhost:8000/workflows/WORKFLOW_ID/audit

# View knowledge graph
curl http://localhost:8000/knowledge-graph/export
```

### Run Individual Tests

```bash
# Test bottleneck detection
pytest tests/test_agents.py::test_critic_detects_bottleneck -v -s

# Test knowledge graph
pytest tests/test_agents.py::test_knowledge_graph_circular_dependency -v -s
```

---

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
# Or use a different port
python -m uvicorn backend.api.main:app --port 8001
```

### Import Errors
```bash
# Make sure you're in the virtual environment
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### AsyncIO Issues
```bash
# If you see asyncio warnings, this is normal in development
# The mock services handle it gracefully
```

---

## Next Steps for Hackathon

### Immediate (First Few Hours)
1. ✅ Understand the architecture (you've read this!)
2. ✅ Run the demo (`python demo.py`)
3. ✅ Test the API endpoints
4. ✅ Read the innovation section in README

### For Judges (What to Show)
1. Run the API server
2. Create a workflow via API
3. Get the Critic audit report showing autonomous replans
4. Explain the 5-dimensional audit
5. Show knowledge graph relationships

### To Strengthen Before Submission
1. Add real calendar integration (Google Calendar API)
2. Implement Firestore persistence
3. Add email notifications
4. Create a web dashboard frontend
5. Write performance benchmarks

### Presentation Tips
- **Lead with**: Critic Agent's autonomous replanning
- **Show**: Real workflow optimization (30%+ efficiency gain)
- **Explain**: Transparent reasoning behind decisions
- **Demo**: API endpoints with actual requests/responses
- **Emphasize**: This is agentic AI, not just automation

---

## Success Criteria for Winning

✅ **Innovation**: Critic Agent with proactive goal anticipation  
✅ **Technical Complexity**: Multi-agent coordination with graph algorithms  
✅ **GCP Integration**: Vertex AI, Pub/Sub, Firestore, Cloud Run  
✅ **Practical Value**: Solves real scheduling problems  
✅ **Code Quality**: Well-structured, tested, documented  

---

## Quick Reference Commands

```bash
# Activate environment
.\venv\Scripts\activate

# Start API server
python -m uvicorn backend.api.main:app --reload

# Run demo
python demo.py

# Run tests
pytest tests/ -v

# Test specific endpoint
curl -X POST http://localhost:8000/workflows \
  -H "Content-Type: application/json" \
  -d '{"goal":"Test workflow","description":"Test","priority":"high"}'

# Access API docs
http://localhost:8000/docs
```

---

## Questions?

All code is well-documented:
- **Docstrings** in every module
- **Type hints** throughout
- **Comments** on complex logic
- **Examples** in README

Read the code - it's the best documentation!

---

**Good luck with the hackathon! 🚀**

Remember: The Critic Agent is what wins. Lead with it. Demonstrate it. Explain how it elevates your system to true agentic AI.
