# GCP Deployment Quick Reference

## 🚀 Quick Start (5 minutes)

### 1. Set Environment Variables
```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
export ENVIRONMENT="staging"  # or prod
```

### 2. Authenticate with GCP
```bash
gcloud auth login
gcloud config set project $PROJECT_ID
```

### 3. Enable APIs
```bash
gcloud services enable run.googleapis.com \
    pubsub.googleapis.com firestore.googleapis.com \
    aiplatform.googleapis.com artifactregistry.googleapis.com
```

### 4. Build & Push Image
```bash
# Create Artifact Registry repo
gcloud artifacts repositories create productivity-assistant \
    --repository-format=docker --location=$REGION

# Configure Docker
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Build and push
docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/productivity-assistant/productivity-assistant:latest .
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/productivity-assistant/productivity-assistant:latest
```

### 5. Deploy with Terraform
```bash
cd deployment/terraform
terraform init
terraform plan -var-file="${ENVIRONMENT}.tfvars"
terraform apply -var-file="${ENVIRONMENT}.tfvars"
```

---

## 📋 Command Reference

### Project Management
```bash
# List projects
gcloud projects list

# Set active project
gcloud config set project PROJECT_ID

# Get project info
gcloud projects describe PROJECT_ID
```

### Service Management
```bash
# List enabled services
gcloud services list --enabled

# Enable service
gcloud services enable SERVICE_NAME

# Disable service
gcloud services disable SERVICE_NAME
```

### Cloud Run
```bash
# List deployments
gcloud run services list

# Get service details
gcloud run services describe SERVICE_NAME --region=$REGION

# View logs
gcloud run logs read SERVICE_NAME --limit=50

# Update service
gcloud run services update SERVICE_NAME \
    --image=IMAGE_URL \
    --region=$REGION

# Delete service
gcloud run services delete SERVICE_NAME
```

### Pub/Sub
```bash
# List topics
gcloud pubsub topics list

# Create topic
gcloud pubsub topics create TOPIC_NAME

# Publish message
gcloud pubsub topics publish TOPIC_NAME --message="message"

# List subscriptions
gcloud pubsub subscriptions list

# Read messages
gcloud pubsub subscriptions pull SUBSCRIPTION_NAME
```

### Firestore
```bash
# List collections
gcloud firestore collections list

# Get document
gcloud firestore documents get COLLECTION/DOCUMENT

# Delete collection
gcloud firestore collections delete COLLECTION

# Export data
gcloud firestore export gs://BUCKET/export-path

# Import data
gcloud firestore import gs://BUCKET/import-path
```

### Artifact Registry
```bash
# List repositories
gcloud artifacts repositories list --location=$REGION

# List images
gcloud artifacts docker images list ${REGION}-docker.pkg.dev/${PROJECT_ID}/repository

# Delete image
gcloud artifacts docker images delete IMAGE_URL
```

### Cloud Logging
```bash
# Stream logs real-time
gcloud logging read "resource.type=cloud_run_revision" \
    --limit=10 --follow

# Search logs
gcloud logging read "severity=ERROR" --limit=20

# Create log sink
gcloud logging sinks create SINK_NAME DESTINATION_URL
```

### IAM & Service Accounts
```bash
# Create service account
gcloud iam service-accounts create SA_NAME

# Grant role
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:SA_EMAIL" \
    --role="roles/ROLE_NAME"

# List service accounts
gcloud iam service-accounts list

# Delete service account
gcloud iam service-accounts delete SA_EMAIL
```

---

## 🔧 Terraform Commands

### Common Workflows
```bash
# Initialize
terraform init

# Validate
terraform validate

# Format
terraform fmt -recursive

# Plan
terraform plan -var-file="prod.tfvars" -out=tfplan

# Apply
terraform apply tfplan

# Destroy
terraform destroy -var-file="prod.tfvars"

# Get outputs
terraform output -json
terraform output cloud_run_url

# Refresh state
terraform refresh

# State management
terraform state list
terraform state show resource.name
terraform state rm resource.name
terraform state mv old.name new.name
```

---

## 📊 Monitoring URLs

After deployment, access these endpoints:

```bash
SERVICE_URL=$(gcloud run services describe productivity-assistant \
    --platform managed --region $REGION --format='value(status.url)')

# System status
echo "$SERVICE_URL/"

# Health check
echo "$SERVICE_URL/health"

# Swagger documentation
echo "$SERVICE_URL/docs"

# Metrics
echo "$SERVICE_URL/metrics"
```

---

## 🔑 Important Environment Variables

```bash
# Copy these to deployment/terraform/*.tfvars

# GCP Configuration
GCP_PROJECT_ID="your-project-id"
GCP_REGION="us-central1"
VERTEX_AI_LOCATION="us-central1"

# Service Flags
USE_MOCK_LLM=false                # false in production
USE_MOCK_PUBSUB=false             # false in production
USE_FIRESTORE=true

# LLM Configuration
LLM_MODEL="gemini-1.5-pro"        # or gemini-1.5-flash
LLM_TEMPERATURE="0.7"
LLM_MAX_TOKENS="2048"

# Performance
MAX_CONCURRENT_WORKFLOWS="100"
REQUEST_TIMEOUT_SECONDS="30"
LLM_TIMEOUT_SECONDS="60"

# Logging
ENABLE_CLOUD_LOGGING="true"
LOG_LEVEL="INFO"                  # DEBUG|INFO|WARNING|ERROR

# Container
cloud_run_memory="2Gi"
cloud_run_cpu="2"
cloud_run_min_instances="1"
cloud_run_max_instances="100"
```

---

## 🐛 Common Issues & Fixes

### Cloud Run Image not found
```bash
# Verify image exists
gcloud artifacts docker images list ${REGION}-docker.pkg.dev/${PROJECT_ID}/productivity-assistant

# Push image again
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/productivity-assistant/productivity-assistant:latest
```

### Vertex AI Permission Denied
```bash
# Grant permission to service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/aiplatform.user"

# Test access
gcloud ai models list --location=$REGION
```

### Firestore Connection Failed
```bash
# Verify Firestore is enabled
gcloud firestore databases describe

# Enable Firestore if needed
gcloud firestore databases create --location=$REGION --type=FIRESTORE_NATIVE
```

### Pub/Sub Message Not Received
```bash
# Check topic exists
gcloud pubsub topics describe $TOPIC_NAME

# Check subscription exists  
gcloud pubsub subscriptions describe $SUBSCRIPTION_NAME

# Check message expiration
gcloud pubsub topics describe $TOPIC_NAME --format="value(messageRetentionDuration)"
```

### Cloud Run Service Timeout
```bash
# Increase timeout (max 3600s)
gcloud run services update $SERVICE_NAME \
    --timeout=600s \
    --region=$REGION

# Increase memory/CPU
gcloud run services update $SERVICE_NAME \
    --memory=2Gi \
    --cpu=2 \
    --region=$REGION
```

---

## 💰 Cost Estimation

**Monthly cost estimate for typical usage:**

| Service | Usage | Cost |
|---------|-------|------|
| Cloud Run | 1M requests/month | $0.24 |
| Pub/Sub | 100M messages/month | $5.00 |
| Firestore | 10M ops/month | $6.00 |
| Vertex AI | 10B tokens/month | $75.00 |
| Cloud Logging | 10GB logs | $5.00 |
| Total | | ~$91.24 |

**Cost optimization tips:**
1. Use auto-scaling (min: 0, max: 50)
2. Use gemini-1.5-flash instead of pro
3. Implement caching to reduce API calls
4. Set appropriate log retention
5. Use Firestore spending limits

---

## 📖 Documentation References

- [GCP Deployment Guide](GCP_DEPLOYMENT_GUIDE.md) - Comprehensive guide
- [Configuration](backend/services/config.py) - All config options
- [Terraform Variables](deployment/terraform/variables.tf) - All Terraform vars
- [Cloud Run YAML](deployment/cloud-run.yaml) - Cloud Run configuration

---

## 🆘 Help & Support

```bash
# Get help on any gcloud command
gcloud run --help
gcloud pubsub --help
gcloud firestore --help

# Get Terraform help
terraform --help
terraform apply --help

# Check logs for errors
gcloud run logs read productivity-assistant --follow

# View service details
gcloud run services describe productivity-assistant \
    --platform managed --region=$REGION --format=json
```

---

**Last Updated:** April 4, 2026
**Status:** Ready for Production
