# Vignan AI Classroom Monitoring System

A Flask + YOLO + OpenCV classroom analytics project prepared for Vercel deployment.

## Architecture

- **Vercel:** Flask dashboard and REST API.
- **Database:** SQLite for local development; PostgreSQL for persistent production data.
- **AI worker:** Runs on a computer/server that can access physical USB/IP cameras.
- **Dashboard:** Polls the Flask API every 5 seconds.
- **Camera streams:** Optional browser-accessible stream URLs can be configured with `CAMERA_URL_1` ... `CAMERA_URL_25`.

> Important: a Vercel Function cannot directly access USB cameras attached to your laptop. Do not put a permanent `while True` camera loop in the Vercel Flask request handler. Run `worker/ai_worker.py` on the machine that has camera access and send metrics to Vercel.

## Project structure

```text
tara/
├── app.py
├── requirements.txt
├── pyproject.toml
├── vercel.json
├── .env.example
├── .gitignore
├── models/
│   └── yolo11n.pt
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   └── analytics.html
├── static/
│   ├── css/style.css
│   └── js/dashboard.js
├── services/
│   ├── analytics.py
│   ├── attendance.py
│   ├── behavior.py
│   ├── camera_registry.py
│   ├── database.py
│   └── detection.py
├── worker/
│   └── ai_worker.py
├── database/
│   ├── classroom.db
│   └── schema.sql
└── legacy/
    ├── dashboard-original.html
    └── analytics-original.html
```

## Local Windows setup

PowerShell:

```powershell
cd path\to\tara
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

Test:

```text
http://127.0.0.1:5000/
http://127.0.0.1:5000/analytics
http://127.0.0.1:5000/api/health
http://127.0.0.1:5000/api/dashboard
```

## Local AI camera worker

From the project root, with the same virtual environment:

```powershell
$env:VERCEL_API_URL="http://127.0.0.1:5000"
$env:WORKER_API_KEY="change-this-to-a-long-random-value"
python worker\ai_worker.py --camera 1 --source 0
```

For a second USB camera:

```powershell
python worker\ai_worker.py --camera 2 --source 1
```

The worker detects COCO `person` objects and sends counts/attention/activity to `/api/cameras/<id>/heartbeat`.

## GitHub

```powershell
git init
git add .
git commit -m "Prepare Vignan AI Classroom for Vercel"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

If `origin` already exists, skip the `git remote add origin` line.

## Vercel

Import the GitHub repository in Vercel. Vercel recognizes Flask applications and can deploy Flask with its Python runtime.

Recommended environment variables:

```text
WORKER_API_KEY=your-long-secret-key
DATABASE_URL=your-postgresql-connection-string
```

If you use only the local SQLite fallback, it is suitable for local testing, not persistent production storage.

Optional live stream variables:

```text
CAMERA_URL_1=https://your-camera-stream.example/stream
CAMERA_URL_2=https://your-camera-stream.example/stream
```

## Production camera setup

1. Put the AI worker on a machine that can access the cameras.
2. Give the worker the deployed Vercel URL using `VERCEL_API_URL`.
3. Give both Vercel and the worker the same `WORKER_API_KEY`.
4. Start one worker process per camera, or extend the worker to manage multiple cameras.
5. Configure browser-accessible stream URLs if you want the dashboard to display the actual camera feed.

Example:

```powershell
$env:VERCEL_API_URL="https://YOUR-PROJECT.vercel.app"
$env:WORKER_API_KEY="your-long-secret-key"
python worker\ai_worker.py --camera 1 --source 0
```

## Notes about Vercel

Vercel supports Flask through its Python runtime. The current project uses a minimal `vercel.json` because modern Flask deployments are zero-configuration. The continuous camera loop is deliberately outside the Vercel request handler.
