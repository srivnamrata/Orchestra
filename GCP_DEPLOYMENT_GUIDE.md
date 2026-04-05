# Google Cloud Platform Deployment Guide

## Multi-Agent Productivity Assistant on Google Cloud Platform

This guide covers deploying the Multi-Agent Productivity Assistant to Google Cloud Platform with complete integration of GCP services.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [GCP Services Overview](#gcp-services-overview)
3. [Architecture](#architecture)
4. [Setup Instructions](#setup-instructions)
5. [Deployment Methods](#deployment-methods)
6. [Configuration](#configuration)
7. [Monitoring & Logging](#monitoring--logging)
8. [Troubleshooting](#troubleshooting)
9. [Cost Optimization](#cost-optimization)

---

## Prerequisites

### Tools & Access
- [ ] GCP Account with billing enabled
- [ ] `gcloud` CLI installed and configured
- [ ] Docker installed and running
- [ ] Terraform installed (v1.0+)
- [ ] kubectl installed (optional, for GKE)
- [ ] Git installed

### GCP Permissions Required
- [ ] Cloud Run Admin
- [ ] Pub/Sub Admin
- [ ] Vertex AI User
- [ ] Firestore Admin
- [ ] Service Accounts Admin
- [ ] Artifact Registry Writer
- [ ] Cloud Logging Admin

### Verify Prerequisites
```bash
# Check gcloud
gcloud --version

# Check Docker
docker --version

# Check Terraform
terraform --version

# Authenticate with GCP
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

---

## GCP Services Overview

### 1. **Cloud Run** - Application Deployment
- **Purpose:** Serverless container execution
- **Configuration:** 
  - Min instances: 1
  - Max instances: 100 (adjustable)
  - Memory: 1-2 GB
  - CPU: 1-2 vCPU
  - Timeout: 300 seconds
- **Cost:** ~$0.24 per 1M requests + compute per GB-second
- **Benefits:** Auto-scaling, zero infrastructure management, pay-per-use

### 2. **Cloud Pub/Sub** - Agent Communication
- **Purpose:** Real-time messaging between agents
- **Topics:**
  - `productivity-assistant-workflow-progress` - Step completions
  - `productivity-assistant-workflow-replan` - Critic replans
  - `productivity-assistant-agent-health` - Agent health metrics
  - `productivity-assistant-system-events` - System events
- **Cost:** ~$0.05 per 1M messages
- **Benefits:** Decoupled communication, reliable delivery, multiple subscribers

### 3. **Firestore** - Data Persistence
- **Purpose:** Store workflows, audit trails, decision history
- **Collections:**
  - `workflows` - Workflow state and history
  - `agents` - Agent configurations and metrics
  - `decisions` - AI decision records
  - `audit_logs` - Action audit logs
- **Cost:** Pay per read/write/delete operation
- **Benefits:** Real-time sync, serverless, automated backups

### 4. **Vertex AI (Gemini)** - LLM Integration
- **Purpose:** Semantic reasoning, planning, decision-making
- **Model:** gemini-1.5-pro (production) or gemini-1.5-flash (staging)
- **Cost:** Per token consumption (~$0.00075/1K input tokens, ~$0.003/1K output)
- **Benefits:** Enterprise-grade LLM, low latency, integrated with GCP

### 5. **Cloud Logging** - Application Logs
- **Purpose:** Centralized logging for all services
- **Integration:** Automatic JSON payload parsing
- **Features:**
  - Structured logging
  - Log-based metrics
  - Real-time log sink
- **Cost:** First 50GB free per month, then ~$0.50/GB

### 6. **Cloud Monitoring** - Metrics & Alerts
- **Purpose:** Monitor system health and performance
- **Metrics Tracked:**
  - Request latency
  - Error rates
  - LLM token usage
  - Pub/Sub message throughput
  - Firestore operations
- **Cost:** Free for basic metrics, charges for advanced monitoring

### 7. **Cloud Trace** - Distributed Tracing
- **Purpose:** Trace requests across services
- **Benefits:** Identify bottlenecks, optimize performance
- **Cost:** ~$2.50 per million spans

### 8. **Artifact Registry** - Container Registry
- **Purpose:** Store Docker images
- **Cost:** ~$0.10 per GB stored per month
- **Benefits:** Private, secure, integrated with Cloud Run

---

## Architecture

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Cloud Run Service                      │
│  (Multi-Agent Productivity Assistant Container)         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  • Orchestrator Agent       • Knowledge Agent           │
│  • Critic Agent             • Scheduler Agent           │
│  • Security Auditor         • Task Agent                │
│  • Debate Engine            • FastAPI Server            │
└──────────┬──────────────────────────────┬──────────────┘
           │                              │
           ↓                              ↓
    ┌─────────────┐              ┌──────────────┐
    │ Cloud Pub/Sub │             │ Firestore DB │
    ├─────────────┤              ├──────────────┤
    │ Topics:     │              │ Collections: │
    │ • Progress  │              │ • workflows  │
    │ • Replans   │              │ • agents     │
    │ • Health    │              │ • decisions  │
    │ • Events    │              │ • audit_logs │
    └─────────────┘              └──────────────┘
           ↑                              ↑
           └──────────────┬───────────────┘
                         │
                         ↓
            ┌────────────────────────┐
            │  Vertex AI (Gemini)    │
            │  LLM Reasoning Engine  │
            └────────────────────────┘
                         │
                         ├────────────────┐
                         ↓                ↓
            ┌──────────────────┐  ┌────────────────┐
            │ Cloud Logging    │  │ Cloud Monitoring
            │ (Structured Logs)│  │ (Metrics/Alerts)
            └──────────────────┘  └────────────────┘
```

### Data Flow

```
User Request
    ↓
Cloud Run API
    ↓
Orchestrator Agent → Generate Plan
    ↓
Knowledge Graph ← Build Context
    ↓
Start Sub-Agents (parallel)
    ├→ Scheduler Agent
    ├→ Task Agent
    └→ Knowledge Agent
    ↓
Critic Agent (monitors via Pub/Sub)
    ├→ Detect issues
    └→ Autonomous replan (if >15% efficiency)
    ↓
Security Auditor (reviews high-stakes actions)
    ├→ 5-point audit
    └→ Approve/Reject
    ↓
Debate Engine (consensus on controversial decisions)
    ├→ All agents vote
    └→ Fitness scoring
    ↓
Firestore (persist results)
    ↓
Cloud Logging (send logs)
    ↓
Respond to User
```

---

## Setup Instructions

### Step 1: Create GCP Project

```bash
# Create new project
gcloud projects create productivity-assistant \
    --name="Multi-Agent Productivity Assistant"

# Set as current project
gcloud config set project productivity-assistant

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
echo $PROJECT_ID
```

### Step 2: Enable Billing

```bash
# Link billing account to project
gcloud billing projects link $PROJECT_ID \
    --billing-account=YOUR_BILLING_ACCOUNT_ID

# Verify
gcloud billing projects describe $PROJECT_ID
```

### Step 3: Create Service Account

```bash
# Create service account
gcloud iam service-accounts create productivity-assistant-sa \
    --display-name="Productivity Assistant Service Account" \
    --description="Service account for deployment"

# Get service account email
SA_EMAIL="productivity-assistant-sa@${PROJECT_ID}.iam.gserviceaccount.com"
echo $SA_EMAIL

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/pubsub.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/datastore.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/monitoring.metricWriter"
```

### Step 4: Clone and Setup Repository

```bash
# Clone repository
git clone <repository-url>
cd MultiAgent-Productivity

# Install local dependencies (for development)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 5: Build and Push Docker Image

```bash
# Set region
REGION="us-central1"

# Create Artifact Registry repository
gcloud artifacts repositories create productivity-assistant \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository for Productivity Assistant"

# Configure Docker authentication
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Build Docker image
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/productivity-assistant/productivity-assistant:latest .

# Push to Artifact Registry
docker push $REGION-docker.pkg.dev/$PROJECT_ID/productivity-assistant/productivity-assistant:latest
```

---

## Deployment Methods

### Method 1: Terraform (Recommended)

```bash
# Navigate to terraform directory
cd deployment/terraform

# Initialize Terraform
terraform init

# Review plan (staging)
terraform plan -var-file="staging.tfvars" -out=tfplan

# Apply configuration (staging)
terraform apply tfplan

# For production
terraform plan -var-file="prod.tfvars" -out=tfplan-prod
terraform apply tfplan-prod

# Get outputs
terraform output cloud_run_url
terraform output service_account_email
terraform output pubsub_topics
```

### Method 2: Automated Deployment Script

#### macOS/Linux:
```bash
# Make script executable
chmod +x deployment/gcp-deploy.sh

# Deploy with image build
./deployment/gcp-deploy.sh \
    --project $PROJECT_ID \
    --region us-central1 \
    --env prod \
    --build \
    --deploy

# Deploy without image build
./deployment/gcp-deploy.sh \
    --project $PROJECT_ID \
    --region us-central1 \
    --env prod \
    --deploy
```

#### Windows (PowerShell):
```powershell
# Run deployment script
.\deployment\gcp-deploy.ps1 `
    -ProjectId $PROJECT_ID `
    -Region "us-central1" `
    -Environment "prod" `
    -BuildImage `
    -Deploy
```

### Method 3: Manual gcloud Commands

```bash
# Deploy container to Cloud Run
gcloud run deploy productivity-assistant \
    --image $REGION-docker.pkg.dev/$PROJECT_ID/productivity-assistant/productivity-assistant:latest \
    --platform managed \
    --region $REGION \
    --service-account $SA_EMAIL \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --set-env-vars ENVIRONMENT=production,GCP_PROJECT_ID=$PROJECT_ID,USE_FIRESTORE=true \
    --min-instances 1 \
    --max-instances 100 \
    --allow-unauthenticated
```

---

## Configuration

### Environment Variables

Key environment variables (set in main.tf or via gcloud):

```bash
# Deployment
ENVIRONMENT=production                    # development|staging|production
GCP_PROJECT_ID=your-project-id           # Your GCP Project ID
GCP_REGION=us-central1                   # GCP Region

# Services
USE_MOCK_LLM=false                       # true for testing, false for production
USE_MOCK_PUBSUB=false                    # true for testing, false for production
USE_FIRESTORE=true                       # Enable Firestore persistence

# Vertex AI
LLM_MODEL=gemini-1.5-pro                 # LLM model selection
VERTEX_AI_LOCATION=us-central1           # Vertex AI region

# Pub/Sub
PUBSUB_TOPIC_PREFIX=productivity-assistant

# Logging & Monitoring
ENABLE_CLOUD_LOGGING=true
ENABLE_CLOUD_MONITORING=true
ENABLE_CLOUD_TRACE=true
LOG_LEVEL=INFO                           # DEBUG|INFO|WARNING|ERROR

# Performance
MAX_CONCURRENT_WORKFLOWS=100
REQUEST_TIMEOUT_SECONDS=30
LLM_TIMEOUT_SECONDS=60
```

### Cloud Run Configuration

Recommended settings in terraform/prod.tfvars:

```hcl
# Performance
cloud_run_memory        = "2Gi"           # 2GB RAM
cloud_run_cpu           = "2"             # 2 CPU
cloud_run_min_instances = 1               # Scale down to 0 for cost savings
cloud_run_max_instances = 100             # Auto-scale up to 100

# Timeouts
timeout_seconds = 300                     # 5 minutes for long-running workflows

# Model
llm_model = "gemini-1.5-pro"             # gemini-1.5-flash for staging/cost

# Logging
log_level = "INFO"                        # DEBUG for troubleshooting
```

---

## Monitoring & Logging

### Cloud Logging

View logs from Cloud Run:

```bash
# Stream real-time logs
gcloud run logs read productivity-assistant \
    --limit 50 \
    --follow

# Search for errors
gcloud logging read "resource.type=cloud_run_revision AND severity=ERROR" \
    --limit 10

# Export logs to BigQuery for analysis
gcloud logging sinks create export-to-bq bigquery.googleapis.com/projects/$PROJECT_ID/datasets/logs \
    --log-filter='resource.type="cloud_run_revision"'
```

### Cloud Monitoring

Create dashboards:

```bash
# View Cloud Run metrics
gcloud monitoring dashboards create \
    --config-from-file=deployment/monitoring-dashboard.yaml
```

Check service health:

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe productivity-assistant \
    --platform managed \
    --region $REGION \
    --format='value(status.url)')

# Health check
curl $SERVICE_URL/health

# Full system status
curl $SERVICE_URL/
```

### Alerts

Create alerts for critical issues:

```bash
# Alert on high error rate (>5%)
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="Productivity Assistant - High Error Rate" \
    --condition-display-name="Error Rate > 5%" \
    --condition-threshold-value=0.05
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check service status
gcloud run services describe productivity-assistant \
    --platform managed \
    --region $REGION

# Check recent deployments
gcloud run revisions list --service=productivity-assistant

# View detailed logs
gcloud run logs read productivity-assistant --follow

# Rollback to previous revision
gcloud run services update-traffic productivity-assistant \
    --to-revisions PREVIOUS_REVISION=100
```

### LLM Errors

```bash
# Verify Vertex AI permissions
gcloud auth list

# Test Vertex AI access
gcloud ai models list --location=us-central1

# Check service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:$SA_EMAIL"
```

### Pub/Sub Issues

```bash
# List topics
gcloud pubsub topics list

# Check subscriptions
gcloud pubsub subscriptions list

# Test publish message
gcloud pubsub topics publish productivity-assistant-test-topic \
    --message="test message"

# Monitor message flow
gcloud pubsub subscriptions pull productivity-assistant-workflow-progress-sub
```

### Firestore Issues

```bash
# Check Firestore status
gcloud firestore collections list

# View database details
gcloud firestore databases describe

# Export data for backup
gcloud firestore export gs://YOUR_BUCKET/backup

# Restore from backup
gcloud firestore import gs://YOUR_BUCKET/backup
```

---

## Cost Optimization

### Reducing Costs

```bash
# 1. Use auto-scaling with lower min instances
cloud_run_min_instances = 0  # Scale to zero when idle
cloud_run_max_instances = 50

# 2. Use cheaper LLM for staging
llm_model = "gemini-1.5-flash"

# 3. Enable Cloud Run cache
cloud_run_cache_enabled = true

# 4. Reduce log verbosity in staging
log_level = "WARNING"  # Instead of INFO

# 5. Use Firestore spending limits
# Set via gcloud:
gcloud firestore databases update \
    --app-engine-api-enabled \
    --type=datastore-mode
```

### Cost Monitoring

```bash
# View Cloud Billing
gcloud billing accounts list
gcloud billing budgets create \
    --billing-account=YOUR_BILLING_ACCOUNT \
    --display-name="Productivity Assistant Budget" \
    --budget-amount=1000

# Estimate costs
# Cloud Run: $0.24/1M requests + $0.00001667/GB-second
# Pub/Sub: $0.05/1M messages  
# Firestore: Per operation (~$0.06/100K operations)
# Vertex AI: ~$0.00075/1K input tokens, ~$0.003/1K output
```

### Export/Billing Insights

Export usage data for custom analysis:

```bash
# Export to BigQuery
gcloud billing accounts list
gcloud billing budgets update BUDGET_ID \
    --billing-account=ACCOUNT_ID
```

---

## Production Checklist

- [ ] Authentication enabled (remove allUsers access)
- [ ] Cloud Armor configured for DDoS protection
- [ ] SSL/TLS certificate configured
- [ ] Backup strategy in place (Firestore daily backups)
- [ ] CDN enabled via Cloud CDN
- [ ] Monitoring and alerting configured
- [ ] Error budget defined and tracked
- [ ] Disaster recovery plan documented
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Cost optimization reviewed
- [ ] Documentation updated
- [ ] Team training completed

---

## Support & Further Reading

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Pub/Sub Documentation](https://cloud.google.com/pubsub/docs)
- [Firestore Documentation](https://cloud.google.com/firestore/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [GCP Pricing Calculator](https://cloud.google.com/products/calculator)

---

**Last Updated:** April 4, 2026
**Version:** 1.0.0
