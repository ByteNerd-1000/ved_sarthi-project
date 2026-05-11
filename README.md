# 🏥 Veda Sarthi – AI Health Assistant

A multilingual AI-powered healthcare chatbot with a FastAPI backend and static HTML/CSS/JS frontend.

## Tech Stack
- **Backend**: Python · FastAPI · SQLite · Groq LLM API
- **Frontend**: HTML · CSS · Vanilla JS (static site)
- **Deployment**: Render (backend) · Vercel (frontend)

---

## 🚀 Deployment

### Backend → Render
1. Push this repo to GitHub.
2. Go to [render.com](https://render.com) → **New** → **Web Service** → connect your repo.
3. Set **Root Directory** to `backend`.
4. Render will auto-detect `render.yaml`. Confirm:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. In **Environment Variables**, add:
   - `GROQ_API_KEY` = your Groq API key
6. Click **Deploy**. Copy your Render URL (e.g., `https://veda-sarthi-backend.onrender.com`).

### Frontend → Vercel
1. Open `frontend/script.js` and set `RENDER_BACKEND_URL` to your Render URL:
   ```js
   const RENDER_BACKEND_URL = 'https://veda-sarthi-backend.onrender.com';
   ```
2. Commit & push.
3. Go to [vercel.com](https://vercel.com) → **New Project** → import your repo.
4. Set **Root Directory** to `frontend`.
5. Click **Deploy**. Done ✅

### Post-deploy: Lock CORS (optional hardening)
In `backend/app/main.py`, replace `"*"` in `ALLOWED_ORIGINS` with your actual Vercel URL:
```python
"https://your-app.vercel.app",
```
Then remove the `"*"` entry and redeploy.

---

## 🖥️ Local Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # add your GROQ_API_KEY
uvicorn app.main:app --reload --port 8002
```

### Frontend
Open `frontend/index.html` in a browser, or use Live Server (VS Code).
Make sure `RENDER_BACKEND_URL` in `script.js` is empty (`''`) for local dev.

---

## 📁 Project Structure
```
.
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── routers/
│   │   └── services/
│   ├── requirements.txt
│   ├── render.yaml
│   └── .env.example
└── frontend/
    ├── index.html
    ├── styles.css
    ├── script.js
    └── vercel.json
```
