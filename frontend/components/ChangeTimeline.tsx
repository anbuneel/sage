'use client';

import { useState } from 'react';
import type { PolicyUpdate, GSE } from '@/lib/types';
import { mockPolicyUpdates } from '@/lib/api';
import {
  Calendar,
  Envelope,
  Newspaper,
  BookOpen,
  Warning,
  FileText,
} from '@phosphor-icons/react';

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
      className={`gse-badge ${isFannie ? 'gse-badge-fannie' : 'gse-badge-freddie'}`}
    >
      {isFannie ? 'Fannie Mae' : 'Freddie Mac'}
    </span>
  );
}

function UpdateTypeBadge({ type }: { type: string }) {
  const typeConfig: Record<string, { icon: React.ReactNode; label: string; color: string }> = {
    lender_letter: {
      icon: <Envelope size={12} weight="thin" />,
      label: 'Lender Letter',
      color: 'bg-gold-500/10 text-gold-600',
    },
    bulletin: {
      icon: <Newspaper size={12} weight="thin" />,
      label: 'Bulletin',
      color: 'bg-success/10 text-success',
    },
    guide_update: {
      icon: <BookOpen size={12} weight="thin" />,
      label: 'Guide Update',
      color: 'bg-indigo/10 text-indigo',
    },
  };

  const config = typeConfig[type] || {
    icon: <FileText size={12} weight="thin" />,
    label: type,
    color: 'bg-ink-300/10 text-ink-500',
  };

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-mono ${config.color}`}
    >
      {config.icon}
      {config.label}
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
    <div className="relative pl-10 pb-10 border-l-2 border-border last:border-l-0 last:pb-0 animate-fade-up">
      {/* Timeline dot */}
      <div className="absolute -left-[7px] top-0 w-3 h-3 bg-sage-600 border-2 border-paper rounded-full" />

      {/* Content */}
      <div
        className="bg-paper border border-border p-5 md:p-6 hover:border-sage-600 hover:shadow-md transition-all duration-200 cursor-pointer group"
        onClick={() => onSelect?.(update)}
      >
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-2">
            <GSEBadge gse={update.gse} />
            <UpdateTypeBadge type={update.update_type} />
          </div>
          <span className="text-xs font-mono text-ink-500 flex items-center gap-1.5">
            <Calendar size={14} weight="thin" />
            {formatDate(update.publish_date)}
          </span>
        </div>

        <h3 className="font-display text-lg font-semibold text-ink-900 mb-2 group-hover:text-sage-600 transition-colors">
          {update.update_number}
        </h3>
        <p className="text-ink-700 mb-4">
          {update.title}
        </p>

        <p className="text-sm text-ink-500 mb-5 line-clamp-2 leading-relaxed">
          {update.summary}
        </p>

        <div className="flex items-center justify-between">
          <div className="flex flex-wrap gap-1.5">
            {update.affected_sections.slice(0, 3).map((section) => (
              <span
                key={section}
                className="px-2 py-1 bg-surface border border-border text-xs font-mono text-ink-700"
              >
                {section}
              </span>
            ))}
            {update.affected_sections.length > 3 && (
              <span className="px-2 py-1 bg-surface border border-border text-xs font-mono text-ink-500">
                +{update.affected_sections.length - 3}
              </span>
            )}
          </div>

          {update.effective_date && (
            <span className="text-xs text-ink-500 font-mono">
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
      <div className="mb-8 flex items-center gap-5">
        <span className="text-xs font-mono uppercase tracking-widest text-ink-500">
          Filter:
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 text-sm font-medium transition-all duration-200 ${
              filter === 'all'
                ? 'bg-sage-600 text-white shadow-md'
                : 'bg-surface border border-border text-ink-700 hover:border-sage-600 hover:shadow-sm'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('fannie_mae')}
            className={`px-4 py-2 text-sm font-medium transition-all duration-200 ${
              filter === 'fannie_mae'
                ? 'bg-fannie text-white shadow-md'
                : 'bg-surface border border-border text-ink-700 hover:border-fannie hover:shadow-sm'
            }`}
          >
            Fannie Mae
          </button>
          <button
            onClick={() => setFilter('freddie_mac')}
            className={`px-4 py-2 text-sm font-medium transition-all duration-200 ${
              filter === 'freddie_mac'
                ? 'bg-freddie text-white shadow-md'
                : 'bg-surface border border-border text-ink-700 hover:border-freddie hover:shadow-sm'
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
        <div className="text-center py-12 bg-surface border border-border">
          <FileText size={48} weight="thin" className="text-ink-300 mx-auto mb-4" />
          <p className="text-ink-500">No policy updates found.</p>
        </div>
      )}

      {/* Placeholder notice */}
      <div className="mt-8 p-4 bg-gold-500/5 border border-gold-500/20">
        <div className="flex gap-3">
          <Warning size={20} weight="thin" className="text-gold-600 mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-medium text-ink-900 text-sm">Placeholder Data</p>
            <p className="text-sm text-ink-500 mt-1">
              This timeline is showing mock data. Real policy updates will be loaded
              from the backend when the scraping system is connected.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
