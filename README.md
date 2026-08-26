# reliability-api

A small Flask service plus the full deployment stack around it, built as a
hands-on SRE/DevOps portfolio piece: containerized app → Helm chart → CI/CD
pipeline that tests, builds, pushes, and deploys it → optional Terraform for
a real EKS cluster.

Nothing here is a toy diagram — it's real, runnable code. The tests already
pass locally (`pytest app/tests -v`, 5/5 green). Run the rest yourself before
you put it on your resume; see "Using this on your resume" at the bottom.

## What it demonstrates

- **App instrumentation**: `/healthz` (liveness), `/readyz` (readiness),
  `/metrics` (Prometheus format via `prometheus_client`), request-count and
  latency histograms.
- **Containerization**: multi-stage `Dockerfile`, non-root user, `HEALTHCHECK`.
- **Kubernetes deployment**: Helm chart with rolling-update strategy,
  resource requests/limits, liveness/readiness probes, and a
  HorizontalPodAutoscaler.
- **CI/CD**: GitHub Actions pipeline — test → build & push image to GHCR →
  deploy to an ephemeral `kind` cluster → verify rollout → smoke test.
- **IaC**: Terraform module for a real EKS cluster + VPC (optional, costs
  money — only apply it if/when you want to run this against real AWS).

## Run it locally (free, ~15 minutes)

```bash
# 1. Run the app directly
cd app
pip install -r requirements-dev.txt
pytest tests/ -v
python main.py &
curl localhost:8080/healthz
curl localhost:8080/readyz
curl localhost:8080/metrics

# 2. Build and run the container
cd ..
docker build -t reliability-api:local .
docker run -p 8080:8080 reliability-api:local

# 3. Deploy to a local Kubernetes cluster
brew install kind helm kubectl      # or your OS's equivalent
kind create cluster --name demo
kind load docker-image reliability-api:local --name demo
helm upgrade --install reliability-api ./helm/reliability-api \
  --set image.repository=reliability-api \
  --set image.tag=local \
  --set image.pullPolicy=Never
kubectl get pods
kubectl port-forward svc/reliability-api 8080:80
```

Then try `curl -X POST localhost:8080/toggle-ready` and watch
`kubectl get pods` / `kubectl describe pod` show the pod drop out of
Ready — that's the readiness probe doing its job, and it's a good thing to
be able to talk through in an interview.

## Push it and watch the pipeline run

1. Create a repo on GitHub, push this code.
2. Go to Settings → Actions → General and confirm workflow permissions
   allow `packages: write` (needed to push to GHCR).
3. Push to `main` — the Actions tab will show test → build/push → deploy →
   smoke test running for real, against a real ephemeral cluster, in CI.

## Terraform (optional, costs money)

`terraform/` provisions a real VPC + EKS cluster via the standard
`terraform-aws-modules` modules, plus one example least-privilege IAM
policy (read-only CloudWatch Logs access, scoped to this cluster's log
group). This is **not required** to demo the project — the CI pipeline
above deploys to a free ephemeral cluster. Only run this if you want to
point the pipeline at a real AWS cluster:

```bash
cd terraform
terraform init
terraform plan
# terraform apply   -- only if you're ready to pay for a running EKS cluster
```

## Using this on your resume

Only claim what you've actually run yourself. Once you've done the local
run-through above and pushed it so the pipeline goes green in your own
GitHub Actions tab, these are honest, defensible bullets:

- "Built and containerized a Python service (Flask) instrumented with
  Prometheus metrics and Kubernetes liveness/readiness probes."
- "Wrote a Helm chart defining a rolling-update Deployment, Service, and
  HorizontalPodAutoscaler; deployed and validated it on a local Kubernetes
  cluster."
- "Built a GitHub Actions CI/CD pipeline that tests, builds/pushes a
  container image, and deploys via Helm to a Kubernetes cluster with an
  automated rollout and smoke-test verification step."
- "Wrote Terraform for a VPC + EKS cluster and a least-privilege IAM policy
  using the standard terraform-aws-modules." *(only if you actually ran
  `terraform plan`/`apply` — reading the file doesn't count.)*

If an interviewer asks "walk me through it," you should be able to open the
repo and explain any file. That's the whole point of doing it yourself
instead of pasting in something you didn't write.
