# Cloud Run Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Multi-Agent Productivity System to Google Cloud Run.

## Prerequisites

### Required Tools
- Google Cloud CLI (gcloud)
- Docker and Docker Compose
- Git
- A Google Cloud project

### GCP Setup

1. **Create a project** (if you don't have one):
   ```bash
   gcloud projects create multi-agent-productivity --name="Multi-Agent Productivity"
   gcloud config set project multi-agent-productivity
   ```

2. **Enable required APIs**:
   ```bash
   gcloud services enable \
     run.googleapis.com \
     containerregistry.googleapis.com \
     cloudbuild.googleapis.com \
     firestore.googleapis.com \
     pubsub.googleapis.com \
     compute.googleapis.com \
     logging.googleapis.com
   ```

3. **Authenticate with Docker**:
   ```bash
   gcloud auth configure-docker
   ```

4. **Create Firestore database**:
   ```bash
   gcloud firestore databases create \
     --region=us-central1 \
     --type=firestore-native
   ```

5. **Create Pub/Sub topics**:
   ```bash
   gcloud pubsub topics create prod-events
   gcloud pubsub topics create prod-audit
   gcloud pubsub topics create prod-errors
   gcloud pubsub subscriptions create prod-events-sub --topic=prod-events
   gcloud pubsub subscriptions create prod-audit-sub --topic=prod-audit
   gcloud pubsub subscriptions create prod-errors-sub --topic=prod-errors
   ```

## Deployment Methods

### Method 1: Automated Deployment (Recommended)

1. **Prepare configuration**:
   ```bash
   # Copy and configure production environment
   cp .env.production .env.production.local
   
   # Edit with your actual project ID
   sed -i 's/your-gcp-project-id/MY-PROJECT-ID/g' .env.production.local
   ```

2. **Run deployment script**:
   ```bash
   chmod +x deploy-to-cloud.sh
   ./deploy-to-cloud.sh MY-PROJECT-ID us-central1
   ```

3. **Verify deployment**:
   ```bash
   gcloud run services list --format="table(serviceName,status,url)"
   ```

### Method 2: CI/CD with Cloud Build

1. **Connect repository**:
   ```bash
   gcloud builds connect --repository-name=multi-agent --repository-owner=YOUR_GITHUB_USER
   ```

2. **Create build trigger**:
   ```bash
   gcloud builds triggers create github \
     --name=multi-agent-deploy \
     --repo-name=multi-agent \
     --repo-owner=YOUR_GITHUB_USER \
     --branch-pattern=^main$ \
     --build-config=cloudbuild.yaml
   ```

3. **Push to trigger deployment**:
   ```bash
   git push origin main
   ```

### Method 3: Manual Docker Deployment

1. **Build images**:
   ```bash
   docker build -t gcr.io/MY-PROJECT-ID/multi-agent-orchestrator:latest -f Dockerfile .
   
   docker build \
     -t gcr.io/MY-PROJECT-ID/multi-agent-task:latest \
     -f Dockerfile.mcp \
     --build-arg MCP_SERVER=task .
   
   docker build \
     -t gcr.io/MY-PROJECT-ID/multi-agent-calendar:latest \
     -f Dockerfile.mcp \
     --build-arg MCP_SERVER=calendar .
   
   # ... repeat for notes, critic, auditor, event_monitor
   ```

2. **Push images**:
   ```bash
   docker push gcr.io/MY-PROJECT-ID/multi-agent-orchestrator:latest
   docker push gcr.io/MY-PROJECT-ID/multi-agent-task:latest
   # ... push all images
   ```

3. **Deploy services**:
   ```bash
   gcloud run deploy multi-agent-orchestrator \
     --image=gcr.io/MY-PROJECT-ID/multi-agent-orchestrator:latest \
     --platform=managed \
     --region=us-central1 \
     --memory=1Gi \
     --cpu=1 \
     --allow-unauthenticated \
     --set-env-vars="FIRESTORE_MODE=production,PROJECT_ID=MY-PROJECT-ID"
   ```

## Post-Deployment Configuration

### 1. Configure Service Networking

Cloud Run services on the same region can communicate via service names:

```yaml
# Update MCP client configuration to use Cloud Run service URLs instead of localhost
MCP_TASK_HOST: https://multi-agent-task-RANDOM.run.app
MCP_CALENDAR_HOST: https://multi-agent-calendar-RANDOM.run.app
# ... etc
```

### 2. Set up API Gateway (Optional)

For public access through a single endpoint:

```bash
gcloud api-gateway apis create multi-agent \
  gcloud api-gateway api-configs create v1 \
    --api=multi-agent \
    --openapi-spec=openapi-spec.yaml
```

### 3. Configure Load Balancing (Optional)

For improved performance and reliability:

```bash
gcloud compute backend-services create multi-agent-backend \
  --global \
  --protocol=HTTP2 \
  --health-checks=multi-agent-health-check
```

## Monitoring and Logs

### View Logs

```bash
# Orchestrator logs
gcloud run logs read multi-agent-orchestrator --limit 50

# All services logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=multi-agent-*" \
  --format json --limit 100

# Filter by severity
gcloud logging read "severity>=ERROR AND resource.type=cloud_run_revision" \
  --format json --limit 50
```

### Set up Monitoring

```bash
# Create uptime checks
gcloud monitoring uptime create multi-agent \
  --display-name="Multi-Agent Orchestrator" \
  --monitored-resource=uptime-url \
  --http-check \
  --resource-labels=host=<ORCHESTRATOR_URL>

# Create alert policy
gcloud alpha monitoring policies create \
  --display-name="Multi-Agent Error Rate" \
  --condition-display-name="High error rate"
```

## Scaling Configuration

### Auto-scaling

By default, Cloud Run handles auto-scaling. To customize:

```bash
gcloud run services update multi-agent-orchestrator \
  --min-instances=1 \
  --max-instances=100 \
  --region=us-central1
```

### Resource Allocation

```bash
# Update CPU and memory
gcloud run services update multi-agent-orchestrator \
  --cpu=2 \
  --memory=2Gi \
  --region=us-central1
```

## Security Configuration

### 1. Restrict Access

```bash
# Require authentication
gcloud run services update multi-agent-orchestrator \
  --no-allow-unauthenticated \
  --region=us-central1

# Grant access to specific users
gcloud run services add-iam-policy-binding multi-agent-orchestrator \
  --member=user:user@example.com \
  --role=roles/run.invoker \
  --region=us-central1
```

### 2. Set up VPC Connector

```bash
# Create VPC connector
gcloud compute networks vpc-access connectors create multi-agent-connector \
  --network=default \
  --region=us-central1 \
  --min-instances=2 \
  --max-instances=10

# Update service to use VPC connector
gcloud run services update multi-agent-orchestrator \
  --vpc-connector=multi-agent-connector \
  --vpc-egress=all \
  --region=us-central1
```

### 3. Enable Identity and Access Management

```bash
# Create service account
gcloud iam service-accounts create multi-agent-app

# Grant Firestore access
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=serviceAccount:multi-agent-app@PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/datastore.admin

# Update service to use service account
gcloud run services update multi-agent-orchestrator \
  --service-account=multi-agent-app@PROJECT_ID.iam.gserviceaccount.com \
  --region=us-central1
```

## Troubleshooting

### Service won't start

1. Check logs for errors:
   ```bash
   gcloud run logs read multi-agent-orchestrator --limit 20
   ```

2. Verify environment variables are set correctly

3. Ensure all dependencies are installed in requirements.txt

### Services can't communicate

1. Verify services are on the same region

2. Check Cloud Run service-to-service authentication settings

3. Update MCP client configuration with correct service URLs

### Memory/CPU issues

1. Monitor resource usage:
   ```bash
   gcloud monitoring read projects/PROJECT_ID/timeSeries \
     --filter="metric.type=run.googleapis.com/request_count"
   ```

2. Increase allocation:
   ```bash
   gcloud run services update multi-agent-orchestrator \
     --memory=2Gi --cpu=2 --region=us-central1
   ```

## Cost Optimization

1. **Use appropriate resource allocation**:
   - Start with 512Mi memory, 0.5 CPU
   - Monitor and scale up only if needed

2. **Set min-instances**:
   ```bash
   gcloud run services update multi-agent-orchestrator \
     --min-instances=0 --max-instances=10
   ```

3. **Use Cloud Run Scheduler for batch jobs**:
   ```bash
   gcloud scheduler jobs create app-engine multi-agent-batch \
     --schedule="0 2 * * *" \
     --http-method=POST \
     --uri=<DEPLOYMENTS_URL>/batch \
     --headers="Authorization: Bearer token"
   ```

## Cleanup

To remove all resources:

```bash
# Delete Cloud Run services
gcloud run services delete multi-agent-orchestrator multi-agent-task multi-agent-calendar \
  multi-agent-notes multi-agent-critic multi-agent-auditor multi-agent-event-monitor \
  --region=us-central1

# Delete container images
gcloud container images delete gcr.io/PROJECT_ID/multi-agent-orchestrator \
  gcr.io/PROJECT_ID/multi-agent-task \
  --quiet

# Delete Firestore database
gcloud firestore databases delete default

# Delete Pub/Sub topics
gcloud pubsub topics delete prod-events prod-audit prod-errors
```

## Support and Troubleshooting

For detailed information, see:
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Firestore Documentation](https://cloud.google.com/firestore/docs)
- [Pub/Sub Documentation](https://cloud.google.com/pubsub/docs)

---

**Last Updated**: 2024
**Version**: 1.0
