# openshift/ — OpenShift manifests

Static YAML, no keys. The Secret (`token-golf-keys`) is applied by hand
in-cluster and is never committed to git.

- `buildconfig.yaml` — BuildConfig, docker strategy, git source tracking
  the `dev` branch; output ImageStream `token-golf:latest`.
- `imagestream.yaml` — ImageStream receiving the built image.
- `deployment.yaml` — envFrom the `token-golf-keys` Secret;
  `DATABASE_PATH=/data/token-golf.db`; PVC `token-golf-data` mounted at
  `/data`; imageChange trigger for auto-rollout.
- `service.yaml` / `route.yaml` — port 3000, edge-terminated route.

## Manual steps (in order)

1. Rotate provider keys; write `.env.secrets` (gitignored, never in git).
2. `oc login` / `oc project <namespace>`.
3. `oc apply -f openshift/`
4. `oc create secret generic token-golf-keys --from-env-file=.env.secrets`
5. `oc start-build token-golf` (v1 deploy trigger is manual; webhook
   automation is follow-up).
6. `oc rollout status deploy/token-golf`, then `oc get route token-golf`.

## Key rotation (idempotent)

```
oc create secret generic token-golf-keys --from-env-file=.env.secrets --dry-run=client -o yaml | oc apply -f -
oc rollout restart deploy/token-golf
```
