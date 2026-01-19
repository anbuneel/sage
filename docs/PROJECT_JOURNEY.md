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

## Phase 3c: Intelligent Reasoner ✅ (January 2026)

### The Challenge

The hardcoded rules engine was generating fake "demo data" that didn't reflect actual guide content. We needed real RAG-powered reasoning with actual citations.

### The Solution

Created `EligibilityReasonerService` that:
1. Runs parallel RAG queries for each eligibility rule category
2. Builds a structured prompt with loan data and retrieved context
3. Uses Claude with JSON output schema for structured results
4. Returns real citations from actual guide sections
5. Falls back gracefully to hardcoded rules on API errors

### Key Features
- **Parallel retrieval:** Queries for credit score, LTV, DTI, occupancy, property type, income limits - all in parallel
- **Real citations:** Section IDs like "B5-6-02" directly from retrieved guide content
- **Structured output:** JSON schema forces Claude to return typed, parseable results
- **Graceful fallback:** API failures don't break the app - we fall back to hardcoded rules

---

## Phase 3d: Fix Finder Agent ✅ (January 2026)

### The Challenge

Basic fix suggestions were single-pass, generic, and lacked prioritization. We needed intelligent, iterative analysis with confidence scores and what-if testing.

### The Solution

Created `FixFinderService` using the ReAct pattern (Reason + Act):

```
OBSERVE → THINK → ACT → OBSERVE → THINK → ACT → ... (max 3 iterations)
```

### Tools Available to the Agent

| Tool | Purpose |
|------|---------|
| `query_guides` | Search for compensating factors, exceptions, alternatives |
| `simulate_scenario` | Test what-if changes (e.g., "pay down $200/mo debt") |
| `compare_products` | Compare HomeReady vs Home Possible requirements |

### Key Features

- **Confidence scores (0-1):** How likely each fix will work
- **Priority ordering:** Which fixes to try first
- **Estimated timelines:** "Immediate", "1-2 weeks", "3-6 months"
- **Citations:** Guide sections supporting each recommendation
- **Multi-step sequences:** Ordered fix paths with effort-vs-benefit scoring
- **What-if simulations:** See exactly how changes would affect eligibility
- **Full transparency:** ReAct trace shows agent's thinking in demo mode

### Usage

```bash
POST /api/check-loan?demo_mode=true&enable_fix_finder=true
```

---

## Progress Summary

| Milestone | Status | Description |
|-----------|--------|-------------|
| 3a. Full Guide Coverage | ✅ Done | 4,866 pages indexed |
| 3b. Dual-Mode UI | ✅ Done | LO Mode + Demo Mode with AI transparency |
| 3c. Intelligent Reasoner | ✅ Done | RAG-powered reasoning with real citations |
| 3d. Fix Finder Agent | ✅ Done | ReAct-based intelligent fix suggestions |
| 3e. Natural Language Input | 🔜 Next | Describe loans in plain English |

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
