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
    <div className="bg-paper p-6 md:p-8 flex flex-col">
      {/* GSE Badge */}
      <div className={`gse-badge ${gseClass} mb-5`}>
        {product.gse === 'fannie_mae' ? 'Fannie Mae' : 'Freddie Mac'}
      </div>

      {/* Product Name */}
      <h3 className="font-display text-xl md:text-2xl font-semibold mb-6">
        {product.product_name}
      </h3>

      {/* Stamp */}
      <div className="flex justify-center my-8">
        <Stamp
          eligible={product.eligible}
          productName={product.product_name}
          citation={primaryCitation}
        />
      </div>

      {/* Violations */}
      {product.violations.length > 0 && (
        <div className="mt-auto">
          <h4 className="text-sm font-semibold text-ink-500 mb-4 flex items-center gap-2">
            <Warning size={18} weight="thin" />
            Violations ({product.violations.length})
          </h4>
          <ul className="space-y-4">
            {product.violations.map((violation, index) => (
              <ViolationItem key={index} violation={violation} />
            ))}
          </ul>
        </div>
      )}

      {/* Success message */}
      {product.eligible && product.violations.length === 0 && (
        <p className="mt-auto text-success flex items-center gap-2 font-medium">
          <CheckCircle size={20} weight="fill" />
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
    easy: 'bg-success/10 text-success border-success/20',
    moderate: 'bg-gold-500/10 text-gold-600 border-gold-500/20',
    hard: 'bg-error/10 text-error border-error/20',
  };

  return (
    <div className="flex items-start gap-5 p-5 md:p-6 bg-surface border border-border hover:border-sage-600/50 transition-colors">
      <div className="p-2 bg-gold-500/10">
        <Lightbulb size={24} weight="thin" className="text-gold-500" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-semibold text-ink-900">{suggestion.description}</p>
        <p className="text-sm text-ink-500 mt-2 leading-relaxed">{suggestion.impact}</p>
      </div>
      <span
        className={`px-3 py-1.5 text-xs font-mono uppercase tracking-wide border ${
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
    <div className="bg-surface border-2 border-border p-6 md:p-8 mb-10 animate-fade-up">
      <h3 className="text-xs font-mono uppercase tracking-widest text-ink-500 mb-6">
        Loan Scenario Summary
      </h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-8">
        <div>
          <p className="text-xs text-ink-500 mb-2">Credit Score</p>
          <p className="text-3xl font-mono font-semibold text-ink-900">
            {scenario.credit_score}
          </p>
        </div>
        <div>
          <p className="text-xs text-ink-500 mb-2">LTV Ratio</p>
          <p className={`text-3xl font-mono font-semibold ${getLtvColor(calculated_ltv)}`}>
            {formatPercent(calculated_ltv)}
          </p>
        </div>
        <div>
          <p className="text-xs text-ink-500 mb-2">DTI Ratio</p>
          <p className={`text-3xl font-mono font-semibold ${getDtiColor(calculated_dti)}`}>
            {formatPercent(calculated_dti)}
          </p>
        </div>
        <div>
          <p className="text-xs text-ink-500 mb-2">Loan Amount</p>
          <p className="text-3xl font-mono font-semibold text-ink-900">
            {formatCurrency(scenario.loan_amount)}
          </p>
        </div>
      </div>
      <div className="divider my-8" />
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-sm">
        <div>
          <p className="text-xs text-ink-500 mb-1">Property Value</p>
          <p className="font-mono text-ink-900 font-medium">{formatCurrency(scenario.property_value)}</p>
        </div>
        <div>
          <p className="text-xs text-ink-500 mb-1">Annual Income</p>
          <p className="font-mono text-ink-900 font-medium">{formatCurrency(scenario.annual_income)}</p>
        </div>
        <div>
          <p className="text-xs text-ink-500 mb-1">Property Type</p>
          <p className="text-ink-900 capitalize font-medium">{scenario.property_type.replace(/_/g, ' ')}</p>
        </div>
        <div>
          <p className="text-xs text-ink-500 mb-1">Location</p>
          <p className="text-ink-900 font-medium">{scenario.property_county}, {scenario.property_state}</p>
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
    <div className="space-y-10">
      {/* Recommendation Banner */}
      <div
        className={`p-6 md:p-8 animate-fade-up ${
          allEligible
            ? 'bg-success/10 border-2 border-success/30'
            : anyEligible
            ? 'bg-gold-500/10 border-2 border-gold-500/30'
            : 'bg-error/10 border-2 border-error/30'
        }`}
      >
        <p className="text-lg md:text-xl text-ink-900 leading-relaxed font-medium">
          {result.recommendation}
        </p>
      </div>

      {/* Scenario Summary */}
      <ScenarioSummary result={result} />

      {/* Split Comparison View */}
      <div className="animate-fade-up" style={{ animationDelay: '100ms' }}>
        <h2 className="font-display text-xl md:text-2xl font-semibold mb-6">
          Program Eligibility
        </h2>
        <div className="grid md:grid-cols-2 gap-px bg-border border-2 border-border">
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
        <div className="animate-fade-up" style={{ animationDelay: '150ms' }}>
          <h2 className="font-display text-xl md:text-2xl font-semibold mb-3">
            How to Improve
          </h2>
          <p className="text-ink-500 mb-6">
            Consider these options to improve your eligibility:
          </p>
          <div className="space-y-4">
            {result.fix_suggestions.map((suggestion, index) => (
              <FixSuggestionCard key={index} suggestion={suggestion} />
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-4 pt-8 border-t border-border animate-fade-up" style={{ animationDelay: '200ms' }}>
        <button
          onClick={onReset}
          className="btn btn-primary btn-lg flex-1 inline-flex items-center justify-center gap-3"
        >
          <ArrowCounterClockwise size={20} weight="bold" />
          Check Another Scenario
        </button>
        <button
          onClick={() => window.print()}
          className="btn btn-secondary btn-lg inline-flex items-center justify-center gap-2"
        >
          <Printer size={20} weight="thin" />
          Print Results
        </button>
      </div>

      {/* Disclaimer */}
      <div className="p-5 md:p-6 bg-gold-500/5 border border-gold-500/20">
        <div className="flex gap-4">
          <Warning size={24} weight="thin" className="text-gold-600 mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-semibold text-ink-900">Disclaimer</p>
            <p className="text-sm text-ink-500 mt-2 leading-relaxed">
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
