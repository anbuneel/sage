# SAGE — Smart Agentic Guide Engine

> **"Policy intelligence that works for you."**

A production-grade AI solution that transforms mortgage guidelines from static documents into an intelligent system that monitors policy changes, reasons about loan scenarios, and generates actionable outputs.

---

## The Problem

The Fannie Mae Selling Guide and Freddie Mac Seller/Servicer Guide are massive (1,200+ pages each) and change frequently via Lender Letters and Bulletins. Lenders struggle to:

- Keep up with policy changes across both GSEs
- Understand which product fits a specific loan scenario
- Know *why* a loan fails eligibility and *how* to fix it
- Update internal underwriting rules to stay compliant

---

## How SAGE Goes Beyond AskPoli

| AskPoli (Exists Today) | SAGE (Your Solution) |
|------------------------|----------------------|
| Reactive search/Q&A | **Proactive** change monitoring |
| Answers questions | **Anticipates** impact of changes |
| Text responses | **Generates code** showing rule updates |
| User-initiated | **Agent-initiated** alerts |
| Finds the rule | **Reasons** about your specific loan scenario |
| "Here's the policy" | "Here's how to **fix your loan** to meet the policy" |
| Fannie Mae only | **Fannie + Freddie** comparison |

### The Pitch

> *"AskPoli is an excellent **Reference Tool** for finding policy. SAGE builds on that foundation to create an **Action Engine**. It transforms the Selling Guide from a document you read into a system that:*
> - *Actively monitors for policy changes*
> - *Reasons about your specific loan scenarios*
> - *Compares eligibility across Fannie Mae and Freddie Mac*
> - *Suggests fixes when loans fail eligibility*
> - *Writes the code to keep you compliant."*

---

## The Four Agentic Layers

| Agent | What It Does |
|-------|--------------|
| **Change Detection Agent** | Monitors Fannie Mae Lender Letters and Freddie Mac Bulletins; detects when new policies drop |
| **Impact Analyst Agent** | Compares old vs new policy; identifies semantic shifts (e.g., "DTI limit changed from 45% to 50% for high-balance loans") |
| **Code Generation Agent** | Drafts illustrative code updates showing how an underwriting rules engine would need to change |
| **Scenario Reasoning Agent** | Takes a specific loan profile, determines eligibility for both GSEs, explains failures, and suggests actionable fixes |

---

## Web App Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              SAGE                                            │
│                    Smart Agentic Guide Engine                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────┐  ┌───────────┐  ┌───────────────┐  ┌────────────────────────┐ │
│  │  ASK TAB  │  │ CHANGES   │  │ CODE UPDATES  │  │  CHECK MY LOAN  ⭐     │ │
│  └───────────┘  └───────────┘  └───────────────┘  └────────────────────────┘ │
│                                                                              │
│  "Ask the       "What           "Generated        "Scenario Analyzer"        │
│   Guide"         Changed"        Updates"          - Input loan details      │
│   - Chat UI      - Timeline      - Code diffs      - Get pass/fail verdict   │
│   - RAG Q&A      - Impact        - Before/after    - See WHY it fails        │
│   - Citations      analysis      - Format toggle   - Get FIX suggestions     │
│                                                    - Compare Fannie/Freddie  │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │  Status: Agent last checked 2 hours ago                               │   │
│  │  12 Lender Letters analyzed since Jan 2024 | 847 scenarios evaluated  │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Tab 1: "Ask the Guide"
- Standard RAG chat interface
- Demonstrates baseline capability (what AskPoli does)
- Includes citations to specific guide sections
- Supports both Fannie Mae and Freddie Mac guides

### Tab 2: "What Changed"
- Timeline/feed of detected Lender Letters and Bulletins
- Each entry shows:
  - Date detected
  - GSE (Fannie or Freddie)
  - Summary of changes
  - Affected guide sections
  - Impact analysis

### Tab 3: "Generated Updates"
- For each detected change, show the drafted code update
- Side-by-side diff view (before/after)
- Format toggle (Python | TypeScript | YAML | JSON)
- Disclaimer: "Draft update for review — adapt to your system"

### Tab 4: "Check My Loan" ⭐ (The Differentiator)

This transforms SAGE from a **reference tool** into a **problem-solving tool**.

**User inputs loan scenario:**
- DTI, LTV, credit score, loan amount, property type, product type, etc.

**Agent outputs:**
1. **Pass/Fail verdict** — Does this loan meet requirements for HomeReady? Home Possible? Both?
2. **Side-by-side comparison** — Which GSE product is the better fit and why
3. **Failure explanation** — Which specific rules are violated
4. **Actionable fixes** — Concrete steps to make the loan eligible

**Example interaction:**
```
┌─────────────────────────────────────────────────────────────────────────┐
│  LOAN SCENARIO INPUT                                                    │
├─────────────────────────────────────────────────────────────────────────┤
│  Product: Affordable    DTI: 52%    LTV: 85%    Credit: 680             │
│  Property: Single-family    Loan Amount: $350,000                       │
│                                                                         │
│  [Analyze Eligibility]                                                  │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  RESULTS: COMPARISON                                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────┐    ┌─────────────────────────┐             │
│  │ FANNIE MAE: HomeReady   │    │ FREDDIE MAC: Home Poss. │             │
│  ├─────────────────────────┤    ├─────────────────────────┤             │
│  │ ❌ INELIGIBLE            │    │ ❌ INELIGIBLE            │             │
│  │                         │    │                         │             │
│  │ Issues:                 │    │ Issues:                 │             │
│  │ • DTI 52% > 50% max     │    │ • DTI 52% > 50% max     │             │
│  │                         │    │ • Credit 680 > 660 min  │             │
│  │                         │    │   (Wait... 680 passes!) │             │
│  └─────────────────────────┘    └─────────────────────────┘             │
│                                                                         │
│  💡 RECOMMENDATION: Both products fail on DTI. Fix the DTI issue        │
│     and this loan qualifies for BOTH programs.                          │
│                                                                         │
│  SUGGESTED FIXES:                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Option 1: Pay off $4,200 in revolving debt                      │    │
│  │           → Reduces DTI to 49.8% ✓                              │    │
│  │                                                                 │    │
│  │ Option 2: Add co-borrower with $800/mo income                   │    │
│  │           → Reduces DTI to 48.5% ✓                              │    │
│  │                                                                 │    │
│  │ Option 3: Increase loan term from 20yr to 30yr                  │    │
│  │           → Reduces monthly payment, DTI drops to 47% ✓         │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  📖 Citations: Fannie B3-4.1-01, Freddie 4301.1                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Code Generation: What It Actually Is

### Honest Framing
The code generation is **illustrative, not production-ready**. Every lender's underwriting engine is different. SAGE drafts a starting point showing what would need to change — a human engineer reviews and adapts it.

### Example

**Lender Letter says:**
> "Effective July 1, 2025, the maximum DTI ratio for high-balance loans is increased from 45% to 50% for borrowers with credit scores ≥ 720."

**SAGE generates (Python):**

```python
# BEFORE (current rule)
def check_dti_limit(loan):
    if loan.is_high_balance:
        return loan.dti <= 0.45
    return loan.dti <= 0.50

# AFTER (updated rule)
def check_dti_limit(loan):
    if loan.is_high_balance:
        if loan.borrower_credit_score >= 720:
            return loan.dti <= 0.50  # Updated per LL-2025-XX
        return loan.dti <= 0.45
    return loan.dti <= 0.50
```

**SAGE generates (YAML config):**

```yaml
# BEFORE
high_balance_dti_limit: 0.45

# AFTER
high_balance_dti_limit:
  default: 0.45
  exceptions:
    - condition: credit_score >= 720
      limit: 0.50
      effective_date: 2025-07-01
      source: LL-2025-XX
```

### Why It's Valuable

| What It Shows | Why It Matters |
|---------------|----------------|
| Policy → Code translation | Agent understands **meaning**, not just text |
| Structured output | Goes beyond summaries to actionable artifacts |
| Multiple formats | Python, TypeScript, YAML, JSON — shows flexibility |
| Diff view | Before/after makes the change concrete |

---

## MVP Scope

### Products Supported
| GSE | Product | Why |
|-----|---------|-----|
| Fannie Mae | HomeReady | Popular affordable product, well-documented |
| Freddie Mac | Home Possible | Direct competitor, enables side-by-side comparison |

### Eligibility Rules to Encode

| Rule | HomeReady (Fannie) | Home Possible (Freddie) |
|------|-------------------|------------------------|
| **Max DTI** | 50% | 50% |
| **Max LTV** | 97% | 97% |
| **Min Credit** | 620 | 660 |
| **Income Limit** | 80% AMI (most areas) | 80% AMI |
| **Occupancy** | Primary only | Primary only |
| **Property Types** | SFR, Condo, PUD | SFR, Condo, PUD |
| **First-Time Buyer** | Not required | Not required |
| **Homeownership Education** | Required | Required |

---

## Tech Stack (Production-Ready)

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Frontend** | Next.js + Tailwind | Modern, fast, professional look |
| **Backend** | FastAPI (Python) | Clean API, async, great for AI workloads |
| **Vector DB** | Pinecone | Scalable, managed, no infra headaches |
| **Embeddings** | OpenAI text-embedding-3-small | Best quality/price ratio |
| **LLM** | Claude 3.5 Sonnet | Superior reasoning for eligibility logic |
| **Agentic Framework** | LangGraph | Fine-grained control over agent workflows |
| **Database** | PostgreSQL (Supabase) | Free tier, managed, real database |
| **Deployment** | Vercel (frontend) + Railway (backend) | Professional, scalable, affordable |

---

## Data Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA MODEL                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐     │
│  │ GUIDE_CHUNKS     │     │ PRODUCTS         │     │ ELIGIBILITY_RULES│     │
│  ├──────────────────┤     ├──────────────────┤     ├──────────────────┤     │
│  │ id (uuid)        │     │ id (uuid)        │     │ id (uuid)        │     │
│  │ gse (fannie/     │     │ name             │     │ product_id (fk)  │     │
│  │     freddie)     │     │ gse              │     │ rule_type        │     │
│  │ section_id       │     │ description      │     │ condition_json   │     │
│  │ content          │     │ guide_reference  │     │ limit_value      │     │
│  │ embedding (vec)  │     └──────────────────┘     │ failure_message  │     │
│  │ source_url       │              │               │ fix_suggestions[]│     │
│  │ last_updated     │              │               │ guide_citation   │     │
│  └──────────────────┘              │               └──────────────────┘     │
│           │                        │                        │               │
│           │         ┌──────────────┴──────────────┐         │               │
│           │         │                             │         │               │
│           ▼         ▼                             ▼         ▼               │
│  ┌──────────────────┐                    ┌──────────────────┐               │
│  │ POLICY_UPDATES   │                    │ SCENARIO_RESULTS │               │
│  ├──────────────────┤                    ├──────────────────┤               │
│  │ id (uuid)        │                    │ id (uuid)        │               │
│  │ gse              │                    │ input_params     │               │
│  │ update_number    │                    │ product_results[]│               │
│  │ publish_date     │                    │   - product_id   │               │
│  │ title            │                    │   - eligible     │               │
│  │ summary          │                    │   - issues[]     │               │
│  │ changes_json     │                    │   - fixes[]      │               │
│  │ affected_rules[] │                    │ recommendation   │               │
│  │ code_update      │                    │ created_at       │               │
│  └──────────────────┘                    └──────────────────┘               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
sage/
├── frontend/                 # Next.js app
│   ├── app/
│   │   ├── page.tsx         # Landing / Tab navigation
│   │   ├── ask/             # Tab 1: RAG Chat
│   │   ├── changes/         # Tab 2: What Changed
│   │   ├── code-updates/    # Tab 3: Generated Updates
│   │   └── check-loan/      # Tab 4: Scenario Analyzer
│   ├── components/
│   │   ├── ChatInterface.tsx
│   │   ├── LoanForm.tsx
│   │   ├── EligibilityResult.tsx
│   │   ├── CodeDiff.tsx
│   │   └── ChangeTimeline.tsx
│   ├── lib/
│   │   └── api.ts           # API client
│   └── package.json
│
├── backend/                  # FastAPI
│   ├── app/
│   │   ├── main.py          # FastAPI app entry
│   │   ├── config.py        # Environment config
│   │   ├── routers/
│   │   │   ├── chat.py      # RAG endpoints
│   │   │   ├── changes.py   # Policy update endpoints
│   │   │   ├── code.py      # Code generation endpoints
│   │   │   └── scenarios.py # Loan analysis endpoints
│   │   ├── agents/
│   │   │   ├── change_detector.py
│   │   │   ├── impact_analyst.py
│   │   │   ├── code_generator.py
│   │   │   └── scenario_reasoner.py
│   │   ├── models/          # Pydantic models
│   │   │   ├── loan.py
│   │   │   ├── eligibility.py
│   │   │   └── policy.py
│   │   ├── db/              # Database models & migrations
│   │   │   ├── models.py
│   │   │   └── connection.py
│   │   └── services/
│   │       ├── embeddings.py
│   │       ├── pinecone_client.py
│   │       ├── rules_engine.py
│   │       └── llm_client.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── data/
│   ├── fannie/
│   │   ├── selling_guide/   # Chunked PDF content
│   │   └── lender_letters/  # Historical letters
│   └── freddie/
│       ├── seller_servicer_guide/
│       └── bulletins/
│
├── scripts/
│   ├── ingest_fannie_guide.py
│   ├── ingest_freddie_guide.py
│   ├── seed_eligibility_rules.py
│   └── check_for_updates.py  # Cron job script
│
├── docker-compose.yml
└── README.md
```

---

## What Makes SAGE Impressive (Self-Service Demo)

| Visitor Sees | What It Proves |
|--------------|----------------|
| "Last checked: 2 hours ago" | System is autonomous, running on its own |
| 10+ policy updates analyzed | Agent has been working over time |
| Specific impact analysis | Agent reasons, doesn't just retrieve |
| Generated code diffs | Agent produces actionable output |
| **"Check My Loan" with Fannie/Freddie comparison** | **Agent solves problems across GSEs** |
| **Actionable fix suggestions** | **Agent thinks like an underwriter** |
| Clean UI with citations | Production-quality work |

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
1. Set up project structure (Next.js + FastAPI)
2. Ingest Fannie Mae Selling Guide (chunk + embed)
3. Ingest Freddie Mac Seller/Servicer Guide
4. Build Tab 1: RAG chat with citations
5. Deploy MVP to Vercel + Railway

### Phase 2: Scenario Reasoning (Week 2)
6. Build loan scenario input form (Tab 4)
7. Encode eligibility rules for HomeReady + Home Possible
8. Implement Scenario Reasoning Agent
9. Add side-by-side GSE comparison
10. Add fix suggestions logic

### Phase 3: Change Detection (Week 3)
11. Index historical Lender Letters and Bulletins
12. Build Tab 2: "What Changed" timeline
13. Implement Impact Analyst Agent
14. Add Code Generation Agent (Tab 3)
15. Set up background monitoring job

### Phase 4: Polish (Week 4)
16. UI/UX refinement
17. Add more eligibility rules
18. Performance optimization
19. Documentation
20. Demo video / walkthrough

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Guides indexed | 2 (Fannie + Freddie) |
| Products supported | 2 (HomeReady + Home Possible) |
| Eligibility rules encoded | 8+ per product |
| Policy updates analyzed | 10+ historical |
| Response time (RAG chat) | < 3 seconds |
| Response time (scenario analysis) | < 5 seconds |

---

## Open Questions / Future Enhancements

- [ ] Add more loan products (Standard, FHA, VA)
- [ ] Integrate AMI lookup by county for income limits
- [ ] Add DU/LP findings integration
- [ ] Email alerts for policy changes
- [ ] User accounts to save scenarios
- [ ] API access for lender system integration
