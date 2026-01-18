'use client';

import type { ViewMode } from '@/lib/types';
import { User, Robot } from '@phosphor-icons/react';

interface ModeToggleProps {
  mode: ViewMode;
  onModeChange: (mode: ViewMode) => void;
}

export default function ModeToggle({ mode, onModeChange }: ModeToggleProps) {
  return (
    <div className="flex items-center gap-2 p-1 bg-surface border border-border rounded-sm">
      <button
        onClick={() => onModeChange('lo')}
        className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-all ${
          mode === 'lo'
            ? 'bg-sage-600 text-white'
            : 'text-ink-500 hover:text-ink-900 hover:bg-surface-hover'
        }`}
      >
        <User size={18} weight={mode === 'lo' ? 'fill' : 'regular'} />
        LO Mode
      </button>
      <button
        onClick={() => onModeChange('demo')}
        className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-all ${
          mode === 'demo'
            ? 'bg-sage-600 text-white'
            : 'text-ink-500 hover:text-ink-900 hover:bg-surface-hover'
        }`}
      >
        <Robot size={18} weight={mode === 'demo' ? 'fill' : 'regular'} />
        Demo Mode
      </button>
    </div>
  );
}
