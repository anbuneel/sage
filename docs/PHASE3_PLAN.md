# SAGE Phase 3 Plan: Full Guide Intelligence

> Updated January 2026

## Context

### The Goal
- **Primary:** Portfolio project showcasing GenAI for software engineering
- **Audience:** Senior leaders at Fannie Mae (internal pitch)
- **Constraint:** Built on personal machine with public data only

### The Challenge
Initial SAGE was a basic eligibility checker that:
- Competed with AskPoli on policy Q&A (losing battle)
- Only covered HomeReady/Home Possible (~500KB)
- Would get "this won't scale" pushback from leaders

### The Pivot
SAGE is NOT an AskPoli competitor. It's a **loan structuring assistant** that does what AskPoli cannot:

| AskPoli | SAGE |
|---------|------|
| "What does the guide say?" | "Is THIS loan eligible?" |
| Retrieves policy text | **Reasons** through scenarios |
| Fannie Mae only | **Fannie + Freddie** comparison |
| No loan analysis | **Specific fix suggestions** |

---

## Phase 3 Objectives

### 1. Full Guide Coverage
Address the "won't scale" objection by indexing complete guides.

| Guide | Source | Status |
|-------|--------|--------|
| Fannie Mae Selling Guide | https://selling-guide.fanniemae.com/ | To scrape |
| Freddie Mac Seller/Servicer Guide | https://guide.freddiemac.com/ | To scrape |

**Why this matters:**
- Demonstrates RAG scales to real document sizes (1,200+ pages)
- Enables reasoning across ANY guide section, not just HomeReady
- Addresses senior leader skepticism

### 2. Intelligent Loan Reasoner
Upgrade from hardcoded rules to AI-powered reasoning.

**Current (Phase 2):**
```
Input: Loan data
→ Hardcoded rules check
→ Pass/fail result
```

**Target (Phase 3):**
```
Input: Loan data (or natural language description)
→ RAG retrieves relevant guide sections
→ AI reasons through eligibility
→ Detailed analysis with citations
→ Specific fix suggestions
```

### 3. Fix Finder Agent
The key differentiator - intelligent loan restructuring.

**Example interaction:**
```
User: "Teacher in Houston, $52K salary, 640 credit,
       wants $280K townhouse, has $8K saved"

SAGE: "Analyzing against HomeReady and Home Possible...

       HomeReady: ELIGIBLE with conditions
       - DTI: 47% ✓ (under 50% limit)
       - LTV: 97% ✓ (at limit, requires MI)
       - Credit: 640 ✓ (meets 620 minimum)
       - Income: Under 80% AMI ✓

       Home Possible: NOT ELIGIBLE
       - Credit: 640 ✗ (needs 660 for 1-unit)

       Recommendation: Proceed with HomeReady.

       To unlock Home Possible:
       - Improve credit score by 20 points (est. 2-3 months)
       - This would enable comparison shopping between GSEs"
```

### 4. Natural Language Input
Accept loan scenarios in plain English, not just form fields.

```
"I have a borrower who's a nurse making $65K, credit around 700,
looking at a $350K condo in Miami, can put 5% down"

→ SAGE extracts: income=$65K, credit=700, property=condo,
  price=$350K, down=5%, location=Miami (high-cost area)
→ Runs full analysis
```

---

## Technical Architecture

### Data Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                     GUIDE SCRAPING                          │
├─────────────────────────────────────────────────────────────┤
│  Fannie Mae Selling Guide    Freddie Mac Guide              │
│  (selling-guide.fanniemae.com) (guide.freddiemac.com)       │
│           │                         │                       │
│           ▼                         ▼                       │
│    ┌──────────────────────────────────────┐                │
│    │  Structured Text Files               │                │
│    │  - Section hierarchy preserved       │                │
│    │  - Metadata (section ID, title, URL) │                │
│    └──────────────────────────────────────┘                │
│                       │                                     │
│                       ▼                                     │
│    ┌──────────────────────────────────────┐                │
│    │  Chunking                            │                │
│    │  - Semantic boundaries               │                │
│    │  - Overlap for context               │                │
│    │  - ~500-1000 tokens per chunk        │                │
│    └──────────────────────────────────────┘                │
│                       │                                     │
│                       ▼                                     │
│    ┌──────────────────────────────────────┐                │
│    │  Voyage AI Embeddings                │                │
│    │  - voyage-2 model (1024 dims)        │                │
│    │  - Rate limited ingestion            │                │
│    └──────────────────────────────────────┘                │
│                       │                                     │
│                       ▼                                     │
│    ┌──────────────────────────────────────┐                │
│    │  Pinecone Vector Index               │                │
│    │  - Full guide searchable             │                │
│    │  - Metadata filtering (GSE, section) │                │
│    └──────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### Reasoning Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                   LOAN ANALYSIS FLOW                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User Input (form or natural language)                      │
│           │                                                 │
│           ▼                                                 │
│  ┌────────────────────┐                                    │
│  │ Input Parser       │ ← Extract loan parameters          │
│  └────────────────────┘                                    │
│           │                                                 │
│           ▼                                                 │
│  ┌────────────────────┐     ┌─────────────────────┐       │
│  │ Query Generator    │────▶│ Pinecone Search     │       │
│  │ (what to look up)  │     │ (retrieve sections) │       │
│  └────────────────────┘     └─────────────────────┘       │
│           │                          │                     │
│           │    ┌─────────────────────┘                     │
│           ▼    ▼                                           │
│  ┌─────────────────────────────────────────┐              │
│  │ Claude Sonnet 4 Reasoning               │              │
│  │ - Analyze loan against retrieved rules  │              │
│  │ - Check both GSEs                       │              │
│  │ - Identify violations                   │              │
│  │ - Generate fix suggestions              │              │
│  └─────────────────────────────────────────┘              │
│           │                                                │
│           ▼                                                │
│  ┌────────────────────┐                                   │
│  │ Structured Output  │                                   │
│  │ - Eligibility      │                                   │
│  │ - Violations       │                                   │
│  │ - Citations        │                                   │
│  │ - Fix suggestions  │                                   │
│  └────────────────────┘                                   │
│                                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 3a: Full Guide Coverage (COMPLETE)
- [x] Parse Fannie Mae Selling Guide from PDF (1,181 pages, 367 sections)
- [x] Parse Fannie Mae Servicing Guide from PDF (771 pages, 108 sections)
- [x] Parse Freddie Mac Seller/Servicer Guide from PDF (2,914 pages, 728 sections)
- [x] Store with proper metadata (section IDs, hierarchy, source)
- [x] **Total: 4,866 pages indexed**

### Phase 3b: Full Guide Indexing (COMPLETE)
- [x] Update chunking strategy for larger corpus
- [x] Ingest all guides into Pinecone (6,174 vectors)
- [x] Verify retrieval quality
- [x] Implement dual-mode UI (LO Mode / Demo Mode)

### Phase 3c: Intelligent Reasoner (COMPLETE)
- [x] Created `EligibilityReasonerService` in `backend/app/services/eligibility_reasoner.py`
- [x] Parallel RAG retrieval for each eligibility rule category
- [x] Claude analysis with JSON output schema
- [x] Real citations from actual guide sections
- [x] Graceful fallback to hardcoded rules on API errors
- [x] See: [Phase 3c Implementation Details](./PHASE3C_INTELLIGENT_REASONER.md)

### Phase 3d: Fix Finder Agent (COMPLETE)
- [x] Design ReAct loop for fix suggestions (OBSERVE → THINK → ACT, max 3 iterations)
- [x] Implement three tools: query_guides, simulate_scenario, compare_products
- [x] Add enhanced fixes with confidence scores, priority ordering, citations
- [x] Build multi-step fix sequences with effort-vs-benefit scoring
- [x] Enable via `enable_fix_finder=true` query parameter
- [x] See: [Phase 3d Implementation Details](./PHASE3D_FIX_FINDER.md)

### Phase 3e: Natural Language Input (1 day)
- [ ] Add NL parsing for loan descriptions
- [ ] Handle ambiguity and missing fields
- [ ] Integrate with reasoning pipeline

### Phase 3f: Polish & Demo Prep (1-2 days)
- [ ] Update UI for new capabilities
- [ ] Create demo scenarios
- [ ] Document build stats (lines of code, time spent, etc.)
- [ ] Prepare presentation materials

---

## Success Metrics

### Technical
- [ ] Full Selling Guide indexed (est. 1,200+ pages)
- [ ] Full Freddie Mac Guide indexed
- [ ] RAG retrieval accuracy on test queries
- [ ] All 11 existing test scenarios pass

### Demo Quality
- [ ] Can answer questions about ANY guide section
- [ ] Loan analysis is accurate with citations
- [ ] Fix suggestions are actionable and specific
- [ ] Natural language input works smoothly

### Pitch Effectiveness
- [ ] Clear differentiation from AskPoli articulated
- [ ] "Won't scale" objection addressed
- [ ] Build stats demonstrate GenAI productivity
- [ ] Senior leaders see value for engineering teams

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Guide scraping blocked | Can't get full content | Use official PDFs, manual extraction |
| Pinecone costs too high | Budget constraint | Use smaller embedding model, reduce chunks |
| RAG quality insufficient | Bad answers | Improve chunking, add reranking |
| Reasoning too slow | Poor demo experience | Cache common queries, optimize prompts |
| Guide changes frequently | Content out of date | Note "as of" date, show update capability |

---

## The Pitch (Final Form)

> "I built SAGE on nights and weekends using Claude Code. It's a loan structuring assistant that does what AskPoli can't: analyze your specific loan scenario, compare Fannie Mae vs Freddie Mac eligibility, and tell you exactly how to fix a failing loan.
>
> The full Selling Guide - all 1,200+ pages - is indexed and searchable. Ask it anything.
>
> This is what one person with GenAI can build. Imagine what our engineering teams could do."

---

## Next Steps

1. Start with guide scraping to understand scope
2. Build incrementally, test often
3. Document the process for the pitch
