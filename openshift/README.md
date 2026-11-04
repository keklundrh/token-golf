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
   (do this BEFORE the pod starts: the Deployment envFrom's this Secret,
   and without it the container crash-loops on missing provider keys)
5. Create the build-webhook secret (value = any random hex; this value
   is the URL path token — see the webhook section below):
   `oc create secret generic token-golf-webhook-secret --from-literal=WebHookSecretKey=$(openssl rand -hex 20)`
6. Grant anonymous build-triggering (webhook POSTs are unauthenticated;
   without this role GitHub's calls get 403):
   `oc adm policy add-role-to-user system:webhook system:anonymous -n token-golf`
   ⚠ Shared-cluster caution: this lets ANY caller with network access
   trigger builds in this namespace. Get cluster-admin sign-off; the
   no-anonymous-grants alternative is GitHub Actions with a bot token
   running `oc start-build token-golf` (also enables dev-only filtering).
7. First build (once; the webhook handles later pushes to `dev`):
   `oc start-build token-golf`
8. `oc rollout status deploy/token-golf`, then `oc get route token-golf`.

## GitHub webhook (push-to-deploy, one-time)

`git push origin dev` deploys automatically once the webhook exists —
without it, builds only happen via `oc start-build` by hand.

1. Get the webhook URL. `oc describe bc token-golf` shows the template
   with a literal `<secret>` placeholder (the trigger uses
   `secretReference`, so describe can't embed the value):
   `https://api.<cluster>/apis/build.openshift.io/v1/namespaces/<namespace>/buildconfigs/token-golf/webhooks/<secret>/generic`
   Substitute `<secret>` with the Secret's key value:
   `oc get secret token-golf-webhook-secret -o jsonpath='{.data.WebHookSecretKey}' | base64 -d`
2. GitHub repo → Settings → Webhooks → Add webhook:
   Payload URL = that URL (the secret IN the URL path is the real auth —
   keep the full URL secret) · Content type = `application/json` ·
   Secret field = the `WebHookSecretKey` value (GitHub uses it to sign
   deliveries; OpenShift's generic endpoint ignores the signature —
   filling it is optional but harmless) ·
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
