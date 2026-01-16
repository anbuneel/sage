'use client';

import { useState } from 'react';
import type { CodeFormat } from '@/lib/types';
import { Copy, Check, Warning } from '@phosphor-icons/react';

interface CodeDiffProps {
  updateId?: string;
  initialCode?: string;
}

const MOCK_CODE_PYTHON = `# Generated rule update for HomeReady income limits
# Based on: LL-2025-04

from dataclasses import dataclass
from typing import Optional

@dataclass
class IncomeLimit:
    """2025 Area Median Income limits for HomeReady eligibility."""

    # Updated limits effective 2025-02-01
    base_limit_percentage: float = 0.80  # 80% of AMI

    def check_eligibility(
        self,
        annual_income: float,
        area_median_income: float
    ) -> bool:
        """
        Check if borrower income is within HomeReady limits.

        Args:
            annual_income: Borrower's annual income
            area_median_income: Area Median Income for the property location

        Returns:
            True if income is <= 80% of AMI
        """
        max_income = area_median_income * self.base_limit_percentage
        return annual_income <= max_income

# Example AMI values (2025)
AMI_LIMITS_2025 = {
    "CA": {
        "Los Angeles": 91_100,
        "San Francisco": 149_600,
        "San Diego": 106_900,
    },
    "TX": {
        "Harris": 83_500,
        "Dallas": 89_200,
        "Travis": 110_300,
    },
    # ... additional counties
}
`;

const MOCK_CODE_TYPESCRIPT = `// Generated rule update for HomeReady income limits
// Based on: LL-2025-04

interface IncomeLimit {
  baseLimitPercentage: number;
}

interface AMILimits {
  [state: string]: {
    [county: string]: number;
  };
}

// Updated limits effective 2025-02-01
const INCOME_LIMIT: IncomeLimit = {
  baseLimitPercentage: 0.80, // 80% of AMI
};

/**
 * Check if borrower income is within HomeReady limits.
 */
function checkIncomeEligibility(
  annualIncome: number,
  areaMedianIncome: number
): boolean {
  const maxIncome = areaMedianIncome * INCOME_LIMIT.baseLimitPercentage;
  return annualIncome <= maxIncome;
}

// Example AMI values (2025)
const AMI_LIMITS_2025: AMILimits = {
  CA: {
    "Los Angeles": 91_100,
    "San Francisco": 149_600,
    "San Diego": 106_900,
  },
  TX: {
    Harris: 83_500,
    Dallas: 89_200,
    Travis: 110_300,
  },
};

export { checkIncomeEligibility, AMI_LIMITS_2025 };
`;

const MOCK_CODE_YAML = `# Generated rule update for HomeReady income limits
# Based on: LL-2025-04
# Effective: 2025-02-01

homeready:
  income_limits:
    base_percentage: 0.80  # 80% of AMI

  ami_limits_2025:
    CA:
      Los Angeles: 91100
      San Francisco: 149600
      San Diego: 106900
    TX:
      Harris: 83500
      Dallas: 89200
      Travis: 110300
    # Additional counties...

  eligibility_rules:
    - name: max_income
      description: "Income must not exceed 80% of AMI"
      citation: "B5-6-01"
      check: "annual_income <= area_median_income * 0.80"
`;

const MOCK_CODE_JSON = `{
  "update_id": "LL-2025-04",
  "effective_date": "2025-02-01",
  "program": "HomeReady",
  "income_limits": {
    "base_percentage": 0.80,
    "description": "80% of Area Median Income"
  },
  "ami_limits_2025": {
    "CA": {
      "Los Angeles": 91100,
      "San Francisco": 149600,
      "San Diego": 106900
    },
    "TX": {
      "Harris": 83500,
      "Dallas": 89200,
      "Travis": 110300
    }
  },
  "citation": "Fannie Mae Selling Guide B5-6-01"
}`;

const CODE_SAMPLES: Record<CodeFormat, string> = {
  python: MOCK_CODE_PYTHON,
  typescript: MOCK_CODE_TYPESCRIPT,
  yaml: MOCK_CODE_YAML,
  json: MOCK_CODE_JSON,
};

const FORMAT_LABELS: Record<CodeFormat, string> = {
  python: 'Python',
  typescript: 'TypeScript',
  yaml: 'YAML',
  json: 'JSON',
};

export default function CodeDiff({ updateId, initialCode }: CodeDiffProps) {
  const [format, setFormat] = useState<CodeFormat>('python');
  const [copied, setCopied] = useState(false);

  const code = initialCode || CODE_SAMPLES[format];

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div className="bg-paper border border-border overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-surface border-b border-border">
        <div className="flex items-center gap-4">
          <span className="text-xs font-mono uppercase tracking-wider text-ink-500">
            Format:
          </span>
          <div className="flex gap-1">
            {(Object.keys(CODE_SAMPLES) as CodeFormat[]).map((fmt) => (
              <button
                key={fmt}
                onClick={() => setFormat(fmt)}
                className={`px-3 py-1 text-sm font-mono transition-colors ${
                  format === fmt
                    ? 'bg-sage-600 text-white'
                    : 'bg-paper border border-border text-ink-700 hover:border-sage-600'
                }`}
              >
                {FORMAT_LABELS[fmt]}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={handleCopy}
          className="btn btn-secondary text-sm py-1.5 px-3 inline-flex items-center gap-2"
        >
          {copied ? (
            <>
              <Check size={16} weight="bold" className="text-success" />
              Copied!
            </>
          ) : (
            <>
              <Copy size={16} weight="thin" />
              Copy
            </>
          )}
        </button>
      </div>

      {/* Code Block */}
      <div className="code-panel relative">
        <div className="flex">
          {/* Line numbers */}
          <div className="select-none text-ink-500 text-right pr-4 border-r border-ink-700/30">
            {code.split('\n').map((_, i) => (
              <div key={i} className="leading-relaxed">
                {i + 1}
              </div>
            ))}
          </div>
          {/* Code content */}
          <pre className="pl-4 overflow-x-auto flex-1">
            <code className="leading-relaxed">{code}</code>
          </pre>
        </div>
      </div>

      {/* Footer */}
      <div className="px-4 py-3 bg-surface border-t border-border">
        <div className="flex items-center justify-between text-sm">
          <div className="text-ink-500 font-mono text-xs">
            {updateId ? (
              <span>
                Generated from: <strong className="text-ink-900">{updateId}</strong>
              </span>
            ) : (
              <span>Select a policy update to view generated code</span>
            )}
          </div>
          <div className="text-ink-500 font-mono text-xs">
            {code.split('\n').length} lines | {FORMAT_LABELS[format]}
          </div>
        </div>
      </div>

      {/* Placeholder notice */}
      <div className="px-4 py-3 bg-gold-500/5 border-t border-gold-500/20">
        <div className="flex gap-3">
          <Warning size={20} weight="thin" className="text-gold-600 mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-medium text-ink-900 text-sm">Placeholder Code</p>
            <p className="text-sm text-ink-500 mt-1">
              This is example code showing the expected output format. Real code
              will be generated from policy updates when the LLM integration is
              complete.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
