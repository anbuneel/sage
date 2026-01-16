# SAGE — Smart Agentic Guide Engine

> **"Policy intelligence that works for you."**

SAGE is an AI-powered solution that transforms mortgage guidelines from static documents into an intelligent system that:

- **Monitors** policy changes across Fannie Mae and Freddie Mac
- **Reasons** about loan scenarios and eligibility
- **Compares** GSE products side-by-side
- **Suggests** actionable fixes when loans fail eligibility
- **Generates** code updates for compliance

## The Problem

The Fannie Mae Selling Guide and Freddie Mac Seller/Servicer Guide are massive (1,200+ pages each) and change frequently. Lenders struggle to keep up with policy changes, understand eligibility, and maintain compliance.

## How SAGE Goes Beyond AskPoli

| AskPoli | SAGE |
|---------|------|
| Reactive search/Q&A | **Proactive** change monitoring |
| Text responses | **Generates code** showing rule updates |
| Finds the rule | **Reasons** about your specific loan scenario |
| Fannie Mae only | **Fannie + Freddie** comparison |

## Features

### Four Tabs

1. **Ask the Guide** — RAG-powered Q&A with citations
2. **What Changed** — Timeline of detected policy updates
3. **Generated Updates** — Code diffs for rule engine updates
4. **Check My Loan** — Scenario analyzer with fix suggestions

### Four Agentic Layers

| Agent | Function |
|-------|----------|
| Change Detection | Monitors for new Lender Letters and Bulletins |
| Impact Analyst | Compares old vs new policy semantically |
| Code Generator | Drafts rule engine updates |
| Scenario Reasoner | Analyzes loans, explains failures, suggests fixes |

## Tech Stack

- **Frontend:** Next.js 16 + Tailwind CSS 4
- **Backend:** FastAPI (Python 3.11+)
- **Vector DB:** Pinecone
- **LLM:** Claude 3.5 Sonnet
- **Agentic Framework:** LangGraph
- **Database:** PostgreSQL (Fly Postgres)
- **Deployment:** Fly.io

## MVP Scope

- **Products:** HomeReady (Fannie Mae) + Home Possible (Freddie Mac)
- **Comparison:** Side-by-side eligibility analysis across GSEs

## Documentation

- [Project Specification](./PROJECT_SPEC.md) — Detailed architecture, data model, and implementation plan

## Status

✅ **Phase 1 Complete** - Core UI and eligibility rules engine implemented

- Next.js frontend with 4 functional tabs
- FastAPI backend with eligibility checking endpoint
- 880-line rules engine covering HomeReady and Home Possible requirements
- Scraped 17 guide files from Fannie Mae and Freddie Mac (~490K characters)

✅ **Design System Complete** - "The Modern Ledger" professional fintech aesthetic

- Typography: Fraunces (display), Public Sans (body), JetBrains Mono (monospace)
- Color palette: Sage green, amber gold, paper backgrounds
- Phosphor icons with consistent "thin" weight
- GSE brand colors for Fannie Mae/Freddie Mac badges
- Enhanced animations with staggered entrance effects
- Improved spacing and visual hierarchy across all pages
- Ledger-style patterns, textures, and interactive states

🚧 **Phase 2 In Progress** - RAG chat, Pinecone vector DB, LangGraph agents

---

Built to showcase AI/GenAI/Agentic capabilities for mortgage industry applications.
