'use client';

import type {
  EligibilityResult as EligibilityResultType,
  ProductResult,
  RuleViolation,
  FixSuggestion,
} from '@/lib/types';

interface EligibilityResultProps {
  result: EligibilityResultType;
  onReset: () => void;
}

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function formatCurrency(value: number): string {
  return value.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
}

function getDifficultyColor(difficulty: string): string {
  switch (difficulty) {
    case 'easy':
      return 'bg-green-100 text-green-800';
    case 'moderate':
      return 'bg-amber-100 text-amber-800';
    case 'hard':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
}

function GSEBadge({ gse }: { gse: string }) {
  const isFannie = gse === 'fannie_mae';
  return (
    <span
      className={`
        inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
        ${isFannie ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}
      `}
    >
      {isFannie ? 'Fannie Mae' : 'Freddie Mac'}
    </span>
  );
}

function EligibilityBadge({ eligible }: { eligible: boolean }) {
  return (
    <span
      className={`
        inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold
        ${eligible ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}
      `}
    >
      {eligible ? (
        <>
          <svg
            className="w-4 h-4 mr-1.5"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
          Eligible
        </>
      ) : (
        <>
          <svg
            className="w-4 h-4 mr-1.5"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
          Not Eligible
        </>
      )}
    </span>
  );
}

function ProductCard({ product }: { product: ProductResult }) {
  return (
    <div
      className={`
        rounded-lg border-2 p-6
        ${product.eligible
          ? 'border-green-200 bg-green-50'
          : 'border-red-200 bg-red-50'
        }
      `}
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            {product.product_name}
          </h3>
          <GSEBadge gse={product.gse} />
        </div>
        <EligibilityBadge eligible={product.eligible} />
      </div>

      {product.violations.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            Violations ({product.violations.length})
          </h4>
          <ul className="space-y-2">
            {product.violations.map((violation, index) => (
              <ViolationItem key={index} violation={violation} />
            ))}
          </ul>
        </div>
      )}

      {product.eligible && product.violations.length === 0 && (
        <p className="text-sm text-green-700">
          All eligibility requirements met.
        </p>
      )}
    </div>
  );
}

function ViolationItem({ violation }: { violation: RuleViolation }) {
  return (
    <li className="bg-white rounded-md p-3 border border-red-100">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-red-800">
            {violation.rule_description}
          </p>
          <div className="mt-1 flex items-center space-x-4 text-sm">
            <span className="text-gray-600">
              Actual: <span className="font-medium text-red-600">{violation.actual_value}</span>
            </span>
            <span className="text-gray-600">
              Required: <span className="font-medium text-gray-900">{violation.required_value}</span>
            </span>
          </div>
        </div>
      </div>
      <p className="mt-2 text-xs text-gray-500">
        Citation: {violation.citation}
      </p>
    </li>
  );
}

function FixSuggestionCard({ suggestion }: { suggestion: FixSuggestion }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-900">
            {suggestion.description}
          </p>
          <p className="mt-1 text-sm text-gray-600">{suggestion.impact}</p>
        </div>
        <span
          className={`ml-4 px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${getDifficultyColor(
            suggestion.difficulty
          )}`}
        >
          {suggestion.difficulty}
        </span>
      </div>
    </div>
  );
}

function ScenarioSummary({ result }: { result: EligibilityResultType }) {
  const { scenario, calculated_ltv, calculated_dti } = result;

  return (
    <div className="bg-gray-50 rounded-lg p-6 mb-6">
      <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">
        Loan Scenario Summary
      </h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <p className="text-xs text-gray-500">Credit Score</p>
          <p className="text-lg font-semibold text-gray-900">
            {scenario.credit_score}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Annual Income</p>
          <p className="text-lg font-semibold text-gray-900">
            {formatCurrency(scenario.annual_income)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Loan Amount</p>
          <p className="text-lg font-semibold text-gray-900">
            {formatCurrency(scenario.loan_amount)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Property Value</p>
          <p className="text-lg font-semibold text-gray-900">
            {formatCurrency(scenario.property_value)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">LTV Ratio</p>
          <p
            className={`text-lg font-semibold ${
              calculated_ltv > 0.97
                ? 'text-red-600'
                : calculated_ltv > 0.95
                ? 'text-amber-600'
                : 'text-green-600'
            }`}
          >
            {formatPercent(calculated_ltv)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">DTI Ratio</p>
          <p
            className={`text-lg font-semibold ${
              calculated_dti > 0.50
                ? 'text-red-600'
                : calculated_dti > 0.45
                ? 'text-amber-600'
                : 'text-green-600'
            }`}
          >
            {formatPercent(calculated_dti)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Property Type</p>
          <p className="text-lg font-semibold text-gray-900 capitalize">
            {scenario.property_type.replace(/_/g, ' ')}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Location</p>
          <p className="text-lg font-semibold text-gray-900">
            {scenario.property_county}, {scenario.property_state}
          </p>
        </div>
      </div>
    </div>
  );
}

export default function EligibilityResult({
  result,
  onReset,
}: EligibilityResultProps) {
  const anyEligible = result.products.some((p) => p.eligible);
  const allEligible = result.products.every((p) => p.eligible);

  return (
    <div className="space-y-6">
      {/* Overall Status Banner */}
      <div
        className={`
          rounded-lg p-6 text-center
          ${allEligible
            ? 'bg-green-600'
            : anyEligible
            ? 'bg-amber-500'
            : 'bg-red-600'
          }
        `}
      >
        <div className="flex items-center justify-center mb-2">
          {allEligible ? (
            <svg
              className="w-12 h-12 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          ) : anyEligible ? (
            <svg
              className="w-12 h-12 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          ) : (
            <svg
              className="w-12 h-12 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          )}
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">
          {allEligible
            ? 'Congratulations!'
            : anyEligible
            ? 'Partial Eligibility'
            : 'Not Currently Eligible'}
        </h2>
        <p className="text-white text-opacity-90 max-w-2xl mx-auto">
          {result.recommendation}
        </p>
      </div>

      {/* Scenario Summary */}
      <ScenarioSummary result={result} />

      {/* Product Results */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Program Eligibility
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {result.products.map((product) => (
            <ProductCard key={product.product_name} product={product} />
          ))}
        </div>
      </div>

      {/* Fix Suggestions */}
      {result.fix_suggestions.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            How to Improve Your Eligibility
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Consider these options to improve your loan scenario:
          </p>
          <div className="space-y-3">
            {result.fix_suggestions.map((suggestion, index) => (
              <FixSuggestionCard key={index} suggestion={suggestion} />
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-4 pt-6 border-t border-gray-200">
        <button
          onClick={onReset}
          className="flex-1 px-6 py-3 rounded-lg font-semibold text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
        >
          Check Another Scenario
        </button>
        <button
          onClick={() => window.print()}
          className="px-6 py-3 rounded-lg font-semibold text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 transition-colors"
        >
          <span className="flex items-center justify-center">
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"
              />
            </svg>
            Print Results
          </span>
        </button>
      </div>

      {/* Disclaimer */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mt-6">
        <div className="flex">
          <svg
            className="w-5 h-5 text-amber-600 mt-0.5 mr-3 flex-shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          <div>
            <h4 className="text-sm font-medium text-amber-800">Disclaimer</h4>
            <p className="text-sm text-amber-700 mt-1">
              This eligibility check is for informational purposes only and does not
              constitute a loan approval or commitment. Actual eligibility may vary based
              on additional factors including income verification, asset documentation,
              property appraisal, and current lending guidelines. Please consult with a
              licensed mortgage professional for a complete assessment.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
