'use client';

import { useState } from 'react';
import TabNav from '@/components/TabNav';
import ChangeTimeline from '@/components/ChangeTimeline';
import type { PolicyUpdate } from '@/lib/types';
import {
  X,
  Calendar,
  CalendarCheck,
  Article,
  Tag,
  Lightning,
  Code,
  FileText,
} from '@phosphor-icons/react';

export default function ChangesPage() {
  const [selectedUpdate, setSelectedUpdate] = useState<PolicyUpdate | null>(null);

  return (
    <div className="min-h-screen bg-paper">
      <TabNav />

      <main className="max-w-6xl mx-auto px-6 lg:px-8 py-16 md:py-20">
        {/* Page Header */}
        <div className="mb-12 animate-fade-up">
          <h1 className="font-display text-4xl md:text-5xl font-bold text-ink-900 mb-4">
            What Changed
          </h1>
          <p className="text-ink-500 text-lg md:text-xl max-w-2xl leading-relaxed">
            Track the latest updates to Fannie Mae and Freddie Mac guidelines.
            See lender letters, bulletins, and guide updates as they are
            published.
          </p>
        </div>

        {/* Layout: Timeline and Detail Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
          {/* Timeline Column */}
          <div className="lg:col-span-2">
            <ChangeTimeline onSelectUpdate={setSelectedUpdate} />
          </div>

          {/* Detail Panel */}
          <div className="lg:col-span-1">
            {selectedUpdate ? (
              <div className="sticky top-24 bg-surface border-2 border-border p-6 md:p-8 shadow-sm animate-scale-in">
                <div className="flex items-center justify-between mb-4">
                  <div
                    className={`gse-badge ${
                      selectedUpdate.gse === 'fannie_mae'
                        ? 'gse-badge-fannie'
                        : 'gse-badge-freddie'
                    }`}
                  >
                    {selectedUpdate.gse === 'fannie_mae'
                      ? 'Fannie Mae'
                      : 'Freddie Mac'}
                  </div>
                  <button
                    onClick={() => setSelectedUpdate(null)}
                    className="p-1 text-ink-500 hover:text-ink-900 hover:bg-paper transition-colors"
                    aria-label="Close detail panel"
                  >
                    <X size={20} weight="thin" />
                  </button>
                </div>

                <h3 className="font-display text-lg font-semibold text-ink-900 mb-1">
                  {selectedUpdate.update_number}
                </h3>
                <h4 className="text-ink-700 mb-6">
                  {selectedUpdate.title}
                </h4>

                <div className="space-y-5">
                  <div className="flex items-start gap-3">
                    <Calendar size={16} weight="thin" className="text-ink-500 mt-0.5" />
                    <div>
                      <p className="text-xs font-mono uppercase tracking-wider text-ink-500">
                        Published
                      </p>
                      <p className="text-sm text-ink-900">
                        {new Date(selectedUpdate.publish_date).toLocaleDateString(
                          'en-US',
                          { year: 'numeric', month: 'long', day: 'numeric' }
                        )}
                      </p>
                    </div>
                  </div>

                  {selectedUpdate.effective_date && (
                    <div className="flex items-start gap-3">
                      <CalendarCheck size={16} weight="thin" className="text-ink-500 mt-0.5" />
                      <div>
                        <p className="text-xs font-mono uppercase tracking-wider text-ink-500">
                          Effective Date
                        </p>
                        <p className="text-sm text-ink-900">
                          {new Date(
                            selectedUpdate.effective_date
                          ).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                          })}
                        </p>
                      </div>
                    </div>
                  )}

                  <div className="flex items-start gap-3">
                    <Article size={16} weight="thin" className="text-ink-500 mt-0.5" />
                    <div>
                      <p className="text-xs font-mono uppercase tracking-wider text-ink-500">
                        Summary
                      </p>
                      <p className="text-sm text-ink-700 leading-relaxed">
                        {selectedUpdate.summary}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <Tag size={16} weight="thin" className="text-ink-500 mt-0.5" />
                    <div>
                      <p className="text-xs font-mono uppercase tracking-wider text-ink-500 mb-2">
                        Affected Sections
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {selectedUpdate.affected_sections.map((section) => (
                          <span
                            key={section}
                            className="px-2 py-1 bg-paper border border-border text-xs font-mono text-ink-700"
                          >
                            {section}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  {selectedUpdate.impact_analysis && (
                    <div className="flex items-start gap-3">
                      <Lightning size={16} weight="thin" className="text-gold-600 mt-0.5" />
                      <div>
                        <p className="text-xs font-mono uppercase tracking-wider text-ink-500">
                          Impact Analysis
                        </p>
                        <p className="text-sm text-ink-700 leading-relaxed">
                          {selectedUpdate.impact_analysis}
                        </p>
                      </div>
                    </div>
                  )}
                </div>

{/* View Generated Code button hidden - not needed for demo */}
              </div>
            ) : (
              <div className="sticky top-24 bg-surface border-2 border-border border-dashed p-10 text-center">
                <FileText size={56} weight="thin" className="text-ink-300 mx-auto mb-5" />
                <p className="text-ink-500 text-lg">
                  Select an update from the timeline to view details
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
