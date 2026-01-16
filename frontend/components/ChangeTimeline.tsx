'use client';

import { useState } from 'react';
import type { PolicyUpdate, GSE } from '@/lib/types';
import { mockPolicyUpdates } from '@/lib/api';

interface ChangeTimelineProps {
  onSelectUpdate?: (update: PolicyUpdate) => void;
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function GSEBadge({ gse }: { gse: GSE }) {
  const isFannie = gse === 'fannie_mae';
  return (
    <span
      className={`
        inline-flex items-center px-2 py-0.5 rounded text-xs font-medium
        ${isFannie ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}
      `}
    >
      {isFannie ? 'Fannie Mae' : 'Freddie Mac'}
    </span>
  );
}

function UpdateTypeBadge({ type }: { type: string }) {
  const typeColors: Record<string, string> = {
    lender_letter: 'bg-amber-100 text-amber-800',
    bulletin: 'bg-green-100 text-green-800',
    guide_update: 'bg-indigo-100 text-indigo-800',
  };

  const typeLabels: Record<string, string> = {
    lender_letter: 'Lender Letter',
    bulletin: 'Bulletin',
    guide_update: 'Guide Update',
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
        typeColors[type] || 'bg-gray-100 text-gray-800'
      }`}
    >
      {typeLabels[type] || type}
    </span>
  );
}

function TimelineItem({
  update,
  onSelect,
}: {
  update: PolicyUpdate;
  onSelect?: (update: PolicyUpdate) => void;
}) {
  return (
    <div className="relative pl-8 pb-8 border-l-2 border-gray-200 last:border-l-0 last:pb-0">
      {/* Timeline dot */}
      <div className="absolute -left-2 top-0 w-4 h-4 rounded-full bg-indigo-600 border-2 border-white" />

      {/* Content */}
      <div
        className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
        onClick={() => onSelect?.(update)}
      >
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center space-x-2">
            <GSEBadge gse={update.gse} />
            <UpdateTypeBadge type={update.update_type} />
          </div>
          <span className="text-xs text-gray-500">
            {formatDate(update.publish_date)}
          </span>
        </div>

        <h3 className="font-medium text-gray-900 mb-1">
          {update.update_number}: {update.title}
        </h3>

        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {update.summary}
        </p>

        <div className="flex items-center justify-between">
          <div className="flex flex-wrap gap-1">
            {update.affected_sections.slice(0, 3).map((section) => (
              <span
                key={section}
                className="px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-700"
              >
                {section}
              </span>
            ))}
            {update.affected_sections.length > 3 && (
              <span className="px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-700">
                +{update.affected_sections.length - 3} more
              </span>
            )}
          </div>

          {update.effective_date && (
            <span className="text-xs text-gray-500">
              Effective: {formatDate(update.effective_date)}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ChangeTimeline({ onSelectUpdate }: ChangeTimelineProps) {
  const [filter, setFilter] = useState<GSE | 'all'>('all');
  const [updates] = useState<PolicyUpdate[]>(mockPolicyUpdates);

  const filteredUpdates =
    filter === 'all'
      ? updates
      : updates.filter((u) => u.gse === filter);

  return (
    <div>
      {/* Filter Controls */}
      <div className="mb-6 flex items-center space-x-4">
        <span className="text-sm font-medium text-gray-700">Filter by:</span>
        <div className="flex space-x-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
              filter === 'all'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('fannie_mae')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
              filter === 'fannie_mae'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Fannie Mae
          </button>
          <button
            onClick={() => setFilter('freddie_mac')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
              filter === 'freddie_mac'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Freddie Mac
          </button>
        </div>
      </div>

      {/* Timeline */}
      {filteredUpdates.length > 0 ? (
        <div className="space-y-0">
          {filteredUpdates.map((update) => (
            <TimelineItem
              key={update.id}
              update={update}
              onSelect={onSelectUpdate}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
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
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <p className="text-gray-500">No policy updates found.</p>
        </div>
      )}

      {/* Placeholder notice */}
      <div className="mt-8 p-4 bg-amber-50 border border-amber-200 rounded-lg">
        <div className="flex">
          <svg
            className="w-5 h-5 text-amber-600 mt-0.5 mr-3 flex-shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
              clipRule="evenodd"
            />
          </svg>
          <div>
            <h4 className="text-sm font-medium text-amber-800">
              Placeholder Data
            </h4>
            <p className="text-sm text-amber-700 mt-1">
              This timeline is showing mock data. Real policy updates will be loaded
              from the backend when the scraping system is connected.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
