# openshift/ — OpenShift manifests

Static YAML, no keys. Secrets (`token-golf-keys`, the build-webhook
`token-golf-webhook-secret`) are applied by hand in-cluster and are
never committed to git.

- `buildconfig.yaml` — BuildConfig, docker strategy, git source tracking
  the `dev` branch; output ImageStream `token-golf:latest`; generic-webhook
  trigger (secret via `token-golf-webhook-secret` Secret reference) so a
  GitHub push fires the build.
- `pvc.yaml` — PersistentVolumeClaim `token-golf-data` (1Gi, ReadWriteOnce)
  backing the SQLite mount; the Deployment references it by name.
- `deployment.yaml` — envFrom the `token-golf-keys` Secret;
  `DATABASE_PATH=/data/token-golf.db`; PVC `token-golf-data` mounted at
  `/data`; imageChange trigger for auto-rollout.
- `service.yaml` / `route.yaml` — port 3000, edge-terminated route.

## Manual steps (in order)

1. Rotate provider keys; write `.env.secrets` (gitignored, never in git).
2. `oc login` / `oc project <namespace>`.
3. `oc apply -f openshift/`
4. `oc create secret generic token-golf-keys --from-env-file=.env.secrets`
5. Create the build-webhook secret (value = any random hex; the same
   value goes into the GitHub webhook's Secret field):
   `oc create secret generic token-golf-webhook-secret --from-literal=WebHookSecretKey=$(openssl rand -hex 20)`
6. First build (once; the webhook handles later pushes to `dev`):
   `oc start-build token-golf`
7. `oc rollout status deploy/token-golf`, then `oc get route token-golf`.

## GitHub webhook (push-to-deploy, one-time)

`git push origin dev` deploys automatically once the webhook exists —
without it, builds only happen via `oc start-build` by hand.

1. Get the webhook URL (the BC's `Generic` webhook trigger references the
   `token-golf-webhook-secret` Secret; the URL embeds its key):
   `oc describe bc token-golf | grep -A2 Webhook`
   — e.g.
   `https://api.<cluster>/apis/build.openshift.io/v1/namespaces/<namespace>/buildconfigs/token-golf/webhooks/<secret>/generic`
2. GitHub repo → Settings → Webhooks → Add webhook:
   Payload URL = that URL · Content type = `application/json` ·
   Secret = the `WebHookSecretKey` value from step 5 above ·
   Trigger = "Just the push event" · Active ✓
   (CLI alternative: `gh api repos/keklundrh/token-golf/hooks -f name=web
   -f 'config[url]=<URL>' -f 'config[content_type]=json'
   -f 'config[secret]=<value>' -F 'events[]=push'`)
3. Verify: the GitHub webhook's `ping` delivers with a green ✓, then any
   push to `dev` starts a build (`oc get builds`).

Caveat: the generic webhook fires on pushes to ANY branch, but every
build builds `ref: dev` — a push to a feature branch starts a build that
just reproduces the same dev image. Noisy, not harmful; dev-only
triggering needs the GitHub Actions path instead.

## Key rotation (idempotent)

```
oc create secret generic token-golf-keys --from-env-file=.env.secrets --dry-run=client -o yaml | oc apply -f -
oc rollout restart deploy/token-golf
```
