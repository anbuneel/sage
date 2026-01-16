# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SAGE (Smart Agentic Guide Engine) is an AI-powered mortgage policy intelligence system that transforms Fannie Mae and Freddie Mac guidelines into an actionable platform. It monitors policy changes, reasons about loan scenarios, compares GSE products, and generates code updates for compliance.

**Status:** Phase 1 Complete - Core UI and eligibility rules engine implemented.

## Tech Stack

- **Frontend:** Next.js 16 + Tailwind CSS 4
- **Backend:** FastAPI (Python 3.11+)
- **Vector DB:** Pinecone (Phase 2)
- **LLM:** Claude 3.5 Sonnet via LangGraph for agentic workflows (Phase 2)
- **Database:** PostgreSQL (Phase 2)
- **Embeddings:** OpenAI text-embedding-3-small (Phase 2)

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
│       ├── api.ts               # API client with mock functions
│       └── types.ts             # TypeScript interfaces
├── backend/                     # FastAPI application
│   └── app/
│       ├── main.py              # Application entry point
│       ├── config.py            # Settings and configuration
│       ├── routers/             # API endpoints
│       │   ├── eligibility.py   # POST /api/check-loan
│       │   ├── chat.py          # POST /api/chat
│       │   └── changes.py       # GET /api/changes
│       ├── models/              # Pydantic models
│       │   ├── loan.py          # LoanScenario, EligibilityResult
│       │   ├── chat.py          # ChatMessage, ChatResponse
│       │   └── policy.py        # PolicyUpdate, CodeDiffResponse
│       ├── services/            # Business logic
│       │   └── rules_engine.py  # 880-line eligibility rules engine
│       └── db/                  # Database (Phase 2)
├── contracts/                   # API contracts
│   └── api_contracts.md         # Shared interfaces between frontend/backend
├── data/                        # Scraped guide content
│   └── scraped_guides/          # 17 guide files (~490K characters)
└── scripts/
    └── scrape_guides.py         # Guide scraping script
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
python ingest_fannie_guide.py     # Ingest Fannie Mae Selling Guide
python ingest_freddie_guide.py    # Ingest Freddie Mac Guide
python seed_eligibility_rules.py  # Seed eligibility rules for HomeReady/Home Possible
python check_for_updates.py       # Check for new Lender Letters/Bulletins
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

## Phase 2 Notes (from Gemini Review)

### Code Generation Tab
- Output **JSON Logic** or **YAML** rules instead of just Python
- Makes it look enterprise-ready (compatible with BRE like Drools, IBM ODM)

### Data Model Enhancement
- Add `affected_rule_ids` (Array of UUIDs) to `POLICY_UPDATES` table
- Links policy changes to specific rows in `ELIGIBILITY_RULES`
- Enables "which rules are now obsolete" flagging

### Fix Finder Agent (ReAct Loop Pattern)
```
1. Evaluate  → Check loan against rule set
2. Identify  → "DTI is 52%, limit is 50%"
3. Reason    → "Need to lower DTI by 2%"
4. Tool Use  → Calculator: solve for required debt reduction
5. Verify    → Re-run new numbers against rules
6. Output    → Present the fix with confidence
```

### AMI Income Limits
- Skip geocoding/Census Tract lookups for MVP demo
- Hardcode specific "High Cost" and "Low Cost" areas if needed
- Full AMI lookup is a rabbit hole that can break demos

### Already Addressed ✅
- Fix suggestions use Python math (not LLM) in `rules_engine.py`
- Fannie vs Freddie side-by-side comparison
- Focus on DTI/LTV/Credit Score rules

## Development Notes

- This is a Windows development environment
- When committing, update README.md and CLAUDE.md as needed, then commit and push
