# Multi-Agent Productivity System - Complete Deployment Guide

## Table of Contents

1. [Quick Start](#quick-start)
2. [Local Deployment](#local-deployment)
3. [Cloud Run Deployment](#cloud-run-deployment-recommended)
4. [Kubernetes Deployment](#kubernetes-deployment-gke)
5. [Production Checklist](#production-checklist)
6. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)

---

## Quick Start

### Local Testing (30 seconds)

```bash
cd d:\MultiAgent-Productivity

# Start all services with one command
docker-compose up

# In another terminal, test the system
curl http://localhost:8000/health

# View logs in real-time
docker-compose logs -f orchestrator
```

### Production Deployment (5 minutes with setup)

```bash
# 1. Set up GCP
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Deploy
./deploy-to-cloud.sh YOUR_PROJECT_ID us-central1

# 3. Get URL
gcloud run services describe multi-agent-orchestrator --format='value(status.url)'
```

---

## Local Deployment

### Prerequisites

- Docker & Docker Compose installed
- Python 3.11+ (for local development)
- ~2GB free disk space

### Step 1: Verify Setup

```bash
docker --version
docker-compose --version
```

Expected output:
```
Docker version 24.0.0+
docker-compose version 2.20.0+
```

### Step 2: Build Images

```bash
cd d:\MultiAgent-Productivity

# Start all services (builds images on first run)
docker-compose up
```

The first run takes 3-5 minutes:
- Downloads base images
- Installs dependencies
- Builds 7 service images

### Step 3: Verify Services

In another terminal:

```bash
# Check all services are healthy
curl http://localhost:8000/health
curl http://localhost:8001/health  # Task
curl http://localhost:8002/health  # Calendar
curl http://localhost:8003/health  # Notes
curl http://localhost:8004/health  # Critic
curl http://localhost:8005/health  # Auditor
curl http://localhost:8006/health  # Event Monitor

# Should return: {"status": "healthy"}
```

### Step 4: Test API Endpoints

```bash
# Create a task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "Testing the system",
    "priority": "high"
  }'

# List tasks
curl http://localhost:8000/tasks

# Create calendar event
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Event",
    "start_time": "2024-01-15T09:00:00Z",
    "end_time": "2024-01-15T10:00:00Z"
  }'

# Create note
curl -X POST http://localhost:8000/notes \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Note",
    "content": "This is a test note"
  }'
```

### Step 5: View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f orchestrator
docker-compose logs -f task-mcp
docker-compose logs -f calendar-mcp

# Last 50 lines
docker-compose logs --tail=50
```

### Step 6: Stop Services

```bash
# Stop all services
docker-compose down

# Remove volumes (deletes local data)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

---

## Cloud Run Deployment (Recommended)

### Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **Docker** installed
4. **~15 minutes** for first-time setup

### Step 1: GCP Setup (One-time)

```bash
# Authenticate with Google Cloud
gcloud auth login

# Set default project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs (takes 1-2 minutes)
gcloud services enable \
  run.googleapis.com \
  containerregistry.googleapis.com \
  cloudbuild.googleapis.com \
  firestore.googleapis.com \
  pubsub.googleapis.com \
  logging.googleapis.com

# Create Firestore database
gcloud firestore databases create \
  --region=us-central1 \
  --type=firestore-native

# Create Pub/Sub topics
gcloud pubsub topics create prod-events
gcloud pubsub topics create prod-audit
gcloud pubsub topics create prod-errors
```

Expected time: 2-3 minutes

### Step 2: Configure Docker Registry

```bash
# Configure Docker to push to Google Container Registry
gcloud auth configure-docker
```

### Step 3: Run Deployment Script

```bash
# Update deploy script permissions
chmod +x deploy-to-cloud.sh

# Deploy to Cloud Run
./deploy-to-cloud.sh YOUR_PROJECT_ID us-central1
```

What the script does:
1. Builds 7 Docker images (3-5 minutes)
2. Pushes to Google Container Registry (2-3 minutes)
3. Deploys 7 services to Cloud Run (2-3 minutes)
4. Configures networking and health checks (1 minute)

Total time: ~10 minutes

### Step 4: Get Service URLs

```bash
# Get orchestrator URL
ORCHESTRATOR_URL=$(gcloud run services describe multi-agent-orchestrator \
  --region=us-central1 --format='value(status.url)')

echo $ORCHESTRATOR_URL

# Test the service
curl $ORCHESTRATOR_URL/health
```

### Step 5: Configure Environment

```bash
# Update MCP service URLs in production config
gcloud run services update multi-agent-orchestrator \
  --set-env-vars="MCP_TASK_HOST=$(gcloud run services describe multi-agent-task --region=us-central1 --format='value(status.url)' | sed 's|https://||;s|/$||')" \
  --region=us-central1
```

Or, use service names for internal communication:

```bash
gcloud run services update multi-agent-orchestrator \
  --set-env-vars="MCP_TASK_HOST=multi-agent-task,MCP_CALENDAR_HOST=multi-agent-calendar,MCP_NOTES_HOST=multi-agent-notes,MCP_CRITIC_HOST=multi-agent-critic,MCP_AUDITOR_HOST=multi-agent-auditor,MCP_EVENT_MONITOR_HOST=multi-agent-event-monitor" \
  --region=us-central1
```

### Step 6: Verify Cloud Deployment

```bash
# List all deployed services
gcloud run services list --format="table(serviceName,status,url)"

# View logs
gcloud run logs read multi-agent-orchestrator --limit=20

# Check service details
gcloud run services describe multi-agent-orchestrator --region=us-central1
```

---

## Kubernetes Deployment (GKE)

### Prerequisites

1. **Google Cloud Account** with Kubernetes Engine API enabled
2. **kubectl** installed
3. **gcloud CLI** configured
4. **~20 minutes** for first-time setup

### Step 1: Create GKE Cluster

```bash
# Create cluster (takes 5-10 minutes)
gcloud container clusters create multi-agent-cluster \
  --zone=us-central1-a \
  --num-nodes=3 \
  --machine-type=n1-standard-2 \
  --enable-autoscaling \
  --min-nodes=3 \
  --max-nodes=10

# Get credentials
gcloud container clusters get-credentials multi-agent-cluster --zone=us-central1-a

# Verify connection
kubectl get nodes
```

### Step 2: Deploy Services

```bash
# Update PROJECT_ID in k8s-deployment.yaml
sed -i 's/PROJECT_ID/YOUR_PROJECT_ID/g' k8s-deployment.yaml

# Create namespace and deploy
kubectl apply -f k8s-deployment.yaml

# Wait for rollout
kubectl rollout status deployment/orchestrator -n multi-agent --timeout=5m

# Check pods
kubectl get pods -n multi-agent
```

### Step 3: Get Service URL

```bash
# Get external IP
kubectl get service orchestrator -n multi-agent

# Wait for external IP to be assigned (might take 1-2 minutes)
# Then test:
curl http://EXTERNAL_IP:8000/health
```

### Step 4: View Logs

```bash
# View logs for orchestrator
kubectl logs deployment/orchestrator -n multi-agent -f

# View logs for specific pod
kubectl logs pod/orchestrator-xxxxx -n multi-agent -f

# View all logs
kubectl logs -n multi-agent -l app=orchestrator --all-containers=true
```

### Step 5: Scale Services

```bash
# Scale orchestrator to 5 replicas
kubectl scale deployment orchestrator -n multi-agent --replicas=5

# Scale other services
kubectl scale deployment task-mcp -n multi-agent --replicas=3
kubectl scale deployment calendar-mcp -n multi-agent --replicas=3
```

---

## Production Checklist

Before deploying to production, ensure:

### Security ( Required)

- [ ] Disable public access for MCP services
  ```bash
  gcloud run services update multi-agent-orchestrator \
    --no-allow-unauthenticated --region=us-central1
  ```

- [ ] Set up IAM roles
  ```bash
  gcloud iam service-accounts create multi-agent-app
  gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=serviceAccount:multi-agent-app@PROJECT_ID.iam.gserviceaccount.com \
    --role=roles/datastore.admin
  ```

- [ ] Configure VPC connector (for private database access)
  ```bash
  gcloud compute networks vpc-access connectors create multi-agent-connector \
    --network=default --region=us-central1 \
    --min-instances=2 --max-instances=10
  ```

- [ ] Enable Cloud Audit Logs
  ```bash
  gcloud logging sinks create firestore-audit logging.googleapis.com/projects/PROJECT_ID/logs/firestore_admin_activity \
    --log-filter='protoPayload.serviceName="firestore.googleapis.com"'
  ```

### Performance (Recommended)

- [ ] Set appropriate resource limits
  - Orchestrator: 1 CPU, 1Gi memory
  - MCP Services: 0.5 CPU, 512Mi memory

- [ ] Enable auto-scaling
  ```bash
  gcloud run services update multi-agent-orchestrator \
    --min-instances=1 --max-instances=100 --region=us-central1
  ```

- [ ] Set up CDN for static assets (if applicable)

- [ ] Configure connection pooling in MCP clients
  - Connection timeout: 5 seconds
  - Pool size: 10 connections per service
  - Retry logic: 3 attempts with exponential backoff

### Monitoring (Recommended)

- [ ] Set up Cloud Monitoring dashboards
- [ ] Configure log aggregation
- [ ] Set up alerting policies for error rates
- [ ] Enable distributed tracing (Cloud Trace)
- [ ] Monitor Firestore quota and costs

### Data & Backups (Required)

- [ ] Enable Firestore backups
  ```bash
  gcloud firestore backups create --database=default
  ```

- [ ] Set up backup retention policy
- [ ] Test disaster recovery procedure
- [ ] Document data retention policies

### Documentation (Required)

- [ ] Document all deployment steps
- [ ] Maintain runbook for common issues
- [ ] Document API endpoints and usage
- [ ] Create deployment checklist
- [ ] Document scaling procedures

---

## Monitoring and Troubleshooting

### Common Issues

#### 1. Services Can't Communicate

**Problem**: Orchestrator can't reach MCP servers

**Solution**:
```bash
# Check service URLs
gcloud run services describe multi-agent-orchestrator --format='value(status.url)'

# Verify environment variables
gcloud run services describe multi-agent-orchestrator --format='value(spec.template.spec.containers[0].env)'

# Update if needed
gcloud run services update multi-agent-orchestrator \
  --set-env-vars="MCP_TASK_HOST=multi-agent-task"
```

#### 2. Memory or CPU Issues

**Problem**: Services running out of memory

**Solution**:
```bash
# Check current allocation
gcloud run services describe multi-agent-orchestrator --format='value(spec.template.spec.containers[0].resources)'

# Increase resources
gcloud run services update multi-agent-orchestrator \
  --memory=2Gi --cpu=2 --region=us-central1
```

#### 3. High Latency

**Problem**: Slow response times

**Solution**:
1. Check logs for bottlenecks
2. Increase min instances:
   ```bash
   gcloud run services update multi-agent-orchestrator \
     --min-instances=3 --region=us-central1
   ```
3. Check Firestore indexes
4. Monitor network latency

#### 4. Build Failures

**Problem**: Docker build fails

**Solution**:
```bash
# Check build logs
gcloud builds list
gcloud builds log BUILD_ID

# Try manual build
docker build -t test:latest -f Dockerfile .

# Check for syntax errors
docker image inspect gcr.io/PROJECT_ID/multi-agent-orchestrator:latest
```

### Monitoring Commands

```bash
# View real-time metrics
gcloud monitoring read projects/PROJECT_ID/timeSeries \
  --format=json \
  --filter='metric.type="run.googleapis.com/request_count"'

# Get error rate
gcloud logging read \
  'resource.type=cloud_run_revision AND severity=ERROR' \
  --format=json \
  --limit=100

# Check Firestore usage
gcloud firestore databases describe default

# Monitor Pub/Sub
gcloud pubsub subscriptions describe prod-events-sub
```

---

## Support and Resources

- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **Firestore Docs**: https://cloud.google.com/firestore/docs
- **GKE Docs**: https://cloud.google.com/kubernetes-engine/docs
- **Cloud Build Docs**: https://cloud.google.com/build/docs
- **GitHub Issues**: [Your repo URL]

---

## Next Steps

1. Choose deployment method (Local → Cloud Run → GKE)
2. Complete GCP setup if deploying to cloud
3. Run deployment scripts
4. Verify services are healthy
5. Configure monitoring and alerts
6. Set up backup procedures
7. Document your deployment

**Estimated Total Time from Zero to Production: 30-60 minutes**

---

**Last Updated**: 2024
**Version**: 1.0
**Maintained By**: Multi-Agent Team
