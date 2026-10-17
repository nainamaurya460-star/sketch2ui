# Sketch2UI Deployment & Containerization Guide

This guide details the step-by-step procedure for deploying the **Sketch2UI** application to production using a containerized FastAPI backend and a zero-configuration single-page application (SPA) frontend.

---

## Architecture Overview

```
┌──────────────────────────────┐                ┌──────────────────────────────┐
│       Frontend (SPA)         │   REST API     │       Backend (FastAPI)      │
│  Platform: Vercel / Netlify  │ ─────────────> │  Platform: Render / Railway  │
│  Framework: React 19 + Vite  │   (JSON/MIME)  │  Engine: YOLOv8n + OpenCV    │
│  Env: VITE_API_URL           │                │  Env: ALLOWED_ORIGINS, PORT  │
└──────────────────────────────┘                └──────────────────────────────┘
```

---

## Step 1: Deploying the Backend (Render / Railway / Hugging Face Spaces)

The backend is packaged with a multi-stage Dockerfile and a `Procfile` / `render.yaml` for zero-friction cloud deployment.

### Option A: Render (1-Click or Blueprint)

1. **Connect Repository**: Go to [Render Dashboard](https://dashboard.render.com/) and create a new **Web Service** or use **Blueprints** pointing to `render.yaml`.
2. **Configuration Settings**:
   - **Environment**: `Docker` (or `Python 3.11`)
   - **Build Command** (if Python): `pip install -r requirements.txt`
   - **Start Command** (if Python): `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Docker Context**: Repository root (`.`)
   - **Dockerfile Path**: `./Dockerfile`
3. **Environment Variables**:
   | Variable | Value | Description |
   |---|---|---|
   | `PORT` | `8000` (auto-assigned by Render) | Listening port for Uvicorn |
   | `ALLOWED_ORIGINS` | `https://your-frontend.vercel.app,http://localhost:5173` | Comma-delimited list of allowed CORS origins |
4. **Health Check Path**: `/` (returns HTTP 200 `{"message": "Welcome to ASketch2UI Backend Engine!"}`)

### Option B: Railway

1. **Deploy from GitHub**: Connect your GitHub repository on [Railway](https://railway.app/).
2. Railway detects the `Dockerfile` automatically.
3. Add the following **Variables** in Railway dashboard:
   - `PORT`: `8000`
   - `ALLOWED_ORIGINS`: `https://your-frontend.vercel.app,http://localhost:5173`
4. The service will build the container, install system dependencies (`libgl1`, `libglib2.0-0`), package YOLOv8 weights (`app/models/best.pt`), and start `uvicorn`.

### Option C: Hugging Face Spaces

1. Create a new Space on [Hugging Face Spaces](https://huggingface.co/spaces).
2. Select **Docker** SDK with a blank template.
3. Push the repository to your Space. The Space uses the root `Dockerfile` and exposes port `8000` (or `7860` if mapped via `PORT`).
4. Set Space Secret `ALLOWED_ORIGINS` to your frontend production URL.

---

## Step 2: Deploying the Frontend (Vercel)

The frontend is an optimized React 19 + Tailwind CSS single-page application built with Vite.

1. **Import Project**: Navigate to [Vercel Dashboard](https://vercel.com/new) and import the `sketch2ui` repository.
2. **Project Settings**:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`
3. **Environment Variables**:
   | Variable | Value | Description |
   |---|---|---|
   | `VITE_API_URL` | `https://sketch2ui-backend.onrender.com` | Base URL of your deployed backend without trailing slash |
4. **SPA Route Handling**: Handled automatically via `frontend/vercel.json`:
   ```json
   {
     "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
   }
   ```
5. Click **Deploy**. Vercel will build and serve your SPA globally.

---

## Step 3: Verification & Live Healthchecks

Once both backend and frontend are deployed, verify system connectivity and inference end-to-end:

### 1. Backend Live Health Check
Send a GET request to the root endpoint:
```bash
curl -s https://sketch2ui-backend.onrender.com/
```
Expected response:
```json
{"message":"Welcome to ASketch2UI Backend Engine!"}
```

### 2. CORS Verification
Send a preflight OPTIONS request:
```bash
curl -I -X OPTIONS https://sketch2ui-backend.onrender.com/api/v1/sketch/predict \
  -H "Origin: https://your-frontend.vercel.app" \
  -H "Access-Control-Request-Method: POST"
```
Expected response headers:
```http
HTTP/1.1 200 OK
access-control-allow-origin: https://your-frontend.vercel.app
access-control-allow-methods: *
access-control-allow-headers: *
```

### 3. End-to-End Sketch Conversion
1. Open your deployed frontend URL: `https://your-frontend.vercel.app`
2. Navigate to **Studio Workspace**.
3. Upload a wireframe image (e.g., from `test_images/sketches.png`) or use the built-in webcam capture tool.
4. Verify that:
   - Upload succeeds without CORS blocks.
   - YOLOv8 inference returns detected UI components (`Button`, `Input`, `Card`, etc.).
   - The interactive React preview renders and the Tailwind JSX code is synthesized.

---

## Local Container Testing

To test the container locally before pushing to production:

```bash
# 1. Build the production Docker image
docker build -t sketch2ui-backend .

# 2. Run the container locally
docker run -p 8000:8000 -e ALLOWED_ORIGINS="http://localhost:5173,http://localhost:3000" sketch2ui-backend

# 3. Test the container healthcheck
curl http://localhost:8000/
```
