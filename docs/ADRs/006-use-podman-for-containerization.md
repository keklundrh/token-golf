# ADR 006: Use Podman for Containerization

## Status

Accepted

## Context

The project requires containerization for:
- Local development consistency
- OpenShift deployment (production target)
- Multi-developer environment parity
- Conference demo reliability

While Docker is the most common containerization tool, Podman offers several advantages particularly relevant to our OpenShift deployment target and development workflow.

Key considerations:
- **OpenShift Native**: Red Hat OpenShift uses Podman/CRI-O under the hood
- **Rootless by Default**: Better security posture, no daemon required
- **Docker Compatibility**: Drop-in replacement with `alias docker=podman`
- **Development Environment**: Team preference and existing tooling
- **OCI Compliance**: Standard container format, portable across runtimes

## Decision

We will use Podman (with podman-compose) for all container operations in development and leverage OpenShift's native container runtime in production.

**Implementation Details**:
- Use `podman` and `podman-compose` commands throughout documentation
- Maintain Docker compatibility via standard Dockerfile and compose.yml syntax
- All container images built with Podman will work in OpenShift without modification
- Document Podman installation as a prerequisite
- Provide Docker migration notes for contributors who prefer Docker

**What we will do**:
- Install and use Podman for local development
- Use `podman-compose` instead of `docker-compose`
- Write Dockerfiles using OCI-compliant standards (already Docker-compatible)
- Test container builds with Podman before committing
- Update all documentation to reference Podman commands

**What we won't do**:
- Require Docker installation
- Maintain separate Docker and Podman configurations
- Use Docker-specific features that aren't OCI-standard
- Run containers as root (leverage Podman's rootless design)

## Consequences

### Positive Consequences

- **Better OpenShift Alignment**: Same container runtime locally as in production reduces "works on my machine" issues
- **Enhanced Security**: Rootless containers by default, no daemon running as root
- **Simpler Architecture**: No background daemon required, containers run as child processes
- **Resource Efficiency**: Lower memory footprint without daemon overhead
- **Kubernetes/OpenShift Native**: Direct compatibility with our production deployment target
- **Development Parity**: What we test locally is closer to production behavior

### Negative Consequences

- **Learning Curve**: Developers familiar with Docker need to learn Podman nuances
- **Ecosystem Maturity**: Docker has larger community and more third-party tooling
- **Compose Compatibility**: `podman-compose` is less mature than `docker-compose`
- **Documentation**: Most tutorials assume Docker, may need translation

### Risks and Mitigations

**Risk**: Developers get stuck with Podman-specific issues
- **Mitigation**: Document common gotchas, provide Docker compatibility notes
- **Mitigation**: Most Podman commands are 1:1 with Docker (`alias docker=podman` works)

**Risk**: CI/CD pipelines assume Docker
- **Mitigation**: OpenShift uses its own build system, not dependent on local tooling
- **Mitigation**: GitHub Actions and most CI systems support Podman

**Risk**: podman-compose feature gaps vs docker-compose
- **Mitigation**: Our compose file uses basic features well-supported in both
- **Mitigation**: Can fall back to `podman play kube` for advanced scenarios

## Alternatives Considered

### Alternative 1: Docker

**Description**: Use Docker and Docker Compose for development

**Pros**:
- Industry standard, largest user base
- Mature tooling ecosystem (Docker Desktop, extensions)
- docker-compose is feature-complete and stable
- Most documentation and tutorials use Docker

**Cons**:
- Requires daemon running as root (security concern)
- Different runtime than production OpenShift environment
- License changes (Docker Desktop requires paid license for some orgs)
- Heavier resource usage due to daemon

**Why not chosen**: 
- Production target (OpenShift) uses Podman/CRI-O
- Rootless operation is better security practice
- Team preference for Podman
- No technical blocker, but misalignment with production

### Alternative 2: Kubernetes/Kind for Local Development

**Description**: Use Kind (Kubernetes in Docker) or Minikube for local development

**Pros**:
- Even closer to production Kubernetes/OpenShift environment
- Full orchestration features locally
- Good for testing multi-service deployments

**Cons**:
- Overkill for single-service development in early phases
- Slower startup and iteration times
- Higher resource requirements (laptop RAM/CPU)
- Steeper learning curve for contributors

**Why not chosen**: 
- Too heavy for MVP development phase
- Can revisit for Phase 8 (production preparation)
- Podman provides sufficient container parity without orchestration overhead

### Alternative 3: No Containers in Development

**Description**: Run FastAPI directly with Python virtual environments

**Pros**:
- Fastest iteration cycle
- Simpler setup for Python developers
- Direct debugging without container overhead

**Cons**:
- "Works on my machine" problems
- Different environment than production
- Harder to ensure dependency consistency
- Manual database and service management

**Why not chosen**:
- Project explicitly requires "containerize from the start" (see DEVELOPMENT_PHASES.md)
- Production is containerized, development should match
- Multi-developer consistency is critical

## References

- [Podman Documentation](https://docs.podman.io/)
- [OpenShift Container Platform](https://docs.openshift.com/container-platform/)
- [Podman vs Docker](https://docs.podman.io/en/latest/Introduction.html)
- [podman-compose](https://github.com/containers/podman-compose)
- Related ADRs: 
  - ADR 001: Tech Stack Selection
  - ADR 004: Use Alembic for Database Migrations

## Migration Notes for Docker Users

For developers comfortable with Docker, Podman is almost identical:

```bash
# Create alias (add to .bashrc or .zshrc)
alias docker=podman
alias docker-compose=podman-compose

# Commands are 1:1
podman build -t image .          # Same as: docker build
podman run -p 8000:8000 image    # Same as: docker run
podman-compose up                # Same as: docker-compose up
```

---

**Date**: 2026-09-09  
**Author**: Token Golf Team  
**Status**: Accepted - Effective immediately for all development
