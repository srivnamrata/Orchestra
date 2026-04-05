# DLQ Quick Reference Card

## 🎯 Cheat Sheet for Operators

### Check DLQ Status (Do This Daily)

```bash
# Get message count in all DLQs
for topic in workflow-progress workflow-replan agent-health system-events; do
    MSG_COUNT=$(gcloud pubsub subscriptions describe \
        productivity-assistant-${topic}-dlq-sub \
        --format="value(numUnackedMessages)")
    echo "$topic DLQ: $MSG_COUNT messages"
done

# Expected: All should be 0 or very small
# Alert triggers if any > 0
```

### When Alert Fires: 5-Step Emergency Response

```bash
# ===== STEP 1: DIAGNOSE (2 min) =====
# Get error logs from past hour
gcloud logging read \
    "resource.type=cloud_run_revision AND severity=ERROR" \
    --limit=20 --format="table(timestamp, textPayload)"

# ===== STEP 2: IDENTIFY ROOT CAUSE (3-5 min) =====
# Check specific error patterns
gcloud logging read \
    "textPayload:\"timeout\" OR textPayload:\"quota\" OR textPayload:\"LLM\"" \
    --limit=10

# ===== STEP 3: FIX (Varies) =====
# Example fixes:
# A) Timeout issue → increase timeout in config
# B) Quota issue → request quota increase
# C) Crash → deploy fixed version
# D) Transient → wait, might auto-recover

# ===== STEP 4: REPROCESS (1-2 min) =====
# Pull messages from DLQ
gcloud pubsub subscriptions pull \
    productivity-assistant-TOPIC-dlq-sub \
    --auto-ack=false --limit=50 --format=json | \
    jq -r '.[] | [.ackId, .message.data] | @csv' > dlq_msgs.csv

# Republish to main topic
while IFS=',' read ack_id data; do
    echo "$data" | base64 -d | \
    gcloud pubsub topics publish productivity-assistant-TOPIC \
        --message="$(cat)"
    sleep 0.1  # Rate limit
done < dlq_msgs.csv

# ===== STEP 5: VERIFY (1 min) =====
# Acknowledge messages
gcloud pubsub subscriptions ack productivity-assistant-TOPIC-dlq-sub \
    --ack-ids=$(cat dlq_msgs.csv | cut -d',' -f1 | paste -sd, -)

# Check that DLQ is now empty
gcloud pubsub subscriptions describe \
    productivity-assistant-TOPIC-dlq-sub \
    --format="value(numUnackedMessages)"
# Should be: 0
```

---

## 🔗 Topic to DLQ Mapping

| Main Topic | DLQ Topic | DLQ Subscription |
|-----------|-----------|-----------------|
| `workflow-progress` | `workflow-progress-dlq` | `workflow-progress-dlq-sub` |
| `workflow-replan` | `workflow-replan-dlq` | `workflow-replan-dlq-sub` |
| `agent-health` | `agent-health-dlq` | `agent-health-dlq-sub` |
| `system-events` | `system-events-dlq` | `system-events-dlq-sub` |

**Note:** Use full names: `productivity-assistant-{topic}`

---

## 🔍 Diagnostic Commands

### Check if DLQ is Growing (Bad Sign)
```bash
# Run every 5 minutes
watch -n 5 'gcloud pubsub subscriptions describe productivity-assistant-workflow-progress-dlq-sub --format="value(numUnackedMessages)"'

# If growing = systematic failure = investigate urgently
```

### See What's in DLQ
```bash
# Get first message from DLQ
gcloud pubsub subscriptions pull productivity-assistant-TOPIC-dlq-sub \
    --auto-ack=false --limit=1 --format="table(ackId, message.data, message.publishTime)"

# Decode the message (it's base64)
echo "BASE64_DATA" | base64 -d | jq '.'
```

### Find Root Cause by Timestamp
```bash
# If message published at 10:00, check logs around that time
gcloud logging read \
    "resource.type=cloud_run_revision AND timestamp >= '2024-01-15T09:55:00Z' AND timestamp <= '2024-01-15T10:05:00Z'" \
    --limit=50 --format="table(timestamp, severity, textPayload)"
```

### Check if Specific Service Down
```bash
# Vertex AI (LLM)
gcloud ai models list --location us-central1

# Firestore
gcloud firestore collections list

# Pub/Sub
gcloud pubsub subscriptions list

# Cloud Run
gcloud run services list
```

---

## ✅ Quick Actions

### Reprocess All DLQ Messages (Nuclear Option)

```bash
#!/bin/bash
# Reprocess everything from a DLQ

TOPIC="workflow-progress"  # Change as needed
DLQ_SUB="productivity-assistant-${TOPIC}-dlq-sub"
MAIN_TOPIC="productivity-assistant-${TOPIC}"

# Count messages
COUNT=$(gcloud pubsub subscriptions describe $DLQ_SUB --format="value(numUnackedMessages)")
echo "Reprocessing $COUNT messages from $TOPIC DLQ..."

# Pull and reprocess
gcloud pubsub subscriptions pull $DLQ_SUB \
    --auto-ack=false --limit=$COUNT --format=json | \
    jq -r '.[] | .message.data' | \
    while read data; do
        echo "$data" | base64 -d | \
        gcloud pubsub topics publish $MAIN_TOPIC \
            --message="$(cat)" &
    done

wait
echo "✅ Reprocessing complete"
```

### Purge All DLQ Messages (For Dead Messages)

```bash
# WARNING: THIS IS IRREVERSIBLE!
# Use only if messages are definitively unrecoverable

for topic in workflow-progress workflow-replan agent-health system-events; do
    DLQ_SUB="productivity-assistant-${topic}-dlq-sub"
    echo "Purging $DLQ_SUB..."
    gcloud pubsub subscriptions seek $DLQ_SUB --time=2030-01-01T00:00:00Z
done

echo "✅ All DLQs purged"
```

### Enable Debug Logging for DLQ Issues

```bash
# Deploy with DEBUG logging
gcloud run deploy productivity-assistant \
    --set-env-vars="LOG_LEVEL=DEBUG"

# Tail logs
gcloud run logs read productivity-assistant --follow

# Look for "retry", "backoff", "dlq" in output

# After debugging, reduce back to INFO
gcloud run deploy productivity-assistant \
    --set-env-vars="LOG_LEVEL=INFO"
```

---

## 🚨 Decision Tree: What to Do with DLQ Message?

```
DLQ Message Exists?
    ↓
├─→ Message is valid JSON?
│   ├─→ YES: Process successfully?
│   │   ├─→ YES: Delete it (duplicate)
│   │   └─→ NO: Reprocess → investigate error
│   └─→ NO: Delete it (corrupt)
│
└─→ Root cause ongoing?
    ├─→ YES: Fix cause first, then reprocess
    └─→ NO: Reprocess immediately
```

---

## 📊 Metrics to Monitor

```bash
# Daily standup checks
echo "=== DLQ Health Check ==="

# 1. Message count (should be 0)
gcloud pubsub subscriptions describe productivity-assistant-workflow-progress-dlq-sub \
    --format="value(numUnackedMessages)"

# 2. Oldest message age (should be < 1 hour)
gcloud pubsub subscriptions describe productivity-assistant-workflow-progress-dlq-sub \
    --format="value(oldestRetainedAckedMessageAge)"

# 3. Messages in last hour
gcloud logging read \
    "jsonPayload.moved_to_dlq=true AND timestamp >= '1h'" | wc -l

# 4. Current error rate
gcloud logging read \
    "resource.type=cloud_run_revision AND severity=ERROR AND timestamp >= '5m'" | wc -l
```

---

## 🆘 When to Escalate

**Escalate to platform team if:**

- DLQ messages > 100 and growing
- Same error repeats > 10 times
- Messages stuck in DLQ > 24 hours
- Multiple DLQs filling up together
- Reprocessing doesn't help
- Root cause unknown after 1 hour investigation

**Escalation:**
1. Slack: #productivity-assistant-incidents
2. Page: On-call engineer
3. Create ticket: [Incident Tracking System]

---

## 📚 Deep Dives

For more information, see:

- **[DLQ_HANDLING_GUIDE.md](DLQ_HANDLING_GUIDE.md)** (600 lines) - Complete reference
- **[OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md)** - Full emergency procedures
- **[GCP Pub/Sub DLQ Docs](https://cloud.google.com/pubsub/docs/dead-letter-topics)** - Official docs

---

## 💡 Pro Tips

1. **Batch your reprocessing**
   - Don't republish 1,000 messages one-by-one
   - Use limit=100 and process in batches
   - Add small delay between batches

2. **Always check root cause first**
   - Don't reprocess if cause is still present
   - You'll just get more DLQ messages
   - Fix first, reprocess second

3. **Monitor P99 latency**
   - DLQ is symptom, not disease
   - Root cause is usually latency issue
   - Track: workflow-progress latency, LLM latency, DB latency

4. **Use message attributes for tracking**
   - Add `dlq_reprocessed=true` attribute when republishing
   - Helps identify reprocessed vs original
   - Useful for auditing

5. **Set up alerting on DLQ trends**
   - Not just "DLQ > 0"
   - Also: "DLQ growing over time" indicates systematic issue
   - Set up forecast alert

---

**Last Updated:** April 4, 2026
**Questions?** See DLQ_HANDLING_GUIDE.md or contact platform team
