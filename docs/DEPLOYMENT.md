# SAGE Deployment Guide

Complete guide for deploying SAGE to Fly.io.

## Prerequisites

1. **Fly.io CLI installed**
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex

   # Mac/Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Fly.io account** - Sign up at https://fly.io

3. **API Keys ready:**
   - `PINECONE_API_KEY` - From https://app.pinecone.io
   - `ANTHROPIC_API_KEY` - From https://console.anthropic.com
   - `VOYAGE_API_KEY` - From https://dash.voyageai.com

4. **Pinecone index created:** `sage-guides` with 1024 dimensions (voyage-2)

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  sage-web       │────▶│  sage-api       │────▶│  Pinecone       │
│  (Next.js)      │     │  (FastAPI)      │     │  (Vector DB)    │
│  fly.dev        │     │  fly.dev        │     │  Cloud          │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  Claude API     │
                        │  (Anthropic)    │
                        └─────────────────┘
```

## Step 1: Authenticate

```bash
fly auth login
```

## Step 2: Create Apps (First Time Only)

```bash
# Backend
cd backend
fly apps create sage-api

# Frontend
cd ../frontend
fly apps create sage-web
```

## Step 3: Set Secrets (Backend)

**Required secrets** (these are NOT in fly.toml for security):

```bash
cd backend
fly secrets set \
  PINECONE_API_KEY="your-pinecone-key" \
  ANTHROPIC_API_KEY="your-anthropic-key" \
  VOYAGE_API_KEY="your-voyage-key"
```

**Optional** (if using Fly Postgres):
```bash
fly secrets set DATABASE_URL="postgres://user:pass@host:5432/db"
```

## Step 4: Deploy Backend

```bash
cd backend
fly deploy
```

**Verify deployment:**
```bash
# Check status
fly status

# Check logs
fly logs

# Test health endpoint
curl https://sage-api.fly.dev/api/health
```

Expected response:
```json
{"status": "ok", "version": "0.1.0"}
```

## Step 5: Deploy Frontend

```bash
cd frontend
fly deploy
```

**Verify deployment:**
```bash
fly status
fly logs
```

Visit https://sage-web.fly.dev to confirm the app is running.

## Step 6: Verify End-to-End

1. Go to https://sage-web.fly.dev
2. Click "Ask the Guide"
3. Ask: "What is the minimum credit score for HomeReady?"
4. Should get a response with citations from the indexed guides

## Troubleshooting

### CORS Errors
If you see CORS errors in browser console:
- Check that `https://sage-web.fly.dev` is in `backend/app/config.py` CORS list
- Redeploy backend: `cd backend && fly deploy`

### 500 Errors on API
```bash
cd backend
fly logs --app sage-api
```
Common causes:
- Missing API keys (check `fly secrets list`)
- Pinecone index not found

### App Not Starting
```bash
fly status
fly logs
```
Check for:
- Port mismatch (backend: 8000, frontend: 3000)
- Memory issues (upgrade VM if needed)

### Pinecone Empty
If RAG returns no results, the index may be empty. Run ingestion locally:
```bash
cd scripts
python ingest_guides.py
```

## Environment Variables Reference

### Backend (fly.toml [env])
| Variable | Value | Description |
|----------|-------|-------------|
| APP_NAME | SAGE API | Application name |
| DEBUG | false | Disable debug mode |
| ENABLE_RAG_CHAT | true | Enable RAG chat feature |
| ENABLE_RAG_ELIGIBILITY | true | Enable RAG eligibility |
| ENABLE_FIX_FINDER | true | Enable Fix Finder Agent |
| PINECONE_INDEX_NAME | sage-guides | Pinecone index name |

### Backend (secrets - set via CLI)
| Secret | Required | Description |
|--------|----------|-------------|
| PINECONE_API_KEY | Yes | Pinecone API key |
| ANTHROPIC_API_KEY | Yes | Claude API key |
| VOYAGE_API_KEY | Yes | Voyage AI embeddings key |
| DATABASE_URL | No | PostgreSQL URL (optional) |

### Frontend (fly.toml [env])
| Variable | Value | Description |
|----------|-------|-------------|
| NEXT_PUBLIC_API_URL | https://sage-api.fly.dev/api | Backend API URL |

## Scaling

### Upgrade VM Resources
```bash
# Backend
fly scale memory 1024 --app sage-api

# Frontend
fly scale memory 1024 --app sage-web
```

### Keep Warm (Prevent Cold Starts)
```bash
# Keep at least 1 machine running
fly scale count 1 --app sage-api
```

## Useful Commands

```bash
# View app info
fly info

# SSH into container
fly ssh console

# View secrets
fly secrets list

# Delete a secret
fly secrets unset SECRET_NAME

# View deployment history
fly releases

# Rollback to previous release
fly releases rollback
```

## Cost Estimate

With auto-scaling to zero:
- **Idle:** ~$0/month (scales to zero)
- **Light usage:** ~$5-10/month
- **Demo day:** A few cents

Fly.io charges for:
- Compute time (VM running)
- Outbound bandwidth
- Persistent volumes (if using Postgres)

## URLs

| Service | URL |
|---------|-----|
| Frontend | https://sage-web.fly.dev |
| Backend API | https://sage-api.fly.dev/api |
| API Docs | https://sage-api.fly.dev/api/docs |
| Health Check | https://sage-api.fly.dev/api/health |
