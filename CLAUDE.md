# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SAGE (Smart Agentic Guide Engine) is a **loan structuring assistant** that helps loan officers and borrowers find eligibility across GSE products. Unlike AskPoli (which answers "What does the guide say?"), SAGE answers "Is this specific loan eligible, and how do I fix it?"

**Core Value Proposition:**
- Analyze loan scenarios against HomeReady (Fannie Mae) and Home Possible (Freddie Mac)
- Side-by-side GSE comparison (AskPoli is Fannie-only)
- Actionable fix suggestions when loans fail eligibility

**Status:** Phase 3d Complete ✅ - Fix Finder Agent with ReAct-based intelligent fix suggestions. 4,866 pages indexed across both GSEs.

**Strategic Direction:** See [Competitive Analysis](./docs/COMPETITIVE_ANALYSIS.md) for positioning vs AskPoli.

## Tech Stack

- **Frontend:** Next.js 16 + Tailwind CSS 4
- **Backend:** FastAPI (Python 3.11+)
- **Vector DB:** Pinecone (active)
- **LLM:** Claude Sonnet 4 via Anthropic SDK (active)
- **Database:** PostgreSQL via SQLAlchemy async (falls back to SQLite)
- **Embeddings:** Voyage AI voyage-2 (active)

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
│   │   ├── check/page.tsx       # Loan eligibility checker
│   │   └── usage/page.tsx       # LLM usage dashboard
│   ├── components/              # React components
│   │   ├── TabNav.tsx           # Navigation tabs
│   │   ├── LoanForm.tsx         # Loan scenario input form
│   │   ├── EligibilityResult.tsx # Eligibility results display
│   │   ├── ChatInterface.tsx    # RAG chat component
│   │   ├── ChangeTimeline.tsx   # Policy updates timeline
│   │   ├── CodeDiff.tsx         # Code diff viewer
│   │   └── Footer.tsx           # Site-wide footer
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
│       │   ├── changes.py       # GET /api/changes (DB-enabled)
│       │   └── usage.py         # GET /api/usage/summary (LLM tracking)
│       ├── models/              # Pydantic models
│       │   ├── loan.py          # LoanScenario, EligibilityResult
│       │   ├── chat.py          # ChatMessage, ChatResponse
│       │   └── policy.py        # PolicyUpdate, CodeDiffResponse
│       ├── services/            # Business logic
│       │   ├── rules_engine.py  # 880-line eligibility rules engine
│       │   ├── pinecone_service.py   # Vector DB operations
│       │   ├── embedding_service.py  # Text embeddings
│       │   ├── rag_service.py        # RAG pipeline for chat
│       │   ├── eligibility_reasoner.py  # RAG-powered loan eligibility analysis
│       │   ├── fix_finder_service.py    # ReAct-based Fix Finder Agent
│       │   ├── llm_usage_service.py     # LLM usage tracking and cost calculation
│       │   └── scrapers/             # Policy update scrapers
│       │       ├── base_scraper.py
│       │       ├── fannie_mae_scraper.py
│       │       └── freddie_mac_scraper.py
│       └── db/                  # Database layer
│           ├── database.py      # Async SQLAlchemy connection
│           └── models.py        # ORM models (PolicyUpdate, etc.)
├── contracts/                   # API contracts
│   └── api_contracts.md         # Shared interfaces between frontend/backend
├── data/                        # Full GSE guide content (4,866 pages)
│   ├── fannie_mae_guide/        # Selling Guide: 367 sections (1,181 pages)
│   ├── fannie_mae_servicing_guide/  # Servicing Guide: 108 sections (771 pages)
│   └── freddie_mac_guide/       # Seller/Servicer Guide: 728 sections (2,914 pages)
└── scripts/
    ├── scrape_guides.py         # Guide scraping script
    ├── ingest_guides.py         # Embed guides into Pinecone
    └── test_scenarios.py        # Automated loan scenario tests
```

## Commands

### Frontend (from `frontend/`)
```bash
npm install          # Install dependencies
npm run dev          # Start development server (port 4000)
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
python parse_fannie_mae_pdf.py    # Parse Fannie Mae Selling Guide PDF
python parse_freddie_mac.py       # Parse Freddie Mac Guide PDF
python ingest_guides.py           # Embed all guides into Pinecone (dynamic discovery, batched)
python ingest_guides.py --fresh   # Clear and re-ingest everything
python ingest_guides.py --dry-run # Just count files without ingesting
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

### What's Hardcoded vs Database

**Database is OPTIONAL for core features.** The main AI capabilities work without PostgreSQL:

| Component | Storage | Notes |
|-----------|---------|-------|
| **Eligibility Rules** | Hardcoded in `rules_engine.py` | 880 lines of Python, not in DB |
| **Guide Content** | Pinecone vectors | 6,174 vectors, not in DB |
| **RAG Chat** | Pinecone + Claude | No DB needed |
| **Fix Finder** | Claude + Pinecone | No DB needed |
| Policy Updates | DB (PolicyUpdate) | Optional - for "What Changed" tab |
| Chat History | DB (Conversation) | Optional - sessions don't persist without it |
| LLM Usage Tracking | DB (LLMUsage) | Optional - for `/usage` dashboard |

**To run without a database:** Just don't set `DATABASE_URL`. The app falls back to SQLite (`./sage.db`) which auto-creates. For a pure demo, even SQLite is optional if you skip the DB-dependent features.

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

**Test Suite:**
- 11 automated loan scenarios (`scripts/test_scenarios.py`)
- Covers credit scores, DTI, LTV, occupancy, property types
- Each test references official GSE guide sections

**UI Polish:**
- Site-wide footer with quick links and official resources
- GSE brand colors (Fannie Mae blue, Freddie Mac green)
- Staggered entrance animations

## Phase 3: Full Guide Intelligence

**See [Phase 3 Plan](./docs/PHASE3_PLAN.md) for detailed roadmap.**

### Objectives

1. ✅ **Full Guide Coverage** — All GSE guides indexed: 4,866 pages, 1,203 sections, 6,174 vectors in Pinecone
   - Fannie Mae Selling Guide: 1,181 pages, 367 sections
   - Fannie Mae Servicing Guide: 771 pages, 108 sections
   - Freddie Mac Seller/Servicer Guide: 2,914 pages, 728 sections

2. ✅ **Dual-Mode UI** — Toggle between LO Mode (practical results) and Demo Mode (AI transparency)
   - LO Mode: Clean eligibility results with fix suggestions for loan officers
   - Demo Mode: Full transparency showing RAG retrieval, reasoning chain, token usage, and index stats

3. ✅ **Intelligent Reasoner** — RAG-powered AI reasoning that retrieves relevant guide sections and analyzes loans dynamically
   - `EligibilityReasonerService` with parallel RAG retrieval
   - Claude analysis with JSON output schema for structured results
   - Real citations from actual guide sections
   - See: [Phase 3c Implementation](./docs/PHASE3C_INTELLIGENT_REASONER.md)

4. ✅ **Fix Finder Agent** — ReAct-based agent for intelligent loan restructuring suggestions with trade-off analysis
   - `FixFinderService` with iterative OBSERVE → THINK → ACT loop (max 3 iterations)
   - Three tools: `query_guides` (RAG search), `simulate_scenario` (what-if testing), `compare_products` (GSE comparison)
   - Enhanced fixes with confidence scores, priority ordering, citations, and compensating factors
   - Multi-step fix sequences with effort-vs-benefit scoring
   - Enable via `enable_fix_finder=true` query parameter

5. **Natural Language Input** — Accept loan scenarios in plain English, not just form fields

### The Pitch

> "AskPoli tells you what the guide says. SAGE tells you if your specific loan works, and if not, exactly how to fix it - across both Fannie and Freddie products. All 4,866 pages are indexed."

### Context

- **Goal:** Portfolio project + internal pitch showcasing GenAI for software engineering
- **Audience:** Senior Fannie Mae leaders
- **Constraint:** Built on personal machine with public data only

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
- **Fannie Mae:** `#05314D` - official blue (badge)
- **Freddie Mac:** `#6CB516` - official green (badge)

### Icons
- Phosphor Icons with consistent "thin" weight throughout
- Examples: ChatText, ClockCounterClockwise, Code, CheckCircle, Scales

### CSS Custom Properties
All design tokens defined in `frontend/app/globals.css` using Tailwind CSS 4 `@theme inline` syntax.

## Development Notes

- This is a Windows development environment
- When committing, update README.md and CLAUDE.md as needed, then commit and push
