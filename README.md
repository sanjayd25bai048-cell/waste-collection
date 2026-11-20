# EcoTrack — Waste Collection & Recycling Operations

A full-stack project for registering waste pickup requests, assigning collection teams, recording collected weights, tracking sorting/recycling destinations and reporting completion rates.

## Technology
- Frontend: React, Vite, Recharts, Lucide icons
- Backend: Python Flask, Flask-SQLAlchemy, Flask-CORS
- Database: SQLite (created automatically)

## Features
- Role switcher for Resident, Collection Worker, Route Supervisor and Recycling Manager (demo role-based workflow)
- Resident pickup request form with waste categories, address, preferred date and contact details
- Request search, status filters and detail view
- Supervisor team/worker assignment
- Worker status and collected-weight updates
- Recycling sorting category and destination recording
- Dashboard KPIs, collection progress, category charts and destination summaries
- CSV report export
- Demo records seeded automatically on first backend start

## Run locally
You need Python 3.10+ and Node.js 18+.

### 1. Start backend
Open a terminal in `backend`:

```bash
python -m venv venv
# Windows
venv\\Scripts\\activate
# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
Backend: http://localhost:5000 (health check: http://localhost:5000/api/health)

### 2. Start frontend
Open another terminal in `frontend`:

```bash
npm install
npm run dev
```
Open the URL printed by Vite (usually http://localhost:5173).

## Important notes
- Keep the backend terminal running while using the frontend.
- The SQLite database file `backend/waste_ops.db` is generated on first run and is not required in the ZIP.
- Use the role selector in the top-right to preview each role's workflow. This is a classroom/demo role switcher, not production authentication. Add login, password hashing and server-side authorization before deploying publicly.
- API base URL is configured in `frontend/src/main.jsx` as `http://localhost:5000/api`.

## API overview
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | API health |
| GET | `/api/pickups` | List/filter pickup requests |
| POST | `/api/pickups` | Create pickup request |
| GET | `/api/pickups/<id>` | Get request details |
| PATCH | `/api/pickups/<id>` | Update assignment, collection and recycling fields |
| DELETE | `/api/pickups/<id>` | Delete request |
| GET | `/api/dashboard` | Dashboard and report aggregates |
| GET | `/api/teams` | Available collection teams |
