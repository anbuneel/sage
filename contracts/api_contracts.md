# SAGE API Contracts

This document defines the shared interfaces between frontend, backend, and rules engine.
All agents MUST follow these contracts exactly.

---

## Base URL

- Development: `http://localhost:8000/api`
- Production: `https://sage-api.fly.dev/api`

---

## Data Models

### LoanScenario (Input for eligibility check)

```python
# Python (Pydantic)
class LoanScenario(BaseModel):
    # Borrower
    credit_score: int                    # e.g., 680
    annual_income: float                 # e.g., 75000.00
    is_first_time_buyer: bool            # True/False

    # Loan
    loan_amount: float                   # e.g., 350000.00
    property_value: float                # e.g., 400000.00
    loan_term_years: int = 30            # 15, 20, or 30

    # Calculated (backend computes these)
    # ltv: float                         # loan_amount / property_value
    # dti: float                         # provided or calculated

    # Debt (for DTI calculation)
    monthly_debt_payments: float         # e.g., 500.00 (car, student loans, etc.)

    # Property
    property_type: str                   # "single_family" | "condo" | "pud" | "2_unit" | "3_unit" | "4_unit" | "manufactured"
    property_state: str                  # e.g., "CA"
    property_county: str                 # e.g., "Los Angeles"
    occupancy: str = "primary"           # "primary" | "secondary" | "investment"
```

```typescript
// TypeScript
interface LoanScenario {
  credit_score: number;
  annual_income: number;
  is_first_time_buyer: boolean;
  loan_amount: number;
  property_value: number;
  loan_term_years: 15 | 20 | 30;
  monthly_debt_payments: number;
  property_type: 'single_family' | 'condo' | 'pud' | '2_unit' | '3_unit' | '4_unit' | 'manufactured';
  property_state: string;
  property_county: string;
  occupancy: 'primary' | 'secondary' | 'investment';
}
```

---

### EligibilityResult (Output from eligibility check)

```python
# Python (Pydantic)
class RuleViolation(BaseModel):
    rule_name: str                       # e.g., "max_dti"
    rule_description: str                # e.g., "Maximum DTI ratio"
    actual_value: str                    # e.g., "52%"
    required_value: str                  # e.g., "≤ 50%"
    citation: str                        # e.g., "Fannie Mae B5-6-02"

class FixSuggestion(BaseModel):
    description: str                     # e.g., "Pay off $4,200 in revolving debt"
    impact: str                          # e.g., "Reduces DTI to 49.8%"
    difficulty: str                      # "easy" | "moderate" | "hard"

class ProductResult(BaseModel):
    product_name: str                    # "HomeReady" | "Home Possible"
    gse: str                             # "fannie_mae" | "freddie_mac"
    eligible: bool
    violations: list[RuleViolation]

class EligibilityResult(BaseModel):
    scenario: LoanScenario               # Echo back the input
    calculated_ltv: float                # e.g., 0.875 (87.5%)
    calculated_dti: float                # e.g., 0.52 (52%)
    products: list[ProductResult]        # Results for each product
    recommendation: str                  # Summary recommendation
    fix_suggestions: list[FixSuggestion] # How to become eligible
```

```typescript
// TypeScript
interface RuleViolation {
  rule_name: string;
  rule_description: string;
  actual_value: string;
  required_value: string;
  citation: string;
}

interface FixSuggestion {
  description: string;
  impact: string;
  difficulty: 'easy' | 'moderate' | 'hard';
}

interface ProductResult {
  product_name: 'HomeReady' | 'Home Possible';
  gse: 'fannie_mae' | 'freddie_mac';
  eligible: boolean;
  violations: RuleViolation[];
}

interface EligibilityResult {
  scenario: LoanScenario;
  calculated_ltv: number;
  calculated_dti: number;
  products: ProductResult[];
  recommendation: string;
  fix_suggestions: FixSuggestion[];
}
```

---

### ChatMessage (For RAG chat)

```python
# Python
class ChatMessage(BaseModel):
    role: str                            # "user" | "assistant"
    content: str
    citations: list[Citation] | None = None

class Citation(BaseModel):
    text: str                            # Quoted text
    source: str                          # e.g., "Fannie Mae Selling Guide B5-6-01"
    url: str | None = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None   # For conversation history

class ChatResponse(BaseModel):
    message: ChatMessage
    conversation_id: str
```

---

### PolicyUpdate (For change detection)

```python
# Python
class PolicyUpdate(BaseModel):
    id: str
    gse: str                             # "fannie_mae" | "freddie_mac"
    update_type: str                     # "lender_letter" | "bulletin" | "guide_update"
    update_number: str                   # e.g., "LL-2025-04" or "2025-16"
    title: str
    publish_date: date
    effective_date: date | None
    summary: str
    affected_sections: list[str]         # e.g., ["B5-6-01", "B3-6-02"]
    impact_analysis: str | None
    code_update: str | None              # Generated code diff
```

---

## API Endpoints

### Tab 1: Ask the Guide (RAG Chat)

```
POST /api/chat
Request: ChatRequest
Response: ChatResponse
```

### Tab 2: What Changed (Policy Updates)

```
GET /api/changes
Query params: ?gse=fannie_mae&limit=20&offset=0
Response: { updates: PolicyUpdate[], total: int }

GET /api/changes/{update_id}
Response: PolicyUpdate
```

### Tab 3: Generated Updates (Code Diffs)

```
GET /api/changes/{update_id}/code
Query params: ?format=python|typescript|yaml|json
Response: { code: string, format: string }
```

### Tab 4: Check My Loan (Eligibility)

```
POST /api/check-loan
Request: LoanScenario
Response: EligibilityResult
```

### Health Check

```
GET /api/health
Response: { status: "ok", version: string }
```

---

## Rules Engine Interface

The rules engine is a pure Python module with no external dependencies (except the data models above).

```python
# backend/app/services/rules_engine.py

class RulesEngine:
    def check_eligibility(self, scenario: LoanScenario) -> EligibilityResult:
        """
        Main entry point. Checks eligibility for both HomeReady and Home Possible.
        Returns a complete EligibilityResult with violations and fix suggestions.
        """
        pass

    def check_homeready(self, scenario: LoanScenario) -> ProductResult:
        """Check eligibility for Fannie Mae HomeReady."""
        pass

    def check_home_possible(self, scenario: LoanScenario) -> ProductResult:
        """Check eligibility for Freddie Mac Home Possible."""
        pass

    def generate_fix_suggestions(
        self,
        scenario: LoanScenario,
        violations: list[RuleViolation]
    ) -> list[FixSuggestion]:
        """Generate actionable fixes based on violations."""
        pass
```

---

## Directory Structure (Agent Ownership)

```
sage/
├── frontend/                    # FRONTEND AGENT OWNS THIS
│   ├── app/
│   │   ├── page.tsx            # Landing with tab navigation
│   │   ├── ask/page.tsx        # Tab 1: RAG Chat
│   │   ├── changes/page.tsx    # Tab 2: What Changed
│   │   ├── code/page.tsx       # Tab 3: Generated Updates
│   │   └── check/page.tsx      # Tab 4: Check My Loan
│   ├── components/
│   │   ├── ChatInterface.tsx
│   │   ├── LoanForm.tsx
│   │   ├── EligibilityResult.tsx
│   │   ├── ChangeTimeline.tsx
│   │   └── CodeDiff.tsx
│   ├── lib/
│   │   ├── api.ts              # API client
│   │   └── types.ts            # TypeScript interfaces (from above)
│   ├── package.json
│   └── tailwind.config.js
│
├── backend/
│   └── app/
│       ├── main.py             # BACKEND AGENT: FastAPI app
│       ├── config.py           # BACKEND AGENT: Settings
│       ├── routers/            # BACKEND AGENT OWNS THIS
│       │   ├── chat.py
│       │   ├── changes.py
│       │   └── eligibility.py
│       ├── models/             # BACKEND AGENT OWNS THIS
│       │   ├── loan.py
│       │   ├── eligibility.py
│       │   ├── chat.py
│       │   └── policy.py
│       ├── db/                 # BACKEND AGENT OWNS THIS
│       │   ├── connection.py
│       │   └── models.py
│       └── services/
│           ├── rules_engine.py # RULES AGENT OWNS THIS
│           ├── embeddings.py   # (Phase 2 - later)
│           └── pinecone_client.py  # (Phase 2 - later)
│
├── contracts/                   # SHARED (read-only for agents)
│   └── api_contracts.md
│
├── data/                        # Already populated
│   ├── fannie/
│   └── freddie/
│
└── scripts/
    └── scrape_guides.py
```

---

## Eligibility Rules Reference (For Rules Engine Agent)

### HomeReady (Fannie Mae)

| Rule | Requirement | Citation |
|------|-------------|----------|
| Min Credit Score | ≥ 620 | B5-6-02 |
| Max DTI | ≤ 50% | B5-6-02 |
| Max LTV | ≤ 97% (1-unit primary) | B5-6-01 |
| Income Limit | ≤ 80% AMI | B5-6-01 |
| Occupancy | Primary residence only | B5-6-01 |
| Property Types | SFR, Condo, PUD, 2-4 unit, Manufactured | B5-6-01 |
| Homeownership Ed | Required if all borrowers are first-time | B5-6-01 |

### Home Possible (Freddie Mac)

| Rule | Requirement | Citation |
|------|-------------|----------|
| Min Credit Score | ≥ 660 | 4501.5 |
| Max DTI | ≤ 45% (43% for LPA) | 4501.5 |
| Max LTV | ≤ 97% | 4501.5 |
| Income Limit | ≤ 80% AMI | 4501.5 |
| Occupancy | Primary residence only | 4501.5 |
| Property Types | SFR, Condo, Co-op, Manufactured | 4501.5 |
| Homeownership Ed | Required if first-time buyer | 4501.9 |

### 2025/2026 Loan Limits

| Area Type | 2025 | 2026 |
|-----------|------|------|
| Base (most areas) | $806,500 | $832,750 |
| High-cost areas | Up to $1,209,750 | Up to $1,249,125 |
