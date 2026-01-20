# ReAct Pattern: How the Fix Finder Agent Works

> **ReAct = Reason + Act**

## What is ReAct?

ReAct is an AI agent pattern where the model alternates between reasoning and taking actions, rather than trying to answer everything in one shot.

The loop:
1. **Reason** - Think about what to do next
2. **Act** - Use a tool to gather information
3. **Observe** - See the result
4. **Repeat** until done

## Fix Finder Agent in Action

Here's a real example of how the Fix Finder processes a loan with 64% DTI (too high):

```
User submits loan with 64% DTI (limit is 50%)
         │
         ▼
┌─────────────────────────────────────────────┐
│  ITERATION 1                                │
│  REASON: "DTI is 64%, limit is 50%.         │
│          Need to find compensating factors" │
│  ACT:    query_guides("DTI compensating     │
│          factors HomeReady")                │
│  OBSERVE: Found sections on reserves,       │
│           credit score offsets...           │
└─────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  ITERATION 2                                │
│  REASON: "Let me simulate reducing debt"    │
│  ACT:    simulate_scenario({                │
│            monthly_debt: -$500              │
│          })                                 │
│  OBSERVE: DTI drops to 52%, still too high  │
└─────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  ITERATION 3                                │
│  REASON: "Need bigger reduction, or         │
│          compare products"                  │
│  ACT:    compare_products("dti")            │
│  OBSERVE: Both GSEs have 50% max...         │
└─────────────────────────────────────────────┘
         │
         ▼
    FINAL ANALYSIS
    "Reduce debt by $767/month to qualify"
```

## Available Tools

The Fix Finder Agent has three tools it can use:

| Tool | Purpose | Example |
|------|---------|---------|
| `query_guides` | Search GSE guides via RAG | Find compensating factors for high DTI |
| `simulate_scenario` | Test what-if changes | "What if we reduce debt by $500?" |
| `compare_products` | Compare HomeReady vs Home Possible | Which has more lenient DTI rules? |

## Why ReAct is Impressive

**The AI decides *what tools to use* and *in what order*** - it's not a hardcoded script. It reasons through the problem iteratively, just like a human loan officer would.

### Comparison

| Approach | How it works | Quality |
|----------|--------------|---------|
| **Single LLM call** | One prompt, one response | Fast but shallow |
| **Hardcoded pipeline** | Fixed sequence of steps | Predictable but inflexible |
| **ReAct (what we use)** | AI chooses tools dynamically | Thorough and adaptive |

## Implementation Details

- **Max iterations:** 3 (prevents infinite loops)
- **Timeouts:** 30s per iteration, 45s for final analysis
- **Model:** Claude Sonnet 4
- **Code:** `backend/app/services/fix_finder_service.py`

## Example Output

After running the ReAct loop, the Fix Finder returns:

```json
{
  "enhanced_fixes": [
    {
      "description": "Reduce monthly debt payments by $767/month",
      "confidence": 0.95,
      "impact": "Brings DTI from 64% to 49.8%",
      "unlocks_products": ["HomeReady", "Home Possible"],
      "effort": "moderate",
      "timeline": "Immediate if paying off revolving debt"
    }
  ],
  "total_iterations": 3,
  "tokens_used": 12631
}
```

---

*This pattern was popularized by the paper "ReAct: Synergizing Reasoning and Acting in Language Models" (Yao et al., 2022)*
