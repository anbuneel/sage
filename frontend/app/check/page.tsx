'use client';

import { useState } from 'react';
import TabNav from '@/components/TabNav';
import LoanForm from '@/components/LoanForm';
import EligibilityResult from '@/components/EligibilityResult';
import type { LoanScenario, EligibilityResult as EligibilityResultType } from '@/lib/types';
import { checkLoanEligibility } from '@/lib/api';

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
    <div className="min-h-screen bg-gray-50">
      <TabNav />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Check My Loan</h1>
          <p className="mt-2 text-gray-600">
            Enter your loan scenario details to check eligibility for Fannie Mae
            HomeReady and Freddie Mac Home Possible programs.
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <svg
                className="w-5 h-5 text-red-600 mt-0.5 mr-3 flex-shrink-0"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
              <div>
                <h4 className="text-sm font-medium text-red-800">Error</h4>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Conditional Rendering: Form or Results */}
        {result ? (
          <EligibilityResult result={result} onReset={handleReset} />
        ) : (
          <LoanForm onSubmit={handleSubmit} isLoading={isLoading} />
        )}

        {/* Help Section */}
        {!result && (
          <div className="mt-12 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              About HomeReady & Home Possible
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-medium text-blue-700 mb-2 flex items-center">
                  <span className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center mr-2 text-xs font-bold">
                    FM
                  </span>
                  Fannie Mae HomeReady
                </h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>- Minimum credit score: 620</li>
                  <li>- Maximum DTI: 50%</li>
                  <li>- Maximum LTV: 97%</li>
                  <li>- Income limit: 80% of Area Median Income</li>
                  <li>- Primary residence only</li>
                </ul>
              </div>
              <div>
                <h3 className="font-medium text-purple-700 mb-2 flex items-center">
                  <span className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center mr-2 text-xs font-bold">
                    FM
                  </span>
                  Freddie Mac Home Possible
                </h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>- Minimum credit score: 660</li>
                  <li>- Maximum DTI: 45%</li>
                  <li>- Maximum LTV: 97%</li>
                  <li>- Income limit: 80% of Area Median Income</li>
                  <li>- Primary residence only</li>
                </ul>
              </div>
            </div>
            <p className="mt-4 text-xs text-gray-500">
              Both programs are designed to help low-to-moderate income borrowers
              achieve homeownership with flexible underwriting guidelines and reduced
              mortgage insurance requirements.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
