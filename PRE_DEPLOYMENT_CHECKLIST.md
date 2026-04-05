# Pre-Deployment Checklist

Use this checklist before deploying to any environment. Print or bookmark for each deployment.

---

## 1. Code Quality & Testing

- [ ] All tests passing locally
  ```bash
  pytest tests/ -v
  ```

- [ ] No security vulnerabilities
  ```bash
  pip-audit
  ```

- [ ] Code linting passing
  ```bash
  pylint backend/
  flake8 backend/
  black --check backend/
  ```

- [ ] Type checking passing
  ```bash
  mypy backend/
  ```

- [ ] Requirements.txt up to date
  ```bash
  pip freeze > requirements.txt
  ```

- [ ] No hardcoded secrets or credentials in code

- [ ] All imports are used (no unused imports)

- [ ] Error handling covers edge cases

---

## 2. Configuration & Environment

- [ ] `.env.production` reviewed and accurate

- [ ] GCP project ID correct

- [ ] GCP APIs enabled:
  - [ ] Cloud Run
  - [ ] Container Registry
  - [ ] Firestore
  - [ ] Pub/Sub
  - [ ] Cloud Logging
  - [ ] Cloud Build (if using CI/CD)

- [ ] Firestore database created

- [ ] Pub/Sub topics created

- [ ] Service account with proper permissions created

- [ ] Environment variables documented

- [ ] No hardcoded hostnames or ports

---

## 3. Security Checklist

- [ ] Docker runs as non-root user

- [ ] Container registry access controlled

- [ ] Secrets not in container images

- [ ] Secrets stored in Google Secret Manager

- [ ] IAM roles follow least privilege principle

- [ ] API requires authentication (if public)

- [ ] CORS properly configured

- [ ] Rate limiting enabled

- [ ] Logging enabled for audit trail

- [ ] SSL/TLS certificates valid

- [ ] VPC or network policies configured (if needed)

---

## 4. Performance & Scaling

- [ ] Resource limits set appropriately
  - Orchestrator: 1 CPU, 1Gi memory
  - MCP Servers: 0.5 CPU, 512Mi memory

- [ ] Health checks configured

- [ ] Timeouts set (service: 30s, MCP: 25s)

- [ ] Connection pooling configured (10 connections)

- [ ] Caching enabled for appropriate endpoints

- [ ] Database indexes created for queries

- [ ] No N+1 queries identified

- [ ] Batch operations configured

- [ ] Auto-scaling thresholds set
  - min-instances: 1-2
  - max-instances: 10-100
  - CPU threshold: 70%
  - Memory threshold: 80%

---

## 5. Monitoring & Logging

- [ ] Cloud Logging enabled

- [ ] Log level appropriate (DEBUG for dev, INFO for prod)

- [ ] Structured logging implemented

- [ ] Error tracking configured

- [ ] Health check endpoints functional

- [ ] Metrics collection enabled

- [ ] Alerting policies created for:
  - [ ] High error rate (>5%)
  - [ ] High latency (>5 seconds)
  - [ ] Service unavailability
  - [ ] Database quota exceeded

- [ ] Dashboard created for monitoring

- [ ] Log retention policy set

---

## 6. Data & Backup

- [ ] Firestore backup scheduled

- [ ] Backup retention policy documented

- [ ] Disaster recovery procedure tested

- [ ] Data encryption enabled

- [ ] Firestore indexes deployed

- [ ] Database queries validated

- [ ] Pub/Sub dead letter topics configured

- [ ] Data retention policies enforced

---

## 7. Documentation

- [ ] Deployment guide reviewed and updated

- [ ] API documentation current

- [ ] Runbook created for common issues

- [ ] Architecture diagram updated

- [ ] Service dependencies documented

- [ ] Configuration options documented

- [ ] Troubleshooting guide updated

- [ ] Team trained on deployment procedure

---

## 8. Build & Deployment

### Docker Build

- [ ] Dockerfile syntax checked
- [ ] All dependencies in requirements.txt
- [ ] Build succeeds without errors
- [ ] Image size reasonable (<500MB)
- [ ] Layers optimized for caching

### Cloud Run Deployment

- [ ] `deploy-to-cloud.sh` script tested

- [ ] GCP project ID correct

- [ ] Region selected and available

- [ ] Service names don't conflict

- [ ] Memory/CPU allocations appropriate

- [ ] Networking configured

- [ ] Environment variables loaded correctly

### Kubernetes Deployment (if applicable)

- [ ] Namespace created

- [ ] RBAC configured

- [ ] Resource quotas set

- [ ] Network policies configured

- [ ] PersistentVolumes created (if needed)

- [ ] StatefulSets configured (if needed)

---

## 9. Post-Deployment Validation

### Immediate After Deploy

- [ ] All services are running
  ```bash
  gcloud run services list
  # or
  kubectl get pods -n multi-agent
  ```

- [ ] Health checks passing
  ```bash
  curl https://orchestrator-url/health
  ```

- [ ] APIs responding
  ```bash
  curl https://orchestrator-url/tasks
  ```

- [ ] Logs not showing errors
  ```bash
  gcloud run logs read SERVICE_NAME --limit=50
  ```

### 5 Minutes After Deploy

- [ ] No spike in error rates

- [ ] Response times normal

- [ ] Database connections healthy

- [ ] Pub/Sub topics receiving messages

- [ ] All dependent services accessible

### 30 Minutes After Deploy

- [ ] No memory leaks detected

- [ ] CPU usage normal

- [ ] No cascading failures

- [ ] Alerts not triggering

- [ ] Load balanced properly (if applicable)

### End of Day (First Day)

- [ ] 24+ hours of normal logs

- [ ] Zero critical alerts

- [ ] Performance metrics baseline established

- [ ] Team notified of successful deployment

---

## 10. Rollback Plan

- [ ] Previous version backed up

- [ ] Rollback procedure documented

- [ ] Team trained on rollback

- [ ] Rollback time estimated (<15 minutes)

- [ ] Database schema compatible with previous version

- [ ] Canary deployment considered (if high risk)

---

## 11. Communication

- [ ] Deployment scheduled and announced

- [ ] Stakeholders notified

- [ ] Maintenance window scheduled (if needed)

- [ ] Support team briefed

- [ ] Runbook shared with team

- [ ] Change log updated

- [ ] Deployment completed notification sent

---

## 12. Local Testing Checklist

Before any cloud deployment, verify locally:

```bash
# 1. Start local environment
docker-compose up

# 2. Wait for services to be healthy (30-60 seconds)
docker-compose logs

# 3. Run health checks
./health-check.sh

# 4. Test all major features
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "priority": "high"}'

curl http://localhost:8000/tasks

# 5. Check logs for errors
docker-compose logs --tail=100 orchestrator

# 6. Load test (optional)
# ab -n 100 -c 10 http://localhost:8000/health

# 7. Stop and clean up
docker-compose down
```

---

## Deployment Commands Quick Reference

### Local Deployment
```bash
docker-compose up
```

### Cloud Run Deployment
```bash
./deploy-to-cloud.sh PROJECT_ID us-central1
```

### Kubernetes Deployment
```bash
kubectl apply -f k8s-deployment.yaml
```

### Health Check
```bash
./health-check.sh           # Single check
./health-check.sh -m        # Continuous monitoring
```

### View Logs
```bash
# Cloud Run
gcloud run logs read SERVICE_NAME --limit=50

# Kubernetes
kubectl logs deployment/DEPLOYMENT_NAME -n multi-agent -f

# Docker Compose
docker-compose logs -f SERVICE_NAME
```

### Troubleshooting
```bash
# Check services
gcloud run services list
kubectl get pods -n multi-agent
docker-compose ps

# Debug pod/container
kubectl describe pod POD_NAME -n multi-agent
docker logs CONTAINER_NAME
```

---

## Sign-Off

**Deployment Prepared By**: _____________________  
**Date/Time**: _____________________  
**Deployment Performed By**: _____________________  
**Date/Time**: _____________________  
**Verified By**: _____________________  
**Date/Time**: _____________________  

### Notes:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

## Useful Links

- [Cloud Run Docs](https://cloud.google.com/run/docs)
- [Firestore Docs](https://cloud.google.com/firestore/docs)
- [Pub/Sub Docs](https://cloud.google.com/pubsub/docs)
- [GKE Docs](https://cloud.google.com/kubernetes-engine/docs)
- [Docker Docs](https://docs.docker.com)

---

**Last Updated**: 2024  
**Version**: 1.0
