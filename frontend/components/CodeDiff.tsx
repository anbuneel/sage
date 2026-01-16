'use client';

import { useState } from 'react';
import type { CodeFormat } from '@/lib/types';

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
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-gray-700">Format:</span>
          <div className="flex space-x-1">
            {(Object.keys(CODE_SAMPLES) as CodeFormat[]).map((fmt) => (
              <button
                key={fmt}
                onClick={() => setFormat(fmt)}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                  format === fmt
                    ? 'bg-indigo-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                }`}
              >
                {FORMAT_LABELS[fmt]}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={handleCopy}
          className="flex items-center px-3 py-1.5 rounded text-sm font-medium text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 transition-colors"
        >
          {copied ? (
            <>
              <svg
                className="w-4 h-4 mr-1.5 text-green-600"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
              Copied!
            </>
          ) : (
            <>
              <svg
                className="w-4 h-4 mr-1.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                />
              </svg>
              Copy
            </>
          )}
        </button>
      </div>

      {/* Code Block */}
      <div className="relative">
        <pre className="p-4 overflow-x-auto bg-gray-900 text-gray-100 text-sm leading-relaxed">
          <code>{code}</code>
        </pre>

        {/* Line numbers overlay */}
        <div className="absolute top-0 left-0 p-4 select-none pointer-events-none">
          <div className="text-gray-500 text-sm leading-relaxed text-right pr-4 border-r border-gray-700">
            {code.split('\n').map((_, i) => (
              <div key={i}>{i + 1}</div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <div className="text-gray-500">
            {updateId ? (
              <span>
                Generated from update: <strong>{updateId}</strong>
              </span>
            ) : (
              <span>Select a policy update to view generated code</span>
            )}
          </div>
          <div className="text-gray-500">
            {code.split('\n').length} lines | {format.toUpperCase()}
          </div>
        </div>
      </div>

      {/* Placeholder notice */}
      <div className="px-4 py-3 bg-amber-50 border-t border-amber-200">
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
              Placeholder Code
            </h4>
            <p className="text-sm text-amber-700 mt-1">
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
