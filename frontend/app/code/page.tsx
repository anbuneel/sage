'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import TabNav from '@/components/TabNav';
import CodeDiff from '@/components/CodeDiff';

function CodePageContent() {
  const searchParams = useSearchParams();
  const updateId = searchParams.get('update') || undefined;

  return (
    <div className="min-h-screen bg-gray-50">
      <TabNav />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Generated Updates</h1>
          <p className="mt-2 text-gray-600">
            View auto-generated code changes based on policy updates. Choose your
            preferred format and copy the code directly into your eligibility
            engine.
          </p>
        </div>

        {/* Code Viewer */}
        <CodeDiff updateId={updateId} />

        {/* Info Cards */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Auto-Generated</h3>
            <p className="text-sm text-gray-600">
              Code is automatically generated from policy updates using LLM
              analysis of the changes.
            </p>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
                />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Multiple Formats</h3>
            <p className="text-sm text-gray-600">
              Export code in Python, TypeScript, YAML, or JSON format depending
              on your tech stack.
            </p>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-purple-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Cited Sources</h3>
            <p className="text-sm text-gray-600">
              Every code block includes comments citing the exact guideline
              section for traceability.
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="mt-8 bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            How It Works
          </h2>
          <div className="space-y-4">
            <div className="flex items-start">
              <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-semibold text-sm mr-4">
                1
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Policy Update Detected</h3>
                <p className="text-sm text-gray-600">
                  Our system monitors Fannie Mae and Freddie Mac for new lender
                  letters, bulletins, and guide updates.
                </p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-semibold text-sm mr-4">
                2
              </div>
              <div>
                <h3 className="font-medium text-gray-900">LLM Analysis</h3>
                <p className="text-sm text-gray-600">
                  The update is analyzed to identify specific rule changes and
                  their implications for eligibility logic.
                </p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-semibold text-sm mr-4">
                3
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Code Generation</h3>
                <p className="text-sm text-gray-600">
                  Executable code is generated with proper comments, citations,
                  and documentation for your review.
                </p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-semibold text-sm mr-4">
                4
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Human Review</h3>
                <p className="text-sm text-gray-600">
                  Review the generated code and integrate it into your
                  eligibility engine with confidence.
                </p>
              </div>
            </div>
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
        <div className="min-h-screen bg-gray-50">
          <TabNav />
          <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="animate-pulse">
              <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-8"></div>
              <div className="h-96 bg-gray-200 rounded"></div>
            </div>
          </main>
        </div>
      }
    >
      <CodePageContent />
    </Suspense>
  );
}
