# SAGE: The Journey So Far

## The Vision

**SAGE (Smart Agentic Guide Engine)** set out to answer a question AskPoli can't:

> "Is this specific loan eligible, and if not, how do I fix it?"

While AskPoli tells you what the Fannie Mae guide says, SAGE analyzes your actual loan scenario against both GSEs and suggests fixes.

---

## Phase 1: Foundation ✅

**Built the core product:**
- Next.js frontend with 4 tabs (Ask, Changes, Code, Check)
- FastAPI backend with eligibility checking
- 880-line rules engine for HomeReady & Home Possible
- "The Modern Ledger" design system (Fraunces, Public Sans, sage green palette)

---

## Phase 2: Intelligence ✅

**Added the AI layer:**
- Pinecone vector DB for semantic search
- Voyage AI embeddings + Claude Sonnet 4 for RAG chat
- PostgreSQL for policy tracking
- Fannie Mae/Freddie Mac scrapers for bulletins
- Code generation in Python, TypeScript, YAML, JSON
- 11 automated loan scenario tests

---

## Phase 3a: Full Guide Coverage ✅ (January 2026)

### The "Big Data" Challenge

We hit a wall trying to index the full GSE guides. The blockers seemed insurmountable:
- "The file is too big"
- Only 11 out of 720 Freddie Mac sections were being extracted
- Ingestion script was hardcoded for 12 files

### Root Cause Analysis

| Problem | Symptom | Actual Cause |
|---------|---------|--------------|
| Freddie Mac parser failing | 11/720 sections | CRLF line endings (`\r\n` vs `\n`) |
| Regex not matching | 0 matches after newline | Used `\n` instead of `^` with MULTILINE |
| Ingestion ignoring files | 12 files only | Hardcoded `GUIDE_METADATA` dict |
| Missing Fannie Mae content | 367 vs ~475 sections | Only had Selling Guide, not Servicing Guide |

### The Fix

1. **2-line fix** for CRLF normalization
2. **Regex change** from `\n(\d{4}...)` to `^(\d{4}...)`
3. **Rewrote ingestion** with dynamic discovery, batching, checkpointing
4. **Downloaded** Fannie Mae Servicing Guide (771 pages)

### Result

| Guide | Pages | Sections | Vectors |
|-------|-------|----------|---------|
| Fannie Mae Selling Guide | 1,181 | 367 | ~1,800 |
| Fannie Mae Servicing Guide | 771 | 108 | ~750 |
| Freddie Mac Seller/Servicer Guide | 2,914 | 728 | ~3,600 |
| **Total** | **4,866** | **1,203** | **6,174** |

---

## The Point Proven

> **Coding agents CAN handle "big data" challenges.**

The blockers were never about data size. They were about:
- Diagnosing root causes (encoding issues, regex patterns)
- Building robust pipelines (batching, rate limiting, checkpointing)
- Not giving up when things fail

The entire process - from "it's too big" to "4,866 pages indexed" - took about an hour.

---

## Phase 3b: Dual-Mode UI ✅ (January 2026)

### The Challenge

How do you build one interface that serves two different audiences?
- **Loan Officers** want clean, practical results - eligibility status and fix suggestions
- **SVP/Senior Leaders** want to see the AI in action - RAG retrieval, reasoning chains, performance stats

### The Solution

A toggle between LO Mode and Demo Mode:

**LO Mode:**
- Clean eligibility results with ELIGIBLE/INELIGIBLE stamps
- Side-by-side HomeReady vs Home Possible comparison
- Actionable fix suggestions ranked by difficulty

**Demo Mode:**
- Everything from LO Mode, PLUS:
- RAG retrieval results showing which guide sections were found
- Step-by-step reasoning chain with pass/fail for each rule
- Performance stats (retrieval time, reasoning time, tokens used)
- Index coverage (4,866 pages, 1,203 sections, 6,174 vectors)

### New Components
- `ModeToggle.tsx` - Toggle between LO Mode and Demo Mode
- `DemoModePanel.tsx` - Renders RAG retrieval, reasoning chain, and stats
- Backend updates to return detailed reasoning data when `demo_mode=true`

---

## What's Next (Phase 3c-e)

| Milestone | Status | Description |
|-----------|--------|-------------|
| 3a. Full Guide Coverage | ✅ Done | 4,866 pages indexed |
| 3b. Dual-Mode UI | ✅ Done | LO Mode + Demo Mode with AI transparency |
| 3c. Intelligent Reasoner | 🔜 Next | Replace hardcoded rules with RAG-powered reasoning |
| 3d. Fix Finder Agent | Planned | ReAct loop for loan restructuring suggestions |
| 3e. Natural Language Input | Planned | Describe loans in plain English |

---

## The Pitch

> "AskPoli tells you what the guide says. SAGE tells you if your specific loan works, and if not, exactly how to fix it - across both Fannie and Freddie products. **All 4,866 pages are indexed.**"

---

## Technical Stack

- **Frontend:** Next.js 16 + Tailwind CSS 4
- **Backend:** FastAPI (Python 3.11+)
- **Vector DB:** Pinecone (6,174 vectors)
- **LLM:** Claude Sonnet 4 via Anthropic SDK
- **Embeddings:** Voyage AI voyage-2
- **Database:** PostgreSQL via SQLAlchemy async
- **Deployment:** Fly.io

---

*Last updated: January 2026*
