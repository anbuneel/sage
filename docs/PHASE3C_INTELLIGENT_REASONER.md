# Phase 3c: Intelligent Reasoner Implementation

**Status:** Implemented
**Date:** 2026-01-18

## Overview

Replaced hardcoded eligibility rules with RAG-powered AI reasoning that retrieves relevant GSE guide sections and uses Claude to analyze loan eligibility.

## Problem Statement

The original eligibility checker used hardcoded if/else rules that:
- Couldn't adapt to guide changes without code updates
- Generated fake "demo data" that didn't reflect real guide content
- Couldn't cite specific guide sections accurately

## Solution

Created `EligibilityReasonerService` that:
1. Runs parallel RAG queries to retrieve relevant guide sections for each eligibility rule
2. Builds a structured prompt with loan data and retrieved context
3. Uses Claude to analyze eligibility with JSON output schema
4. Returns real citations from actual guide sections
5. Falls back to hardcoded rules on API errors

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Eligibility Router                           │
│  POST /api/check-loan?demo_mode=true                           │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              EligibilityReasonerService                         │
├─────────────────────────────────────────────────────────────────┤
│ 1. retrieve_eligibility_context()                               │
│    - Parallel queries for each rule category                    │
│    - Filter by GSE (fannie_mae / freddie_mac)                  │
│    - Deduplicate results                                        │
├─────────────────────────────────────────────────────────────────┤
│ 2. build_analysis_prompt()                                      │
│    - Format loan scenario data                                  │
│    - Organize context by GSE                                    │
├─────────────────────────────────────────────────────────────────┤
│ 3. analyze_with_claude()                                        │
│    - System prompt defines analysis rules                       │
│    - JSON output schema for structured results                  │
├─────────────────────────────────────────────────────────────────┤
│ 4. _convert_to_results()                                        │
│    - Map Claude's JSON to ProductResult objects                 │
│    - Build ReasoningSteps for demo mode                        │
└─────────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Supporting Services                          │
├──────────────────────┬──────────────────────────────────────────┤
│  EmbeddingService    │  Voyage AI voyage-2 embeddings           │
├──────────────────────┼──────────────────────────────────────────┤
│  PineconeService     │  6,174 vectors from 4,866 guide pages    │
├──────────────────────┼──────────────────────────────────────────┤
│  Anthropic Claude    │  claude-3-5-sonnet for analysis          │
└──────────────────────┴──────────────────────────────────────────┘
```

## Files Modified

| File | Action | Description |
|------|--------|-------------|
| `backend/app/services/eligibility_reasoner.py` | CREATE | New RAG-powered eligibility service (340 lines) |
| `backend/app/services/__init__.py` | MODIFY | Export new service |
| `backend/app/routers/eligibility.py` | MODIFY | Integrate reasoner, graceful fallback |
| `backend/app/config.py` | MODIFY | Add `enable_rag_eligibility` and `rag_eligibility_timeout` |

## Query Strategy

Parallel queries for each eligibility rule category:

```python
ELIGIBILITY_QUERIES = {
    "credit_score": [
        "HomeReady minimum credit score requirements eligibility",
        "Home Possible minimum credit score requirements eligibility",
    ],
    "ltv": [
        "HomeReady maximum LTV loan-to-value ratio requirements {property_type}",
        "Home Possible maximum LTV loan-to-value ratio requirements {property_type}",
    ],
    "dti": [
        "HomeReady maximum DTI debt-to-income ratio requirements",
        "Home Possible maximum DTI debt-to-income ratio requirements",
    ],
    "occupancy": [
        "HomeReady occupancy requirements primary residence",
        "Home Possible occupancy requirements primary residence",
    ],
    "property_type": [
        "HomeReady eligible property types {property_type}",
        "Home Possible eligible property types {property_type}",
    ],
    "income_limit": [
        "HomeReady income limits area median income AMI",
        "Home Possible income limits area median income AMI",
    ],
}
```

## Claude Output Schema

```json
{
  "homeready": {
    "eligible": true,
    "confidence": "high",
    "rules_checked": [
      {
        "rule_name": "min_credit_score",
        "requirement": "Minimum 620 credit score",
        "actual_value": "640",
        "result": "pass",
        "citation": "B5-6-02",
        "explanation": "Borrower's score of 640 exceeds minimum"
      }
    ]
  },
  "home_possible": {
    "eligible": false,
    "confidence": "high",
    "rules_checked": [...]
  },
  "recommendation": "Eligible for HomeReady only...",
  "fix_suggestions": [
    {
      "description": "Improve credit score to 660+",
      "impact": "Would qualify for Home Possible",
      "difficulty": "hard"
    }
  ]
}
```

## Error Handling

Graceful degradation when RAG fails:

1. **Claude rate limit** → Fallback to hardcoded rules engine
2. **Timeout** → Fallback to hardcoded rules engine
3. **No context retrieved** → Raise ValueError (indicates Pinecone issue)
4. **JSON parse error** → Raise ValueError (indicates prompt issue)

Errors are logged and the system continues with the fallback.

## Configuration

New settings in `backend/app/config.py`:

```python
# Feature flag to enable/disable RAG eligibility
enable_rag_eligibility: bool = True

# Timeout for RAG eligibility analysis (seconds)
rag_eligibility_timeout: int = 30
```

## Usage

```bash
# With RAG-powered analysis (demo_mode=true)
curl -X POST "http://localhost:8000/api/check-loan?demo_mode=true" \
  -H "Content-Type: application/json" \
  -d '{
    "credit_score": 640,
    "annual_income": 75000,
    "is_first_time_buyer": true,
    "loan_amount": 250000,
    "property_value": 300000,
    "monthly_debt_payments": 500,
    "property_type": "single_family",
    "property_state": "CA",
    "property_county": "Los Angeles",
    "occupancy": "primary"
  }'

# Without RAG (uses hardcoded rules)
curl -X POST "http://localhost:8000/api/check-loan" \
  -H "Content-Type: application/json" \
  -d '...'
```

## Response Enhancements

When `demo_mode=true`, the response includes real RAG data:

- **rag_retrievals**: Actual guide sections retrieved from Pinecone
- **reasoning_steps**: How Claude analyzed each rule
- **retrieval_time_ms**: Time to retrieve context
- **reasoning_time_ms**: Time for Claude to analyze
- **tokens_input/tokens_output**: Actual token usage

## Future Improvements

1. **Always-on RAG**: Make RAG the default instead of demo-only
2. **Caching**: Cache common eligibility queries
3. **Streaming**: Stream Claude's analysis for faster perceived response
4. **Multi-product**: Extend to conventional loans beyond affordable products
