# Deployment Guide — wakeupservice

**Domain:** `thewakeupservice.buzz`
**Server stack:** React + Vite (frontend) · FastAPI + uvicorn (backend) · nginx (reverse proxy) · Let's Encrypt (SSL)

---

## Architecture Overview

```
Client (HTTPS)
  └─► nginx (port 443)
        ├─ /api/*   → proxy to uvicorn at 127.0.0.1:8000  (wakeupbuzz.service)
        └─ /*       → static files at /opt/form-service/frontend/dist/
```

---

## Updating the Frontend

The frontend is a static React/Vite build. Nginx serves files directly from
`/opt/form-service/frontend/dist/`. **No nginx restart is needed** — just rebuild.

```bash
cd /opt/form-service/frontend
npm run build
```

That's it. The new `dist/` files are served immediately on the next request.

### Why no restart is needed

Nginx reads static files from disk on every request (for `index.html`) or after
the cache duration expires (for hashed JS/CSS assets). Vite generates new
content-hashed filenames on each build (e.g. `index-BxQk3a1f.js`), and
`index.html` itself has `Cache-Control: no-cache`, so browsers always fetch
the latest `index.html` first, which then pulls in the correct new asset URLs.

### If you change npm dependencies

```bash
cd /opt/form-service/frontend
npm install
npm run build
```

---

## Updating the Backend

The backend runs as a systemd service called `wakeupbuzz`. After any change to
`main.py` or `requirements.txt`, you must restart the service.

### Code-only changes (main.py)

```bash
sudo systemctl restart wakeupbuzz
```

### Dependency changes (requirements.txt)

```bash
cd /opt/form-service/backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl restart wakeupbuzz
```

### Verify the service came back up

```bash
sudo systemctl status wakeupbuzz
```

Look for `Active: active (running)`. Check logs if it fails:

```bash
sudo journalctl -u wakeupbuzz -n 50
```

### Environment variables (.env)

Variables live in `/opt/form-service/backend/.env`. After editing them,
restart the service:

```bash
sudo systemctl restart wakeupbuzz
```

---

## Updating Nginx Config

The active config is `/etc/nginx/sites-available/wakeupbuzz`.

After editing:

```bash
sudo nginx -t                      # test — must say "syntax is ok"
sudo systemctl reload nginx        # zero-downtime config reload
```

`reload` (not `restart`) is preferred — it applies the new config without
dropping active connections.

---

## SSL Certificates

Certbot is configured to auto-renew. The certificate is valid until
**May 24, 2026** and will renew automatically ~30 days before expiry via a
systemd timer or cron job.

To manually trigger a renewal (e.g. to test):

```bash
sudo certbot renew --dry-run
```

To force renew immediately:

```bash
sudo certbot renew --force-renewal
```

Certbot uses the `nginx` authenticator and installer, so it will update the
nginx config and reload nginx automatically.

---

## Typical Update Workflows

### "I changed the form UI (frontend only)"

```bash
cd /opt/form-service/frontend
npm run build
# Done. No restarts needed.
```

### "I changed the API/backend logic (backend only)"

```bash
sudo systemctl restart wakeupbuzz
sudo systemctl status wakeupbuzz
```

### "I changed both frontend and backend"

```bash
cd /opt/form-service/frontend
npm run build
sudo systemctl restart wakeupbuzz
sudo systemctl status wakeupbuzz
```

### "I pulled new code from git"

```bash
cd /opt/form-service
git pull

# Rebuild frontend if frontend/ changed:
cd frontend && npm install && npm run build && cd ..

# Reinstall backend deps if requirements.txt changed:
cd backend && source venv/bin/activate && pip install -r requirements.txt && deactivate && cd ..

# Restart backend:
sudo systemctl restart wakeupbuzz
```

---

## Service & File Reference

| Thing                  | Location / Command                                    |
|------------------------|-------------------------------------------------------|
| Systemd service        | `/etc/systemd/system/wakeupbuzz.service`             |
| Nginx site config      | `/etc/nginx/sites-available/wakeupbuzz`              |
| Frontend source        | `/opt/form-service/frontend/src/`                    |
| Frontend build output  | `/opt/form-service/frontend/dist/`                   |
| Backend app            | `/opt/form-service/backend/main.py`                  |
| Backend venv           | `/opt/form-service/backend/venv/`                    |
| Backend env vars       | `/opt/form-service/backend/.env`                     |
| SQLite database        | `/opt/form-service/backend/survey.db`                |
| SSL certificate        | `/etc/letsencrypt/live/thewakeupservice.buzz/`       |
| Service logs           | `sudo journalctl -u wakeupbuzz -f`                   |
| Nginx logs             | `/var/log/nginx/access.log`, `/var/log/nginx/error.log` |
| Restart backend        | `sudo systemctl restart wakeupbuzz`                  |
| Reload nginx           | `sudo systemctl reload nginx`                        |
