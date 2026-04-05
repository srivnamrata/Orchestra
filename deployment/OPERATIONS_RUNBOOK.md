# GCP Operations Runbook

## 🚨 Emergency Procedures

### Complete Service Outage (Cloud Run)

**Symptoms:** Service returns 503, all requests timing out

**Diagnosis:**
```bash
# Check service status
gcloud run services describe productivity-assistant --region us-central1

# Check recent revisions
gcloud run revisions list --service productivity-assistant --region us-central1

# Check Cloud Run logs
gcloud run logs read productivity-assistant --limit=50

# Check service health
gcloud compute health-checks list
```

**Resolution (Step 1 - Quick Rollback):**
```bash
# List recent revisions
gcloud run revisions list --service productivity-assistant \
    --region us-central1 --format="table(name,created)"

# Switch to previous working revision (if available)
gcloud run services update-traffic productivity-assistant \
    --to-revisions PREVIOUS-REVISION-NAME=100 \
    --region us-central1
```

**Resolution (Step 2 - Restart Service):**
```bash
# Delete current service (keeps configuration)
gcloud run services delete productivity-assistant --region us-central1

# Re-deploy from Terraform
cd deployment/terraform
terraform apply -target=google_cloud_run_service.main -var-file="prod.tfvars"
```

**Resolution (Step 3 - Full Redeploy):**
```bash
# If rollback and restart fail, rebuild and redeploy
docker build -t us-central1-docker.pkg.dev/${PROJECT_ID}/productivity-assistant/productivity-assistant:latest .
docker push us-central1-docker.pkg.dev/${PROJECT_ID}/productivity-assistant/productivity-assistant:latest

# Update Cloud Run to new image
gcloud run deploy productivity-assistant \
    --image us-central1-docker.pkg.dev/${PROJECT_ID}/productivity-assistant/productivity-assistant:latest \
    --region us-central1 \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300s
```

**Escalation:** If steps 1-3 fail, contact GCP support (provide ticket number)

---

### High Error Rate (>5% errors)

**Symptoms:** 
- Error rate spike in Cloud Monitoring
- Alert triggered: "Cloud Run Error Rate High"
- Application logs show errors

**Initial Diagnosis:**
```bash
# Check recent errors
gcloud logging read "resource.type=cloud_run_revision AND severity=ERROR" \
    --limit=20 --format=json | jq '.[] | {timestamp:.timestamp, message:.textPayload}'

# Check specific error patterns
gcloud logging read "resource.type=cloud_run_revision AND textPayload:\"LLM timeout\"" \
    --limit=10

# Monitor in real-time
gcloud logging read "resource.type=cloud_run_revision" --follow --limit=5

# Check service metrics
gcloud monitoring time-series list \
    --filter='metric.type="run.googleapis.com/request_count" AND resource.label.service_name="productivity-assistant"' \
    --limit=1 --format=json
```

**Common Issues & Fixes:**

#### LLM Timeout
```bash
# Check if Vertex AI API is responding
gcloud ai models list --location us-central1 2>&1

# Increase timeout
gcloud run services update productivity-assistant \
    --timeout=600s \
    --region us-central1

# Check LLM quotas
gcloud quotas list --service=aiplatform.googleapis.com

# Reduce concurrent LLM calls in config.py
# Set: MAX_CONCURRENT_LLM_CALLS = 5 (reduced from 10)
```

#### Pub/Sub Subscription Lag
```bash
# Check subscription lag
gcloud pubsub subscriptions describe workflow-progress-sub \
    --format="value(oldestRetainedAckedMessageAgeSeconds)"

# Increase subscription processing power
# Option 1: Increase instance count
gcloud run services update productivity-assistant \
    --min-instances=2 \
    --region us-central1

# Option 2: Increase Cloud Run CPU
gcloud run services update productivity-assistant \
    --cpu=4 \
    --region us-central1
```

#### Firestore Quota Exceeded
```bash
# Check Firestore metrics
gcloud monitoring time-series list \
    --filter='metric.type="firestore.googleapis.com/document/read_operations"'

# Check current quotas
gcloud firestore admin databases get default

# Options:
# 1. Increase Firestore capacity in Cloud Monitoring
# 2. Implement caching to reduce read operations
# 3. Batch write operations
# 4. Enable Firestore dedicated capacity
```

---

### Memory Limit Exceeded (OOM)

**Symptoms:** 
- Requests fail with 500 errors
- "Memory limit exceeded" in logs
- Service crashes and restarts frequently

**Diagnosis:**
```bash
# Check memory usage
gcloud monitoring time-series list \
    --filter='metric.type="run.googleapis.com/container_memory_utilization"' \
    --limit=1

# Check revision memory allocation
gcloud run services describe productivity-assistant --format='value(spec.template.spec.containers[0].resources.limits.memory)'

# Check for memory leaks in logs
gcloud logging read "resource.type=cloud_run_revision AND textPayload:\"MemoryError\"" \
    --limit=10
```

**Resolution:**
```bash
# Increase memory allocation
gcloud run services update productivity-assistant \
    --memory=4Gi \
    --region us-central1

# Alternatively, update CPU (Cloud Run allocates memory proportionally)
gcloud run services update productivity-assistant \
    --cpu=4 \
    --region us-central1

# Check if memory usage normalizes
gcloud monitoring time-series list \
    --filter='metric.type="run.googleapis.com/container_memory_utilization"' \
    --start-time="-30m"
```

---

### Pub/Sub Message Processing Failure

**Symptoms:**
- Messages stuck in subscription
- Dead-letter topic filling up
- Workflow progress not updating

**Diagnosis:**
```bash
# Check subscription details
gcloud pubsub subscriptions describe workflow-progress-sub

# Check for dead-letter messages
gcloud pubsub subscriptions pull workflow-progress-dlq \
    --auto-ack --limit=5

# Monitor subscription lag
watch -n 5 'gcloud pubsub subscriptions describe workflow-progress-sub \
    --format="table(name, numUnackedMessages)"'

# Check Cloud Run logs for Pub/Sub errors
gcloud logging read "textPayload:\"pubsub\" AND severity=ERROR" --limit=10
```

**Resolution:**
```bash
# Purge dead-letter queue
gcloud pubsub subscriptions seek workflow-progress-dlq --time=2030-01-01T00:00:00Z

# Reprocess messages
gcloud pubsub subscriptions seek workflow-progress-sub --time=2024-01-01T00:00:00Z

# Check message format
gcloud pubsub topics publish workflow-progress \
    --message='{"test": "message"}' \
    --attributes=timestamp=$(date +%s)

# Monitor reprocessing
gcloud logging read "resource.type=cloud_run_revision" --follow --limit=10
```

---

### Database Connection Issues

**Symptoms:**
- "Connection timeout" in logs
- Firestore operations failing
- Request latency spiking

**Diagnosis:**
```bash
# Check Firestore database status
gcloud firestore databases describe

# Check if database is responding
gcloud firestore collections list

# Check network connectivity
gcloud compute networks list
gcloud compute firewall-rules list

# Check Cloud Run service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:*@iam.gserviceaccount.com" \
    --format="table(bindings.role)"
```

---

## 🚨 Dead-Letter Queue (DLQ) Handling

### Messages Automatic Going to DLQ

**Symptoms:**
- Alert: "Messages in Dead Letter Queue"
- DLQ subscription has undelivered messages
- Same messages failing after 5 retry attempts

**Diagnosis:**
```bash
# Check DLQ message count
gcloud pubsub subscriptions describe productivity-assistant-workflow-progress-dlq-sub \
    --format="value(state, numUnackedMessages)"

# View messages in DLQ
gcloud pubsub subscriptions pull productivity-assistant-workflow-progress-dlq-sub \
    --auto-ack=false \
    --limit=3 \
    --format="table(ackId, message.data, message.publishTime)"

# Check all DLQs status
for dlq in workflow-progress-dlq-sub workflow-replan-dlq-sub agent-health-dlq-sub system-events-dlq-sub; do
    echo "=== $dlq ==="
    gcloud pubsub subscriptions describe $dlq \
        --format="value(numUnackedMessages)"
done

# Review error logs from failure time period
gcloud logging read \
    "resource.type=cloud_run_revision AND severity=ERROR AND timestamp >= '2024-01-15T10:00:00Z'" \
    --limit=20 --format="table(timestamp, textPayload)"
```

**Common Causes by Topic:**

1. **workflow-progress-dlq** (workflow status updates failing)
   - Timeout processing workflow state
   - Firestore write timeout
   - LLM latency causing ACK timeout

2. **workflow-replan-dlq** (replan requests failing)
   - Critic agent unavailable
   - LLM model returning errors
   - Firestore transaction conflicts

3. **agent-health-dlq** (health check messages failing)
   - Agent subprocess crashed
   - Health check endpoint timeout
   - Network connectivity issue

4. **system-events-dlq** (system events failing)
   - Logging service overload
   - Invalid event schema
   - Monitoring service unavailable

**Resolution Steps:**

```bash
# Step 1: Diagnose the underlying issue
# Check main topic subscriptions for errors
gcloud logging read \
    "textPayload:~'workflow-progress.*error'" \
    --limit=10 --format="table(timestamp, severity, textPayload)"

# Step 2: Fix the root cause (varies by issue)
# Examples:
# - If LLM timeout: increase LLM_TIMEOUT_SECONDS in config
# - If Firestore timeout: check database load
# - If Cloud Run memory: increase --memory allocation

# Step 3: Re-deploy if configuration changed
cd deployment/terraform
terraform apply -var-file="prod.tfvars"

# Step 4a: Wait for processing to stabilize
sleep 60

# Step 4b: Reprocess DLQ messages
gcloud pubsub subscriptions pull production-assistant-workflow-progress-dlq-sub \
    --auto-ack=false \
    --limit=100 \
    --format="json" | jq -r '.[] | [.ackId, .message.data] | @csv' > dlq_messages.csv

# Step 4c: Republish to main topic
while IFS=',' read ack_id data; do
    ack_id=$(echo "$ack_id" | tr -d '"')
    data=$(echo "$data" | tr -d '"')
    echo "$data" | base64 -d | \
    gcloud pubsub topics publish productivity-assistant-workflow-progress \
        --message="$(cat)" \
        --attribute="dlq_reprocessed=true" \
        --attribute="original_ack_id=$ack_id"
    
    # Acknowledge to remove from DLQ
    gcloud pubsub subscriptions ack \
        productivity-assistant-workflow-progress-dlq-sub \
        --ack-ids="$ack_id"
done < dlq_messages.csv

echo "✅ Reprocessing complete"

# Step 5: Monitor reprocessing
gcloud logging read \
    "resource.type=cloud_run_revision AND jsonPayload.dlq_reprocessed=true" \
    --limit=20 --follow
```

**DLQ Retention:** 7 days for debugging. If messages are older than 7 days or permanently unrecoverable:

```bash
# Delete by acknowledging (removes from queue)
gcloud pubsub subscriptions ack \
    productivity-assistant-workflow-progress-dlq-sub \
    --ack-ids="ACK_ID_FROM_ABOVE"

# Or purge all (seek to future date)
gcloud pubsub subscriptions seek \
    productivity-assistant-workflow-progress-dlq-sub \
    --time=2030-01-01T00:00:00Z
```

**Automated DLQ Reprocessing (Advanced):**

```python
# Add this endpoint to FastAPI for automated reprocessing
from fastapi import APIRouter
from backend.services.gcp_services import GCPServices

router = APIRouter()

@router.post("/admin/reprocess-dlq/{dlq_name}")
async def reprocess_dlq(dlq_name: str, limit: int = 10):
    """Reprocess messages from specified DLQ"""
    gcp = GCPServices.get_instance()
    
    dlq_topic_map = {
        "workflow_progress": "productivity-assistant-workflow-progress",
        "workflow_replan": "productivity-assistant-workflow-replan",
        "agent_health": "productivity-assistant-agent-health",
        "system_events": "productivity-assistant-system-events",
    }
    
    main_topic = dlq_topic_map.get(dlq_name)
    if not main_topic:
        return {"error": f"Unknown DLQ: {dlq_name}"}
    
    # Get DLQ messages
    dlq_sub = f"productivity-assistant-{dlq_name}-dlq-sub"
    messages = gcp.get_dlq_messages(dlq_sub, max_messages=limit)
    
    reprocessed = 0
    for msg in messages:
        if gcp.reprocess_dlq_message(dlq_sub, main_topic, msg['data']):
            gcp.acknowledge_dlq_message(dlq_sub, msg['id'])
            reprocessed += 1
    
    return {
        "dlq": dlq_name,
        "messages_found": len(messages),
        "messages_reprocessed": reprocessed,
        "status": "success" if reprocessed == len(messages) else "partial"
    }
```

Then call it:
```bash
curl -X POST https://$CLOUD_RUN_URL/admin/reprocess-dlq/workflow_progress \
    -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
    -H "Content-Type: application/json"
```

---

### DLQ Monitoring Dashboard Items

**Check these metrics daily:**

```bash
# 1. Total undelivered messages across all DLQs (should be < 10)
gcloud monitoring read \
    --filter='metric.type="pubsub.googleapis.com/subscription/num_undelivered_messages" AND resource.label.subscription_id=~".*-dlq-sub"' \
    --format=json | jq '[.[].value] | add'

# 2. Oldest message age (should be < 1 hour)
gcloud monitoring read \
    --filter='metric.type="pubsub.googleapis.com/subscription/oldest_unacked_message_age" AND resource.label.subscription_id=~".*-dlq-sub"' \
    --format=json | jq 'max_by(.value) | .value'

# 3. Messages moving to DLQ (trends every hour)
gcloud logging read \
    "resource.type=pubsub_topic AND jsonPayload.moved_to_dlq=true" \
    --limit=100 | wc -l
```

---

## Database Connection Issues

**Symptoms:**
- "Connection timeout" in logs
- Firestore operations failing
- Request latency spiking

**Diagnosis:**
```bash
# Check Firestore database status
gcloud firestore databases describe

# Check if database is responding
gcloud firestore collections list

# Check network connectivity
gcloud compute networks list
gcloud compute firewall-rules list

# Check Cloud Run service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:*@iam.gserviceaccount.com" \
    --format="table(bindings.role)"
```

**Resolution:**
```bash
# Verify Firestore permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:CLOUD_RUN_SA_EMAIL" \
    --role="roles/datastore.user"

# Check Cloud Run service account
gcloud run services describe productivity-assistant \
    --format='value(spec.template.spec.serviceAccountName)'

# Test Firestore connectivity from Cloud Run
# Add test endpoint to FastAPI and call:
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
    $CLOUD_RUN_URL/admin/firestore-test

# If still failing, restart Cloud Run service
gcloud run services update productivity-assistant \
    --no-traffic \
    --region us-central1
gcloud run services update-traffic productivity-assistant \
    --to-latest \
    --region us-central1
```

---

## 📊 Performance Issues

### Slow Response Times (P99 > 5s)

**Diagnosis:**
```bash
# Check Cloud Trace
gcloud trace list --limit=10 --filter="latency > 5000"

# Check Cloud Run metrics
gcloud monitoring read \
    --filter='metric.type="run.googleapis.com/request_latencies"' \
    --format=json | jq '.[] | {timestamp:.timestamp, value:.value}'

# Analyze database queries
gcloud logging read "textPayload:\"duration\"" --limit=20

# Check LLM latency
gcloud logging read "textPayload:\"LLM response time\"" --limit=20
```

**Common Causes & Fixes:**

#### Cold Start Issues
```bash
# Increase minimum instances
gcloud run services update productivity-assistant \
    --min-instances=2 \
    --region us-central1

# Monitor cold start frequency
gcloud logging read "textPayload:\"Cold start\"" --limit=20
```

#### Database Query Performance
```bash
# Check Firestore indexes
gcloud firestore indexes list

# Create missing composite indexes
gcloud firestore indexes create \
    --collection=workflows \
    --fields='status=Ascending,created_at=Descending'

# Monitor query patterns
gcloud logging read "textPayload:\"Firestore query\"" --limit=20
```

#### LLM Response Latency
```bash
# Check Vertex AI availability
gcloud ai models list --location us-central1

# Reduce context size in config
# Set: LLM_MAX_CONTEXT = 2000 (reduced from 4000)

# Use faster model for certain tasks
# Set: LLM_SPEED_OPTIMIZED_MODEL = "gemini-1.5-flash"
```

---

### High CPU/Memory Usage

**Diagnosis:**
```bash
# Check CPU usage over time
gcloud monitoring read \
    --filter='metric.type="run.googleapis.com/container_cpu_utilization"' \
    --format=json | jq '.[] | {timestamp:.timestamp, value:.value}'

# Check memory usage
gcloud monitoring read \
    --filter='metric.type="run.googleapis.com/container_memory_utilization"' \
    --format=json

# List running instances
gcloud run revisions list --service productivity-assistant --region us-central1

# Check Cloud Trace for hot paths
gcloud trace describe TRACE_ID --format=json
```

**Optimization Strategies:**

#### CPU Optimization
```bash
# Increase CPU allocation
gcloud run services update productivity-assistant \
    --cpu=4 \
    --region us-central1

# Or reduce concurrency
# Set in config.py: MAX_CONCURRENT_WORKFLOWS = 10 (reduced from 50)

# Enable Cloud Run autoscaling based on CPU
# (Already configured in Terraform with annotation:autoscaling.knative.dev/target-cpu-utilization-percentage=70)
```

#### Memory Optimization
```bash
# Increase memory allocation
gcloud run services update productivity-assistant \
    --memory=4Gi \
    --region us-central1

# Identify memory leaks
gcloud logging read "textPayload:\"memory\"" --limit=20

# Implement connection pooling
# Check backend/services/gcp_services.py for pool configuration
```

---

## 🔄 Scaling & Capacity

### Scale Out (Increase Instances)

**Auto-Scaling Configuration:**
```bash
# View current auto-scaling settings
gcloud run services describe productivity-assistant \
    --format="value(spec.template.metadata.annotations)" | grep autoscaling

# Current settings (from Terraform):
# - target-cpu-utilization: 70%
# - min-instances: 1
# - max-instances: 100
# - target-concurrency: 80 requests per instance

# Manual scaling (if needed)
gcloud run services update productivity-assistant \
    --min-instances=5 \
    --max-instances=200 \
    --region us-central1
```

**Monitor Scaling:**
```bash
# Watch instance count live
watch -n 2 'gcloud run services describe productivity-assistant \
    --region us-central1 \
    --format="value(status.traffic[0].percent)" && \
    gcloud monitoring read \
    --filter="metric.type=run.googleapis.com/container_billable_time" \
    --format="value(value)"'

# Check scaling history
gcloud logging read "resource.type=cloud_run_revision" --limit=100 | \
    grep -i "scale\|instance"
```

### Scale Down (Reduce Costs)

**Identify Under-Utilization:**
```bash
# Check average CPU usage
gcloud monitoring read \
    --filter='metric.type="run.googleapis.com/container_cpu_utilization"' \
    --format=json | jq '.[].value | add / length'

# Check average memory usage
gcloud monitoring read \
    --filter='metric.type="run.googleapis.com/container_memory_utilization"' \
    --format=json | jq '.[].value | add / length'

# View cost breakdown
gcloud billing budgets list
```

**Optimize Resources:**
```bash
# Reduce memory if under 50% utilization
gcloud run services update productivity-assistant \
    --memory=1Gi \
    --region us-central1

# Reduce minimum instances
gcloud run services update productivity-assistant \
    --min-instances=0 \
    --region us-central1

# Use cheaper LLM model
# Update config: LLM_MODEL = "gemini-1.5-flash" (from gemini-1.5-pro)
```

---

## 🔍 Cost Optimization

### Analyze Current Costs

```bash
# Get current month breakdown
gcloud billing budget-accounts describe \
    --format="table(name, budgetAmount, alertThresholdRules)"

# Export costs to BigQuery for analysis
bq query --use_legacy_sql=false '
  SELECT 
    service.description,
    SUM(cost) as total_cost,
    SUM(usage.amount) as total_usage,
    service.description
  FROM `PROJECT_ID.billing_dataset.gcp_billing_export_v1`
  WHERE DATE(usage_start_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  GROUP BY service.description
  ORDER BY total_cost DESC
'
```

### Cost Reduction Actions

**Quick Wins:**
1. **Use gemini-1.5-flash instead of pro** (-70% LLM cost)
   ```bash
   # Update deployment/terraform/prod.tfvars
   # change: llm_model = "gemini-1.5-pro" to "gemini-1.5-flash"
   terraform apply -var-file="prod.tfvars"
   ```

2. **Reduce Cloud Run minimum instances** (if traffic pattern allows)
   ```bash
   gcloud run services update productivity-assistant \
       --min-instances=0 \
       --region us-central1
   ```

3. **Implement caching** (-30-50% API calls)
   - Add Redis-like caching for Firestore queries
   - Cache LLM responses for repeated queries

4. **Right-size memory/CPU** (save 20-40% if over-allocated)
   ```bash
   # Check current utilization first
   gcloud monitoring read \
       --filter='metric.type="run.googleapis.com/container_memory_utilization"'
   ```

---

## 📝 Logging & Debugging

### Enable Debug Logging

```bash
# Update config
gcloud run services update productivity-assistant \
    --set-env-vars="LOG_LEVEL=DEBUG" \
    --region us-central1

# View debug logs
gcloud logging read "resource.type=cloud_run_revision AND severity=DEBUG" \
    --limit=50 --format=json

# Filter by component
gcloud logging read "resource.type=cloud_run_revision AND jsonPayload.module=pubsub" \
    --limit=20
```

### Common Log Searches

```bash
# All errors from last hour
gcloud logging read "resource.type=cloud_run_revision AND severity=ERROR" \
    --limit=100 --format="table(timestamp, textPayload)"

# Specific error type
gcloud logging read "resource.type=cloud_run_revision AND textPayload:\"timeout\"" \
    --limit=20

# By service
gcloud logging read "resource.labels.service_name=productivity-assistant" \
    --limit=50

# Real-time tail
gcloud logging read "resource.type=cloud_run_revision" \
    --follow --limit=5 --format=json

# With timestamps
gcloud logging read "resource.type=cloud_run_revision" \
    --limit=20 --format="table(timestamp, severity, textPayload)"

# Convert to readable JSON
gcloud logging read "resource.type=cloud_run_revision" \
    --limit=5 --format=json | jq '.'
```

---

## 🔐 Security Checks

### Security Audit

```bash
# Check IAM policies
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:*@iam.gserviceaccount.com"

# Check Cloud Run service account
gcloud iam service-accounts list

# Check Firestore security rules
gcloud firestore security-rules describe

# Check VPC service controls
gcloud access-context-manager policies list

# Check organization policies
gcloud resource-manager org-policies list --project=$PROJECT_ID
```

### Secrets Management

```bash
# Check if secrets are properly managed
gcloud secrets list

# View secret (be careful!)
gcloud secrets versions access latest --secret=GOOGLE_CLOUD_API_KEY

# Rotate secrets
gcloud secrets versions add GOOGLE_CLOUD_API_KEY --data-file=new_key.txt

# Audit secret access
gcloud logging read "protoPayload.methodName:secrets.get" --limit=20
```

---

## 📞 Escalation & Support

### GCP Support Ticket

```bash
# Open support case through Cloud Console
# https://console.cloud.google.com/support/cases/new

# Or from CLI
gcloud support tickets create \
    --description="Service outage - Cloud Run errors" \
    --severity=P1 \
    --contact="ON_CALL_EMAIL@company.com"
```

### Internal Escalation
1. Page on-call engineer (see PRODUCTION_CHECKLIST.md)
2. Open incident in Incident Management system
3. Update status page
4. Notify stakeholders

---

## 📊 Dashboard Links

**Cloud Console:**
- Cloud Run: https://console.cloud.google.com/run
- Monitoring: https://console.cloud.google.com/monitoring
- Logging: https://console.cloud.google.com/logs
- Firestore: https://console.cloud.google.com/firestore

**Custom Dashboards:**
```bash
# List custom dashboards
gcloud monitoring dashboards list

# View monitoring dashboard
# https://console.cloud.google.com/monitoring/dashboards/custom/[DASHBOARD_ID]
```

---

**Document Version:** 1.0
**Last Updated:** April 4, 2026
**Next Review:** 30 days
