# Phase 3d: Fix Finder Agent Implementation

**Status:** Implemented
**Date:** 2026-01-18

## Overview

Implemented a ReAct-based (Reason + Act) agent that iteratively analyzes loan violations and finds intelligent fixes by querying GSE guides for compensating factors and simulating what-if scenarios.

## Problem Statement

The basic fix suggestions from Phase 3c were:
- Single-pass, linear suggestions without iteration
- No confidence scores or prioritization
- No what-if scenario testing
- No citations for compensating factors
- No multi-step fix paths with effort/benefit analysis

## Solution

Created `FixFinderService` that:
1. Runs a ReAct loop (OBSERVE → THINK → ACT) with max 3 iterations
2. Uses three tools to gather intelligence: `query_guides`, `simulate_scenario`, `compare_products`
3. Synthesizes findings into enhanced fixes with confidence scores
4. Builds multi-step fix sequences with effort-vs-benefit scoring
5. Provides full transparency via ReAct trace in demo mode

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  POST /api/check-loan?demo_mode=true&enable_fix_finder=true     │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  EligibilityReasonerService (Phase 3c)                          │
│  → Returns violations + basic fixes                             │
└──────────────────────────────┬──────────────────────────────────┘
                               │ Has violations?
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  FixFinderService (NEW)                                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  REACT LOOP (max 3 iterations)                            │  │
│  │  OBSERVE → THINK → ACT → OBSERVE → ...                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  TOOLS:                                                         │
│  • query_guides - Search for compensating factors/exceptions    │
│  • simulate_scenario - Test what-if changes                     │
│  • compare_products - Compare HomeReady vs Home Possible        │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  FixFinderResult                                                │
│  • enhanced_fixes (with confidence, priority, citations)        │
│  • fix_sequences (multi-step paths)                             │
│  • simulations (what-if results)                                │
│  • react_trace (demo mode only)                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Files Created/Modified

| File | Action | Description |
|------|--------|-------------|
| `backend/app/models/fix_finder.py` | CREATE | New Pydantic models (150 lines) |
| `backend/app/services/fix_finder_service.py` | CREATE | ReAct agent with tool execution (500+ lines) |
| `backend/app/models/__init__.py` | MODIFY | Export new models + model_rebuild() |
| `backend/app/services/__init__.py` | MODIFY | Export FixFinderService |
| `backend/app/routers/eligibility.py` | MODIFY | Add enable_fix_finder param, integrate service |
| `backend/app/config.py` | MODIFY | Add fix_finder settings |
| `backend/app/models/loan.py` | MODIFY | Add fix_finder_result field to EligibilityResult |

## ReAct Pattern Implementation

### The Loop

```python
for iteration in range(max_iterations):  # max 3
    # OBSERVE: Review current state and previous findings
    observation = f"Iteration {iteration + 1}: Analyzing violations"

    # THINK: Claude reasons about what information is needed
    response = claude.messages.create(
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=messages
    )

    # ACT: Execute any tool calls
    if response.has_tool_calls:
        for tool_call in response.tool_calls:
            result = execute_tool(tool_call)
            messages.append(result)
    else:
        # No more tools needed, Claude is ready to provide final analysis
        break
```

### Tools Available

```python
TOOLS = [
    {
        "name": "query_guides",
        "description": "Search GSE guides for compensating factors, exceptions, or alternative requirements",
        "input_schema": {
            "query": "string - search query",
            "gse_filter": "fannie_mae | freddie_mac | both",
            "focus_area": "compensating_factors | exceptions | alternative_requirements | general"
        }
    },
    {
        "name": "simulate_scenario",
        "description": "Test what-if changes to loan parameters",
        "input_schema": {
            "changes": {"credit_score": 680, "monthly_debt_payments": 400},
            "description": "Pay down $200/month in debt"
        }
    },
    {
        "name": "compare_products",
        "description": "Compare HomeReady vs Home Possible requirements",
        "input_schema": {
            "requirement_area": "credit_score | ltv | dti | income_limits | property_type | occupancy | reserves"
        }
    }
]
```

## Data Models

### EnhancedFixSuggestion

```python
class EnhancedFixSuggestion(BaseModel):
    description: str                # What the borrower should do
    impact: str                     # How this fix would help
    difficulty: Literal["easy", "moderate", "hard"]
    confidence: float               # 0-1 confidence this will work
    priority_order: int             # Suggested order (1 = highest)
    estimated_timeline: str         # e.g., "1-2 weeks", "3-6 months"
    unlocks_products: list[str]     # ["HomeReady", "Home Possible"]
    citations: list[GuideCitation]  # Guide section references
    compensating_factors: list[CompensatingFactor]
    trade_offs: list[str]           # Potential downsides
```

### FixSequence

```python
class FixSequence(BaseModel):
    sequence_name: str              # e.g., "Quick Path", "Best Value"
    description: str                # Overall approach description
    steps: list[EnhancedFixSuggestion]  # Ordered fixes
    total_effort: Literal["low", "medium", "high", "very_high"]
    effort_vs_benefit_score: float  # 0-10 (10 = best value)
    products_unlocked: list[str]    # End result eligibility
    estimated_total_timeline: str   # Total time to complete
```

### SimulationResult

```python
class SimulationResult(BaseModel):
    scenario_description: str       # What was changed
    parameter_changes: dict         # Modified values
    homeready_eligible: bool        # Result for HomeReady
    home_possible_eligible: bool    # Result for Home Possible
    violations_resolved: list[str]  # Rules that would pass
    remaining_violations: list[str] # Rules that still fail
    feasibility: Literal["easy", "moderate", "hard", "very_hard"]
```

### ReactStep (Demo Mode Trace)

```python
class ReactStep(BaseModel):
    step_number: int                # Iteration number
    observation: str                # What agent observed
    reasoning: str                  # Agent's thinking
    action: str                     # What action was taken
    tool_calls: list[ToolCall]      # Tools executed
    findings: list[str]             # Key discoveries
```

## Claude System Prompt

```text
You are SAGE Fix Finder, an expert mortgage loan restructuring agent.
Your job is to analyze loan eligibility violations and find intelligent ways to fix them.

PROCESS: Use the ReAct pattern (Reason + Act):
1. OBSERVE: Review the current loan violations and any previous findings
2. THINK: Reason about what information you need to find better fixes
3. ACT: Use tools to gather compensating factors, test scenarios, or compare products
4. REPEAT: Continue until you have enough information (max 3 iterations)

PRIORITIZATION GUIDELINES:
1. Easy fixes over hard ones
2. Fixes that unlock BOTH products over just one
3. Quick fixes over long-term ones
4. Low-cost fixes over expensive ones
5. Fixes with official compensating factor support in the guides
```

## Configuration

New settings in `backend/app/config.py`:

```python
# Feature flag for Fix Finder Agent
enable_fix_finder: bool = True

# Max ReAct loop iterations
fix_finder_max_iterations: int = 3

# Max seconds for Fix Finder analysis
fix_finder_timeout: int = 15
```

## Usage

```bash
# With Fix Finder (requires demo_mode)
curl -X POST "http://localhost:8000/api/check-loan?demo_mode=true&enable_fix_finder=true" \
  -H "Content-Type: application/json" \
  -d '{
    "credit_score": 640,
    "annual_income": 75000,
    "loan_amount": 250000,
    "property_value": 260000,
    "monthly_debt_payments": 1200,
    "property_type": "single_family",
    "property_state": "TX",
    "property_county": "Travis",
    "occupancy": "primary"
  }'

# Without Fix Finder (basic fixes only)
curl -X POST "http://localhost:8000/api/check-loan?demo_mode=true" ...
```

## Response Structure

When `enable_fix_finder=true` and violations exist:

```json
{
  "scenario": {...},
  "products": [...],
  "fix_suggestions": [...],
  "demo_data": {...},
  "fix_finder_result": {
    "enhanced_fixes": [
      {
        "description": "Pay down $200/month in existing debt",
        "impact": "Would lower DTI from 52% to 48%, meeting HomeReady's 50% limit",
        "difficulty": "moderate",
        "confidence": 0.85,
        "priority_order": 1,
        "estimated_timeline": "Immediate if using savings",
        "unlocks_products": ["HomeReady"],
        "citations": [
          {
            "section_id": "B5-6-02",
            "gse": "fannie_mae",
            "snippet": "Maximum DTI ratio of 50%...",
            "relevance_score": 0.92
          }
        ],
        "trade_offs": ["Reduces liquid reserves"]
      }
    ],
    "fix_sequences": [
      {
        "sequence_name": "Quick Path to HomeReady",
        "description": "Fastest route to eligibility for one product",
        "steps": [...],
        "total_effort": "medium",
        "effort_vs_benefit_score": 7.5,
        "products_unlocked": ["HomeReady"],
        "estimated_total_timeline": "1-2 weeks"
      }
    ],
    "simulations": [
      {
        "scenario_description": "Pay down $200/month debt",
        "parameter_changes": {"monthly_debt_payments": "1000"},
        "homeready_eligible": true,
        "home_possible_eligible": false,
        "violations_resolved": ["max_dti"],
        "remaining_violations": ["min_credit_score"],
        "feasibility": "moderate"
      }
    ],
    "recommended_path": "Focus on DTI reduction first...",
    "product_comparison": {
      "homeready": "More lenient on DTI (50% vs 45%)",
      "home_possible": "Higher credit requirement (660 vs 620)"
    },
    "react_trace": [
      {
        "step_number": 1,
        "observation": "Analyzing DTI violation of 52%",
        "reasoning": "Need to find compensating factors for high DTI...",
        "action": "tool_calls",
        "tool_calls": [{"tool_name": "query_guides", ...}],
        "findings": ["Found B5-6-02 allows 50% max DTI"]
      }
    ],
    "total_iterations": 2,
    "total_time_ms": 3500,
    "tokens_used": 2100
  }
}
```

## Error Handling

Graceful degradation when Fix Finder fails:

1. **Claude API error** → Return empty fix_finder_result, basic fixes still available
2. **Timeout** → Return partial results with truncated trace
3. **Tool execution error** → Log warning, continue with other tools
4. **JSON parse error** → Return empty analysis, log for debugging

## Key Enhancements Over Basic Fixes

| Basic Fixes (Phase 3c) | Fix Finder Agent (Phase 3d) |
|------------------------|------------------------------|
| Single-pass generation | Iterative ReAct loop (up to 3 iterations) |
| Generic suggestions | Confidence scores (0-1) |
| No citations | Guide citations with snippets |
| No what-if testing | Simulates scenario changes |
| No prioritization | Priority order + effort-vs-benefit |
| No multi-step paths | Fix sequences with dependencies |

## Future Improvements

1. **Streaming**: Stream ReAct steps for real-time progress visibility
2. **Caching**: Cache common violation patterns and their fixes
3. **Learning**: Track which fixes borrowers actually implement
4. **Multi-product**: Extend beyond HomeReady/Home Possible
5. **Cost Estimation**: Add dollar amounts to fix suggestions where applicable
