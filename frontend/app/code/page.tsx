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

      <main className="max-w-6xl mx-auto px-6 py-12">
        {/* Page Header */}
        <div className="mb-10">
          <h1 className="font-display text-4xl font-bold text-ink-900 mb-3">
            Code Updates
          </h1>
          <p className="text-ink-500 text-lg max-w-2xl">
            View auto-generated code changes based on policy updates. Choose your
            preferred format and copy the code directly into your eligibility
            engine.
          </p>
        </div>

        {/* Code Viewer */}
        <CodeDiff updateId={updateId} />

        {/* Info Cards */}
        <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-px bg-border border border-border">
          <div className="bg-paper p-6">
            <div className="w-10 h-10 bg-sage-600/10 flex items-center justify-center mb-4">
              <Robot size={24} weight="thin" className="text-sage-600" />
            </div>
            <h3 className="font-display font-semibold text-ink-900 mb-2">
              Auto-Generated
            </h3>
            <p className="text-sm text-ink-500">
              Code is automatically generated from policy updates using LLM
              analysis of the changes.
            </p>
          </div>

          <div className="bg-paper p-6">
            <div className="w-10 h-10 bg-gold-500/10 flex items-center justify-center mb-4">
              <Code size={24} weight="thin" className="text-gold-600" />
            </div>
            <h3 className="font-display font-semibold text-ink-900 mb-2">
              Multiple Formats
            </h3>
            <p className="text-sm text-ink-500">
              Export code in Python, TypeScript, YAML, or JSON format depending
              on your tech stack.
            </p>
          </div>

          <div className="bg-paper p-6">
            <div className="w-10 h-10 bg-indigo/10 flex items-center justify-center mb-4">
              <BookOpen size={24} weight="thin" className="text-indigo" />
            </div>
            <h3 className="font-display font-semibold text-ink-900 mb-2">
              Cited Sources
            </h3>
            <p className="text-sm text-ink-500">
              Every code block includes comments citing the exact guideline
              section for traceability.
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="mt-10 bg-surface border border-border p-6">
          <h2 className="font-display text-xl font-semibold text-ink-900 mb-6">
            How It Works
          </h2>
          <div className="space-y-6">
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
              <div key={item.step} className="flex items-start gap-4">
                <div className="flex-shrink-0 w-8 h-8 bg-sage-600 flex items-center justify-center text-white font-mono text-sm font-medium">
                  {item.step}
                </div>
                <div>
                  <h3 className="font-medium text-ink-900">{item.title}</h3>
                  <p className="text-sm text-ink-500 mt-1">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Supported Formats */}
        <div className="mt-10 border-t border-border pt-8">
          <h2 className="flex items-center gap-2 text-sm font-mono uppercase tracking-wider text-ink-500 mb-4">
            <Code size={16} weight="thin" />
            Supported Output Formats
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {['Python', 'TypeScript', 'YAML', 'JSON Logic'].map((format) => (
              <div
                key={format}
                className="bg-code-bg p-4 text-center"
              >
                <span className="font-mono text-code-text text-sm">{format}</span>
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
