'use client';

import type {
  FixFinderResult,
  EnhancedFixSuggestion,
  FixSequence,
  SimulationResult,
  ReactStep,
  GuideCitation,
} from '@/lib/types';
import {
  Robot,
  Lightning,
  Coins,
  Clock,
  Target,
  ArrowRight,
  CheckCircle,
  XCircle,
  Lightbulb,
  GitBranch,
  Flask,
  BookOpen,
  CaretDown,
  CaretRight,
  Star,
} from '@phosphor-icons/react';
import { useState } from 'react';

interface FixFinderPanelProps {
  data: FixFinderResult;
  showReactTrace?: boolean;
}

function ConfidenceBadge({ confidence }: { confidence: number }) {
  const percentage = Math.round(confidence * 100);
  const color =
    percentage >= 80
      ? 'bg-success/10 text-success'
      : percentage >= 60
      ? 'bg-gold/10 text-gold-700'
      : 'bg-ink-200 text-ink-600';

  return (
    <span className={`px-2 py-0.5 text-xs font-mono font-medium rounded ${color}`}>
      {percentage}% confidence
    </span>
  );
}

function DifficultyBadge({ difficulty }: { difficulty: string }) {
  const colors: Record<string, string> = {
    easy: 'bg-success/10 text-success',
    moderate: 'bg-gold/10 text-gold-700',
    hard: 'bg-error/10 text-error',
    very_hard: 'bg-error/20 text-error',
  };

  return (
    <span className={`px-2 py-0.5 text-xs font-medium rounded ${colors[difficulty] || 'bg-ink-200 text-ink-600'}`}>
      {difficulty.replace('_', ' ')}
    </span>
  );
}

function CitationCard({ citation }: { citation: GuideCitation }) {
  return (
    <div className="bg-surface border border-border p-3 text-xs">
      <div className="flex items-center gap-2 mb-2">
        <span
          className={`gse-badge ${
            citation.gse === 'fannie_mae' ? 'gse-badge-fannie' : 'gse-badge-freddie'
          }`}
        >
          {citation.gse === 'fannie_mae' ? 'FNMA' : 'FHLMC'}
        </span>
        <span className="font-mono text-sage-700">{citation.section_id}</span>
        <span className="text-ink-400 ml-auto">{Math.round(citation.relevance_score * 100)}%</span>
      </div>
      <p className="text-ink-600 leading-relaxed line-clamp-2">{citation.snippet}</p>
    </div>
  );
}

function EnhancedFixCard({ fix, index }: { fix: EnhancedFixSuggestion; index: number }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="border-2 border-border bg-paper hover:border-sage/30 transition-colors">
      <div
        className="p-5 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-start gap-4">
          <div className="flex items-center justify-center w-8 h-8 bg-sage/10 text-sage font-mono text-sm font-bold shrink-0">
            {fix.priority_order}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <ConfidenceBadge confidence={fix.confidence} />
              <DifficultyBadge difficulty={fix.difficulty} />
              <span className="text-xs text-ink-500">{fix.estimated_timeline}</span>
            </div>
            <p className="font-medium text-ink-900 mb-1">{fix.description}</p>
            <p className="text-sm text-ink-600">{fix.impact}</p>
            {fix.unlocks_products.length > 0 && (
              <div className="flex items-center gap-2 mt-3">
                <span className="text-xs text-ink-500">Unlocks:</span>
                {fix.unlocks_products.map((product) => (
                  <span
                    key={product}
                    className={`gse-badge ${
                      product === 'HomeReady' ? 'gse-badge-fannie' : 'gse-badge-freddie'
                    }`}
                  >
                    {product}
                  </span>
                ))}
              </div>
            )}
          </div>
          <div className="shrink-0 text-ink-400">
            {isExpanded ? <CaretDown size={20} /> : <CaretRight size={20} />}
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="border-t border-border p-5 bg-surface/50 space-y-4">
          {/* Citations */}
          {fix.citations.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <BookOpen size={16} weight="thin" className="text-ink-500" />
                <span className="text-xs font-semibold text-ink-700">Guide Citations</span>
              </div>
              <div className="grid gap-2">
                {fix.citations.slice(0, 3).map((citation, i) => (
                  <CitationCard key={i} citation={citation} />
                ))}
              </div>
            </div>
          )}

          {/* Compensating Factors */}
          {fix.compensating_factors.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Star size={16} weight="thin" className="text-ink-500" />
                <span className="text-xs font-semibold text-ink-700">Compensating Factors</span>
              </div>
              <div className="space-y-2">
                {fix.compensating_factors.map((factor, i) => (
                  <div key={i} className="bg-sage/5 border border-sage/20 p-3 text-sm">
                    <p className="font-medium text-ink-900">{factor.factor_type}</p>
                    <p className="text-ink-600 text-xs mt-1">{factor.description}</p>
                    <p className="text-ink-500 text-xs mt-1">
                      <span className="font-medium">Requirement:</span> {factor.requirement}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Trade-offs */}
          {fix.trade_offs.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Target size={16} weight="thin" className="text-ink-500" />
                <span className="text-xs font-semibold text-ink-700">Trade-offs to Consider</span>
              </div>
              <ul className="space-y-1">
                {fix.trade_offs.map((tradeoff, i) => (
                  <li key={i} className="text-xs text-ink-600 flex items-start gap-2">
                    <span className="text-gold-600 mt-0.5">•</span>
                    {tradeoff}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function FixSequenceCard({ sequence }: { sequence: FixSequence }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="border-2 border-sage/30 bg-sage/5">
      <div
        className="p-5 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-start justify-between mb-3">
          <div>
            <h4 className="font-display font-semibold text-ink-900">{sequence.sequence_name}</h4>
            <p className="text-sm text-ink-600 mt-1">{sequence.description}</p>
          </div>
          <div className="shrink-0 text-ink-400">
            {isExpanded ? <CaretDown size={20} /> : <CaretRight size={20} />}
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-3 text-xs">
          <span className="bg-sage/20 text-sage-700 px-2 py-1 rounded font-medium">
            {sequence.effort_vs_benefit_score.toFixed(1)}/10 score
          </span>
          <span className="text-ink-500">{sequence.total_effort.replace('_', ' ')} effort</span>
          <span className="text-ink-500">{sequence.estimated_total_timeline}</span>
          <div className="flex items-center gap-1 ml-auto">
            {sequence.products_unlocked.map((product) => (
              <span
                key={product}
                className={`gse-badge ${
                  product === 'HomeReady' ? 'gse-badge-fannie' : 'gse-badge-freddie'
                }`}
              >
                {product}
              </span>
            ))}
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="border-t border-sage/20 p-5 bg-paper">
          <p className="text-xs text-ink-500 mb-4">Steps to complete this path:</p>
          <div className="space-y-3">
            {sequence.steps.map((step, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className="flex items-center justify-center w-6 h-6 bg-sage text-white font-mono text-xs font-bold shrink-0 rounded-full">
                  {i + 1}
                </div>
                <div>
                  <p className="text-sm font-medium text-ink-900">{step.description}</p>
                  <p className="text-xs text-ink-500 mt-1">{step.impact}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function SimulationCard({ simulation }: { simulation: SimulationResult }) {
  const isSuccessful = simulation.homeready_eligible || simulation.home_possible_eligible;

  return (
    <div className={`border p-4 ${isSuccessful ? 'border-success/30 bg-success/5' : 'border-border bg-surface'}`}>
      <div className="flex items-start gap-3">
        <div className={`p-1.5 rounded ${isSuccessful ? 'bg-success/20' : 'bg-ink-200'}`}>
          <Flask size={16} weight="thin" className={isSuccessful ? 'text-success' : 'text-ink-500'} />
        </div>
        <div className="flex-1">
          <p className="font-medium text-sm text-ink-900">{simulation.scenario_description}</p>
          <div className="flex flex-wrap gap-2 mt-2">
            {simulation.homeready_eligible && (
              <span className="flex items-center gap-1 text-xs text-success">
                <CheckCircle size={14} weight="fill" />
                HomeReady eligible
              </span>
            )}
            {simulation.home_possible_eligible && (
              <span className="flex items-center gap-1 text-xs text-success">
                <CheckCircle size={14} weight="fill" />
                Home Possible eligible
              </span>
            )}
            {!isSuccessful && (
              <span className="flex items-center gap-1 text-xs text-ink-500">
                <XCircle size={14} />
                Still ineligible
              </span>
            )}
          </div>
          {simulation.violations_resolved.length > 0 && (
            <p className="text-xs text-ink-500 mt-2">
              Resolves: {simulation.violations_resolved.join(', ')}
            </p>
          )}
        </div>
        <DifficultyBadge difficulty={simulation.feasibility} />
      </div>
    </div>
  );
}

function ReactTraceCard({ step }: { step: ReactStep }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="border border-border bg-surface">
      <div
        className="p-4 cursor-pointer hover:bg-ink-50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-7 h-7 bg-sage/10 text-sage font-mono text-sm font-bold rounded-full">
            {step.step_number}
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-medium text-sm text-ink-900 truncate">{step.action}</p>
            <p className="text-xs text-ink-500">
              {step.tool_calls.length} tool call{step.tool_calls.length !== 1 ? 's' : ''} •{' '}
              {step.findings.length} finding{step.findings.length !== 1 ? 's' : ''}
            </p>
          </div>
          <div className="shrink-0 text-ink-400">
            {isExpanded ? <CaretDown size={18} /> : <CaretRight size={18} />}
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="border-t border-border p-4 bg-paper space-y-4 text-xs">
          {/* Observation */}
          <div>
            <p className="font-semibold text-ink-700 mb-1">Observation</p>
            <p className="text-ink-600">{step.observation}</p>
          </div>

          {/* Reasoning */}
          <div>
            <p className="font-semibold text-ink-700 mb-1">Reasoning</p>
            <p className="text-ink-600">{step.reasoning}</p>
          </div>

          {/* Tool Calls */}
          {step.tool_calls.length > 0 && (
            <div>
              <p className="font-semibold text-ink-700 mb-2">Tool Calls</p>
              <div className="space-y-2">
                {step.tool_calls.map((call, i) => (
                  <div key={i} className="bg-ink-900/5 p-2 rounded font-mono">
                    <span className="text-sage-700">{call.tool_name}</span>
                    <span className="text-ink-500">(</span>
                    <span className="text-ink-700">{JSON.stringify(call.arguments)}</span>
                    <span className="text-ink-500">)</span>
                    <p className="text-ink-600 mt-1 font-sans">{call.result_summary}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Findings */}
          {step.findings.length > 0 && (
            <div>
              <p className="font-semibold text-ink-700 mb-2">Findings</p>
              <ul className="space-y-1">
                {step.findings.map((finding, i) => (
                  <li key={i} className="flex items-start gap-2 text-ink-600">
                    <Lightbulb size={14} className="text-gold-600 shrink-0 mt-0.5" />
                    {finding}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function FixFinderPanel({ data, showReactTrace = false }: FixFinderPanelProps) {
  return (
    <div className="space-y-8 mt-10 pt-10 border-t-2 border-sage/30">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-sage/10">
          <Robot size={24} weight="thin" className="text-sage" />
        </div>
        <div>
          <h2 className="font-display text-xl font-semibold text-ink-900">
            Fix Finder Agent Results
          </h2>
          <p className="text-sm text-ink-500">
            AI-powered fix suggestions with RAG retrieval and ReAct reasoning
          </p>
        </div>
      </div>

      {/* Performance Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-surface border border-border p-4">
          <div className="flex items-center gap-2 text-ink-500 mb-2">
            <Lightning size={16} weight="thin" />
            <span className="text-xs font-mono uppercase tracking-wide">Iterations</span>
          </div>
          <p className="text-2xl font-mono font-semibold text-ink-900">{data.total_iterations}</p>
        </div>
        <div className="bg-surface border border-border p-4">
          <div className="flex items-center gap-2 text-ink-500 mb-2">
            <Clock size={16} weight="thin" />
            <span className="text-xs font-mono uppercase tracking-wide">Time</span>
          </div>
          <p className="text-2xl font-mono font-semibold text-ink-900">
            {data.total_time_ms}
            <span className="text-sm text-ink-500 ml-1">ms</span>
          </p>
        </div>
        <div className="bg-surface border border-border p-4">
          <div className="flex items-center gap-2 text-ink-500 mb-2">
            <Coins size={16} weight="thin" />
            <span className="text-xs font-mono uppercase tracking-wide">Tokens</span>
          </div>
          <p className="text-2xl font-mono font-semibold text-ink-900">
            {data.tokens_used.toLocaleString()}
          </p>
        </div>
      </div>

      {/* Recommended Path */}
      {data.recommended_path && (
        <div className="bg-sage/10 border-2 border-sage/30 p-5">
          <div className="flex items-start gap-3">
            <Lightbulb size={20} weight="fill" className="text-sage shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-ink-900 mb-1">Recommended Approach</p>
              <p className="text-sm text-ink-700">{data.recommended_path}</p>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Fixes */}
      {data.enhanced_fixes.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Target size={18} weight="thin" className="text-ink-500" />
            <h3 className="text-sm font-semibold text-ink-900">Enhanced Fix Suggestions</h3>
            <span className="text-xs text-ink-500">({data.enhanced_fixes.length} fixes found)</span>
          </div>
          <div className="space-y-4">
            {data.enhanced_fixes.map((fix, index) => (
              <EnhancedFixCard key={index} fix={fix} index={index} />
            ))}
          </div>
        </div>
      )}

      {/* Fix Sequences */}
      {data.fix_sequences.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <GitBranch size={18} weight="thin" className="text-ink-500" />
            <h3 className="text-sm font-semibold text-ink-900">Multi-Step Paths to Eligibility</h3>
          </div>
          <div className="space-y-4">
            {data.fix_sequences.map((sequence, index) => (
              <FixSequenceCard key={index} sequence={sequence} />
            ))}
          </div>
        </div>
      )}

      {/* Simulations */}
      {data.simulations.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Flask size={18} weight="thin" className="text-ink-500" />
            <h3 className="text-sm font-semibold text-ink-900">What-If Simulations</h3>
            <span className="text-xs text-ink-500">({data.simulations.length} scenarios tested)</span>
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            {data.simulations.map((sim, index) => (
              <SimulationCard key={index} simulation={sim} />
            ))}
          </div>
        </div>
      )}

      {/* Product Comparison */}
      {Object.keys(data.product_comparison).length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <ArrowRight size={18} weight="thin" className="text-ink-500" />
            <h3 className="text-sm font-semibold text-ink-900">Product Comparison Insights</h3>
          </div>
          <div className="bg-surface border border-border p-4 space-y-3">
            {Object.entries(data.product_comparison).map(([key, value]) => (
              <div key={key} className="flex gap-4 text-sm">
                <span className="font-medium text-ink-700 w-40 shrink-0">{key}:</span>
                <span className="text-ink-600">{value}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ReAct Trace (Demo Mode Only) */}
      {showReactTrace && data.react_trace.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Robot size={18} weight="thin" className="text-ink-500" />
            <h3 className="text-sm font-semibold text-ink-900">ReAct Reasoning Trace</h3>
            <span className="text-xs text-ink-500">(OBSERVE → THINK → ACT loop)</span>
          </div>
          <p className="text-xs text-ink-500 mb-4">
            See how the AI agent reasoned through the problem iteratively:
          </p>
          <div className="space-y-3">
            {data.react_trace.map((step, index) => (
              <ReactTraceCard key={index} step={step} />
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="text-center text-xs text-ink-400 pt-6 border-t border-border">
        <p>
          Fix Finder Agent used ReAct pattern to iteratively search {data.tokens_used.toLocaleString()} tokens
          of GSE guidelines across {data.total_iterations} reasoning cycles.
        </p>
      </div>
    </div>
  );
}
