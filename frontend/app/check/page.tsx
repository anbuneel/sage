'use client';

import { useState } from 'react';
import TabNav from '@/components/TabNav';
import LoanForm from '@/components/LoanForm';
import EligibilityResult from '@/components/EligibilityResult';
import ModeToggle from '@/components/ModeToggle';
import DemoModePanel from '@/components/DemoModePanel';
import FixFinderPanel from '@/components/FixFinderPanel';
import type { LoanScenario, EligibilityResult as EligibilityResultType, ViewMode } from '@/lib/types';
import { checkLoanEligibility } from '@/lib/api';
import { Warning, Robot } from '@phosphor-icons/react';

export default function CheckMyLoanPage() {
  const [result, setResult] = useState<EligibilityResultType | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('lo');
  const [enableFixFinder, setEnableFixFinder] = useState(false);

  const handleSubmit = async (scenario: LoanScenario) => {
    setIsLoading(true);
    setError(null);

    try {
      // Pass demo_mode and enable_fix_finder flags
      const eligibilityResult = await checkLoanEligibility(
        scenario,
        viewMode === 'demo',
        enableFixFinder
      );
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

        {/* Fix Finder Toggle */}
        <div className="mb-8 animate-fade-up" style={{ animationDelay: '100ms' }}>
          <label className="flex items-center gap-3 cursor-pointer group">
            <div className="relative">
              <input
                type="checkbox"
                checked={enableFixFinder}
                onChange={(e) => setEnableFixFinder(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-ink-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-sage/50 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-ink-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-sage"></div>
            </div>
            <div className="flex items-center gap-2">
              <Robot size={20} weight="thin" className={enableFixFinder ? 'text-sage' : 'text-ink-400'} />
              <span className={`font-medium ${enableFixFinder ? 'text-sage' : 'text-ink-600'}`}>
                Enable Fix Finder Agent
              </span>
            </div>
            {enableFixFinder && (
              <span className="text-xs text-ink-500 bg-sage/10 px-2 py-1 rounded">
                AI-powered • RAG retrieval • ReAct reasoning
              </span>
            )}
          </label>
          <p className="text-sm text-ink-500 mt-2 ml-14">
            {enableFixFinder
              ? 'The Fix Finder Agent will analyze 4,866 pages of GSE guidelines to find intelligent fixes with citations.'
              : 'Enable to get AI-powered fix suggestions with confidence scores and guide citations.'}
          </p>
        </div>

        {/* Conditional Rendering: Form or Results */}
        {result ? (
          <>
            <EligibilityResult result={result} onReset={handleReset} />
            {/* Fix Finder Panel - shows enhanced AI suggestions */}
            {result.fix_finder_result && (
              <FixFinderPanel data={result.fix_finder_result} showReactTrace={viewMode === 'demo'} />
            )}
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
