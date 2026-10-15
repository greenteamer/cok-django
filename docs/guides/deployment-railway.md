# Production Deployment on Railway

This guide describes the **current production deployment** of `coreofkeen.com`.
For a self-hosted alternative (Ubuntu + Nginx), see [`deployment.md`](./deployment.md).

---

## Topology

```
Internet → Cloudflare (proxy, CDN cache) → Railway service `cok-django`
                                              ├─ Gunicorn → Django (+ WhiteNoise for /static/)
                                              ├─ Django serves /media/ from volume
                                              └─ Railway Postgres service
```

| Railway component | Purpose |
|-------------------|---------|
| Service `cok-django` | Built from this repository's `Dockerfile` (GitHub-connected) |
| Volume `cok-django-volume` | Mounted at `/data`; holds uploaded media (`/data/media`) |
| Service `Postgres` | Database, with its own `postgres-volume` |

There is no Nginx on Railway: static files are served by WhiteNoise, media
files by Django (`SERVE_MEDIA=True`). Cloudflare caches both at the edge.

---

## Build and Startup

1. Railway builds the image from `Dockerfile`.
2. `entrypoint.sh` runs on every container start:
   - waits for PostgreSQL (`DB_HOST`/`DB_PORT`, falling back to `PGHOST`/`PGPORT`; timeout `DB_WAIT_TIMEOUT`)
   - `python manage.py migrate --noinput`
   - `python manage.py collectstatic --noinput`
3. Gunicorn starts on `0.0.0.0:$PORT` (Railway injects `PORT`), workers = `WEB_CONCURRENCY` (default 3).

Migrations and static collection are automatic — no manual `make migrate` on Railway.

Details: [`runtime/lifecycle.md`](../runtime/lifecycle.md).

---

## Service Settings (Railway UI)

Health check settings live in the Railway service settings, not in the
repository (the former `railway.toml` was removed). Recommended values
(same as the removed file):

| Setting | Value |
|---------|-------|
| Healthcheck Path | `/health/` |
| Healthcheck Timeout | `120` s |
| Restart Policy | On failure |

`/health/` is exempt from SSL and canonical-host redirects, see
[`security/overview.md`](../security/overview.md).

---

## Environment Variables

Set on the `cok-django` service → **Variables**. Full reference:
[`config/environment.md`](../config/environment.md).

| Variable | Production value / note |
|----------|------------------------|
| `SECRET_KEY` | strong random value |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | include `coreofkeen.com` (and `www.` if used) |
| `CSRF_TRUSTED_ORIGINS` | `https://coreofkeen.com` (required for admin login behind proxy) |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | from the Postgres service (Railway variable references). **Django reads only `DB_*`**; the `PG*` fallback exists only in `entrypoint.sh` wait loop |
| `MEDIA_ROOT` | `/data/media` — MUST be inside the volume |
| `SERVE_MEDIA` | `True` — Django serves `/media/` (no Nginx) |
| `USE_R2` | unset / `False` (media on volume) |

---

## Media Storage

Container filesystem on Railway is **ephemeral**: everything outside the
volume is wiped on every deploy. Uploaded files survive only because
`MEDIA_ROOT=/data/media` points inside the volume mounted at `/data`.

**Failure mode**: if `MEDIA_ROOT` points outside the volume, uploads work
until the next deploy, then return 404 while the database still references
them. Fix: correct `MEDIA_ROOT`, redeploy, re-upload the images in the admin.

**Alternative**: Cloudflare R2 (`USE_R2=True`), see
[`config/environment.md`](../config/environment.md#cloudflare-r2-storage-settings).
Switching requires moving existing files into the bucket.

**Limitation**: a Railway volume attaches to a single service — do not scale
`cok-django` to multiple replicas while media lives on the volume.

**Backups**: media on the volume is not backed up by this project; use
Railway volume backups or copy `/data/media` periodically.

---

## Deploying a Change

1. Commit and push to the branch connected to the Railway service.
2. Railway builds and deploys automatically; the old container keeps serving
   until the health check of the new one passes.
3. Verify:
   - `https://coreofkeen.com/health/` → `{"status": "ok", "database": "ok"}`
   - `/blog/` renders with images

Cloudflare may serve cached `/media/` and `/static/` responses for up to
4 hours (`cache-control: max-age=14400`); purge the cache in Cloudflare if a
changed file must appear immediately.

---

## Troubleshooting

| Symptom | Likely cause |
|---------|--------------|
| Images 404 after a deploy | `MEDIA_ROOT` outside the volume (see Media Storage) |
| Images 404 always, `DEBUG=False` | `SERVE_MEDIA` not `True` |
| Deploy stuck / restarting | Health check failing — check DB variables, logs in Railway → Deployments |
| `ERROR: PostgreSQL not available` in logs | wrong `DB_HOST`/`DB_PORT`, or Postgres service down |
| Admin login fails with CSRF error | `CSRF_TRUSTED_ORIGINS` missing the https origin |
