'use client';

import { useState } from 'react';
import TabNav from '@/components/TabNav';
import LoanForm from '@/components/LoanForm';
import EligibilityResult from '@/components/EligibilityResult';
import ModeToggle from '@/components/ModeToggle';
import DemoModePanel from '@/components/DemoModePanel';
import type { LoanScenario, EligibilityResult as EligibilityResultType, ViewMode } from '@/lib/types';
import { checkLoanEligibility } from '@/lib/api';
import { Warning } from '@phosphor-icons/react';

export default function CheckMyLoanPage() {
  const [result, setResult] = useState<EligibilityResultType | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('lo');

  const handleSubmit = async (scenario: LoanScenario) => {
    setIsLoading(true);
    setError(null);

    try {
      // Pass demo_mode flag to get detailed reasoning data
      const eligibilityResult = await checkLoanEligibility(scenario, viewMode === 'demo');
      setResult(eligibilityResult);
    } catch (err) {
      console.error('Error checking eligibility:', err);
      setError(
        err instanceof Error
          ? err.message
          : 'An unexpected error occurred. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-paper">
      <TabNav />

      <main className="max-w-5xl mx-auto px-6 lg:px-8 py-16 md:py-20">
        {/* Page Header with Mode Toggle */}
        <div className="mb-12 animate-fade-up">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6 mb-4">
            <h1 className="font-display text-4xl md:text-5xl font-bold text-ink-900">
              Check My Loan
            </h1>
            <ModeToggle mode={viewMode} onModeChange={setViewMode} />
          </div>
          <p className="text-ink-500 text-lg md:text-xl max-w-2xl leading-relaxed">
            {viewMode === 'lo' ? (
              <>Enter your loan scenario to check eligibility for Fannie Mae HomeReady
              and Freddie Mac Home Possible programs.</>
            ) : (
              <>See how AI analyzes loans against 4,866 pages of GSE guidelines using
              RAG retrieval and intelligent reasoning.</>
            )}
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-10 p-5 border-2 border-error/30 bg-error/5 animate-fade-up">
            <div className="flex items-start gap-4">
              <Warning size={24} weight="thin" className="text-error mt-0.5" />
              <div>
                <p className="font-semibold text-error">Error</p>
                <p className="text-sm text-ink-700 mt-2">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Conditional Rendering: Form or Results */}
        {result ? (
          <>
            <EligibilityResult result={result} onReset={handleReset} />
            {/* Demo Mode Panel - shows AI reasoning details */}
            {viewMode === 'demo' && result.demo_data && (
              <DemoModePanel data={result.demo_data} />
            )}
          </>
        ) : (
          <>
            <LoanForm onSubmit={handleSubmit} isLoading={isLoading} />

            {/* Program Reference */}
            <div className="mt-16 grid md:grid-cols-2 gap-px bg-border border-2 border-border">
              <div className="bg-paper p-6 md:p-8">
                <div className="gse-badge gse-badge-fannie mb-4">Fannie Mae</div>
                <h3 className="font-display text-xl font-semibold mb-5">HomeReady Requirements</h3>
                <dl className="space-y-3 text-sm">
                  <div className="flex justify-between py-2 border-b border-border/50">
                    <dt className="text-ink-500">Minimum Credit Score</dt>
                    <dd className="font-mono text-ink-900 font-medium">620</dd>
                  </div>
                  <div className="flex justify-between py-2 border-b border-border/50">
                    <dt className="text-ink-500">Maximum DTI</dt>
                    <dd className="font-mono text-ink-900 font-medium">50%</dd>
                  </div>
                  <div className="flex justify-between py-2 border-b border-border/50">
                    <dt className="text-ink-500">Maximum LTV</dt>
                    <dd className="font-mono text-ink-900 font-medium">97%</dd>
                  </div>
                  <div className="flex justify-between py-2 border-b border-border/50">
                    <dt className="text-ink-500">Income Limit</dt>
                    <dd className="font-mono text-ink-900 font-medium">80% AMI</dd>
                  </div>
                  <div className="flex justify-between py-2">
                    <dt className="text-ink-500">Occupancy</dt>
                    <dd className="font-mono text-ink-900 font-medium">Primary only</dd>
                  </div>
                </dl>
              </div>
              <div className="bg-paper p-6 md:p-8">
                <div className="gse-badge gse-badge-freddie mb-4">Freddie Mac</div>
                <h3 className="font-display text-xl font-semibold mb-5">Home Possible Requirements</h3>
                <dl className="space-y-3 text-sm">
                  <div className="flex justify-between py-2 border-b border-border/50">
                    <dt className="text-ink-500">Minimum Credit Score</dt>
                    <dd className="font-mono text-ink-900 font-medium">660</dd>
                  </div>
                  <div className="flex justify-between py-2 border-b border-border/50">
                    <dt className="text-ink-500">Maximum DTI</dt>
                    <dd className="font-mono text-ink-900 font-medium">45%</dd>
                  </div>
                  <div className="flex justify-between py-2 border-b border-border/50">
                    <dt className="text-ink-500">Maximum LTV</dt>
                    <dd className="font-mono text-ink-900 font-medium">97%</dd>
                  </div>
                  <div className="flex justify-between py-2 border-b border-border/50">
                    <dt className="text-ink-500">Income Limit</dt>
                    <dd className="font-mono text-ink-900 font-medium">80% AMI</dd>
                  </div>
                  <div className="flex justify-between py-2">
                    <dt className="text-ink-500">Occupancy</dt>
                    <dd className="font-mono text-ink-900 font-medium">Primary only</dd>
                  </div>
                </dl>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
