'use client';

import { useState } from 'react';
import TabNav from '@/components/TabNav';
import ChangeTimeline from '@/components/ChangeTimeline';
import type { PolicyUpdate } from '@/lib/types';

export default function ChangesPage() {
  const [selectedUpdate, setSelectedUpdate] = useState<PolicyUpdate | null>(null);

  return (
    <div className="min-h-screen bg-gray-50">
      <TabNav />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">What Changed</h1>
          <p className="mt-2 text-gray-600">
            Track the latest updates to Fannie Mae and Freddie Mac guidelines.
            See lender letters, bulletins, and guide updates as they are
            published.
          </p>
        </div>

        {/* Layout: Timeline and Detail Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Timeline Column */}
          <div className="lg:col-span-2">
            <ChangeTimeline onSelectUpdate={setSelectedUpdate} />
          </div>

          {/* Detail Panel */}
          <div className="lg:col-span-1">
            {selectedUpdate ? (
              <div className="sticky top-8 bg-white rounded-lg border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      selectedUpdate.gse === 'fannie_mae'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-purple-100 text-purple-800'
                    }`}
                  >
                    {selectedUpdate.gse === 'fannie_mae'
                      ? 'Fannie Mae'
                      : 'Freddie Mac'}
                  </span>
                  <button
                    onClick={() => setSelectedUpdate(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </div>

                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {selectedUpdate.update_number}
                </h3>
                <h4 className="text-md text-gray-700 mb-4">
                  {selectedUpdate.title}
                </h4>

                <div className="space-y-4 text-sm">
                  <div>
                    <p className="text-gray-500 font-medium">Published</p>
                    <p className="text-gray-900">
                      {new Date(selectedUpdate.publish_date).toLocaleDateString(
                        'en-US',
                        { year: 'numeric', month: 'long', day: 'numeric' }
                      )}
                    </p>
                  </div>

                  {selectedUpdate.effective_date && (
                    <div>
                      <p className="text-gray-500 font-medium">Effective Date</p>
                      <p className="text-gray-900">
                        {new Date(
                          selectedUpdate.effective_date
                        ).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                        })}
                      </p>
                    </div>
                  )}

                  <div>
                    <p className="text-gray-500 font-medium">Summary</p>
                    <p className="text-gray-700">{selectedUpdate.summary}</p>
                  </div>

                  <div>
                    <p className="text-gray-500 font-medium">Affected Sections</p>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {selectedUpdate.affected_sections.map((section) => (
                        <span
                          key={section}
                          className="px-2 py-1 rounded bg-gray-100 text-gray-700 text-xs"
                        >
                          {section}
                        </span>
                      ))}
                    </div>
                  </div>

                  {selectedUpdate.impact_analysis && (
                    <div>
                      <p className="text-gray-500 font-medium">Impact Analysis</p>
                      <p className="text-gray-700">
                        {selectedUpdate.impact_analysis}
                      </p>
                    </div>
                  )}
                </div>

                <div className="mt-6 pt-4 border-t border-gray-200">
                  <a
                    href={`/code?update=${selectedUpdate.id}`}
                    className="block w-full text-center px-4 py-2 rounded-lg bg-indigo-600 text-white font-medium hover:bg-indigo-700 transition-colors"
                  >
                    View Generated Code
                  </a>
                </div>
              </div>
            ) : (
              <div className="sticky top-8 bg-gray-100 rounded-lg border-2 border-dashed border-gray-300 p-8 text-center">
                <svg
                  className="w-12 h-12 text-gray-400 mx-auto mb-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
                <p className="text-gray-500">
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
