# Infrastructure and scale

## POC

The included Dockerfile packages the typed FastAPI application from [the application-layer POC](../user_experience_application/README.md). From the repository root:

```powershell
docker build -f agents\production\capabilities\infrastructure_scale\Dockerfile -t agent-capabilities-poc .
docker run --rm -p 8000:8000 agent-capabilities-poc
```

Check `http://localhost:8000/health` or `/docs`. The API returns a deterministic demo response. A container image alone does not provide production scale or availability.

## Maturity path

| Stage | Tools, frameworks, and APIs | Add |
|---|---|---|
| Basic POC | Docker, health endpoint | Repeatable local runtime |
| Prototype | Compose, managed PostgreSQL/Redis, CI image build, Terraform | Config separation, migrations, health/readiness, rollback |
| Enterprise | Kubernetes or managed container platform, ingress/service mesh, autoscaling, secrets manager | HA, capacity planning, backups/restore, regional strategy, SLOs, disaster recovery drills |

Pick infrastructure based on operational capacity and measured load. Keep secrets out of images, configure resource limits, run as non-root, pin image dependencies, and test graceful shutdown before production.
