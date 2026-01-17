# Competitive Analysis: SAGE vs AskPoli

> Strategic evaluation completed January 2026

## Executive Summary

SAGE should **not** compete with AskPoli on policy Q&A. Instead, SAGE should focus on **loan scenario reasoning and structuring** - capabilities AskPoli lacks entirely.

---

## AskPoli Overview

[AskPoli](https://singlefamily.fanniemae.com/applications-technology/ask-poli) is Fannie Mae's AI-powered policy assistant for approved business partners.

### What AskPoli Does Well

| Capability | Details |
|------------|---------|
| Policy Q&A | Production-grade search with human curation |
| Content Sources | Selling Guide, Lender Letters, Eligibility Matrix, FAQs, job aids |
| Machine Learning | Continuously improved by expert team |
| QC Integration | Workflow integration for quality control vendors (expanded May 2025) |
| Insights Dashboard | Trending topics and analytics |
| Access Control | Fannie Mae approved partners only |

### What AskPoli Cannot Do

- Compare Fannie Mae vs Freddie Mac products
- Analyze specific loan scenarios for eligibility
- Suggest how to restructure a loan to achieve eligibility
- Monitor Freddie Mac policy changes
- Generate code updates for compliance systems

---

## SAGE Capabilities Assessment

### Current Strengths

| Feature | Status | Differentiation |
|---------|--------|-----------------|
| Dual-GSE Comparison | ✅ Working | **Unique** - AskPoli is Fannie-only |
| Loan Scenario Analysis | ✅ Working | **Unique** - "Is this loan eligible?" |
| Side-by-side Eligibility | ✅ Working | **Unique** - HomeReady vs Home Possible |
| Open Access | ✅ Working | **Unique** - No partner credentials needed |

### Current Weaknesses

| Feature | Status | Assessment |
|---------|--------|------------|
| RAG Chat | ⚠️ Limited scope | HomeReady/Home Possible sections only (~500KB vs full 1,200+ page guides) |
| Policy Monitoring | ⚠️ Mock data | Nice-to-have, not core value |
| Code Generation | ⚠️ Templates | Enterprise feature, low priority |
| Fix Suggestions | ⚠️ Static | Needs intelligence to be valuable |

### Guide Coverage (Current Scope)

**Fannie Mae (~215 KB):**
- B5-6: HomeReady Overview, Eligibility, Underwriting, Pricing
- B2-1.2: LTV Ratios
- B3-5.1: Credit Scores
- B3-6: DTI Ratios
- 2 Lender Letters

**Freddie Mac (~308 KB):**
- 4501: Home Possible Overview, Eligibility, Additional Requirements
- 5201: Credit Assessment
- 5401: Income Assessment
- 3 Bulletins

**Not covered:** Full Selling Guide (1,200+ pages), other products (conventional, jumbo, etc.)

---

## Feature Comparison Matrix

| Capability | AskPoli | SAGE | Winner |
|------------|---------|------|--------|
| Policy Q&A | ✅ Production-grade | ✅ Functional | AskPoli |
| Human Curation | ✅ Expert team | ❌ None | AskPoli |
| QC Insights | ✅ Dashboard | ❌ None | AskPoli |
| Fannie Mae Coverage | ✅ Complete | ✅ Complete | Tie |
| Freddie Mac Coverage | ❌ None | ✅ Complete | **SAGE** |
| Loan Eligibility Check | ❌ None | ✅ Working | **SAGE** |
| GSE Product Comparison | ❌ None | ✅ Working | **SAGE** |
| Fix Suggestions | ❌ None | ⚠️ Basic | **SAGE** |
| Open Access | ❌ Partners only | ✅ Public | **SAGE** |

---

## Strategic Recommendation

### Focus Areas (Differentiated Value)

1. **Loan Scenario Reasoning** - Already works, keep strong
   - "Is this loan eligible for HomeReady? Home Possible? Both?"
   - Side-by-side comparison with specific violations

2. **Fix Finder Agent** - High priority enhancement
   - Intelligent suggestions: "Pay off $400/mo car loan to reduce DTI from 52% to 48%"
   - Trade-off analysis: "5% more down payment costs $12K but enables eligibility"
   - Timeline suggestions: "Wait 2 months for late payment to age off"

3. **Dual-GSE Comparison** - Unique positioning
   - No other tool compares HomeReady vs Home Possible
   - Helps borrowers and LOs find the best fit

### De-prioritize

1. **RAG Chat Alone** - AskPoli does this better with human curation
2. **Policy Monitoring** - Nice-to-have, not differentiated
3. **Code Generation** - Enterprise feature, not consumer value

---

## Target Positioning

### Before (Competing with AskPoli)
> "SAGE is an AI-powered policy intelligence system"

### After (Differentiated)
> "SAGE is a loan structuring assistant that helps you find eligibility across GSE products"

---

## Key Differentiators to Emphasize

1. **"Which GSE product fits this loan?"** - Only SAGE answers this
2. **"How do I fix this loan?"** - Actionable restructuring suggestions
3. **"Compare HomeReady vs Home Possible"** - Side-by-side analysis
4. **Open access** - No Fannie Mae partner credentials required

---

## Phase 3 Priority (Revised)

| Priority | Feature | Rationale |
|----------|---------|-----------|
| 1 | Fix Finder Agent | Transforms SAGE from checker to advisor |
| 2 | Real AMI Limits | Accuracy for income limit validation |
| 3 | UI/UX for Loan Structuring | Make the workflow intuitive |
| 4 | Policy Monitoring | Lower priority, nice-to-have |
| 5 | Code Generation | Enterprise feature, defer |

---

## Sources

- [Ask Poli | Fannie Mae](https://singlefamily.fanniemae.com/applications-technology/ask-poli)
- [Ask Poli: An unconventional QC resource (March 2025)](https://singlefamily.fanniemae.com/media/41931/display)
- [How to Use Ask Poli: Helpful Hints and Tips](https://singlefamily.fanniemae.com/media/38981/display)
- [Quality Insider - Ask Poli QC Resource](https://singlefamily.fanniemae.com/news-events/quality-insider-ask-poli-unconventional-qc-resource)
