'use client';

import { useState } from 'react';
import TabNav from '@/components/TabNav';
import LoanForm from '@/components/LoanForm';
import EligibilityResult from '@/components/EligibilityResult';
import type { LoanScenario, EligibilityResult as EligibilityResultType } from '@/lib/types';
import { checkLoanEligibility } from '@/lib/api';
import { Warning } from '@phosphor-icons/react';

export default function CheckMyLoanPage() {
  const [result, setResult] = useState<EligibilityResultType | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (scenario: LoanScenario) => {
    setIsLoading(true);
    setError(null);

    try {
      const eligibilityResult = await checkLoanEligibility(scenario);
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

      <main className="max-w-5xl mx-auto px-6 py-12">
        {/* Page Header */}
        <div className="mb-10">
          <h1 className="font-display text-4xl font-bold text-ink-900 mb-3">
            Check My Loan
          </h1>
          <p className="text-ink-500 text-lg max-w-2xl">
            Enter your loan scenario to check eligibility for Fannie Mae HomeReady
            and Freddie Mac Home Possible programs.
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-8 p-4 border border-error/30 bg-error/5">
            <div className="flex items-start gap-3">
              <Warning size={20} weight="thin" className="text-error mt-0.5" />
              <div>
                <p className="font-medium text-error">Error</p>
                <p className="text-sm text-ink-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Conditional Rendering: Form or Results */}
        {result ? (
          <EligibilityResult result={result} onReset={handleReset} />
        ) : (
          <>
            <LoanForm onSubmit={handleSubmit} isLoading={isLoading} />

            {/* Program Reference */}
            <div className="mt-12 grid md:grid-cols-2 gap-px bg-border">
              <div className="bg-paper p-6">
                <div className="gse-badge gse-badge-fannie mb-3">Fannie Mae</div>
                <h3 className="font-display text-lg font-semibold mb-3">HomeReady Requirements</h3>
                <dl className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <dt className="text-ink-500">Minimum Credit Score</dt>
                    <dd className="font-mono text-ink-900">620</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-ink-500">Maximum DTI</dt>
                    <dd className="font-mono text-ink-900">50%</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-ink-500">Maximum LTV</dt>
                    <dd className="font-mono text-ink-900">97%</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-ink-500">Income Limit</dt>
                    <dd className="font-mono text-ink-900">80% AMI</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-ink-500">Occupancy</dt>
                    <dd className="font-mono text-ink-900">Primary only</dd>
                  </div>
                </dl>
              </div>
              <div className="bg-paper p-6">
                <div className="gse-badge gse-badge-freddie mb-3">Freddie Mac</div>
                <h3 className="font-display text-lg font-semibold mb-3">Home Possible Requirements</h3>
                <dl className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <dt className="text-ink-500">Minimum Credit Score</dt>
                    <dd className="font-mono text-ink-900">660</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-ink-500">Maximum DTI</dt>
                    <dd className="font-mono text-ink-900">45%</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-ink-500">Maximum LTV</dt>
                    <dd className="font-mono text-ink-900">97%</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-ink-500">Income Limit</dt>
                    <dd className="font-mono text-ink-900">80% AMI</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-ink-500">Occupancy</dt>
                    <dd className="font-mono text-ink-900">Primary only</dd>
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
