// SAGE TypeScript Interfaces
// Generated from contracts/api_contracts.md

// ============================================
// Loan Eligibility Types
// ============================================

export type PropertyType =
  | 'single_family'
  | 'condo'
  | 'pud'
  | '2_unit'
  | '3_unit'
  | '4_unit'
  | 'manufactured';

export type Occupancy = 'primary' | 'secondary' | 'investment';

export type LoanTerm = 15 | 20 | 30;

export interface LoanScenario {
  // Borrower
  credit_score: number;
  annual_income: number;
  is_first_time_buyer: boolean;

  // Loan
  loan_amount: number;
  property_value: number;
  loan_term_years: LoanTerm;

  // Debt (for DTI calculation)
  monthly_debt_payments: number;

  // Property
  property_type: PropertyType;
  property_state: string;
  property_county: string;
  occupancy: Occupancy;
}

export interface RuleViolation {
  rule_name: string;
  rule_description: string;
  actual_value: string;
  required_value: string;
  citation: string;
}

export type Difficulty = 'easy' | 'moderate' | 'hard';

export interface FixSuggestion {
  description: string;
  impact: string;
  difficulty: Difficulty;
}

export type ProductName = 'HomeReady' | 'Home Possible';
export type GSE = 'fannie_mae' | 'freddie_mac';

export interface ProductResult {
  product_name: ProductName;
  gse: GSE;
  eligible: boolean;
  violations: RuleViolation[];
}

export interface EligibilityResult {
  scenario: LoanScenario;
  calculated_ltv: number;
  calculated_dti: number;
  products: ProductResult[];
  recommendation: string;
  fix_suggestions: FixSuggestion[];
  // Demo mode data (optional - only present when demo_mode=true)
  demo_data?: DemoModeData;
}

// ============================================
// Demo Mode Types (for SVP presentation)
// ============================================

export type ViewMode = 'lo' | 'demo';

export interface RAGRetrieval {
  query: string;
  section_id: string;
  section_title: string;
  gse: GSE;
  relevance_score: number;
  snippet: string;
}

export interface ReasoningStep {
  rule: string;
  product: ProductName;
  check: string;
  result: 'pass' | 'fail';
  citation: string;
  details: string;
}

export interface DemoModeData {
  // Parsed scenario (from NL input)
  parsed_input?: {
    raw_text: string;
    extracted_fields: Record<string, string | number | boolean>;
  };
  // RAG retrieval results
  rag_retrievals: RAGRetrieval[];
  retrieval_time_ms: number;
  // Reasoning chain
  reasoning_steps: ReasoningStep[];
  reasoning_time_ms: number;
  // Token usage
  tokens_input: number;
  tokens_output: number;
  // Index stats
  index_stats: {
    total_pages: number;
    total_sections: number;
    total_vectors: number;
  };
}

// ============================================
// Chat Types (Tab 1: Ask the Guide)
// ============================================

export type ChatRole = 'user' | 'assistant';

export interface Citation {
  text: string;
  source: string;
  url?: string;
}

export interface ChatMessage {
  role: ChatRole;
  content: string;
  citations?: Citation[];
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  message: ChatMessage;
  conversation_id: string;
}

// ============================================
// Policy Update Types (Tab 2: What Changed)
// ============================================

export type UpdateType = 'lender_letter' | 'bulletin' | 'guide_update';

export interface PolicyUpdate {
  id: string;
  gse: GSE;
  update_type: UpdateType;
  update_number: string;
  title: string;
  publish_date: string; // ISO date string
  effective_date?: string; // ISO date string
  summary: string;
  affected_sections: string[];
  impact_analysis?: string;
  code_update?: string;
}

export interface PolicyUpdatesResponse {
  updates: PolicyUpdate[];
  total: number;
}

// ============================================
// Code Generation Types (Tab 3: Generated Updates)
// ============================================

export type CodeFormat = 'python' | 'typescript' | 'yaml' | 'json';

export interface CodeResponse {
  code: string;
  format: CodeFormat;
}

// ============================================
// Health Check
// ============================================

export interface HealthResponse {
  status: 'ok' | 'error';
  version: string;
}

// ============================================
// Form State Types (Frontend-only)
// ============================================

export interface LoanFormData {
  credit_score: string;
  annual_income: string;
  is_first_time_buyer: boolean;
  loan_amount: string;
  property_value: string;
  loan_term_years: LoanTerm;
  monthly_debt_payments: string;
  property_type: PropertyType;
  property_state: string;
  property_county: string;
  occupancy: Occupancy;
}

export interface FormErrors {
  [key: string]: string | undefined;
}

// ============================================
// US States for dropdown
// ============================================

export const US_STATES = [
  { code: 'AL', name: 'Alabama' },
  { code: 'AK', name: 'Alaska' },
  { code: 'AZ', name: 'Arizona' },
  { code: 'AR', name: 'Arkansas' },
  { code: 'CA', name: 'California' },
  { code: 'CO', name: 'Colorado' },
  { code: 'CT', name: 'Connecticut' },
  { code: 'DE', name: 'Delaware' },
  { code: 'FL', name: 'Florida' },
  { code: 'GA', name: 'Georgia' },
  { code: 'HI', name: 'Hawaii' },
  { code: 'ID', name: 'Idaho' },
  { code: 'IL', name: 'Illinois' },
  { code: 'IN', name: 'Indiana' },
  { code: 'IA', name: 'Iowa' },
  { code: 'KS', name: 'Kansas' },
  { code: 'KY', name: 'Kentucky' },
  { code: 'LA', name: 'Louisiana' },
  { code: 'ME', name: 'Maine' },
  { code: 'MD', name: 'Maryland' },
  { code: 'MA', name: 'Massachusetts' },
  { code: 'MI', name: 'Michigan' },
  { code: 'MN', name: 'Minnesota' },
  { code: 'MS', name: 'Mississippi' },
  { code: 'MO', name: 'Missouri' },
  { code: 'MT', name: 'Montana' },
  { code: 'NE', name: 'Nebraska' },
  { code: 'NV', name: 'Nevada' },
  { code: 'NH', name: 'New Hampshire' },
  { code: 'NJ', name: 'New Jersey' },
  { code: 'NM', name: 'New Mexico' },
  { code: 'NY', name: 'New York' },
  { code: 'NC', name: 'North Carolina' },
  { code: 'ND', name: 'North Dakota' },
  { code: 'OH', name: 'Ohio' },
  { code: 'OK', name: 'Oklahoma' },
  { code: 'OR', name: 'Oregon' },
  { code: 'PA', name: 'Pennsylvania' },
  { code: 'RI', name: 'Rhode Island' },
  { code: 'SC', name: 'South Carolina' },
  { code: 'SD', name: 'South Dakota' },
  { code: 'TN', name: 'Tennessee' },
  { code: 'TX', name: 'Texas' },
  { code: 'UT', name: 'Utah' },
  { code: 'VT', name: 'Vermont' },
  { code: 'VA', name: 'Virginia' },
  { code: 'WA', name: 'Washington' },
  { code: 'WV', name: 'West Virginia' },
  { code: 'WI', name: 'Wisconsin' },
  { code: 'WY', name: 'Wyoming' },
  { code: 'DC', name: 'District of Columbia' },
] as const;

export const PROPERTY_TYPES: { value: PropertyType; label: string }[] = [
  { value: 'single_family', label: 'Single Family Home' },
  { value: 'condo', label: 'Condominium' },
  { value: 'pud', label: 'Planned Unit Development (PUD)' },
  { value: '2_unit', label: '2-Unit Property' },
  { value: '3_unit', label: '3-Unit Property' },
  { value: '4_unit', label: '4-Unit Property' },
  { value: 'manufactured', label: 'Manufactured Home' },
];

export const OCCUPANCY_TYPES: { value: Occupancy; label: string }[] = [
  { value: 'primary', label: 'Primary Residence' },
  { value: 'secondary', label: 'Secondary/Vacation Home' },
  { value: 'investment', label: 'Investment Property' },
];

export const LOAN_TERMS: { value: LoanTerm; label: string }[] = [
  { value: 30, label: '30 Years' },
  { value: 20, label: '20 Years' },
  { value: 15, label: '15 Years' },
];
