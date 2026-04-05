# Dead-Letter Queue (DLQ) Handling Guide

## 📋 Overview

Dead-Letter Queues (DLQs) in Cloud Pub/Sub automatically capture messages that fail to process after multiple delivery attempts. This guide explains how to monitor, troubleshoot, and reprocess DLQ messages.

---

## 🏗️ DLQ Architecture

### What We're Capturing

```
Main Topics (4)                    DLQ Topics (4)
├─ workflow-progress          ├─ workflow-progress-dlq
├─ workflow-replan       ────→├─ workflow-replan-dlq
├─ agent-health                ├─ agent-health-dlq
└─ system-events              └─ system-events-dlq

Message Flow with Failures:
1. Message arrives in main topic
2. Cloud Run attempts to process (ACK deadline: 60 seconds)
3. If processing fails:
   - Retry with backoff (10s → 30s → 100s → 300s → 600s)
   - After 5 failed delivery attempts
   - Message automatically moves to DLQ (retained 7 days)
4. Operator reviews DLQ messages
5. Reprocess or delete after diagnosis
```

### Configuration

**Retry Policy (In Terraform):**
```hcl
retry_policy {
  minimum_backoff = "10s"   # Start with 10 second delay
  maximum_backoff = "600s"  # Cap at 10 minutes
}
```

**Dead-Letter Policy:**
```hcl
dead_letter_policy {
  dead_letter_topic = "dlq-topic-name"
  max_delivery_attempts = 5  # Move to DLQ after 5 failures
}
```

**Retention:**
- **Main topics:** 24 hours
- **DLQ topics:** 7 days (for debugging)

---

## 🔍 Monitoring DLQ Messages

### View DLQ Status in Cloud Console

```bash
# Open Cloud Console
Start-Process "https://console.cloud.google.com/pubsub/subscriptions?project=$PROJECT_ID"

# Look for subscriptions ending in "-dlq-sub"
# Click each subscription to see:
# - Undelivered message count
# - Oldest unacknowledged message age
# - Subscription metrics
```

### Check DLQ Messages via Cloud Logging

```bash
# Find messages sent to DLQ
gcloud logging read \
    "resource.type=pubsub_subscription AND \
     jsonPayload.subscription_id=~'.*-dlq-sub'" \
    --limit=20 --format=json | jq '.'

# Search for specific failure patterns
gcloud logging read \
    "textPayload:\"dead-letter\" OR textPayload:\"DLQ\"" \
    --limit=20

# Monitor DLQ insertions in real-time
gcloud logging read \
    "resource.type=pubsub_topic AND jsonPayload.message_count > 0" \
    --follow --limit=5
```

### Use Python to Check DLQ Metrics

```python
from backend.services.gcp_services import GCPServices
from backend.services.config import Config

config = Config()
gcp = GCPServices.get_instance(config.GCP_PROJECT_ID)

# Check metrics for each DLQ subscription
dlq_subs = [
    "productivity-assistant-workflow-progress-dlq-sub",
    "productivity-assistant-workflow-replan-dlq-sub",
]

for sub_name in dlq_subs:
    metrics = gcp.get_dlq_metrics(sub_name)
    print(f"\n{sub_name}:")
    print(f"  Undelivered Messages: {metrics['num_undelivered_messages']}")
    print(f"  Message Retention: {metrics['message_retention_duration']}")
```

### Monitoring Alert

An alert is automatically triggered when:
- Any DLQ has undelivered messages > 0
- Alert fires immediately when messages arrive
- Monitored in Cloud Monitoring

**View alert status:**
```bash
# List alert policies
gcloud monitoring alert-policies list \
    --filter="displayName~'Dead.*Letter.*Queue'"

# View alert notifications
gcloud logging read \
    "resource.type=monitoring_alerting_service AND \
     jsonPayload.policy_name=~'.*DLQ.*'" \
    --limit=10
```

---

## 🔧 Troubleshooting DLQ Messages

### Step 1: Pull DLQ Messages for Inspection

```bash
# Retrieve messages from DLQ
gcloud pubsub subscriptions pull productivity-assistant-workflow-progress-dlq-sub \
    --auto-ack=false \
    --limit=5 \
    --format=json

# Output includes:
# - ACK_ID (for reprocessing/deletion)
# - DATA (message content, base64)
# - ATTRIBUTES (metadata)
```

**Using Python:**
```python
dlq_messages = gcp.get_dlq_messages("productivity-assistant-workflow-progress-dlq-sub", max_messages=10)

for msg in dlq_messages:
    print(f"Message ID: {msg['id']}")
    print(f"Data: {msg['data']}")
    print(f"Attributes: {msg['attributes']}")
    print(f"Published: {msg['publish_time']}\n")
```

### Step 2: Diagnose Failure Reason

**Common Failure Reasons:**

1. **Processing Timeout (60s ACK deadline exceeded)**
   - Application took > 60 seconds to process message
   - Check logs: `"deadline exceeded"` or `"timeout"`
   - Solution: Increase ACK deadline or optimize processing

2. **Application Crash/Restart**
   - Cloud Run instance crashed mid-processing
   - Check logs: Error stacktraces in Cloud Logging
   - Solution: Fix the crash, then reprocess

3. **LLM Service Unavailable**
   - Vertex AI quota exceeded or service down
   - Check logs: `"vertexai"` or `"quota"`
   - Solution: Wait for service recovery or increase quota

4. **Database Lock/Conflict**
   - Firestore write conflict or timeout
   - Check logs: `"transaction"` or `"firestore"`
   - Solution: Reprocess after lock is released

5. **Message Format Invalid**
   - Message data corrupted or wrong format
   - Check logs: `"json"` or `"parse"` errors
   - Solution: Manual intervention or discard

### Step 3: Check Logs for Root Cause

```bash
# Search for all errors from past hour
gcloud logging read \
    "resource.type=cloud_run_revision AND severity=ERROR" \
    --limit=50 --format="table(timestamp, textPayload)"

# Search for specific topic errors
gcloud logging read \
    "resource.type=cloud_run_revision AND \
     (textPayload:\"workflow-progress\" OR textPayload:\"replan\")" \
    --limit=20

# Search with timestamp of DLQ message failure
gcloud logging read \
    "resource.type=cloud_run_revision AND \
     timestamp >= '2024-01-15T10:00:00Z' AND \
     timestamp <= '2024-01-15T10:05:00Z'" \
    --limit=10
```

### Step 4: Determine Next Action

**Decision Tree:**

```
DLQ Message Arrived → Inspect Message → Root Cause Found?
                                            ↓
                    ┌───────────────────────┼───────────────────────┐
                    ↓                       ↓                       ↓
            Permanent Error       Temporary Error           Unknown/Error
            (invalid message,     (timeout, quota,         Code issue
             corrupted data)      transient failure)       
                    ↓                       ↓                       ↓
              ┌─DELETE─┐          ┌──REPROCESS──┐        ┌──INVESTIGATE──┐
              └────────┘          └─────────────┘        └────────────────┘
```

---

## 🔄 Reprocessing DLQ Messages

### Option 1: Reprocess via Python

```python
from backend.services.gcp_services import GCPServices
from backend.services.config import Config

config = Config()
gcp = GCPServices.get_instance(config.GCP_PROJECT_ID)

# 1. Get messages from DLQ
dlq_messages = gcp.get_dlq_messages(
    "productivity-assistant-workflow-progress-dlq-sub",
    max_messages=5
)

# 2. Reprocess each message
for msg in dlq_messages:
    success = gcp.reprocess_dlq_message(
        dlq_subscription_name="productivity-assistant-workflow-progress-dlq-sub",
        topic_name="productivity-assistant-workflow-progress",
        message_data=msg['data']
    )
    
    if success:
        # 3. Acknowledge and remove from DLQ
        gcp.acknowledge_dlq_message(
            "productivity-assistant-workflow-progress-dlq-sub",
            msg['id']
        )
        print(f"✅ Reprocessed message: {msg['id']}")
    else:
        print(f"❌ Failed to reprocess: {msg['id']}")
```

### Option 2: Reprocess via gcloud Commands

```bash
# 1. Pull messages without auto-acknowledging
gcloud pubsub subscriptions pull productivity-assistant-workflow-progress-dlq-sub \
    --auto-ack=false \
    --limit=5 \
    --format="table(ack_id, data)"

# 2. Decode and republish message
ACK_ID="<ack_id_from_above>"
MESSAGE_DATA="<base64_decoded_data>"

gcloud pubsub topics publish productivity-assistant-workflow-progress \
    --message="$MESSAGE_DATA" \
    --attribute=dlq_reprocessed=true

# 3. Acknowledge to remove from DLQ
gcloud pubsub subscriptions ack \
    productivity-assistant-workflow-progress-dlq-sub \
    --ack-ids="$ACK_ID"
```

### Option 3: Batch Reprocess All DLQ Messages

```bash
# Script to reprocess all messages from a DLQ
#!/bin/bash

DLQ_SUB="productivity-assistant-workflow-progress-dlq-sub"
MAIN_TOPIC="productivity-assistant-workflow-progress"
PROJECT_ID=$GCP_PROJECT_ID

# Pull all messages
MESSAGES=$(gcloud pubsub subscriptions pull $DLQ_SUB \
    --auto-ack=false \
    --limit=100 \
    --format="json")

# Reprocess each
echo "$MESSAGES" | jq -r '.[] | [.ackId, .message.data] | @csv' | \
while IFS=',' read -r ack_id data; do
    # Republish to main topic
    echo "$data" | base64 -d | \
    gcloud pubsub topics publish $MAIN_TOPIC \
        --message="$(cat)" \
        --attribute=dlq_reprocessed=true
    
    # Acknowledge
    gcloud pubsub subscriptions ack $DLQ_SUB --ack-ids="${ack_id%\"}"
done

echo "Reprocessing complete"
```

---

## 🗑️ Deleting DLQ Messages

### When to Delete Messages

- **Permanent corruption:** Message is malformed, cannot be fixed
- **Duplicate processing:** Message already processed successfully
- **Outdated workflows:** Message for a deleted/cancelled workflow
- **System migration:** Switching to different message format

### Delete Single Message

```bash
# Method 1: Using gcloud
gcloud pubsub subscriptions ack \
    productivity-assistant-workflow-progress-dlq-sub \
    --ack-ids="AcqVD_..."

# Method 2: Using Python
gcp.acknowledge_dlq_message(
    "productivity-assistant-workflow-progress-dlq-sub",
    "AcqVD_..."
)
```

### Delete All Messages from DLQ

```bash
# Seek to future time (deletes all existing messages)
gcloud pubsub subscriptions seek \
    productivity-assistant-workflow-progress-dlq-sub \
    --time=2030-01-01T00:00:00Z

# Verify deletion
gcloud pubsub subscriptions describe \
    productivity-assistant-workflow-progress-dlq-sub
```

### Empty All DLQs at Once

```bash
#!/bin/bash

DLQ_SUBS=(
    "productivity-assistant-workflow-progress-dlq-sub"
    "productivity-assistant-workflow-replan-dlq-sub"
    "productivity-assistant-agent-health-dlq-sub"
    "productivity-assistant-system-events-dlq-sub"
)

for dlq_sub in "${DLQ_SUBS[@]}"; do
    echo "Clearing $dlq_sub..."
    gcloud pubsub subscriptions seek $dlq_sub --time=2030-01-01T00:00:00Z
done

echo "All DLQs cleared"
```

---

## 📊 DLQ Monitoring Dashboard

### Create Custom Monitoring Dashboard

```bash
# View existing dashboards
gcloud monitoring dashboards list

# Create dashboard for DLQ (via Cloud Console)
# https://console.cloud.google.com/monitoring/dashboards/create
```

**Metrics to Monitor:**

```json
{
  "displayName": "DLQ Overview",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Messages in DLQ by Topic",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "metric.type=\"pubsub.googleapis.com/subscription/num_undelivered_messages\" AND resource.label.subscription_id=~\".*-dlq-sub\""
                  }
                }
              }
            ]
          }
        }
      },
      {
        "xPos": 6,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Message Age in DLQ",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "metric.type=\"pubsub.googleapis.com/subscription/oldest_unacked_message_age\" AND resource.label.subscription_id=~\".*-dlq-sub\""
                  }
                }
              }
            ]
          }
        }
      }
    ]
  }
}
```

---

## 🚨 Common DLQ Scenarios

### Scenario 1: Spike in DLQ Messages

**Symptoms:**
- DLQ subscription suddenly has hundreds of messages
- Alert triggered: "Messages in Dead Letter Queue"

**Diagnosis:**
```bash
gcloud logging read \
    "resource.type=cloud_run_revision AND severity=ERROR AND \
     timestamp >= '2024-01-15T09:00:00Z'" \
    --limit=50 --format="table(timestamp, textPayload)"
```

**Common Causes:**
1. Service was down (check Cloud Run revisions)
2. LLM quota exceeded (check Vertex AI quota)
3. Firestore transaction conflicts (check logs)
4. Network connectivity issues

**Resolution:**
```bash
# 1. Fix the underlying issue
# 2. Verify problem is resolved
# 3. Reprocess all messages

# Pull all messages
gcloud pubsub subscriptions pull SUBSCRIPTION_NAME \
    --auto-ack=false \
    --limit=1000

# Batch republish to main topic
# See "Batch Reprocess All DLQ Messages" section above
```

### Scenario 2: Permanent Errors in DLQ

**Symptoms:**
- Messages keep reprocessing but never succeed
- Log errors indicate data corruption
- Same failure after 5 retry attempts

**Diagnosis:**
```bash
# Get sample message
gcloud pubsub subscriptions pull SUBSCRIPTION_NAME \
    --auto-ack=false \
    --limit=1 \
    --format=json | jq '.[] | .message.data' | base64 -d

# Inspect message content
# Try to understand why it's invalid
```

**Resolution:**
```bash
# Only if truly unrecoverable:
# 1. Document the error
# 2. Delete the message
# 3. Investigate root cause to prevent future occurrences

gcloud pubsub subscriptions ack SUBSCRIPTION_NAME --ack-ids="ACK_ID"
```

### Scenario 3: DLQ Messages Growing Over Time

**Symptoms:**
- DLQ message count growing daily
- Oldest message age > 7 days
- Indicates systematic failure

**Diagnosis:**
```bash
# Check if same error repeating
gcloud logging read \
    "textPayload:\"specific_error_pattern\"" \
    --limit=50

# Get failure distribution
gcloud logging read \
    "severity=ERROR" \
    --format="table(severity, textPayload)" | sort | uniq -c | sort -rn
```

**Root Causes:**
- Code regression introduced new bug
- External service dependency down
- Configuration changed incorrectly
- Resource quota exhausted

**Resolution:**
1. Identify and fix root cause
2. Deploy fix to Cloud Run
3. Reprocess DLQ messages
4. Monitor for sustained reduction

---

## 📝 DLQ Operations Checklist

### Daily
- [ ] Monitor DLQ message count (should be near zero)
- [ ] Check alert notifications
- [ ] Review error logs for patterns

### Weekly
- [ ] Analyze DLQ metrics over past 7 days
- [ ] Document any recurring failures
- [ ] Verify retention (7 days) is sufficient

### Monthly
- [ ] Review DLQ handling procedures
- [ ] Test reprocessing workflow
- [ ] Update runbooks with learnings
- [ ] Analyze cost impact of DLQ traffic

### Quarterly
- [ ] Adjust max_delivery_attempts if needed (currently 5)
- [ ] Review retry backoff strategy
- [ ] Evaluate retention period (currently 7 days)
- [ ] Plan improvements to prevent failures

---

## 🔗 Related Documentation

- [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) - Emergency procedures
- [GCP_QUICK_REFERENCE.md](GCP_QUICK_REFERENCE.md) - Commands reference
- [Cloud Pub/Sub DLQ Docs](https://cloud.google.com/pubsub/docs/dead-letter-topics)

---

**Document Version:** 1.0
**Last Updated:** April 4, 2026
**Next Review:** 30 days
