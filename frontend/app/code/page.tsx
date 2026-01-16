'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import TabNav from '@/components/TabNav';
import CodeDiff from '@/components/CodeDiff';
import {
  Robot,
  Code,
  BookOpen,
  Eye,
  CircleNotch,
} from '@phosphor-icons/react';

function CodePageContent() {
  const searchParams = useSearchParams();
  const updateId = searchParams.get('update') || undefined;

  return (
    <div className="min-h-screen bg-paper">
      <TabNav />

      <main className="max-w-6xl mx-auto px-6 lg:px-8 py-16 md:py-20">
        {/* Page Header */}
        <div className="mb-12 animate-fade-up">
          <h1 className="font-display text-4xl md:text-5xl font-bold text-ink-900 mb-4">
            Code Updates
          </h1>
          <p className="text-ink-500 text-lg md:text-xl max-w-2xl leading-relaxed">
            View auto-generated code changes based on policy updates. Choose your
            preferred format and copy the code directly into your eligibility
            engine.
          </p>
        </div>

        {/* Code Viewer */}
        <div className="animate-fade-up" style={{ animationDelay: '50ms' }}>
          <CodeDiff updateId={updateId} />
        </div>

        {/* Info Cards */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-px bg-border border-2 border-border animate-fade-up" style={{ animationDelay: '100ms' }}>
          <div className="bg-paper p-6 md:p-8">
            <div className="w-12 h-12 bg-sage-600/10 flex items-center justify-center mb-5">
              <Robot size={28} weight="thin" className="text-sage-600" />
            </div>
            <h3 className="font-display text-lg font-semibold text-ink-900 mb-3">
              Auto-Generated
            </h3>
            <p className="text-ink-500 leading-relaxed">
              Code is automatically generated from policy updates using LLM
              analysis of the changes.
            </p>
          </div>

          <div className="bg-paper p-6 md:p-8">
            <div className="w-12 h-12 bg-gold-500/10 flex items-center justify-center mb-5">
              <Code size={28} weight="thin" className="text-gold-600" />
            </div>
            <h3 className="font-display text-lg font-semibold text-ink-900 mb-3">
              Multiple Formats
            </h3>
            <p className="text-ink-500 leading-relaxed">
              Export code in Python, TypeScript, YAML, or JSON format depending
              on your tech stack.
            </p>
          </div>

          <div className="bg-paper p-6 md:p-8">
            <div className="w-12 h-12 bg-indigo/10 flex items-center justify-center mb-5">
              <BookOpen size={28} weight="thin" className="text-indigo" />
            </div>
            <h3 className="font-display text-lg font-semibold text-ink-900 mb-3">
              Cited Sources
            </h3>
            <p className="text-ink-500 leading-relaxed">
              Every code block includes comments citing the exact guideline
              section for traceability.
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="mt-12 bg-surface border-2 border-border p-6 md:p-8 animate-fade-up" style={{ animationDelay: '150ms' }}>
          <h2 className="font-display text-xl md:text-2xl font-semibold text-ink-900 mb-8">
            How It Works
          </h2>
          <div className="space-y-8">
            {[
              {
                step: 1,
                title: 'Policy Update Detected',
                description:
                  'Our system monitors Fannie Mae and Freddie Mac for new lender letters, bulletins, and guide updates.',
              },
              {
                step: 2,
                title: 'LLM Analysis',
                description:
                  'The update is analyzed to identify specific rule changes and their implications for eligibility logic.',
              },
              {
                step: 3,
                title: 'Code Generation',
                description:
                  'Executable code is generated with proper comments, citations, and documentation for your review.',
              },
              {
                step: 4,
                title: 'Human Review',
                description:
                  'Review the generated code and integrate it into your eligibility engine with confidence.',
              },
            ].map((item) => (
              <div key={item.step} className="flex items-start gap-5">
                <div className="flex-shrink-0 w-10 h-10 bg-sage-600 flex items-center justify-center text-white font-mono font-semibold">
                  {item.step}
                </div>
                <div>
                  <h3 className="font-semibold text-ink-900 text-lg">{item.title}</h3>
                  <p className="text-ink-500 mt-2 leading-relaxed">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Supported Formats */}
        <div className="mt-12 border-t border-border pt-10 animate-fade-up" style={{ animationDelay: '200ms' }}>
          <h2 className="flex items-center gap-2 text-sm font-mono uppercase tracking-widest text-ink-500 mb-5">
            <Code size={18} weight="thin" />
            Supported Output Formats
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {['Python', 'TypeScript', 'YAML', 'JSON Logic'].map((format) => (
              <div
                key={format}
                className="bg-code-bg p-5 text-center hover:scale-105 transition-transform duration-200"
              >
                <span className="font-mono text-code-text">{format}</span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

export default function CodePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-paper">
          <TabNav />
          <main className="max-w-6xl mx-auto px-6 py-12">
            <div className="flex items-center justify-center py-24">
              <CircleNotch size={32} weight="thin" className="animate-spin text-sage-600" />
            </div>
          </main>
        </div>
      }
    >
      <CodePageContent />
    </Suspense>
  );
}
