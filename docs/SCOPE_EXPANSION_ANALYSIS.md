# Scope Expansion Analysis: Beyond HomeReady & Home Possible

> **Date:** January 2026
> **Status:** Under Consideration
> **Decision:** Pending

---

## The Observation

SAGE has indexed **4,866 pages** across the full GSE guides, but currently only uses a fraction of that content for eligibility checking:

| What We Have Indexed | What We Actually Use |
|---------------------|---------------------|
| Full Fannie Mae Selling Guide (1,181 pages) | HomeReady sections only |
| Full Fannie Mae Servicing Guide (771 pages) | Not used in eligibility |
| Full Freddie Mac Guide (2,914 pages) | Home Possible sections only |
| **6,174 vectors in Pinecone** | ~2 products out of dozens |

---

## Current Scope By Feature

| Feature | Scope | Details |
|---------|-------|---------|
| **Ask the Guide** | ✅ Full 4,866 pages | RAG queries entire Pinecone index |
| **Check My Loan** | ⚠️ 2 products only | HomeReady + Home Possible |
| **What Changed** | ✅ Both GSEs | Lender Letters + Bulletins (all topics) |
| **Generated Updates** | ⚠️ Limited | Tied to detected changes |

---

## What Else Is In The Indexed Guides

### Fannie Mae Products (in Selling Guide)
- Standard conventional loans
- High-balance loans
- HomeStyle Renovation
- HomeReady (currently supported)
- RefiNow / Refi Plus
- MH Advantage (manufactured housing)

### Freddie Mac Products (in Seller/Servicer Guide)
- Standard conventional loans
- Super conforming
- Home Possible (currently supported)
- Refi Possible
- CHOICERenovation
- CHOICEHome

### Underwriting Topics (both GSEs)
- Income calculation methods
- Asset and reserve requirements
- Gift funds documentation
- Employment verification
- Property eligibility
- Condo/co-op/PUD requirements
- Investment property guidelines
- Second home requirements
- 2-4 unit properties
- ARM vs fixed rate requirements

### Servicing Topics (Fannie Mae Servicing Guide)
- Loss mitigation options
- Forbearance programs
- Loan modifications
- Default management

---

## Why Check My Loan Is Currently Limited

```
User Input (loan scenario)
        │
        ▼
┌───────────────────────────────────┐
│  Rules Engine (880 lines)         │  ← Hardcoded for HomeReady/Home Possible
│  - check_credit_score()           │
│  - check_ltv()                    │
│  - check_dti()                    │
│  - check_income_limits()          │
└───────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────┐
│  Intelligent Reasoner             │  ← Prompts scoped to 2 products
│  - RAG queries mention HR/HP      │
│  - Analysis assumes 2-product     │
└───────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────┐
│  Fix Finder Agent                 │  ← compare_products = HR vs HP only
│  - Tools assume 2-product world   │
└───────────────────────────────────┘
```

---

## Expansion Options

### Option 1: Keep Current Scope
**Effort:** None
**Risk:** Low

- HomeReady vs Home Possible remains the focus
- "Ask the Guide" already covers everything
- Document full coverage as "future expansion"
- Pitch stays simple: affordable lending comparison

**Pros:**
- No additional work
- Clear, focused demo story
- Rules engine already tested

**Cons:**
- Underutilizes 4,866 indexed pages
- Limited audience appeal
- "Won't scale" objection partially valid for eligibility checking

---

### Option 2: Expand Reasoner Only (RAG-First Approach)
**Effort:** Medium (2-3 days)
**Risk:** Medium

Let the AI reason about ANY product using RAG, without hardcoded rules:

1. Add product selector dropdown (or auto-detect from loan characteristics)
2. Broaden Reasoner prompts to not assume HomeReady/Home Possible
3. Trust Claude to derive eligibility rules from retrieved context
4. Keep hardcoded rules as fallback/validation

**Implementation:**
```python
# Instead of:
products = ["HomeReady", "Home Possible"]

# Allow:
products = user_selected or infer_best_products(loan_scenario)
# Could include: Standard, High-Balance, HomeStyle, etc.
```

**Pros:**
- Uses full indexed content
- Minimal infrastructure changes
- Demonstrates true RAG power
- More useful to broader audience

**Cons:**
- Less predictable than hardcoded rules
- May need prompt tuning per product
- Fix Finder needs updates for multi-product

---

### Option 3: Full Product Expansion
**Effort:** High (1-2 weeks)
**Risk:** Higher

Complete overhaul to support all major products:

1. Add product selector with all Fannie/Freddie products
2. Expand rules engine with product-specific rules
3. Redesign UI for multi-product comparison (not just 2)
4. Update Fix Finder for cross-product recommendations
5. Add product-specific test scenarios

**Pros:**
- Comprehensive solution
- Maximum utility
- Strongest pitch

**Cons:**
- Significant development time
- More testing required
- UI complexity increases
- Scope creep risk

---

## Recommendation

**Option 2 (Expand Reasoner Only)** offers the best balance:

- Leverages existing RAG infrastructure
- Uses the full 4,866 pages meaningfully
- Moderate effort with high impact
- Keeps hardcoded rules as safety net
- Can be done incrementally

### Suggested Implementation Path

1. **Phase 1:** Add product selector to UI (dropdown with common products)
2. **Phase 2:** Generalize Reasoner prompts to work with any product
3. **Phase 3:** Update Fix Finder to compare across selected products
4. **Phase 4:** Add "auto-detect best products" feature

---

## Key Insight

> **The infrastructure is already there.** Pinecone has everything indexed, the Reasoner can retrieve and analyze any section. The 2-product limitation is artificial - we scoped prompts and tools for MVP simplicity. Expanding is primarily **prompt engineering**, not new infrastructure.

---

## Questions to Consider

1. **Audience:** Are loan officers the primary users, or also borrowers/real estate agents?
2. **Complexity:** How many products should we support? All of them, or a curated list?
3. **Accuracy:** Can we trust RAG-derived rules, or do we need hardcoded validation?
4. **Demo:** Does expanding scope strengthen or complicate the pitch?
5. **Timeline:** Is this a Phase 3e priority, or post-launch enhancement?

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| Jan 2026 | Analysis created | Document options for future consideration |
| *TBD* | *Pending* | *Awaiting decision* |

---

*This document captures the scope expansion discussion for future reference.*
