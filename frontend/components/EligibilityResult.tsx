'use client';

import type {
  EligibilityResult as EligibilityResultType,
  ProductResult,
  RuleViolation,
  FixSuggestion,
} from '@/lib/types';
import {
  CheckCircle,
  XCircle,
  Lightbulb,
  ArrowCounterClockwise,
  Printer,
  Warning,
} from '@phosphor-icons/react';

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

function Stamp({ eligible, productName, citation }: { eligible: boolean; productName: string; citation?: string }) {
  return (
    <div
      className={`stamp stamp-animate ${eligible ? 'stamp-eligible' : 'stamp-ineligible'}`}
    >
      <div className="flex items-center gap-2 text-lg font-bold">
        {eligible ? (
          <CheckCircle size={20} weight="bold" />
        ) : (
          <XCircle size={20} weight="bold" />
        )}
        {eligible ? 'ELIGIBLE' : 'INELIGIBLE'}
      </div>
      <div className="text-xs mt-1 opacity-80">
        {productName.toUpperCase()}
      </div>
      {citation && (
        <div className="text-[10px] mt-1 opacity-60">
          {citation}
        </div>
      )}
    </div>
  );
}

function ProductCard({ product, gseClass }: { product: ProductResult; gseClass: string }) {
  const primaryCitation = product.violations.length > 0
    ? product.violations[0].citation
    : product.gse === 'fannie_mae' ? 'FNMA B5-6' : 'FHLMC 4501';

  return (
    <div className="bg-paper p-6 flex flex-col">
      {/* GSE Badge */}
      <div className={`gse-badge ${gseClass} mb-4`}>
        {product.gse === 'fannie_mae' ? 'Fannie Mae' : 'Freddie Mac'}
      </div>

      {/* Product Name */}
      <h3 className="font-display text-xl font-semibold mb-4">
        {product.product_name}
      </h3>

      {/* Stamp */}
      <div className="flex justify-center my-6">
        <Stamp
          eligible={product.eligible}
          productName={product.product_name}
          citation={primaryCitation}
        />
      </div>

      {/* Violations */}
      {product.violations.length > 0 && (
        <div className="mt-auto">
          <h4 className="text-sm font-medium text-ink-500 mb-3 flex items-center gap-2">
            <Warning size={16} weight="thin" />
            Violations ({product.violations.length})
          </h4>
          <ul className="space-y-3">
            {product.violations.map((violation, index) => (
              <ViolationItem key={index} violation={violation} />
            ))}
          </ul>
        </div>
      )}

      {/* Success message */}
      {product.eligible && product.violations.length === 0 && (
        <p className="mt-auto text-sm text-success flex items-center gap-2">
          <CheckCircle size={16} weight="thin" />
          All requirements met
        </p>
      )}
    </div>
  );
}

function ViolationItem({ violation }: { violation: RuleViolation }) {
  return (
    <li className="text-sm border-l-2 border-error/30 pl-3 py-1">
      <p className="font-medium text-ink-900">{violation.rule_description}</p>
      <div className="flex gap-4 mt-1 font-mono text-xs">
        <span className="text-error">
          Actual: {violation.actual_value}
        </span>
        <span className="text-ink-500">
          Required: {violation.required_value}
        </span>
      </div>
      <p className="text-xs text-ink-500 mt-1">
        {violation.citation}
      </p>
    </li>
  );
}

function FixSuggestionCard({ suggestion }: { suggestion: FixSuggestion }) {
  const difficultyColors = {
    easy: 'bg-success/10 text-success',
    moderate: 'bg-gold-500/10 text-gold-600',
    hard: 'bg-error/10 text-error',
  };

  return (
    <div className="flex items-start gap-4 p-4 bg-surface border border-border">
      <Lightbulb size={20} weight="thin" className="text-gold-500 mt-0.5 flex-shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="font-medium text-ink-900">{suggestion.description}</p>
        <p className="text-sm text-ink-500 mt-1">{suggestion.impact}</p>
      </div>
      <span
        className={`px-2 py-1 text-xs font-mono uppercase tracking-wide ${
          difficultyColors[suggestion.difficulty]
        }`}
      >
        {suggestion.difficulty}
      </span>
    </div>
  );
}

function ScenarioSummary({ result }: { result: EligibilityResultType }) {
  const { scenario, calculated_ltv, calculated_dti } = result;

  const getLtvColor = (ltv: number) => {
    if (ltv > 0.97) return 'text-error';
    if (ltv > 0.95) return 'text-gold-600';
    return 'text-success';
  };

  const getDtiColor = (dti: number) => {
    if (dti > 0.50) return 'text-error';
    if (dti > 0.45) return 'text-gold-600';
    return 'text-success';
  };

  return (
    <div className="bg-surface border border-border p-6 mb-8">
      <h3 className="text-xs font-mono uppercase tracking-wider text-ink-500 mb-4">
        Loan Scenario Summary
      </h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div>
          <p className="text-xs text-ink-500 mb-1">Credit Score</p>
          <p className="text-2xl font-mono font-medium text-ink-900">
            {scenario.credit_score}
          </p>
        </div>
        <div>
          <p className="text-xs text-ink-500 mb-1">LTV Ratio</p>
          <p className={`text-2xl font-mono font-medium ${getLtvColor(calculated_ltv)}`}>
            {formatPercent(calculated_ltv)}
          </p>
        </div>
        <div>
          <p className="text-xs text-ink-500 mb-1">DTI Ratio</p>
          <p className={`text-2xl font-mono font-medium ${getDtiColor(calculated_dti)}`}>
            {formatPercent(calculated_dti)}
          </p>
        </div>
        <div>
          <p className="text-xs text-ink-500 mb-1">Loan Amount</p>
          <p className="text-2xl font-mono font-medium text-ink-900">
            {formatCurrency(scenario.loan_amount)}
          </p>
        </div>
      </div>
      <div className="divider" />
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-sm">
        <div>
          <p className="text-xs text-ink-500 mb-1">Property Value</p>
          <p className="font-mono text-ink-900">{formatCurrency(scenario.property_value)}</p>
        </div>
        <div>
          <p className="text-xs text-ink-500 mb-1">Annual Income</p>
          <p className="font-mono text-ink-900">{formatCurrency(scenario.annual_income)}</p>
        </div>
        <div>
          <p className="text-xs text-ink-500 mb-1">Property Type</p>
          <p className="text-ink-900 capitalize">{scenario.property_type.replace(/_/g, ' ')}</p>
        </div>
        <div>
          <p className="text-xs text-ink-500 mb-1">Location</p>
          <p className="text-ink-900">{scenario.property_county}, {scenario.property_state}</p>
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
    <div className="space-y-8">
      {/* Recommendation Banner */}
      <div
        className={`p-6 ${
          allEligible
            ? 'bg-success/10 border border-success/20'
            : anyEligible
            ? 'bg-gold-500/10 border border-gold-500/20'
            : 'bg-error/10 border border-error/20'
        }`}
      >
        <p className="text-lg text-ink-900 leading-relaxed">
          {result.recommendation}
        </p>
      </div>

      {/* Scenario Summary */}
      <ScenarioSummary result={result} />

      {/* Split Comparison View */}
      <div>
        <h2 className="font-display text-xl font-semibold mb-4">
          Program Eligibility
        </h2>
        <div className="grid md:grid-cols-2 gap-px bg-border border border-border">
          {result.products.map((product) => (
            <ProductCard
              key={product.product_name}
              product={product}
              gseClass={product.gse === 'fannie_mae' ? 'gse-badge-fannie' : 'gse-badge-freddie'}
            />
          ))}
        </div>
      </div>

      {/* Fix Suggestions */}
      {result.fix_suggestions.length > 0 && (
        <div>
          <h2 className="font-display text-xl font-semibold mb-2">
            How to Improve
          </h2>
          <p className="text-sm text-ink-500 mb-4">
            Consider these options to improve your eligibility:
          </p>
          <div className="space-y-3">
            {result.fix_suggestions.map((suggestion, index) => (
              <FixSuggestionCard key={index} suggestion={suggestion} />
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-4 pt-6 border-t border-border">
        <button
          onClick={onReset}
          className="btn btn-primary flex-1 inline-flex items-center justify-center gap-2"
        >
          <ArrowCounterClockwise size={18} weight="bold" />
          Check Another Scenario
        </button>
        <button
          onClick={() => window.print()}
          className="btn btn-secondary inline-flex items-center justify-center gap-2"
        >
          <Printer size={18} weight="thin" />
          Print Results
        </button>
      </div>

      {/* Disclaimer */}
      <div className="p-4 bg-gold-500/5 border border-gold-500/20">
        <div className="flex gap-3">
          <Warning size={20} weight="thin" className="text-gold-600 mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-medium text-ink-900 text-sm">Disclaimer</p>
            <p className="text-sm text-ink-500 mt-1">
              This eligibility check is for informational purposes only. Actual eligibility
              depends on additional factors including income verification, asset documentation,
              and property appraisal. Consult a licensed mortgage professional.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
