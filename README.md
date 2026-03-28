# ☁️ Alaska's Cloud Runner — Google Cloud Run Deployment Lab

**Author:** Alaska Tengli  
**Course:** MLOps | Lab Assignment 5  
**Date:** March 27, 2026  
**Live URL:** [https://cloud-runner-app-359520805860.us-central1.run.app](https://cloud-runner-app-359520805860.us-central1.run.app)

---

## 📌 Overview

This project demonstrates deploying a containerized Python Flask application to **Google Cloud Run** — a fully managed serverless platform that automatically scales stateless containers. The application serves a styled HTML dashboard, a JSON API endpoint, a health check, and a dynamic greeting route.

This lab is based on the [Cloud Runner Beginner Lab](https://github.com/raminmohammadi/MLOps/tree/main/Labs/GCP_Labs/Cloud_Runner_Labs/Begineer_Lab) from the MLOps course repository, with significant custom modifications detailed below.

---

## ✅ Modifications from the Original Lab

| Feature | Original Lab | This Project |
|---|---|---|
| **Routes** | Single `/` returning plain text | 4 routes: `/`, `/api/info`, `/health`, `/greet/<name>` |
| **Home Page** | Plain "Hello, World!" string | Styled HTML dashboard with gradient UI, glassmorphism card design, and live server info |
| **API Endpoint** | None | `/api/info` returns JSON metadata (app version, hostname, Python version, timestamp, environment) |
| **Health Check** | None | `/health` endpoint for monitoring and load balancer integration |
| **Dynamic Route** | None | `/greet/<name>` for parameterized greeting responses |
| **Python Version** | 3.8-slim | **3.11-slim** (upgraded) |
| **WSGI Server** | Flask dev server (`python app.py`) | Production-grade **Gunicorn** with 2 workers |
| **Docker Best Practices** | Basic Dockerfile | `.dockerignore`, layer caching with separate `requirements.txt` copy, env variables, `--no-cache-dir` pip flag |
| **Port Config** | Hardcoded `8080` | Reads from `PORT` environment variable (Cloud Run compatible) |
| **Dependencies** | Only Flask | Flask 3.0 + Gunicorn 21.2 via `requirements.txt` |

---

## 🏗️ Architecture

```
User Request (Browser / curl)
     │
     ▼
┌─────────────────────────┐
│   Google Cloud Run       │
│   (Serverless Platform)  │
│   Region: us-central1   │
└───────────┬─────────────┘
            │  Auto-scales 0 → 3 instances
            ▼
┌─────────────────────────┐
│   Docker Container       │
│   Python 3.11-slim       │
│   Gunicorn (2 workers)   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   Flask Application      │
│                          │
│   GET /          → HTML  │
│   GET /api/info  → JSON  │
│   GET /health    → JSON  │
│   GET /greet/:n  → JSON  │
└─────────────────────────┘
```

---

## 📁 Project Structure

```
cloud-runner-lab/
├── app.py              # Flask application with 4 routes and styled HTML template
├── Dockerfile          # Multi-step container config (Python 3.11 + Gunicorn)
├── requirements.txt    # Python dependencies (Flask 3.0, Gunicorn 21.2)
├── .dockerignore       # Files excluded from Docker build context
└── README.md           # Project documentation (this file)
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
3. Name it (e.g., `cloud-runner-lab-alaska`) and click **Create**.
4. Make sure the new project is selected in the dropdown.

#### What I did:

```bash
# Created the project
gcloud projects create cloud-runner-lab-alaska

# Set it as the active project
gcloud config set project cloud-runner-lab-alaska

# Linked billing account
gcloud billing projects link cloud-runner-lab-alaska --billing-account=014951-5E5C98-A30739

# Enabled required APIs
gcloud services enable run.googleapis.com containerregistry.googleapis.com cloudbuild.googleapis.com
```

> 💡 You need billing enabled to use Cloud Run, Container Registry, and Cloud Build APIs. The free tier covers this lab easily.

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

Visit `http://localhost:8080` to verify all routes work.

---

### Step 4: Build and Push Docker Image to Google Container Registry

1. **Authenticate Docker with GCR:**

```bash
gcloud auth configure-docker
```

2. **Build the image:**

> ⚠️ **Important for Apple Silicon (M1/M2/M3) Macs:** You must specify `--platform linux/amd64` because Cloud Run requires x86 images, not ARM.

```bash
# For Apple Silicon Macs (M1/M2/M3):
docker build --platform linux/amd64 -t gcr.io/YOUR_PROJECT_ID/cloud-runner-app .

# For Intel Macs / Linux:
docker build -t gcr.io/YOUR_PROJECT_ID/cloud-runner-app .
```

#### What I did:

```bash
gcloud auth configure-docker

# First build without --platform flag failed on Cloud Run with:
# ERROR: Container manifest type 'application/vnd.oci.image.index.v1+json' must support amd64/linux
# Fixed by adding --platform linux/amd64:
docker build --platform linux/amd64 -t gcr.io/cloud-runner-lab-alaska/cloud-runner-app .
```

3. **Push to Container Registry:**

```bash
docker push gcr.io/YOUR_PROJECT_ID/cloud-runner-app
```

#### What I did:

```bash
docker push gcr.io/cloud-runner-lab-alaska/cloud-runner-app
```

> ⏳ The push takes 1–2 minutes depending on internet speed.

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

#### What I did:

```bash
gcloud run deploy cloud-runner-app \
  --image gcr.io/cloud-runner-lab-alaska/cloud-runner-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 256Mi \
  --min-instances 0 \
  --max-instances 3
```

Output:
```
Service [cloud-runner-app] revision [cloud-runner-app-00002-s6j] has been deployed and is serving 100 percent of traffic.
Service URL: https://cloud-runner-app-359520805860.us-central1.run.app
```

#### Option B — Using the Google Cloud Console:

1. Go to [Cloud Run](https://console.cloud.google.com/run) in the Console.
2. Click **Create Service**.
3. Select **Deploy one revision from an existing container image**.
4. Browse and select `gcr.io/YOUR_PROJECT_ID/cloud-runner-app`.
5. Set **Region** to `us-central1`.
6. Under **Authentication**, select **Allow unauthenticated invocations**.
7. Click **Create**.

---

### Step 6: Test the Deployed Application

Open the provided URL and test all endpoints:

| Endpoint | URL | Expected Response |
|---|---|---|
| Home Dashboard | `https://cloud-runner-app-359520805860.us-central1.run.app/` | Styled HTML page with server info |
| API Info (JSON) | `https://cloud-runner-app-359520805860.us-central1.run.app/api/info` | JSON with app metadata |
| Health Check | `https://cloud-runner-app-359520805860.us-central1.run.app/health` | `{"status": "healthy", ...}` |
| Dynamic Greeting | `https://cloud-runner-app-359520805860.us-central1.run.app/greet/Alaska` | Personalized greeting JSON |

You can also test with `curl`:

```bash
# Test home page
curl https://cloud-runner-app-359520805860.us-central1.run.app/

# Test JSON API
curl https://cloud-runner-app-359520805860.us-central1.run.app/api/info

# Test health check
curl https://cloud-runner-app-359520805860.us-central1.run.app/health

# Test dynamic greeting
curl https://cloud-runner-app-359520805860.us-central1.run.app/greet/Alaska
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

- **Request Count**: Total number of requests hitting the service.
- **Request Latency**: Response time percentiles (p50, p95, p99).
- **Container Instance Count**: Number of active instances (demonstrates auto-scaling).
- **Memory Utilization**: Memory consumed by each container instance.

---

### Step 8: Auto-Scaling Behavior

Cloud Run automatically scales your service:

- **Scale to Zero**: If no traffic arrives, Cloud Run shuts down all instances (zero cost).
- **Scale Up**: When requests arrive, Cloud Run spins up new instances automatically.
- **Concurrency**: Each instance handles up to 80 concurrent requests by default.

The deployment configuration sets:
- `--min-instances 0` → Scales to zero when idle (cost-efficient).
- `--max-instances 3` → Caps at 3 instances to control costs.
- `--memory 256Mi` → Each instance gets 256MB of memory.

---

## 🐛 Issues Encountered & Solutions

| Issue | Solution |
|---|---|
| `FAILED_PRECONDITION: Billing account not found` | Linked billing account to project using `gcloud billing projects link` |
| `Permission denied` on project | Was logged into wrong Google account. Fixed with `gcloud auth login tenglisuruchi51@gmail.com --force` |
| `Container manifest must support amd64/linux` | Building on Apple Silicon Mac produces ARM images. Fixed by adding `--platform linux/amd64` to `docker build` |

---

## 🧹 Cleanup (Important!)

To avoid unexpected charges after grading, delete the resources:

```bash
# Delete the Cloud Run service
gcloud run services delete cloud-runner-app --region us-central1

# Delete the container image
gcloud container images delete gcr.io/cloud-runner-lab-alaska/cloud-runner-app --force-delete-tags

# (Optional) Delete the entire project
gcloud projects delete cloud-runner-lab-alaska
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
- **Gunicorn 21.2** — Production WSGI HTTP server
- **Docker** — Containerization
- **Google Cloud Run** — Serverless container platform
- **Google Container Registry (GCR)** — Docker image hosting

---

## 📚 References

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Docker Documentation](https://docs.docker.com/)
- [Original Lab Repository](https://github.com/raminmohammadi/MLOps/tree/main/Labs/GCP_Labs/Cloud_Runner_Labs/Begineer_Lab)

---

## 📄 License

This project is for educational purposes as part of the MLOps course at Northeastern University.