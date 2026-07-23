# Student Details System (FastAPI + Railway)

Same structure/pattern as your Event Registration project, adapted for
student enrollment details.

Files:
- `main.py` — FastAPI app: CRUD routes for students
- `database.py` — SQLAlchemy models (SQLite locally, Postgres on Railway)
- `requirements.txt`
- `Procfile` — tells Railway how to start the app
- `index.html` — the enrollment form (host this on GitHub Pages)

## Local run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Visit http://localhost:8000/ to confirm it's running, and
http://localhost:8000/docs for interactive API docs.

## Deploy to Railway

1. Push these files to a GitHub repo.
2. On Railway: New Project → Deploy from GitHub repo.
3. Add a Postgres database (Railway plugin) — `DATABASE_URL` is injected
   automatically.
4. (Optional) Set `FRONTEND_ORIGIN` to your GitHub Pages URL, e.g.
   `https://dharumin.github.io`, to lock down CORS instead of allowing `*`.
5. Once deployed, copy your Railway URL (e.g.
   `https://your-app.up.railway.app`) into `API_BASE` inside `index.html`.

## Routes

- `GET /` — health check
- `GET /students` — list all students
- `GET /students/{id}` — get one student
- `POST /students` — create a student
- `PUT /students/{id}` — update a student
- `DELETE /students/{id}` — delete a student
