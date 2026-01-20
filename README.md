# SAGE — Smart Agentic Guide Engine

> **"The loan structuring assistant that finds eligibility across GSE products."**

SAGE helps loan officers and borrowers answer the question AskPoli can't: **"Is this specific loan eligible, and if not, how do I fix it?"**

- **Analyzes** loan scenarios against HomeReady and Home Possible requirements
- **Compares** Fannie Mae vs Freddie Mac eligibility side-by-side
- **Suggests** actionable fixes when loans fail eligibility
- **Explains** exactly which rules are violated and why

## The Problem

AskPoli answers "What does the Fannie Mae guide say?" but loan officers need to answer:
- "Is *this specific loan* eligible for HomeReady? Home Possible? Both?"
- "If it fails, what's the easiest fix?"
- "Which GSE product is the better fit?"

## How SAGE Complements AskPoli

| Need | AskPoli | SAGE |
|------|---------|------|
| "What's the DTI limit?" | ✅ Policy lookup | Use AskPoli |
| "Is my 52% DTI loan eligible?" | ❌ Can't analyze scenarios | ✅ **SAGE answers this** |
| "HomeReady vs Home Possible?" | ❌ Fannie Mae only | ✅ **Side-by-side comparison** |
| "How do I fix this loan?" | ❌ No suggestions | ✅ **Actionable fixes** |

See [Competitive Analysis](./docs/COMPETITIVE_ANALYSIS.md) for detailed comparison.

## Features

### Core Value (Differentiated)

1. **Check My Loan** — Enter a loan scenario, get instant eligibility for both HomeReady and Home Possible with specific violations and fix suggestions
2. **Side-by-Side Comparison** — See exactly where each GSE product differs on your specific loan
3. **Dual-Mode UI** — Toggle between LO Mode (clean, practical results) and Demo Mode (full AI transparency with RAG retrieval, reasoning chain, and performance stats)

### Supporting Features

3. **Ask the Guide** — RAG-powered Q&A with citations (for policy lookup)
4. **What Changed** — Timeline of detected policy updates
5. **Generated Updates** — Code diffs for rule engine updates (enterprise feature)
6. **LLM Usage Dashboard** — Track token usage and costs across all AI services (`/usage`)

## Tech Stack

- **Frontend:** Next.js 16 + Tailwind CSS 4
- **Backend:** FastAPI (Python 3.11+)
- **Vector DB:** Pinecone
- **LLM:** Claude Sonnet 4 (Anthropic)
- **Embeddings:** Voyage AI voyage-2
- **Database:** PostgreSQL (Fly Postgres) / SQLite fallback
- **Deployment:** Fly.io

## MVP Scope

- **Products:** HomeReady (Fannie Mae) + Home Possible (Freddie Mac)
- **Comparison:** Side-by-side eligibility analysis across GSEs

## Documentation

- [Phase 3 Plan](./docs/PHASE3_PLAN.md) — Full Guide Intelligence roadmap
- [Competitive Analysis](./docs/COMPETITIVE_ANALYSIS.md) — Strategic positioning vs AskPoli
- [Project Specification](./PROJECT_SPEC.md) — Detailed architecture, data model, and implementation plan

## Status

✅ **Phase 1 Complete** - Core UI and eligibility rules engine

- Next.js frontend with 4 functional tabs
- FastAPI backend with eligibility checking endpoint
- 880-line rules engine covering HomeReady and Home Possible requirements
- Guide sections for HomeReady (B5-6) and Home Possible (4501) eligibility (~500KB)

✅ **Design System Complete** - "The Modern Ledger" professional fintech aesthetic

- Typography: Fraunces (display), Public Sans (body), JetBrains Mono (monospace)
- Color palette: Sage green, amber gold, paper backgrounds
- Phosphor icons with consistent "thin" weight
- GSE brand colors for Fannie Mae/Freddie Mac badges
- Enhanced animations with staggered entrance effects
- Ledger-style patterns, textures, and interactive states

✅ **Phase 2 Complete** - RAG chat and policy updates fully operational

- Pinecone vector DB service for semantic search
- Voyage AI voyage-2 embeddings for guide content vectorization
- Claude Sonnet 4 integration for RAG chat responses with citations
- PostgreSQL database models (PolicyUpdate, EligibilityRule, Conversation, LLMUsage)
- Fannie Mae Lender Letters scraper
- Freddie Mac Bulletins scraper
- Code generation in Python, TypeScript, YAML, and JSON formats
- 11 automated loan scenario tests with GSE guide references
- Site-wide footer with quick links and official resources

✅ **Phase 3 Complete** — Full Guide Intelligence

See [Phase 3 Plan](./docs/PHASE3_PLAN.md) for detailed roadmap and [Project Journey](./docs/PROJECT_JOURNEY.md) for the full timeline.

| Milestone | Status | Description |
|-----------|--------|-------------|
| **3a. Full Guide Coverage** | ✅ Complete | 4,866 pages indexed (1,203 sections, 6,174 vectors) |
| **3b. Dual-Mode UI** | ✅ Complete | LO Mode + Demo Mode with RAG/reasoning transparency |
| **3c. Intelligent Reasoner** | ✅ Complete | RAG-powered AI reasoning with guide citations |
| **3d. Fix Finder Agent** | ✅ Complete | ReAct-based intelligent fix suggestions with simulations |
| **3e. Natural Language Input** | 🔜 Future | Describe loans in plain English |

**Guide Coverage (4,866 pages total):**
- Fannie Mae Selling Guide: 1,181 pages, 367 sections
- Fannie Mae Servicing Guide: 771 pages, 108 sections
- Freddie Mac Seller/Servicer Guide: 2,914 pages, 728 sections

**The Pitch:** "AskPoli tells you what the guide says. SAGE tells you if your specific loan works, and if not, exactly how to fix it — across both Fannie and Freddie products. All 4,866 pages are indexed."

## Live Demo

| Service | URL |
|---------|-----|
| **Frontend** | https://sage-web.fly.dev |
| **Backend API** | https://sage-api.fly.dev/api |
| **API Docs** | https://sage-api.fly.dev/api/docs |

Deployed on Fly.io with auto-scaling (scales to zero when idle).

---

Built to showcase AI/GenAI/Agentic capabilities for mortgage industry applications.
