# ☁️ Alaska's Cloud Runner — Google Cloud Run Deployment Lab

**Author:** Alaska Tengli  
**Course:** MLOps | Lab Assignment 5  
**Date:** March 27 2026  

---

## 📌 Overview

This project demonstrates deploying a containerized Python Flask application to **Google Cloud Run** — a fully managed serverless platform that automatically scales stateless containers. The application serves a styled HTML dashboard, a JSON API endpoint, a health check, and a dynamic greeting route.

### Modifications from the Original Lab

This project builds upon the [Cloud Runner Beginner Lab](https://github.com/raminmohammadi/MLOps/tree/main/Labs/GCP_Labs/Cloud_Runner_Labs/Begineer_Lab) with the following custom changes:

| Feature | Original Lab | This Project |
|---|---|---|
| **Routes** | Single `/` returning plain text | 4 routes: `/`, `/api/info`, `/health`, `/greet/<name>` |
| **Home Page** | Plain "Hello, World!" string | Styled HTML dashboard with gradient UI and server info |
| **API Endpoint** | None | `/api/info` returns JSON metadata (version, hostname, timestamp) |
| **Health Check** | None | `/health` endpoint for monitoring and load balancer integration |
| **Dynamic Route** | None | `/greet/<name>` for parameterized greeting |
| **Python Version** | 3.8-slim | 3.11-slim |
| **WSGI Server** | Flask dev server (`python app.py`) | Production-grade **Gunicorn** with 2 workers |
| **Docker Best Practices** | Basic Dockerfile | `.dockerignore`, layer caching, env variables, `--no-cache-dir` |
| **Port Config** | Hardcoded `8080` | Reads from `PORT` environment variable (Cloud Run compatible) |

---

## 🏗️ Architecture

```
User Request
     │
     ▼
┌──────────────┐
│ Google Cloud  │
│    Run        │
│  (Serverless) │
└──────┬───────┘
       │  Auto-scales 0 → N instances
       ▼
┌──────────────┐
│   Docker      │
│  Container    │
│  (Gunicorn)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Flask App    │
│  - /          │
│  - /api/info  │
│  - /health    │
│  - /greet/:n  │
└──────────────┘
```

---

## 📁 Project Structure

```
cloud-runner-lab/
├── app.py              # Flask application with 4 routes
├── Dockerfile          # Container configuration (Python 3.11 + Gunicorn)
├── requirements.txt    # Python dependencies
├── .dockerignore       # Files excluded from Docker build
└── README.md           # This file
```

---

## 🚀 Prerequisites

Before starting, make sure you have:

- [Google Cloud Account](https://cloud.google.com/) with billing enabled
- [Google Cloud SDK (`gcloud`)](https://cloud.google.com/sdk/docs/install) installed
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Python 3.11+ (for local testing)
- A GitHub account (for submission)

---

## 📝 Step-by-Step Deployment Guide

### Step 1: Set Up Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown at the top → **New Project**.
3. Name it something like `cloud-runner-lab-alaska` and click **Create**.
4. Make sure the project is selected in the dropdown.
5. Enable the required APIs by running in **Cloud Shell** or your terminal:

```bash
gcloud config set project YOUR_PROJECT_ID

gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

> 💡 Replace `YOUR_PROJECT_ID` with your actual project ID (e.g., `cloud-runner-lab-alaska`).

---

### Step 2: Clone This Repository

```bash
git clone https://github.com/tengli-alaska/cloud-runner-lab.git
cd cloud-runner-lab
```

---

### Step 3: Test Locally (Optional but Recommended)

#### Option A — Run with Python directly:

```bash
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:8080` in your browser.

#### Option B — Run with Docker locally:

```bash
docker build -t cloud-runner-app .
docker run -p 8080:8080 cloud-runner-app
```

Visit `http://localhost:8080` to verify.

---

### Step 4: Build and Push Docker Image to Google Container Registry

1. **Authenticate Docker with GCR:**

```bash
gcloud auth configure-docker
```

2. **Build the image:**

```bash
docker build -t gcr.io/YOUR_PROJECT_ID/cloud-runner-app .
```

3. **Push to Container Registry:**

```bash
docker push gcr.io/YOUR_PROJECT_ID/cloud-runner-app
```

> ⏳ The push may take 1–2 minutes depending on your internet speed.

---

### Step 5: Deploy to Google Cloud Run

#### Option A — Using the `gcloud` CLI (Recommended):

```bash
gcloud run deploy cloud-runner-app \
  --image gcr.io/YOUR_PROJECT_ID/cloud-runner-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 256Mi \
  --min-instances 0 \
  --max-instances 3
```

#### Option B — Using the Google Cloud Console:

1. Go to [Cloud Run](https://console.cloud.google.com/run) in the Console.
2. Click **Create Service**.
3. Select **Deploy one revision from an existing container image**.
4. Browse and select `gcr.io/YOUR_PROJECT_ID/cloud-runner-app`.
5. Set **Region** to `us-central1`.
6. Under **Authentication**, select **Allow unauthenticated invocations**.
7. Click **Create**.

After deployment, you'll get a URL like:
```
https://cloud-runner-app-xxxxx-uc.a.run.app
```

---

### Step 6: Test the Deployed Application

Open the provided URL and test all endpoints:

| Endpoint | URL | Expected Response |
|---|---|---|
| Home Dashboard | `https://YOUR_URL/` | Styled HTML page with server info |
| API Info (JSON) | `https://YOUR_URL/api/info` | JSON with app metadata |
| Health Check | `https://YOUR_URL/health` | `{"status": "healthy", ...}` |
| Dynamic Greeting | `https://YOUR_URL/greet/Alaska` | Personalized greeting JSON |

You can also test with `curl`:

```bash
# Test home page
curl https://YOUR_URL/

# Test JSON API
curl https://YOUR_URL/api/info

# Test health check
curl https://YOUR_URL/health

# Test dynamic greeting
curl https://YOUR_URL/greet/Alaska
```

---

### Step 7: Monitor the Service

1. Go to [Cloud Run Console](https://console.cloud.google.com/run).
2. Click on your `cloud-runner-app` service.
3. Explore the tabs:
   - **Metrics** — View request count, latency (ms), and container instance count.
   - **Logs** — See real-time application logs and request traces.
   - **Revisions** — View deployment history and traffic splitting.

#### Key Metrics to Observe:

- **Request Count**: How many requests hit your service.
- **Request Latency**: Response time (p50, p95, p99).
- **Container Instance Count**: How many instances Cloud Run spun up (auto-scaling in action).
- **Memory Utilization**: Memory used by each container instance.

---

### Step 8: Auto-Scaling Behavior

Cloud Run automatically scales your service:

- **Scale to Zero**: If no traffic comes in, Cloud Run shuts down all instances (you pay nothing).
- **Scale Up**: When requests arrive, Cloud Run spins up new instances automatically.
- **Concurrency**: Each instance can handle up to 80 concurrent requests by default.

The deployment command above sets:
- `--min-instances 0` → Scales to zero when idle.
- `--max-instances 3` → Caps at 3 instances to control costs.

---

## 🧹 Cleanup (Important!)

To avoid unexpected charges, delete the resources after the lab:

```bash
# Delete the Cloud Run service
gcloud run services delete cloud-runner-app --region us-central1

# Delete the container image
gcloud container images delete gcr.io/YOUR_PROJECT_ID/cloud-runner-app --force-delete-tags

# (Optional) Delete the entire project
gcloud projects delete YOUR_PROJECT_ID
```

---

## 📸 Screenshots

> Add screenshots of the following for your submission:
> 1. The home page (`/`) rendered in browser
> 2. The `/api/info` JSON response
> 3. Cloud Run Console showing the deployed service
> 4. Metrics tab showing request count and latency

---

## 🔧 Technologies Used

- **Python 3.11** — Programming language
- **Flask 3.0** — Lightweight web framework
- **Gunicorn** — Production WSGI HTTP server
- **Docker** — Containerization
- **Google Cloud Run** — Serverless container platform
- **Google Container Registry** — Docker image hosting

---

## 📚 References

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Original Lab Repository](https://github.com/raminmohammadi/MLOps/tree/main/Labs/GCP_Labs/Cloud_Runner_Labs/Begineer_Lab)

---

## 📄 License

This project is for educational purposes as part of the MLOps course at Northeastern University.