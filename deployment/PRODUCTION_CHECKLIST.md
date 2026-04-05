# Production Deployment Checklist

## 📋 Pre-Deployment Phase

### GCP Account & Project Setup
- [ ] GCP Project created and active
- [ ] Billing account linked to project
- [ ] Billing alerts configured ($100 monthly limit recommended)
- [ ] Required APIs enabled:
  - [ ] Cloud Run API
  - [ ] Cloud Pub/Sub API
  - [ ] Firestore API
  - [ ] Vertex AI API
  - [ ] Artifact Registry API
  - [ ] Cloud Logging API
  - [ ] Cloud Monitoring API
  - [ ] Cloud Trace API

### Local Environment Setup
- [ ] `gcloud` CLI installed and configured
- [ ] Docker installed and running
- [ ] Terraform (v1.0+) installed
- [ ] Git repository cloned locally
- [ ] Python 3.10+ environment available
- [ ] All Python dependencies installed
  ```bash
  pip install -r requirements.txt
  ```

### Credentials & Permissions
- [ ] GCP Service Account created
- [ ] Service Account has minimum required roles:
  - [ ] Cloud Run Admin
  - [ ] Pub/Sub Admin
  - [ ] Firestore Admin
  - [ ] Vertex AI User
  - [ ] Service Account User
  - [ ] Storage Admin (for Artifact Registry)
  - [ ] Cloud Logging Log Writer
- [ ] Service account key downloaded and secured
- [ ] Local gcloud authenticated:
  ```bash
  gcloud auth login
  gcloud config set project PROJECT_ID
  ```

### Code Quality
- [ ] All tests pass
  ```bash
  pytest tests/ -v
  ```
- [ ] Code quality checks pass
  ```bash
  pylint backend/ services/
  flake8 backend/ services/
  ```
- [ ] Security scan passes
  ```bash
  bandit -r backend/ services/
  ```
- [ ] No hardcoded secrets in code
- [ ] All configuration in environment variables
- [ ] `.env.example` created and documented

### Docker Image
- [ ] Dockerfile builds successfully
  ```bash
  docker build -t test:latest .
  ```
- [ ] Image runs locally
  ```bash
  docker run -p 8080:8080 test:latest
  ```
- [ ] Image size < 500MB
  ```bash
  docker images | grep test
  ```
- [ ] Non-root user configured
- [ ] Health endpoints working

### Configuration Files
- [ ] `backend/services/config.py` validated for production
  - [ ] `USE_MOCK_LLM = False`
  - [ ] `USE_MOCK_PUBSUB = False`
  - [ ] `ENABLE_CLOUD_LOGGING = True`
  - [ ] `ENABLE_CLOUD_MONITORING = True`
- [ ] `deployment/terraform/prod.tfvars` configured
  - [ ] `gcp_project_id` set
  - [ ] `gcp_region` set
  - [ ] `environment = "prod"`
  - [ ] `cloud_run_memory = "2Gi"`
  - [ ] `cloud_run_cpu = "2"`
  - [ ] `cloud_run_min_instances = 1`
  - [ ] `cloud_run_max_instances = 100`
  - [ ] LLM model is `gemini-1.5-pro`
- [ ] Terraform backend configured
  - [ ] GCS bucket for state created
  - [ ] `backend.tf` updated with bucket name
  - [ ] Bucket versioning enabled
  - [ ] Bucket encryption enabled

---

## 🚀 Deployment Phase

### Artifact Registry Setup
- [ ] Repository created
  ```bash
  gcloud artifacts repositories create productivity-assistant \
      --repository-format=docker \
      --location=us-central1
  ```
- [ ] Docker authenticated
  ```bash
  gcloud auth configure-docker us-central1-docker.pkg.dev
  ```
- [ ] Image built and tagged
  ```bash
  docker build -t us-central1-docker.pkg.dev/PROJECT_ID/productivity-assistant/productivity-assistant:latest .
  ```
- [ ] Image pushed to registry
  ```bash
  docker push us-central1-docker.pkg.dev/PROJECT_ID/productivity-assistant/productivity-assistant:latest
  ```
- [ ] Image verified in Artifact Registry
  ```bash
  gcloud artifacts docker images list us-central1-docker.pkg.dev/PROJECT_ID/productivity-assistant
  ```

### Terraform Deployment
- [ ] Terraform files validated
  ```bash
  cd deployment/terraform
  terraform validate
  ```
- [ ] Terraform plan reviewed
  ```bash
  terraform plan -var-file="prod.tfvars" -out=tfplan
  ```
- [ ] Plan shows expected resources (12 resources)
- [ ] No unexpected deletions
- [ ] Terraform applied
  ```bash
  terraform apply tfplan
  ```
- [ ] All resources created successfully
- [ ] Terraform outputs verified
  ```bash
  terraform output -json
  ```

### Cloud Run Service Verification
- [ ] Service deployed and running
  ```bash
  gcloud run services list
  ```
- [ ] Service is public (if needed)
  ```bash
  gcloud run services get-iam-policy productivity-assistant
  ```
- [ ] Environment variables set correctly
  ```bash
  gcloud run services describe productivity-assistant --format=json | jq '.spec.template.spec.containers[0].env'
  ```
- [ ] Resource limits correct (2Gi memory, 2 CPU)
- [ ] Timeout set correctly (300s)
- [ ] Health probes configured
  ```bash
  gcloud run services describe productivity-assistant --format=json | jq '.spec.template.spec.containers[0].livenessProbe'
  ```

### Database Verification
- [ ] Firestore database created
  ```bash
  gcloud firestore databases list
  ```
- [ ] Collections created:
  - [ ] workflows
  - [ ] agents
  - [ ] decisions
  - [ ] audit_logs
- [ ] Firestore security rules configured (not permissive)
- [ ] Backup policy set (daily exports enabled)

### Pub/Sub Verification
- [ ] Topics created (4 topics):
  - [ ] workflow-progress
  - [ ] workflow-replan
  - [ ] agent-health
  - [ ] system-events
- [ ] Subscriptions created
- [ ] Message retention set (7 days recommended)
- [ ] Dead-letter topics created

### Monitoring & Logging Setup
- [ ] Cloud Logging configured
  ```bash
  gcloud logging sinks list
  ```
- [ ] Log router policy created for Cloud Run
- [ ] Log retention set (30 days recommended)
- [ ] Cloud Monitoring configured
  ```bash
  gcloud monitoring alert-policies list
  ```
- [ ] Alert policy for high error rate created
- [ ] Alert notification channels configured
  - [ ] Email notifications enabled
  - [ ] Slack webhook configured (optional)
  - [ ] PagerDuty integration (optional)

---

## 🔍 Post-Deployment Validation

### Service Health
- [ ] Cloud Run service endpoint accessible
  ```bash
  CLOUD_RUN_URL=$(gcloud run services describe productivity-assistant \
      --platform managed --region us-central1 --format='value(status.url)')
  curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
      $CLOUD_RUN_URL/health
  ```
- [ ] Health check returns 200 status
- [ ] Response includes all service statuses
- [ ] LLM service responding
- [ ] Pub/Sub service responding
- [ ] Firestore service responding

### Functional Testing
- [ ] Create test workflow (authenticated request)
  ```bash
  curl -X POST $CLOUD_RUN_URL/api/workflows \
      -H "Content-Type: application/json" \
      -d '{"name":"test","tasks":[]}'
  ```
- [ ] Workflow persisted to Firestore
- [ ] Workflow ID returned
- [ ] Retrieve workflow (GET request)
- [ ] Update workflow (PUT request)
- [ ] List workflows (list endpoint)

### Performance Testing
- [ ] Response time < 1s for simple requests
- [ ] P99 latency under 5s
- [ ] No timeout errors
- [ ] Memory usage < 80% of allocated
- [ ] CPU usage < 80% of allocated
- [ ] Load test: 100 concurrent requests
  ```bash
  ab -n 1000 -c 100 $CLOUD_RUN_URL/health
  ```

### Security Validation
- [ ] HTTPS enforced (Cloud Run default)
- [ ] Service account has minimal permissions
- [ ] No public Firestore database access
- [ ] Pub/Sub subscriptions restricted
- [ ] API authentication required
- [ ] Rate limiting configured (if needed)
- [ ] CORS properly configured
- [ ] Security headers configured (Cloud Run annotations)

### Logging & Monitoring
- [ ] Logs appear in Cloud Logging
  ```bash
  gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=productivity-assistant"
  ```
- [ ] Application logs structured (JSON format)
- [ ] Request logs present
- [ ] Error logs present
- [ ] Monitoring metrics visible in Cloud Monitoring
  - [ ] Request count
  - [ ] Request latency
  - [ ] Error rate
  - [ ] CPU usage
  - [ ] Memory usage
- [ ] Alert policy test successful
  ```bash
  # Trigger high error rate by sending bad requests
  for i in {1..100}; do curl $CLOUD_RUN_URL/bad-endpoint; done
  ```

### Networking & Access
- [ ] Service accessible from external IP
- [ ] Service not accessible with wrong authentication
- [ ] Custom domain working (if configured)
  ```bash
  curl https://your-domain.com/health
  ```
- [ ] Load balancer distributing traffic
- [ ] CDN caching working (if configured)

---

## 📊 Monitoring Phase (First 24 Hours)

### Real-Time Monitoring
- [ ] Monitor dashboard open and viewable
  ```bash
  gcloud monitoring dashboards list
  ```
- [ ] Key metrics visible:
  - [ ] Request count trending correctly
  - [ ] Error rate < 0.1%
  - [ ] P99 latency < acceptable threshold
  - [ ] Instance count stable
- [ ] Check logs every hour for anomalies
- [ ] Set up on-call rotation if not already
- [ ] Team notified of production status

### Issue Response
- [ ] Error budget tracking
- [ ] Escalation path defined
- [ ] Rollback procedure tested
  ```bash
  # To rollback to previous revision
  gcloud run services update-traffic productivity-assistant \
      --to-revisions REVISION_NAME=100
  ```
- [ ] Incident response procedure documented
- [ ] Communication with stakeholders established

### Optimization
- [ ] Analyze cold start time
  - [ ] Increase min instances if > 5s cold starts
  - [ ] Pre-warm service if needed
- [ ] Review auto-scaling behavior
  - [ ] Target CPU utilization appropriate
  - [ ] Max instances sufficient for peak load
- [ ] Optimize Firestore queries
  - [ ] Create composite indexes if needed
  ```bash
  gcloud firestore indexes list
  ```
- [ ] Monitor Pub/Sub queue depth
  - [ ] Add subscribers if lag increasing

---

## 🔐 Security & Compliance Phase

### Access Control
- [ ] Service account usage audited
- [ ] IAM deny policies in place (if needed)
- [ ] Regular security reviews scheduled
- [ ] SLAs for security issues defined
- [ ] Audit logs retention set appropriately

### Data Protection
- [ ] Firestore data encrypted at rest (default)
- [ ] Regular backups configured
  ```bash
  gcloud firestore databases backup create
  ```
- [ ] Backup restoration tested
- [ ] Data retention policy documented
- [ ] GDPR/compliance requirements met

### Compliance & Documentation
- [ ] SLA documented and shared with stakeholders
- [ ] RTO/RPO defined and met
- [ ] Disaster recovery procedure documented
- [ ] Runbook for common issues created
- [ ] On-call procedures documented
- [ ] Cost allocation tags set
  ```bash
  gcloud resource-manager tags values create \
      --tag-key=PARENT/cost-center --description="cost-center" cost-center-prod
  ```

---

## 📈 Ongoing Operations Phase

### Weekly Tasks
- [ ] Review error logs for patterns
- [ ] Check cost trends
- [ ] Verify backups completed successfully
- [ ] Review performance metrics
- [ ] Check alert firing (if any)

### Monthly Tasks
- [ ] Detailed cost analysis
- [ ] Capacity planning review
- [ ] Performance metrics review
- [ ] Security audit
- [ ] Disaster recovery test
- [ ] Update runbooks
- [ ] Team knowledge sync

### Quarterly Tasks
- [ ] Load test infrastructure
- [ ] Terraform plan/apply (no changes)
- [ ] Update dependencies
- [ ] Security assessment
- [ ] Cost optimization review
- [ ] Architecture review
- [ ] SLA review and update

---

## 🆘 Emergency Contacts & Escalation

| Role | Contact | On-Call | Escalation |
|------|---------|---------|------------|
| Platform Lead | [Name] | [Phone] | [Email] |
| DevOps | [Name] | [Phone] | [Email] |
| SRE | [Name] | [Phone] | [Email] |
| Security | [Name] | [Phone] | [Email] |
| Leadership | [Name] | [Phone] | [Email] |

---

## ✅ Final Sign-Off

- [ ] All checklist items completed
- [ ] All tests passing
- [ ] Performance acceptable
- [ ] Monitoring active
- [ ] Team trained
- [ ] Documentation complete

**Deployment Date:** _______________

**Deployed By:** _______________

**Approved By:** _______________

**Notes:** 

_______________________________________________

_______________________________________________

_______________________________________________

---

**Document Version:** 1.0
**Last Updated:** April 4, 2026
**Next Review:** [1 Month Post-Deployment]
