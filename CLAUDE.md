# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SAGE (Smart Agentic Guide Engine) is an AI-powered mortgage policy intelligence system that transforms Fannie Mae and Freddie Mac guidelines into an actionable platform. It monitors policy changes, reasons about loan scenarios, compares GSE products, and generates code updates for compliance.

**Status:** Phase 2 Infrastructure Complete - RAG chat and policy updates backend ready. Requires API keys to activate.

## Tech Stack

- **Frontend:** Next.js 16 + Tailwind CSS 4
- **Backend:** FastAPI (Python 3.11+)
- **Vector DB:** Pinecone (implemented, needs API key)
- **LLM:** Claude Sonnet 4.5 via Anthropic SDK (implemented, needs API key)
- **Database:** PostgreSQL via SQLAlchemy async (implemented, falls back to SQLite)
- **Embeddings:** Voyage AI voyage-2 (implemented, needs API key)

## Hosting (Fly.io)

- **Frontend:** Fly.io machine
- **Backend:** Fly.io machine
- **Database:** Fly Postgres

## Project Structure

```
sage/
├── frontend/                    # Next.js 16 application
│   ├── app/                     # App router pages
│   │   ├── page.tsx             # Landing page
│   │   ├── layout.tsx           # Root layout
│   │   ├── ask/page.tsx         # RAG chat interface
│   │   ├── changes/page.tsx     # Policy updates timeline
│   │   ├── code/page.tsx        # Code diffs view
│   │   └── check/page.tsx       # Loan eligibility checker
│   ├── components/              # React components
│   │   ├── TabNav.tsx           # Navigation tabs
│   │   ├── LoanForm.tsx         # Loan scenario input form
│   │   ├── EligibilityResult.tsx # Eligibility results display
│   │   ├── ChatInterface.tsx    # RAG chat component
│   │   ├── ChangeTimeline.tsx   # Policy updates timeline
│   │   └── CodeDiff.tsx         # Code diff viewer
│   └── lib/                     # Utilities
│       ├── api.ts               # API client
│       └── types.ts             # TypeScript interfaces
├── backend/                     # FastAPI application
│   └── app/
│       ├── main.py              # Application entry point with DB lifecycle
│       ├── config.py            # Settings and configuration
│       ├── routers/             # API endpoints
│       │   ├── eligibility.py   # POST /api/check-loan
│       │   ├── chat.py          # POST /api/chat (RAG-enabled)
│       │   └── changes.py       # GET /api/changes (DB-enabled)
│       ├── models/              # Pydantic models
│       │   ├── loan.py          # LoanScenario, EligibilityResult
│       │   ├── chat.py          # ChatMessage, ChatResponse
│       │   └── policy.py        # PolicyUpdate, CodeDiffResponse
│       ├── services/            # Business logic
│       │   ├── rules_engine.py  # 880-line eligibility rules engine
│       │   ├── pinecone_service.py   # Vector DB operations
│       │   ├── embedding_service.py  # Text embeddings
│       │   ├── rag_service.py        # RAG pipeline
│       │   └── scrapers/             # Policy update scrapers
│       │       ├── base_scraper.py
│       │       ├── fannie_mae_scraper.py
│       │       └── freddie_mac_scraper.py
│       └── db/                  # Database layer
│           ├── database.py      # Async SQLAlchemy connection
│           └── models.py        # ORM models (PolicyUpdate, etc.)
├── contracts/                   # API contracts
│   └── api_contracts.md         # Shared interfaces between frontend/backend
├── data/                        # Scraped guide content
│   └── scraped_guides/          # 17 guide files (~490K characters)
└── scripts/
    ├── scrape_guides.py         # Guide scraping script
    └── ingest_guides.py         # Embed guides into Pinecone
```

## Commands

### Frontend (from `frontend/`)
```bash
npm install          # Install dependencies
npm run dev          # Start development server
npm run build        # Production build
npm run lint         # Run ESLint
```

### Backend (from `backend/`)
```bash
pip install -r requirements.txt   # Install dependencies
uvicorn app.main:app --reload     # Start development server
pytest                            # Run tests
pytest tests/test_file.py -k "test_name"  # Run single test
```

### Data Ingestion (from `scripts/`)
```bash
python scrape_guides.py           # Scrape guide content from GSE websites
python ingest_guides.py           # Embed guides into Pinecone (requires VOYAGE_API_KEY, PINECONE_API_KEY)
```

### Environment Setup
```bash
# Copy example env file
cp backend/.env.example backend/.env

# Required API keys for Phase 2 features:
# - PINECONE_API_KEY: Vector storage for RAG
# - ANTHROPIC_API_KEY: Claude Sonnet 4.5 for chat responses
# - VOYAGE_API_KEY: Voyage AI voyage-2 for text embeddings
# - DATABASE_URL: PostgreSQL connection (optional, uses SQLite by default)
```

## Architecture

### Four Agentic Layers

1. **Change Detection Agent** - Monitors Fannie Mae Lender Letters and Freddie Mac Bulletins for policy changes
2. **Impact Analyst Agent** - Compares old vs new policy, identifies semantic shifts
3. **Code Generation Agent** - Drafts code updates showing how underwriting rules would need to change
4. **Scenario Reasoning Agent** - Analyzes loan eligibility for both GSEs, explains failures, suggests fixes

### Four Web App Tabs

1. **Ask the Guide** - RAG-powered Q&A with citations
2. **What Changed** - Timeline of detected policy updates
3. **Generated Updates** - Code diffs showing rule engine updates
4. **Check My Loan** - Scenario analyzer comparing HomeReady vs Home Possible eligibility

## MVP Scope

- **Products:** HomeReady (Fannie Mae) and Home Possible (Freddie Mac)
- **Key eligibility rules:** Max DTI (50%), Max LTV (97%), Min Credit (620/660), Income Limit (80% AMI), Occupancy, Property Types, Homeownership Education

## Phase 2 Implementation Status

### Completed ✅

**RAG Chat Infrastructure:**
- Pinecone vector DB service (`services/pinecone_service.py`)
- Voyage AI embedding service (`services/embedding_service.py`)
- RAG pipeline with Claude Sonnet 4.5 (`services/rag_service.py`)
- Guide ingestion script with rate limiting (`scripts/ingest_guides.py`)
- Chat router with RAG support (`routers/chat.py`)

**Policy Updates Infrastructure:**
- PostgreSQL database models (`db/models.py`)
- Async SQLAlchemy connection (`db/database.py`)
- Fannie Mae Lender Letters scraper
- Freddie Mac Bulletins scraper
- Changes router with DB queries (`routers/changes.py`)
- Background refresh endpoint (`POST /api/changes/refresh`)

**Code Generation Tab:**
- Output **JSON**, **YAML**, **TypeScript**, and Python formats ✅
- Makes it enterprise-ready (compatible with BRE like Drools, IBM ODM)

**Data Model:**
- `affected_rule_ids` array in `POLICY_UPDATES` table ✅
- Links policy changes to `ELIGIBILITY_RULES` table ✅

### Remaining Work

**To Activate Features:**
1. Set up Pinecone index (1024 dimensions for voyage-2) and add API key
2. Add Anthropic API key for Claude Sonnet 4.5
3. Add Voyage AI API key for embeddings
4. Run `python scripts/ingest_guides.py` to embed guide content (takes ~45min due to rate limits)
5. Optionally configure PostgreSQL (uses SQLite by default)

**Future Enhancements:**
- Fix Finder Agent (ReAct loop pattern for loan fix suggestions)
- AMI Income Limits lookup (currently hardcoded for demo)
- LangGraph agent orchestration

## Deployment (Fly.io)

### First-time setup
```bash
# Install Fly CLI
# Windows: iwr https://fly.io/install.ps1 -useb | iex
# Mac/Linux: curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Create apps (one-time)
cd backend && fly apps create sage-api
cd ../frontend && fly apps create sage-app
```

### Deploy
```bash
# Backend
cd backend && fly deploy

# Frontend (set API URL)
cd frontend && fly deploy --build-arg NEXT_PUBLIC_API_URL=https://sage-api.fly.dev/api
```

### URLs after deployment
- Frontend: https://sage-app.fly.dev
- Backend API: https://sage-api.fly.dev/api
- API Docs: https://sage-api.fly.dev/api/docs

## Design System: "The Modern Ledger"

A professional fintech aesthetic built for mortgage industry applications.

### Typography
- **Display font:** Fraunces (serif) - headings and titles
- **Body font:** Public Sans - readable body text
- **Monospace:** JetBrains Mono - numbers, code, data

### Color Palette
- **Paper:** `#F9F8F4` - warm off-white background
- **Sage green:** `#3A6B56` - primary brand color
- **Gold:** `#E0A82E` - accent/warning
- **Ink:** `#1C1917` to `#A8A29E` - text hierarchy
- **Fannie Mae:** `#00447C` - blue badge
- **Freddie Mac:** `#8B2332` - red badge

### Icons
- Phosphor Icons with consistent "thin" weight throughout
- Examples: ChatText, ClockCounterClockwise, Code, CheckCircle, Scales

### CSS Custom Properties
All design tokens defined in `frontend/app/globals.css` using Tailwind CSS 4 `@theme inline` syntax.

## Development Notes

- This is a Windows development environment
- When committing, update README.md and CLAUDE.md as needed, then commit and push
