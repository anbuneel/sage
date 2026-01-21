# SAGE Demo Script

A step-by-step guide for demonstrating SAGE's loan structuring capabilities.

---

## 🎬 Quick Recording Guide

### Recording Setup (Windows)
1. Press `Win + G` to open Xbox Game Bar
2. Press `Win + Alt + R` to start recording
3. Execute demo steps below
4. Press `Win + Alt + R` to stop
5. Video saves to `Videos/Captures`

### Warm Up Site First
```bash
curl -s https://sage-web.fly.dev > /dev/null
curl -s https://sage-api.fly.dev/api/health
```

### Copy-Paste Values for Form Entry

| Field | Value |
|-------|-------|
| Credit Score | `680` |
| Annual Income | `72000` |
| Monthly Debt | `1050` |
| Purchase Price | `350000` |
| Down Payment % | `3` |
| Property Type | Single Family |
| Occupancy | Primary Residence |
| First-Time Buyer | ✓ (checked) |
| State | Texas |
| County | Harris (Houston) |

**Calculated Values:**
- Loan Amount: **$339,500** ($350k - 3% down)
- LTV: **97%** (at program max)
- Monthly Income: **$6,000**
- **DTI: 51.4%** (just over 50% limit)

### Recording Steps
1. Open https://sage-web.fly.dev
2. Click **"Check My Loan"**
3. **Toggle ON "Enable Fix Finder Agent"** ← Important!
4. Enter values from table above
5. Click **"Check Eligibility"** — wait 30-40 seconds (AI is reasoning)
6. Scroll to see Fix Finder Agent results with confidence scores
7. (Optional) Click **"Ask the Guide"** → ask: `What compensating factors offset high DTI?`
8. Stop recording

**Expected Result:** DTI 51.4% fails both programs → Fix Finder suggests reducing debt by **$115/month** (95% confidence)

---

## Demo Overview

**Duration:** 3-5 minutes
**Audience:** Senior Fannie Mae leaders
**Goal:** Show how SAGE answers "Is this loan eligible, and how do I fix it?" — the question AskPoli can't answer.

---

## The Scenario: Maria's First Home

**Borrower Profile:**
- **Name:** Maria (first-time homebuyer)
- **Location:** Houston, TX (Harris County)
- **Situation:** Good credit, stable job, but carrying some debt
- **Goal:** Buy a $350,000 home with 3% down

**Loan Details:**
- **Purchase Price:** $350,000
- **Down Payment:** $10,500 (3%)
- **Loan Amount:** $339,500
- **LTV:** 97%

**The Challenge:** Her debt-to-income ratio is slightly too high for standard approval.

---

## Demo Script

### Part 1: Check My Loan (The Problem)

**Step 1: Navigate to Check My Loan**
- Go to https://sage-web.fly.dev
- Click "Check My Loan" card

**Step 2: Enter Maria's Loan Scenario**

| Field | Value | Notes |
|-------|-------|-------|
| Credit Score | 680 | Good, not great |
| Annual Income | $72,000 | $6,000/month |
| Monthly Debt | $1,050 | Car payment + credit card |
| Purchase Price | $350,000 | Modest home |
| Down Payment | 3% | Minimum for these programs |
| Property Type | Single Family | Standard |
| Occupancy | Primary Residence | Required |
| First-Time Buyer | Yes | ✓ Check this |
| State | Texas | - |
| County | Harris | Houston metro |

**Step 3: Click "Check Eligibility"**

**Expected Result:**
- ❌ **HomeReady: INELIGIBLE** — DTI 51.4% exceeds 50% max
- ❌ **Home Possible: INELIGIBLE** — DTI 51.4% exceeds 45% max

**Talking Point:**
> "Maria has good credit and stable income, but her DTI of 51.4% is just over the limit. A traditional system would just say 'denied.' Let's see what SAGE suggests."

---

### Part 2: Fix Finder Agent (The Solution)

**Step 4: Enable Fix Finder** (do this BEFORE entering data)
- Toggle ON **"Enable Fix Finder Agent"** at the top of the form
- You'll see: "AI-powered • RAG retrieval • ReAct reasoning"

**Step 5: Review AI-Powered Fix Suggestions**

The Fix Finder Agent will run 3 ReAct iterations (~35 seconds) and return:

**Performance Metrics:**
- 3 reasoning cycles (OBSERVE → THINK → ACT)
- ~11,500 tokens analyzed
- ~35 seconds processing time

**Expected Fixes (5 suggestions with confidence scores):**

| Priority | Fix | Confidence | Unlocks |
|----------|-----|------------|---------|
| 1 | Reduce debt by **$115/month** → DTI 50% | **95%** | HomeReady |
| 2 | Reduce debt by **$385/month** → DTI 45% | **95%** | Both |
| 3 | Increase income by $350/month | 70% | HomeReady |
| 4 | Exclude 30-day balances with payoff | 80% | — |
| 5 | Reduce loan amount ($10k = ~$65/mo) | 90% | Both |

**Recommended Approach:**
> "Reduce monthly debt by $115 to achieve 50% DTI for HomeReady eligibility"

**Product Comparison Insights:**
- HomeReady has 50% DTI limit (easier)
- Home Possible has 45% DTI limit (harder)
- 6% DTI gap makes HomeReady significantly more accessible

**Talking Point:**
> "The Fix Finder Agent used the ReAct pattern to iteratively search GSE guidelines. It found the MINIMUM change needed — Maria only needs to reduce debt by $115/month, not $200. It also found creative alternatives like excluding 30-day account balances if she has payoff funds."

---

### Part 3: Ask the Guide (The Research)

**Step 6: Navigate to Ask the Guide**
- Click "Ask the Guide" in navigation

**Step 7: Ask a Follow-up Question**

Type: `What compensating factors can offset high DTI for HomeReady?`

**Expected Response:**
- Lists compensating factors from the actual Fannie Mae guide
- Includes citations to specific sections (B3-5.1, etc.)
- Mentions reserves, credit score offsets, etc.

**Talking Point:**
> "Unlike a chatbot that might hallucinate, SAGE retrieves actual text from the indexed guides and provides citations. This is RAG — Retrieval Augmented Generation — grounded in 4,866 pages of real policy."

---

### Part 4: Demo Mode (Optional - AI Transparency)

**Step 8: Toggle Demo Mode**
- Find the Demo Mode toggle (top right of results)
- Turn it ON

**What it shows:**
- Number of guide sections retrieved
- RAG retrieval time
- Claude reasoning chain
- Token usage and estimated cost

**Talking Point:**
> "For technical audiences, Demo Mode shows full transparency into the AI's reasoning — what it retrieved, how it reasoned, and performance metrics."

---

## Key Talking Points

### The Pitch (memorize this)
> "AskPoli tells you what the guide says. SAGE tells you if YOUR SPECIFIC LOAN works, and if not, exactly how to fix it — across both Fannie and Freddie products."

### Differentiation
| Question | AskPoli | SAGE |
|----------|---------|------|
| "What's the DTI limit?" | ✅ Answers | Use AskPoli |
| "Is Maria's 51.4% DTI eligible?" | ❌ Can't do | ✅ **SAGE** |
| "How much debt should she pay off?" | ❌ Can't do | ✅ **SAGE** |

### Technical Highlights
- **4,866 pages indexed** across Fannie Mae + Freddie Mac
- **ReAct Agent** that reasons iteratively (not just one LLM call)
- **Real citations** from actual guide sections
- **Side-by-side GSE comparison** (AskPoli is Fannie-only)

---

## Backup Scenarios

### Scenario B: Credit Score Edge Case
- Credit Score: **615** (below 620 minimum)
- Everything else good
- Shows: Clear failure with specific fix (improve credit to 620)

### Scenario C: Perfect Loan
- Credit Score: 720
- DTI: 35%
- Everything passing
- Shows: ✅ Eligible for both programs (green checkmarks)

---

## Recording Tips

1. **Warm up the app first** — Visit the site 30 seconds before recording to avoid cold start
2. **Use Demo Mode selectively** — Show it briefly, don't dwell on technical details unless asked
3. **Pause on results** — Let the eligibility results display for 2-3 seconds
4. **Narrate the value** — Don't just click; explain what SAGE is doing differently

---

## Pre-Demo Checklist

- [ ] Site is live: https://sage-web.fly.dev
- [ ] Backend is healthy: https://sage-api.fly.dev/api/health
- [ ] Visited site once to warm up (avoid cold start)
- [ ] Screen recording software ready
- [ ] Scenario values written down for quick entry
- [ ] Talking points reviewed

---

## Quick Reference: Maria's Numbers

```
Credit Score:    680
Annual Income:   $72,000
Monthly Debt:    $1,050
Purchase Price:  $350,000
Down Payment:    3% ($10,500)
Loan Amount:     $339,500
LTV:             97%
Property Type:   Single Family
Occupancy:       Primary Residence
First-Time:      Yes
State:           Texas
County:          Harris (Houston)
```

**Result:** DTI = 51.4% (fails both programs — just over 50% limit)
**Fix:** Reduce debt by **$115/month** → DTI drops to 50.0% (HomeReady eligible!)

---

## Verified Results (January 2026)

### Eligibility Check Results
| Program | Status | Violation |
|---------|--------|-----------|
| HomeReady (Fannie Mae) | ❌ INELIGIBLE | DTI 51.4% > 50% max |
| Home Possible (Freddie Mac) | ❌ INELIGIBLE | DTI 51.4% > 45% max |

### Fix Finder Agent Results
**Performance:**
- ReAct Iterations: 3 cycles
- Processing Time: 35.8 seconds
- Tokens Used: 11,510

**Recommended Approach:**
> "Reduce monthly debt by $115 to achieve 50% DTI for HomeReady eligibility"

**Enhanced Fix Suggestions:**

| # | Fix | Impact | Confidence | Timeline | Unlocks |
|---|-----|--------|------------|----------|---------|
| 1 | Reduce debt by $115/month | DTI: 51.4% → 50.0% | 95% | Immediate | HomeReady |
| 2 | Reduce debt by $385/month | DTI: 51.4% → 45.0% | 95% | Immediate | Both |
| 3 | Increase income by $350/month | DTI: 51.4% → 50.0% | 70% | 30-60 days | HomeReady |
| 4 | Exclude 30-day balances with payoff | Depends on balances | 80% | Immediate | — |
| 5 | Reduce loan amount | ~$65/mo per $10k | 90% | Immediate | Both |

**Product Comparison Insights:**
- `homeready_advantage`: Lower DTI requirement (50% vs 45%), easier to qualify
- `home_possible_advantage`: May offer different rate/fee structures
- `key_difference`: 6% DTI gap makes HomeReady significantly more accessible
- `recommendation`: Focus on HomeReady qualification first
