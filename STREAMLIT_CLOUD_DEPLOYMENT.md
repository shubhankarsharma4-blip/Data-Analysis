# Streamlit Cloud Deployment Guide

This guide covers deploying your E-commerce Analytics Dashboard to various cloud platforms.

## 🚀 Quick Overview

Your dashboard can be deployed to:
1. **Streamlit Cloud** (Recommended - Free & Easy) ⭐
2. **Heroku** (Free tier available)
3. **AWS** (EC2, Elastic Beanstalk, or App Runner)
4. **Azure** (App Service)
5. **Google Cloud Platform** (Cloud Run)
6. **DigitalOcean** (App Platform)
7. **Render** (Free tier available)

---

## Option 1: Streamlit Cloud (Recommended) ⭐

**Best for**: Quick deployment, free hosting, automatic updates

### Prerequisites
- GitHub account (free)
- Your code pushed to a GitHub repository
- Streamlit Cloud account (free at share.streamlit.io)

### Step-by-Step Deployment

#### 1. Prepare Your Repository

Ensure your project structure includes:

```
ecommerce-etl-project/
├── streamlit_app.py          # Main dashboard file
├── requirements.txt           # Dependencies
├── initialize_streamlit.py    # Optional: initialization script
├── Data/
│   └── Processed/            # CSV files (must be committed)
│       ├── dim_products.csv
│       ├── dim_users.csv
│       ├── fact_orders.csv
│       ├── fact_order_items.csv
│       ├── fact_reviews.csv
│       └── fact_events.csv
├── src/                      # Your ETL modules
└── README.md
```

#### 2. Update .gitignore (if needed)

Make sure `Data/Processed/*.csv` files are **NOT** ignored (they're needed for the dashboard):

```gitignore
# Keep Processed CSV files for Streamlit Cloud
!Data/Processed/*.csv
```

#### 3. Create `packages.txt` (Optional)

If you need system-level packages:

```txt
# packages.txt (leave empty if not needed)
```

#### 4. Deploy to Streamlit Cloud

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Go to Streamlit Cloud**:
   - Visit: https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"

3. **Configure Deployment**:
   - **Repository**: Select your `ecommerce-etl-project` repo
   - **Branch**: `main` (or your branch)
   - **Main file**: `streamlit_app.py`
   - **Python version**: 3.9+ (auto-detected)

4. **Click "Deploy"**

5. **Wait 2-3 minutes** for deployment

6. **Your dashboard is live!** 🎉
   - URL: `https://your-app-name.streamlit.app`

### Streamlit Cloud Configuration

Your `.streamlit/config.toml` is already configured:
- Port: 8501 (handled automatically)
- Headless: true (for cloud)
- Auto-reload on git push

### Important Notes for Streamlit Cloud

✅ **What Works**:
- Your dashboard will initialize database from CSV files automatically
- All visualizations and analytics will work
- Free tier includes unlimited apps
- Auto-deploys on every git push

⚠️ **Limitations**:
- SQLite database is ephemeral (resets on restart)
- File system is read-only except for `/tmp`
- 1GB RAM limit on free tier
- Apps sleep after 1 hour of inactivity (free tier)

💡 **Solution for Persistent Data**:
- Use external database (PostgreSQL, MySQL) via connection string
- Or rely on CSV files (which persist in git)

---

## Option 2: Heroku

**Best for**: More control, PostgreSQL database support

### Step 1: Install Heroku CLI

Download from: https://devcenter.heroku.com/articles/heroku-cli

### Step 2: Create Required Files

#### `Procfile`
```
web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

#### `setup.sh` (for initialization)
```bash
#!/bin/bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

#### `runtime.txt`
```
python-3.11.0
```

### Step 3: Deploy

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL (optional, for persistent database)
heroku addons:create heroku-postgresql:mini

# Deploy
git push heroku main

# Open app
heroku open
```

### Step 4: Configure Environment Variables

```bash
# If using PostgreSQL
heroku config:set DATABASE_URL=$(heroku config:get DATABASE_URL)

# Set other variables
heroku config:set STREAMLIT_SERVER_HEADLESS=true
```

---

## Option 3: AWS (Multiple Options)

### Option 3A: AWS App Runner (Easiest)

1. **Create `apprunner.yaml`**:
```yaml
version: 1.0
runtime: python3
build:
  commands:
    build:
      - pip install -r requirements.txt
run:
  runtime-version: 3.11
  command: streamlit run streamlit_app.py --server.port=8000 --server.address=0.0.0.0
  network:
    port: 8000
```

2. **Deploy via AWS Console**:
   - Go to AWS App Runner
   - Create service from source code
   - Connect GitHub repository
   - Deploy

### Option 3B: AWS EC2 (More Control)

1. **Launch EC2 Instance**:
   - Ubuntu 22.04 LTS
   - t2.micro (free tier) or t3.small

2. **SSH and Setup**:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3-pip -y

# Clone repository
git clone https://github.com/your-username/ecommerce-etl-project.git
cd ecommerce-etl-project

# Install dependencies
pip3 install -r requirements.txt

# Install Streamlit
pip3 install streamlit

# Run with nohup (background)
nohup streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 &
```

3. **Configure Security Group**:
   - Open port 8501 (or your chosen port)
   - Allow HTTP/HTTPS traffic

4. **Access Dashboard**:
   - `http://your-ec2-ip:8501`

### Option 3C: AWS Elastic Beanstalk

1. **Install EB CLI**:
```bash
pip install awsebcli
```

2. **Initialize**:
```bash
eb init -p python-3.11 streamlit-dashboard
eb create streamlit-env
```

3. **Create `.ebextensions/streamlit.config`**:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: streamlit_app.py
```

4. **Deploy**:
```bash
eb deploy
eb open
```

---

## Option 4: Azure App Service

### Step 1: Install Azure CLI

```bash
# Windows
winget install -e --id Microsoft.AzureCLI

# Or download from: https://aka.ms/installazurecliwindows
```

### Step 2: Create App Service

```bash
# Login
az login

# Create resource group
az group create --name streamlit-rg --location eastus

# Create app service plan
az appservice plan create --name streamlit-plan --resource-group streamlit-rg --sku FREE

# Create web app
az webapp create --resource-group streamlit-rg --plan streamlit-plan --name your-app-name --runtime "PYTHON|3.11"

# Deploy from GitHub
az webapp deployment source config --name your-app-name --resource-group streamlit-rg --repo-url https://github.com/your-username/ecommerce-etl-project --branch main --manual-integration
```

### Step 3: Configure Startup Command

In Azure Portal → Configuration → General Settings:

**Startup Command**:
```bash
python -m streamlit run streamlit_app.py --server.port=8000 --server.address=0.0.0.0
```

---

## Option 5: Google Cloud Platform (Cloud Run)

### Step 1: Create `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8080", "--server.address=0.0.0.0"]
```

### Step 2: Deploy

```bash
# Install gcloud CLI
# Download from: https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/streamlit-dashboard
gcloud run deploy streamlit-dashboard --image gcr.io/YOUR_PROJECT_ID/streamlit-dashboard --platform managed --region us-central1 --allow-unauthenticated
```

---

## Option 6: Render

**Best for**: Simple deployment, free tier

### Step 1: Connect GitHub

1. Go to: https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"

### Step 2: Configure

- **Repository**: Select your repo
- **Name**: `streamlit-dashboard`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`

### Step 3: Deploy

Click "Create Web Service" - Render will auto-deploy!

---

## Option 7: DigitalOcean App Platform

### Step 1: Create `app.yaml`

```yaml
name: streamlit-dashboard
services:
- name: web
  github:
    repo: your-username/ecommerce-etl-project
    branch: main
  run_command: streamlit run streamlit_app.py --server.port=8080 --server.address=0.0.0.0
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 8080
```

### Step 2: Deploy

1. Go to DigitalOcean App Platform
2. Create app from GitHub
3. Select repository
4. Deploy

---

## 🔧 Pre-Deployment Checklist

Before deploying, ensure:

- [ ] **Dependencies**: All packages in `requirements.txt`
- [ ] **Data Files**: CSV files in `Data/Processed/` are committed (or use external DB)
- [ ] **Database**: Decide on SQLite (ephemeral) or external DB (PostgreSQL/MySQL)
- [ ] **Secrets**: No API keys or passwords in code (use environment variables)
- [ ] **Port Configuration**: App listens on `0.0.0.0` (not `127.0.0.1`)
- [ ] **File Paths**: Use relative paths (not absolute Windows paths)
- [ ] **Error Handling**: Dashboard handles missing data gracefully

---

## 📝 Updating Your Code for Cloud Deployment

### 1. Update Database Path (if needed)

Your `streamlit_app.py` already uses relative paths:
```python
db_path = Path(__file__).parent / 'ecommerce.db'  # ✅ Good
```

### 2. Handle Port Dynamically

For platforms that set `$PORT`:
```python
import os
port = int(os.environ.get('PORT', 8501))
```

### 3. Use Environment Variables for Secrets

```python
import os
database_url = os.environ.get('DATABASE_URL', 'sqlite:///ecommerce.db')
```

---

## 🗄️ Database Options for Cloud

### Option A: SQLite (Simple, Ephemeral)
- ✅ Works out of the box
- ❌ Data resets on restart (Streamlit Cloud)
- ✅ Good for demos/prototypes

### Option B: PostgreSQL (Persistent, Recommended)
- ✅ Data persists
- ✅ Better for production
- ✅ Free tiers available (Heroku, Render, Supabase)

**Update `streamlit_app.py`**:
```python
import os
from sqlalchemy import create_engine

# Use environment variable or default to SQLite
database_url = os.environ.get('DATABASE_URL', 'sqlite:///ecommerce.db')
# PostgreSQL format: postgresql://user:pass@host:5432/dbname

engine = create_engine(database_url)
```

---

## 🚨 Common Issues & Solutions

### Issue: "Module not found"
**Solution**: Ensure all dependencies in `requirements.txt`

### Issue: "Port already in use"
**Solution**: Use `$PORT` environment variable or `0.0.0.0`

### Issue: "Database locked"
**Solution**: Use PostgreSQL instead of SQLite for production

### Issue: "File not found"
**Solution**: Use relative paths, ensure CSV files are committed to git

### Issue: "App sleeps after inactivity"
**Solution**: 
- Use paid tier (Streamlit Cloud)
- Or use other platforms (Render, Heroku)

---

## 📊 Comparison Table

| Platform | Free Tier | Ease | Database | Best For |
|----------|-----------|------|----------|----------|
| **Streamlit Cloud** | ✅ Yes | ⭐⭐⭐⭐⭐ | SQLite/External | Quick demos |
| **Render** | ✅ Yes | ⭐⭐⭐⭐ | PostgreSQL | Small projects |
| **Heroku** | ⚠️ Limited | ⭐⭐⭐ | PostgreSQL | Medium projects |
| **AWS** | ⚠️ Limited | ⭐⭐ | Any | Enterprise |
| **Azure** | ⚠️ Limited | ⭐⭐⭐ | Any | Enterprise |
| **GCP** | ⚠️ Limited | ⭐⭐ | Any | Enterprise |
| **DigitalOcean** | ❌ No | ⭐⭐⭐ | PostgreSQL | Production |

---

## 🎯 Recommended Approach

**For Quick Start**: Use **Streamlit Cloud** (5 minutes to deploy)

**For Production**: Use **Render** or **Heroku** with PostgreSQL

**For Enterprise**: Use **AWS App Runner** or **Azure App Service**

---

## 📚 Additional Resources

- Streamlit Cloud Docs: https://docs.streamlit.io/streamlit-community-cloud
- Heroku Python Guide: https://devcenter.heroku.com/articles/getting-started-with-python
- AWS App Runner: https://aws.amazon.com/apprunner/
- Render Docs: https://render.com/docs

---

## ✅ Next Steps

1. **Choose your platform** (Streamlit Cloud recommended for first-time)
2. **Push code to GitHub** (if not already)
3. **Follow platform-specific steps** above
4. **Test your deployed dashboard**
5. **Share the URL!** 🎉

---

**Need help?** Check the logs in your platform's dashboard or review error messages in the browser console.

