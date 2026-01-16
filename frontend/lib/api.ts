// SAGE API Client
// Handles all communication with the backend

import type {
  LoanScenario,
  EligibilityResult,
  ChatRequest,
  ChatResponse,
  PolicyUpdatesResponse,
  PolicyUpdate,
  CodeResponse,
  CodeFormat,
  HealthResponse,
  GSE,
} from './types';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Custom error class for API errors
export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    message?: string
  ) {
    super(message || `API Error: ${status} ${statusText}`);
    this.name = 'ApiError';
  }
}

// Generic fetch wrapper with error handling
async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };

  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorBody = await response.text().catch(() => '');
    throw new ApiError(response.status, response.statusText, errorBody);
  }

  return response.json();
}

// ============================================
// Tab 1: Ask the Guide (RAG Chat)
// ============================================

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  return fetchApi<ChatResponse>('/chat', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

// ============================================
// Tab 2: What Changed (Policy Updates)
// ============================================

export interface GetChangesParams {
  gse?: GSE;
  limit?: number;
  offset?: number;
}

export async function getChanges(params: GetChangesParams = {}): Promise<PolicyUpdatesResponse> {
  const searchParams = new URLSearchParams();
  if (params.gse) searchParams.set('gse', params.gse);
  if (params.limit) searchParams.set('limit', params.limit.toString());
  if (params.offset) searchParams.set('offset', params.offset.toString());

  const queryString = searchParams.toString();
  const endpoint = `/changes${queryString ? `?${queryString}` : ''}`;

  return fetchApi<PolicyUpdatesResponse>(endpoint);
}

export async function getChangeById(updateId: string): Promise<PolicyUpdate> {
  return fetchApi<PolicyUpdate>(`/changes/${updateId}`);
}

// ============================================
// Tab 3: Generated Updates (Code Diffs)
// ============================================

export async function getChangeCode(
  updateId: string,
  format: CodeFormat = 'python'
): Promise<CodeResponse> {
  return fetchApi<CodeResponse>(`/changes/${updateId}/code?format=${format}`);
}

// ============================================
// Tab 4: Check My Loan (Eligibility)
// ============================================

export async function checkLoanEligibility(
  scenario: LoanScenario
): Promise<EligibilityResult> {
  return fetchApi<EligibilityResult>('/check-loan', {
    method: 'POST',
    body: JSON.stringify(scenario),
  });
}

// ============================================
// Health Check
// ============================================

export async function checkHealth(): Promise<HealthResponse> {
  return fetchApi<HealthResponse>('/health');
}

// ============================================
// Mock Data (for development when API is not ready)
// ============================================

export const mockEligibilityResult: EligibilityResult = {
  scenario: {
    credit_score: 680,
    annual_income: 75000,
    is_first_time_buyer: true,
    loan_amount: 350000,
    property_value: 400000,
    loan_term_years: 30,
    monthly_debt_payments: 500,
    property_type: 'single_family',
    property_state: 'CA',
    property_county: 'Los Angeles',
    occupancy: 'primary',
  },
  calculated_ltv: 0.875,
  calculated_dti: 0.48,
  products: [
    {
      product_name: 'HomeReady',
      gse: 'fannie_mae',
      eligible: true,
      violations: [],
    },
    {
      product_name: 'Home Possible',
      gse: 'freddie_mac',
      eligible: false,
      violations: [
        {
          rule_name: 'max_dti',
          rule_description: 'Maximum Debt-to-Income Ratio',
          actual_value: '48%',
          required_value: '<= 45%',
          citation: 'Freddie Mac Guide 4501.5',
        },
      ],
    },
  ],
  recommendation:
    'Your loan scenario qualifies for Fannie Mae HomeReady. Consider reducing your monthly debt payments to also qualify for Freddie Mac Home Possible, which may offer better terms.',
  fix_suggestions: [
    {
      description: 'Pay off $3,500 in credit card debt',
      impact: 'Reduces DTI to 44.8%, qualifying for Home Possible',
      difficulty: 'moderate',
    },
    {
      description: 'Increase down payment by $20,000',
      impact: 'Reduces LTV to 82.5% and may lower PMI costs',
      difficulty: 'hard',
    },
  ],
};

export const mockPolicyUpdates: PolicyUpdate[] = [
  {
    id: 'LL-2025-04',
    gse: 'fannie_mae',
    update_type: 'lender_letter',
    update_number: 'LL-2025-04',
    title: 'HomeReady Income Limit Updates for 2025',
    publish_date: '2025-01-15',
    effective_date: '2025-02-01',
    summary:
      'Updates to the Area Median Income (AMI) limits for HomeReady eligibility. Most areas see a 4-5% increase in income limits.',
    affected_sections: ['B5-6-01', 'B5-6-02'],
    impact_analysis:
      'More borrowers will qualify for HomeReady due to increased income limits.',
  },
  {
    id: 'B2025-16',
    gse: 'freddie_mac',
    update_type: 'bulletin',
    update_number: '2025-16',
    title: 'Home Possible DTI Flexibilities',
    publish_date: '2025-01-10',
    effective_date: '2025-01-20',
    summary:
      'Introduces new DTI flexibility for Home Possible loans with strong compensating factors.',
    affected_sections: ['4501.5', '4501.9'],
    impact_analysis:
      'Borrowers with credit scores above 700 may qualify with DTI up to 50%.',
  },
];

// Mock API functions for development
export async function mockCheckLoanEligibility(
  scenario: LoanScenario
): Promise<EligibilityResult> {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 1000));

  // Calculate LTV and DTI
  const ltv = scenario.loan_amount / scenario.property_value;
  const monthlyIncome = scenario.annual_income / 12;
  // Estimate monthly mortgage payment (rough calculation)
  const estimatedMonthlyPayment = (scenario.loan_amount * 0.006); // ~7.2% annual rate approximation
  const totalMonthlyDebt = scenario.monthly_debt_payments + estimatedMonthlyPayment;
  const dti = totalMonthlyDebt / monthlyIncome;

  const violations: { homeReady: import('./types').RuleViolation[]; homePossible: import('./types').RuleViolation[] } = {
    homeReady: [],
    homePossible: [],
  };

  // Check HomeReady rules
  if (scenario.credit_score < 620) {
    violations.homeReady.push({
      rule_name: 'min_credit_score',
      rule_description: 'Minimum Credit Score',
      actual_value: scenario.credit_score.toString(),
      required_value: '>= 620',
      citation: 'Fannie Mae Guide B5-6-02',
    });
  }
  if (dti > 0.50) {
    violations.homeReady.push({
      rule_name: 'max_dti',
      rule_description: 'Maximum Debt-to-Income Ratio',
      actual_value: `${(dti * 100).toFixed(1)}%`,
      required_value: '<= 50%',
      citation: 'Fannie Mae Guide B5-6-02',
    });
  }
  if (ltv > 0.97) {
    violations.homeReady.push({
      rule_name: 'max_ltv',
      rule_description: 'Maximum Loan-to-Value Ratio',
      actual_value: `${(ltv * 100).toFixed(1)}%`,
      required_value: '<= 97%',
      citation: 'Fannie Mae Guide B5-6-01',
    });
  }
  if (scenario.occupancy !== 'primary') {
    violations.homeReady.push({
      rule_name: 'occupancy',
      rule_description: 'Primary Residence Required',
      actual_value: scenario.occupancy,
      required_value: 'primary',
      citation: 'Fannie Mae Guide B5-6-01',
    });
  }

  // Check Home Possible rules
  if (scenario.credit_score < 660) {
    violations.homePossible.push({
      rule_name: 'min_credit_score',
      rule_description: 'Minimum Credit Score',
      actual_value: scenario.credit_score.toString(),
      required_value: '>= 660',
      citation: 'Freddie Mac Guide 4501.5',
    });
  }
  if (dti > 0.45) {
    violations.homePossible.push({
      rule_name: 'max_dti',
      rule_description: 'Maximum Debt-to-Income Ratio',
      actual_value: `${(dti * 100).toFixed(1)}%`,
      required_value: '<= 45%',
      citation: 'Freddie Mac Guide 4501.5',
    });
  }
  if (ltv > 0.97) {
    violations.homePossible.push({
      rule_name: 'max_ltv',
      rule_description: 'Maximum Loan-to-Value Ratio',
      actual_value: `${(ltv * 100).toFixed(1)}%`,
      required_value: '<= 97%',
      citation: 'Freddie Mac Guide 4501.5',
    });
  }
  if (scenario.occupancy !== 'primary') {
    violations.homePossible.push({
      rule_name: 'occupancy',
      rule_description: 'Primary Residence Required',
      actual_value: scenario.occupancy,
      required_value: 'primary',
      citation: 'Freddie Mac Guide 4501.5',
    });
  }

  const homeReadyEligible = violations.homeReady.length === 0;
  const homePossibleEligible = violations.homePossible.length === 0;

  // Generate fix suggestions
  const fixSuggestions: import('./types').FixSuggestion[] = [];

  if (dti > 0.45) {
    const excessDti = dti - 0.45;
    const debtReductionNeeded = excessDti * monthlyIncome;
    fixSuggestions.push({
      description: `Reduce monthly debt payments by $${Math.ceil(debtReductionNeeded).toLocaleString()}`,
      impact: 'Brings DTI below 45%, qualifying for Home Possible',
      difficulty: 'moderate',
    });
  }

  if (ltv > 0.90) {
    const additionalDownPayment = (ltv - 0.90) * scenario.property_value;
    fixSuggestions.push({
      description: `Increase down payment by $${Math.ceil(additionalDownPayment).toLocaleString()}`,
      impact: 'Reduces LTV to 90%, potentially lowering PMI costs',
      difficulty: 'hard',
    });
  }

  if (scenario.credit_score < 660 && scenario.credit_score >= 620) {
    fixSuggestions.push({
      description: 'Improve credit score to 660+',
      impact: 'Opens eligibility for Freddie Mac Home Possible',
      difficulty: 'moderate',
    });
  }

  // Generate recommendation
  let recommendation = '';
  if (homeReadyEligible && homePossibleEligible) {
    recommendation =
      'Congratulations! Your loan scenario qualifies for both Fannie Mae HomeReady and Freddie Mac Home Possible. Compare rates from lenders offering both programs.';
  } else if (homeReadyEligible) {
    recommendation =
      'Your loan scenario qualifies for Fannie Mae HomeReady. Review the fix suggestions to potentially qualify for Freddie Mac Home Possible as well.';
  } else if (homePossibleEligible) {
    recommendation =
      'Your loan scenario qualifies for Freddie Mac Home Possible. Review the fix suggestions to potentially qualify for Fannie Mae HomeReady as well.';
  } else {
    recommendation =
      'Your loan scenario does not currently qualify for either program. Review the violations and fix suggestions below to improve your eligibility.';
  }

  return {
    scenario,
    calculated_ltv: ltv,
    calculated_dti: dti,
    products: [
      {
        product_name: 'HomeReady',
        gse: 'fannie_mae',
        eligible: homeReadyEligible,
        violations: violations.homeReady,
      },
      {
        product_name: 'Home Possible',
        gse: 'freddie_mac',
        eligible: homePossibleEligible,
        violations: violations.homePossible,
      },
    ],
    recommendation,
    fix_suggestions: fixSuggestions,
  };
}
