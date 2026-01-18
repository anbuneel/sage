'use client';

import type { DemoModeData, RAGRetrieval, ReasoningStep } from '@/lib/types';
import {
  MagnifyingGlass,
  Brain,
  Clock,
  Database,
  Coins,
  CheckCircle,
  XCircle,
  ArrowRight,
  BookOpen,
  Lightning,
} from '@phosphor-icons/react';

interface DemoModePanelProps {
  data: DemoModeData;
}

function StatCard({
  icon,
  label,
  value,
  unit,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  unit?: string;
}) {
  return (
    <div className="bg-surface border border-border p-4">
      <div className="flex items-center gap-2 text-ink-500 mb-2">
        {icon}
        <span className="text-xs font-mono uppercase tracking-wide">{label}</span>
      </div>
      <p className="text-2xl font-mono font-semibold text-ink-900">
        {value}
        {unit && <span className="text-sm text-ink-500 ml-1">{unit}</span>}
      </p>
    </div>
  );
}

function RAGRetrievalCard({ retrieval, index }: { retrieval: RAGRetrieval; index: number }) {
  return (
    <div className="border border-border bg-surface p-4 hover:border-sage-600/50 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="flex items-center justify-center w-6 h-6 bg-sage-600/10 text-sage-600 font-mono text-xs font-bold">
            {index + 1}
          </span>
          <span
            className={`gse-badge ${
              retrieval.gse === 'fannie_mae' ? 'gse-badge-fannie' : 'gse-badge-freddie'
            }`}
          >
            {retrieval.gse === 'fannie_mae' ? 'FNMA' : 'FHLMC'}
          </span>
        </div>
        <span className="font-mono text-xs text-ink-500">
          {(retrieval.relevance_score * 100).toFixed(1)}% match
        </span>
      </div>
      <p className="font-mono text-xs text-sage-700 mb-2">{retrieval.section_id}</p>
      <p className="text-sm font-medium text-ink-900 mb-2">{retrieval.section_title}</p>
      <p className="text-xs text-ink-500 leading-relaxed line-clamp-3">{retrieval.snippet}</p>
    </div>
  );
}

function ReasoningStepCard({ step, index }: { step: ReasoningStep; index: number }) {
  const isPassing = step.result === 'pass';

  return (
    <div className="flex gap-4">
      {/* Step indicator line */}
      <div className="flex flex-col items-center">
        <div
          className={`flex items-center justify-center w-8 h-8 rounded-full ${
            isPassing
              ? 'bg-success/10 text-success'
              : 'bg-error/10 text-error'
          }`}
        >
          {isPassing ? (
            <CheckCircle size={18} weight="fill" />
          ) : (
            <XCircle size={18} weight="fill" />
          )}
        </div>
        {index < 10 && <div className="w-px h-full bg-border min-h-[20px]" />}
      </div>

      {/* Step content */}
      <div className="flex-1 pb-6">
        <div className="flex items-center gap-2 mb-2">
          <span
            className={`gse-badge ${
              step.product === 'HomeReady' ? 'gse-badge-fannie' : 'gse-badge-freddie'
            }`}
          >
            {step.product}
          </span>
          <span className="text-xs font-mono text-ink-500">{step.rule}</span>
        </div>
        <p className="text-sm font-medium text-ink-900 mb-1">{step.check}</p>
        <p className="text-xs text-ink-500 leading-relaxed">{step.details}</p>
        <p className="text-xs text-ink-400 mt-2 font-mono">{step.citation}</p>
      </div>
    </div>
  );
}

export default function DemoModePanel({ data }: DemoModePanelProps) {
  return (
    <div className="space-y-8 mt-10 pt-10 border-t-2 border-sage-600/20">
      {/* Demo Mode Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-sage-600/10">
          <Brain size={24} weight="thin" className="text-sage-600" />
        </div>
        <div>
          <h2 className="font-display text-xl font-semibold text-ink-900">
            AI Decision Transparency
          </h2>
          <p className="text-sm text-ink-500">
            See how SAGE analyzed your loan scenario
          </p>
        </div>
      </div>

      {/* Performance Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          icon={<Clock size={16} weight="thin" />}
          label="RAG Retrieval"
          value={data.retrieval_time_ms}
          unit="ms"
        />
        <StatCard
          icon={<Lightning size={16} weight="thin" />}
          label="Reasoning"
          value={data.reasoning_time_ms}
          unit="ms"
        />
        <StatCard
          icon={<Coins size={16} weight="thin" />}
          label="Tokens Used"
          value={(data.tokens_input + data.tokens_output).toLocaleString()}
        />
        <StatCard
          icon={<Database size={16} weight="thin" />}
          label="Vectors Searched"
          value={data.index_stats.total_vectors.toLocaleString()}
        />
      </div>

      {/* Index Coverage */}
      <div className="bg-sage-600/5 border border-sage-600/20 p-5">
        <div className="flex items-center gap-2 mb-4">
          <BookOpen size={18} weight="thin" className="text-sage-600" />
          <h3 className="text-sm font-semibold text-ink-900">Guide Coverage</h3>
        </div>
        <div className="grid grid-cols-3 gap-6 text-center">
          <div>
            <p className="text-2xl font-mono font-semibold text-sage-600">
              {data.index_stats.total_pages.toLocaleString()}
            </p>
            <p className="text-xs text-ink-500 mt-1">Pages Indexed</p>
          </div>
          <div>
            <p className="text-2xl font-mono font-semibold text-sage-600">
              {data.index_stats.total_sections.toLocaleString()}
            </p>
            <p className="text-xs text-ink-500 mt-1">Guide Sections</p>
          </div>
          <div>
            <p className="text-2xl font-mono font-semibold text-sage-600">
              {data.index_stats.total_vectors.toLocaleString()}
            </p>
            <p className="text-xs text-ink-500 mt-1">Vector Embeddings</p>
          </div>
        </div>
      </div>

      {/* RAG Retrieval Section */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <MagnifyingGlass size={18} weight="thin" className="text-ink-500" />
          <h3 className="text-sm font-semibold text-ink-900">
            RAG Retrieval Results
          </h3>
          <span className="text-xs text-ink-500">
            ({data.rag_retrievals.length} sections retrieved)
          </span>
        </div>
        <p className="text-xs text-ink-500 mb-4">
          Semantic search found these relevant guide sections based on your loan scenario:
        </p>
        <div className="grid md:grid-cols-2 gap-4">
          {data.rag_retrievals.slice(0, 6).map((retrieval, index) => (
            <RAGRetrievalCard key={index} retrieval={retrieval} index={index} />
          ))}
        </div>
        {data.rag_retrievals.length > 6 && (
          <p className="text-xs text-ink-400 mt-3 text-center">
            +{data.rag_retrievals.length - 6} more sections retrieved
          </p>
        )}
      </div>

      {/* Reasoning Chain */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Brain size={18} weight="thin" className="text-ink-500" />
          <h3 className="text-sm font-semibold text-ink-900">
            Reasoning Chain
          </h3>
          <span className="text-xs text-ink-500">
            ({data.reasoning_steps.length} checks performed)
          </span>
        </div>
        <p className="text-xs text-ink-500 mb-6">
          Step-by-step analysis of your loan against GSE guidelines:
        </p>
        <div className="pl-2">
          {data.reasoning_steps.map((step, index) => (
            <ReasoningStepCard key={index} step={step} index={index} />
          ))}
        </div>
      </div>

      {/* Parsed Input (if available) */}
      {data.parsed_input && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <ArrowRight size={18} weight="thin" className="text-ink-500" />
            <h3 className="text-sm font-semibold text-ink-900">
              Natural Language Input Parsing
            </h3>
          </div>
          <div className="bg-surface border border-border p-4">
            <p className="text-xs text-ink-500 mb-2">Raw Input:</p>
            <p className="text-sm text-ink-700 font-mono bg-ink-900/5 p-3 mb-4">
              "{data.parsed_input.raw_text}"
            </p>
            <p className="text-xs text-ink-500 mb-2">Extracted Fields:</p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {Object.entries(data.parsed_input.extracted_fields).map(([key, value]) => (
                <div key={key} className="flex justify-between bg-ink-900/5 px-3 py-2">
                  <span className="text-xs text-ink-500">{key}:</span>
                  <span className="text-xs font-mono text-ink-900">{String(value)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="text-center text-xs text-ink-400 pt-6 border-t border-border">
        <p>
          SAGE uses Retrieval-Augmented Generation (RAG) with Claude Sonnet 4 to analyze loans
          against {data.index_stats.total_pages.toLocaleString()} pages of GSE guidelines.
        </p>
      </div>
    </div>
  );
}
