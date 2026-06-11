# Deploying UTOS

UTOS is a persistent Python (`http.server`) app backed by SQLite. It needs a
host that runs a **long-lived process** — not a serverless platform like Vercel,
where the process and the SQLite file would not survive between requests. Render
and Railway both fit and run the code unchanged.

## Option A — Render (recommended)

A `render.yaml` blueprint is included.

1. Push this repo to GitHub (already configured as `origin`).
2. Go to <https://dashboard.render.com> and sign in (GitHub login is easiest).
3. **New +** → **Blueprint** → select this repository.
4. Render reads `render.yaml`, creates the **utos** web service, and deploys.
5. When the build finishes, open the service URL (e.g. `https://utos.onrender.com`).
   The health check is `/api/health`.

That's it — the frontend and API are served from the same origin, so there is
nothing else to wire up.

### Data persistence on Render
The **free** plan has no persistent disk, so the SQLite database resets to the
seeded sample data on every deploy or restart (fine for a demo). For durable
data:
1. Change `plan: free` → `plan: starter` in `render.yaml`.
2. Uncomment the `UTOS_DATA_DIR` env var **and** the `disk:` block.
3. Redeploy. SQLite now lives on the mounted disk at `/var/data` and persists.

## Option B — Railway

Railway auto-detects the `Procfile` (`web: python -m app.backend.server`) and
injects `$PORT`, which the server already reads.

1. <https://railway.app> → **New Project** → **Deploy from GitHub repo**.
2. Select this repo. Railway builds and deploys automatically.
3. Under the service's **Settings → Networking**, generate a public domain.

For persistence, add a **Volume** mounted at e.g. `/var/data` and set the
service variable `UTOS_DATA_DIR=/var/data`.

## Environment variables the server understands
| Variable | Purpose | Default |
|----------|---------|---------|
| `UTOS_HOST` | Bind address — set to `0.0.0.0` when hosted | `127.0.0.1` |
| `PORT` | Listen port (injected by Render/Railway) | — |
| `UTOS_PORT` | Local-dev port fallback | `8000` |
| `UTOS_DATA_DIR` | Directory for `utos.sqlite` (point at a disk for persistence) | `app/data` |

## Run locally

```bash
python -m app.backend.server
# open http://127.0.0.1:8000
```

## Load the demo dataset (optional)
With the server running, the `tools/university_seed.py` script populates a
realistic, conflict-free Faculty of Computing timetable and login accounts:

```bash
python tools/university_seed.py
```
