# 🚀 GCP Deployment Guide - Interactive Step-by-Step

## Overview

This guide walks you through deploying the **8-Agent Multi-Agent Productivity System** to Google Cloud Platform. We'll do this **one step at a time** with verification checks.

### What You'll Deploy
- **Orchestrator** (FastAPI service)
- **8 MCP Agents** (Task, Calendar, Notes, Critic, Auditor, Event Monitor, Research, News)
- **Firestore** (Cloud database)
- **Pub/Sub** (Event messaging)
- **Cloud Run** (Serverless hosting)
- **Cloud Build** (CI/CD pipeline)

### Prerequisites
- Google Cloud account (with billing enabled)
- `gcloud` CLI installed locally
- Docker installed
- Git repository with code
- ~30 minutes total deployment time

---

## PHASE 1: Local Setup & Verification

### Step 1.1: Verify Local Installation

Run these commands to confirm your environment is ready:

```bash
# Check gcloud version
gcloud --version

# Check Docker
docker --version

# Check Docker daemon is running
docker ps

# Check git
git --version
```

**📋 Your Task:**
```
Run each command above and report:
- Are all versions showing (gcloud, Docker, git)?
- Is Docker daemon running (shows containers, not connection error)?
```

---

### Step 1.2: Configure gcloud CLI

Set up gcloud with your credentials:

```bash
# Log in to Google Cloud
gcloud auth login

# List your projects
gcloud projects list

# Note down your PROJECT_ID (looks like: my-project-12345)
```

**📋 Your Task:**
```
1. Run 'gcloud auth login' and complete browser authentication
2. Run 'gcloud projects list' and provide your PROJECT_ID
   
Export project ID for later use:
gcloud config set project YOUR_PROJECT_ID

Replace YOUR_PROJECT_ID with the actual ID from step 2.
```

---

### Step 1.3: Verify Your Repository

```bash
# Navigate to project directory
cd d:\MultiAgent-Productivity

# Check Git status
git status

# List key files
ls -la | grep -E "(docker-compose|Dockerfile|requirements.txt|cloudbuild)"
```

**📋 Your Task:**
```
1. Navigate to your project directory
2. Run 'git status' - it should show a working repository
3. Confirm these files exist:
   - Dockerfile
   - Dockerfile.mcp
   - docker-compose.yml
   - cloudbuild.yaml
   - deploy-to-cloud.sh
   - requirements.txt
   
Report: Are all files present?
```

---

## PHASE 2: GCP Project Initialization

### Step 2.1: Create/Select GCP Project

```bash
# Option A: If you have an existing project
gcloud config set project YOUR_PROJECT_ID

# Option B: Create a new project
gcloud projects create multi-agent-prod --name="Multi-Agent Productivity"
gcloud config set project multi-agent-prod

# Verify project is set
gcloud config get-value project
```

**📋 Your Task:**
```
Report back with:
1. Your PROJECT_ID
2. Output of 'gcloud config get-value project' 
   (should match your PROJECT_ID)
```

---

### Step 2.2: Enable Billing

```bash
# List billing accounts
gcloud billing accounts list

# Note your BILLING_ACCOUNT_ID (format: XXXXXX-XXXXXX-XXXXXX)

# Link billing to project (if needed)
# gcloud billing projects link YOUR_PROJECT_ID --billing-account=BILLING_ACCOUNT_ID
```

**📋 Your Task:**
```
1. Run 'gcloud billing accounts list'
2. Do you see at least one billing account? (Yes/No)

If NO:
- Go to: https://console.cloud.google.com/billing
- Set up a billing account first
- Then report back

If YES:
- Note your BILLING_ACCOUNT_ID
- Report: "Billing account found and linked"
```

---

### Step 2.3: Enable Required APIs

This is critical! We need these Google Cloud APIs:

```bash
# Save your project ID
export PROJECT_ID=$(gcloud config get-value project)

# Enable all required APIs (this takes 2-3 minutes)
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  firestore.googleapis.com \
  pubsub.googleapis.com \
  logging.googleapis.com \
  cloudscheduler.googleapis.com \
  \
  --project=$PROJECT_ID

# Verify APIs are enabled
gcloud services list --enabled --project=$PROJECT_ID | grep -E "(run|cloudbuild|firestore|pubsub)"
```

**📋 Your Task:**
```
1. Set PROJECT_ID environment variable:
   export PROJECT_ID=$(gcloud config get-value project)

2. Run the API enablement command (copy-paste the whole block)

3. Wait for all services to enable (2-3 minutes)

4. Run verification command at the end

Report back with:
- "All APIs enabled successfully" if you see all 7 services
- Any error messages if services didn't enable
```

---

## PHASE 3: Firestore Database Setup

### Step 3.1: Create Firestore Database

```bash
# Create Firestore in Native mode
gcloud firestore databases create \
  --location=us-central1 \
  --database-id=default \
  --type=firestore-native

# Verify database was created
gcloud firestore databases list
```

**📋 Your Task:**
```
1. Run the Firestore creation command

2. It will ask for confirmation - type 'Y' and press Enter

3. Wait for database creation (this takes 1-2 minutes)

4. Run the verification command

Report back with:
- Database name shown in output
- Status (should say "ACTIVE")
```

---

### Step 3.2: Create Firestore Indexes

We need to create composite indexes for efficient queries:

```bash
# Create indexes for research_articles collection
gcloud firestore indexes create \
  --collection=research_articles \
  --field-index=published_date:Ascending,category:Ascending

gcloud firestore indexes create \
  --collection=research_articles \
  --field-index=week:Ascending,year:Ascending

gcloud firestore indexes create \
  --collection=research_articles \
  --field-index=source:Ascending,published_date:Descending

# Create indexes for news_articles collection
gcloud firestore indexes create \
  --collection=news_articles \
  --field-index=published_date:Ascending,category:Ascending

gcloud firestore indexes create \
  --collection=news_articles \
  --field-index=week:Ascending,year:Ascending

gcloud firestore indexes create \
  --collection=news_articles \
  --field-index=source:Ascending,published_date:Descending

# Verify indexes
gcloud firestore indexes list
```

**📋 Your Task:**
```
1. Run each index creation command

2. You may see "Already exists" - that's OK!

3. Wait for all indexes to be created (takes 1-2 minutes)

4. Run the verification command

Report back with:
- Number of indexes shown in final list
- "All indexes created successfully"
```

---

## PHASE 4: Pub/Sub Topics Setup

### Step 4.1: Create Pub/Sub Topics

```bash
# Create topics for different services
gcloud pubsub topics create orchestrator-events
gcloud pubsub topics create task-updates
gcloud pubsub topics create calendar-updates
gcloud pubsub topics create research-articles-fetched
gcloud pubsub topics create news-articles-fetched
gcloud pubsub topics create system-events

# Create subscriptions for each topic
gcloud pubsub subscriptions create orchestrator-events-sub \
  --topic=orchestrator-events

gcloud pubsub subscriptions create system-events-sub \
  --topic=system-events

# Verify topics and subscriptions
gcloud pubsub topics list
gcloud pubsub subscriptions list
```

**📋 Your Task:**
```
1. Run each topic creation command

2. Run both verification commands at the end

Report back with:
- Number of topics created (should be 6)
- Number of subscriptions (should be 2+)
- "All Pub/Sub topics created successfully"
```

---

## PHASE 5: Container Registry Setup

### Step 5.1: Configure Docker for GCR

```bash
# Configure Docker authentication for Google Container Registry
gcloud auth configure-docker gcr.io

# Set your project ID
export PROJECT_ID=$(gcloud config get-value project)

# Test by building and pushing a simple test image
echo "FROM python:3.11-slim
RUN echo 'Test image'" > Dockerfile.test

docker build -t gcr.io/${PROJECT_ID}/test-image:latest -f Dockerfile.test .

docker push gcr.io/${PROJECT_ID}/test-image:latest

# Clean up test image
rm Dockerfile.test
```

**📋 Your Task:**
```
1. Run the 'gcloud auth configure-docker' command

2. Run the test build/push commands

3. You should see "Pushing" messages and then success

Report back with:
- "Docker authentication configured successfully"
- Whether the test image pushed successfully
- Any error messages if it failed
```

---

## PHASE 6: Service Account Creation

### Step 6.1: Create Service Account

```bash
export PROJECT_ID=$(gcloud config get-value project)

# Create service account for Cloud Run services
gcloud iam service-accounts create multi-agent-sa \
  --display-name="Multi-Agent Productivity Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:multi-agent-sa@${PROJECT_ID}.iam.gserviceaccount.com \
  --role=roles/datastore.user

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:multi-agent-sa@${PROJECT_ID}.iam.gserviceaccount.com \
  --role=roles/pubsub.editor

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:multi-agent-sa@${PROJECT_ID}.iam.gserviceaccount.com \
  --role=roles/logging.logWriter

# Create and download key
gcloud iam service-accounts keys create sa-key.json \
  --iam-account=multi-agent-sa@${PROJECT_ID}.iam.gserviceaccount.com

# Verify
gcloud iam service-accounts list
```

**📋 Your Task:**
```
1. Run all the service account creation commands

2. Run the verification command

Report back with:
- Service account email shown
- "Service account created successfully"
- Confirm sa-key.json file was created in your directory
```

---

## PHASE 7: Build & Push Images

### Step 7.1: Build Docker Images

```bash
export PROJECT_ID=$(gcloud config get-value project)

# Navigate to your project directory
cd d:\MultiAgent-Productivity

# Build orchestrator image
docker build -t gcr.io/${PROJECT_ID}/multi-agent-orchestrator:latest -f Dockerfile .

# Build MCP server images for each agent
for SERVICE in task calendar notes critic auditor event_monitor research news; do
  docker build \
    -t gcr.io/${PROJECT_ID}/multi-agent-${SERVICE}:latest \
    -f Dockerfile.mcp \
    --build-arg MCP_SERVER=${SERVICE} .
done

# List images
docker images | grep gcr.io
```

**📋 Your Task:**
```
1. Navigate to your project directory

2. Run the first docker build command (orchestrator)
   - Should complete in 2-3 minutes
   - Shows "Successfully tagged..."

3. Run the loop for MCP services
   - 8 services will build in sequence
   - Total time: 10-15 minutes

4. Run 'docker images | grep gcr.io' to verify

Report back with:
- How many images were built successfully? (should be 9)
- Any build errors encountered?
```

---

### Step 7.2: Push Images to GCR

```bash
export PROJECT_ID=$(gcloud config get-value project)

# Push orchestrator
docker push gcr.io/${PROJECT_ID}/multi-agent-orchestrator:latest

# Push all MCP services
for SERVICE in task calendar notes critic auditor event_monitor research news; do
  docker push gcr.io/${PROJECT_ID}/multi-agent-${SERVICE}:latest
done

# Verify images in registry
gcloud container images list
```

**📋 Your Task:**
```
1. Run the push commands

2. You'll see "Pushing" messages and progress bars

3. Total time: 15-20 minutes (first time is slower)

4. Run verification command at end

Report back with:
- Number of images in GCR (should be 9)
- "All images pushed successfully"
- Any upload errors?
```

---

## PHASE 8: Deploy to Cloud Run

### Step 8.1: Deploy Orchestrator Service

```bash
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1
export SA_EMAIL=multi-agent-sa@${PROJECT_ID}.iam.gserviceaccount.com

# Deploy orchestrator
gcloud run deploy multi-agent-orchestrator \
  --image=gcr.io/${PROJECT_ID}/multi-agent-orchestrator:latest \
  --platform=managed \
  --region=${REGION} \
  --memory=1Gi \
  --cpu=1 \
  --timeout=3600 \
  --allow-unauthenticated \
  --service-account=${SA_EMAIL} \
  --set-env-vars=\
FIRESTORE_MODE=production,\
PROJECT_ID=${PROJECT_ID},\
MCP_TASK_HOST=multi-agent-task,\
MCP_CALENDAR_HOST=multi-agent-calendar,\
MCP_NOTES_HOST=multi-agent-notes,\
MCP_CRITIC_HOST=multi-agent-critic,\
MCP_AUDITOR_HOST=multi-agent-auditor,\
MCP_EVENT_MONITOR_HOST=multi-agent-event-monitor,\
MCP_RESEARCH_HOST=multi-agent-research,\
MCP_NEWS_HOST=multi-agent-news

# Note the service URL displayed
# Verify deployment
gcloud run services describe multi-agent-orchestrator --region=${REGION}
```

**📋 Your Task:**
```
1. Run the deployment command

2. Wait for deployment to complete (3-5 minutes)

3. You'll see a service URL like:
   https://multi-agent-orchestrator-xxxxx.run.app

4. Run the verification command

Report back with:
- Service URL (copy the full URL)
- Status shown in describe output
- "Orchestrator deployed successfully"
```

---

### Step 8.2: Deploy MCP Services

```bash
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1
export SA_EMAIL=multi-agent-sa@${PROJECT_ID}.iam.gserviceaccount.com

# Deploy all MCP services
for SERVICE in task calendar notes critic auditor event_monitor research news; do
  PORT=$((8000 + $(echo ${SERVICE} | tr -dc '0-9' | head -c 1)))
  
  case ${SERVICE} in
    task) PORT=8001 ;;
    calendar) PORT=8002 ;;
    notes) PORT=8003 ;;
    critic) PORT=8004 ;;
    auditor) PORT=8005 ;;
    event_monitor) PORT=8006 ;;
    research) PORT=8007 ;;
    news) PORT=8008 ;;
  esac
  
  echo "Deploying ${SERVICE} on port ${PORT}..."
  
  gcloud run deploy multi-agent-${SERVICE} \
    --image=gcr.io/${PROJECT_ID}/multi-agent-${SERVICE}:latest \
    --platform=managed \
    --region=${REGION} \
    --memory=512Mi \
    --cpu=1 \
    --timeout=3600 \
    --allow-unauthenticated \
    --service-account=${SA_EMAIL} \
    --set-env-vars=\
FIRESTORE_MODE=production,\
PROJECT_ID=${PROJECT_ID},\
MCP_SERVER=${SERVICE},\
MCP_PORT=${PORT}
done

# Verify all services
gcloud run services list
```

**📋 Your Task:**
```
1. Run the deployment loop

2. Each service deploys in 3-5 minutes
   - 8 services = 24-40 minutes total for this step
   - Look for "Service deployed" messages

3. Run 'gcloud run services list' to verify

Report back with:
- Total services deployed (should be 9)
- Any failed deployments?
- "All MCP services deployed successfully"
```

---

## PHASE 9: Verification & Testing

### Step 9.1: Health Check All Services

```bash
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1

# Get orchestrator URL
ORCH_URL=$(gcloud run services describe multi-agent-orchestrator \
  --region=${REGION} --format='value(status.url)')

echo "Orchestrator URL: ${ORCH_URL}"

# Test orchestrator health
curl ${ORCH_URL}/health

# Test each MCP service
for SERVICE in task calendar notes critic auditor event_monitor research news; do
  SERVICE_URL=$(gcloud run services describe multi-agent-${SERVICE} \
    --region=${REGION} --format='value(status.url)')
  
  echo "Testing ${SERVICE}..."
  curl ${SERVICE_URL}/health
done
```

**📋 Your Task:**
```
1. Run the health check script

2. Look for responses like:
   {"status": "healthy"} or {"status": "ready"}

Report back with:
- Orchestrator health status
- How many MCP services responded healthy? (should be 8)
- Any services that didn't respond?
- Any error messages?
```

---

### Step 9.2: Test API Functionality

```bash
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1

# Get orchestrator URL
ORCH_URL=$(gcloud run services describe multi-agent-orchestrator \
  --region=${REGION} --format='value(status.url)')

# Test create task endpoint
curl -X POST ${ORCH_URL}/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "Testing GCP deployment",
    "project_id": "test-project"
  }'

# Test fetch research highlights
curl -X POST ${ORCH_URL}/research/highlights \
  -H "Content-Type: application/json" \
  -d '{
    "max_articles": 5
  }'

# Test fetch news headlines
curl -X POST ${ORCH_URL}/news/headlines \
  -H "Content-Type: application/json" \
  -d '{
    "region": "both",
    "max_articles": 5
  }'
```

**📋 Your Task:**
```
1. Run the curl commands

2. You should see JSON responses

Report back with:
- Task creation response (any errors?)
- Research highlights response
- News headlines response
- "API endpoints working successfully"
```

---

### Step 9.3: Check Firestore Collections

```bash
# View Firestore collections via CLI
gcloud firestore collections list

# View documents in a collection (if any exist)
gcloud firestore documents list --collection=research_articles --limit=5

gcloud firestore documents list --collection=news_articles --limit=5
```

**📋 Your Task:**
```
1. Run the collections list command

Report back with:
- Collections shown (may be empty initially)
- "Firestore collections accessible"
```

---

## PHASE 10: CI/CD Pipeline Setup

### Step 10.1: Connect to Cloud Build

```bash
# Your cloudbuild.yaml should already be in the repo
# Cloud Build will auto-detect it

# Trigger a manual build to test the pipeline
export PROJECT_ID=$(gcloud config get-value project)

gcloud builds submit \
  --config=cloudbuild.yaml \
  --project=${PROJECT_ID}

# Check build status
gcloud builds list --limit=1

# View build logs
BUILD_ID=$(gcloud builds list --limit=1 --format='value(id)')
gcloud builds log ${BUILD_ID} --stream=true
```

**📋 Your Task:**
```
1. Run the 'gcloud builds submit' command

2. Wait for build to complete (5-10 minutes)

3. You'll see build steps executing

Report back with:
- Build completed successfully? (Yes/No)
- Any build failures shown in logs?
- Final message from build log
```

---

## PHASE 11: Environment Configuration

### Step 11.1: Create .env.production File

```bash
# Create environment file for production
cat > .env.production << 'EOF'
# GCP Configuration
PROJECT_ID=$(gcloud config get-value project)
FIRESTORE_MODE=production
GOOGLE_APPLICATION_CREDENTIALS=/app/sa-key.json

# Services Configuration
MCP_TASK_HOST=multi-agent-task.run.app
MCP_CALENDAR_HOST=multi-agent-calendar.run.app
MCP_NOTES_HOST=multi-agent-notes.run.app
MCP_CRITIC_HOST=multi-agent-critic.run.app
MCP_AUDITOR_HOST=multi-agent-auditor.run.app
MCP_EVENT_MONITOR_HOST=multi-agent-event-monitor.run.app
MCP_RESEARCH_HOST=multi-agent-research.run.app
MCP_NEWS_HOST=multi-agent-news.run.app

# Logging
LOG_LEVEL=INFO

# Performance
API_TIMEOUT=30
BATCH_SIZE=100
CACHE_TTL=3600
EOF

# Verify file was created
cat .env.production
```

**📋 Your Task:**
```
1. Run the cat command to create .env.production

2. Verify the file was created with all settings

Report back with:
- "Production environment file created"
```

---

## PHASE 12: Final Deployment Summary

### Step 12.1: Generate Deployment Summary

```bash
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1

echo "=== DEPLOYMENT SUMMARY ==="
echo ""
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo ""
echo "=== Cloud Run Services ==="
gcloud run services list

echo ""
echo "=== Firestore Database ==="
gcloud firestore databases list

echo ""
echo "=== Pub/Sub Topics ==="
gcloud pubsub topics list

echo ""
echo "=== Container Images ==="
gcloud container images list

echo ""
echo "=== Service Accounts ==="
gcloud iam service-accounts list --filter="email:multi-agent*"
```

**📋 Your Task:**
```
Run the summary command and report back with:
1. Project ID
2. All services deployed (should show 9 Cloud Run services)
3. Firestore database status
4. Pub/Sub topics count
5. Container images count (should be 9)
6. Service account created
```

---

## What's Next: Monitoring & Troubleshooting

### View Logs

```bash
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1

# View orchestrator logs
gcloud run services logs read multi-agent-orchestrator \
  --region=${REGION} \
  --limit=50

# View specific error logs
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=multi-agent-orchestrator" \
  --limit 20 \
  --format json
```

### Monitor Performance

```bash
# View metrics dashboard
echo "Go to: https://console.cloud.google.com/run/detail/${REGION}/multi-agent-orchestrator/metrics"

# View Cloud Logging
echo "Go to: https://console.cloud.google.com/logs"
```

---

## Summary of All Steps

| Phase | Step | Task | Time |
|-------|------|------|------|
| 1 | 1.1-1.3 | Local setup & verification | 5 min |
| 2 | 2.1-2.3 | GCP project initialization | 10 min |
| 3 | 3.1-3.2 | Firestore setup | 5 min |
| 4 | 4.1 | Pub/Sub setup | 3 min |
| 5 | 5.1 | Container Registry setup | 5 min |
| 6 | 6.1 | Service account creation | 3 min |
| 7 | 7.1-7.2 | Build & push images | 30 min |
| 8 | 8.1-8.2 | Deploy to Cloud Run | 40 min |
| 9 | 9.1-9.3 | Verification & testing | 10 min |
| 10 | 10.1 | CI/CD pipeline setup | 10 min |
| 11 | 11.1 | Environment configuration | 2 min |
| 12 | 12.1 | Final summary | 2 min |
| | **TOTAL** | **Complete deployment** | **~125 min (2 hours)** |

---

## Troubleshooting Guide

### Common Issues & Solutions

#### Issue: "Permission denied" when enabling APIs

```bash
# Solution: Verify billing is enabled
gcloud billing accounts list
gcloud billing projects link YOUR_PROJECT_ID --billing-account=YOUR_BILLING_ACCOUNT

# Then retry API enablement
```

#### Issue: Docker push fails with authentication error

```bash
# Solution: Re-authenticate Docker
gcloud auth login
gcloud auth configure-docker gcr.io
```

#### Issue: Cloud Run deployment times out

```bash
# Solution: Increase timeout
gcloud run deploy SERVICE_NAME \
  --timeout=3600 \
  # other flags...
```

#### Issue: Services can't communicate

```bash
# Solution: Check service URLs in environment variables
gcloud run services describe SERVICE_NAME --format='value(status.url)'

# Update orchestrator environment variables if needed
gcloud run services update multi-agent-orchestrator \
  --set-env-vars=MCP_TASK_HOST=multi-agent-task.run.app
```

---

## Need Help?

If you encounter any errors in any step:

1. **Note the exact error message**
2. **Tell me which step you're on** (e.g., "Phase 7, Step 7.1")
3. **Send the full error output**
4. **I'll help you debug and fix it**

Let's take this one step at a time! 🚀

---

**Ready to start?**

👉 **Begin with PHASE 1, Step 1.1 and report back when complete!**

---

*Last Updated: April 5, 2026*  
*Interactive GCP Deployment Guide v1.0*
