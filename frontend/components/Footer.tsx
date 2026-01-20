'use client';

import Link from 'next/link';
import {
  BookOpenText,
  ArrowSquareOut,
} from '@phosphor-icons/react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-ink-900 text-paper mt-auto">
      <div className="max-w-6xl mx-auto px-6 lg:px-8 py-10">
        {/* Main footer content */}
        <div className="grid md:grid-cols-3 gap-8 mb-8">
          {/* Branding */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <BookOpenText size={24} weight="thin" className="text-sage-400" />
              <span className="font-display text-lg font-semibold">SAGE</span>
            </div>
            <p className="text-ink-300 text-sm leading-relaxed">
              Smart Agentic Guide Engine for Fannie Mae and Freddie Mac mortgage guidelines.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="font-mono text-xs uppercase tracking-widest text-ink-300 mb-4">
              Quick Links
            </h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/check" className="text-paper/80 hover:text-sage-400 transition-colors">
                  Check My Loan
                </Link>
              </li>
              <li>
                <Link href="/ask" className="text-paper/80 hover:text-sage-400 transition-colors">
                  Ask the Guide
                </Link>
              </li>
              <li>
                <Link href="/changes" className="text-paper/80 hover:text-sage-400 transition-colors">
                  What Changed
                </Link>
              </li>
{/* Code Updates hidden - not needed for demo */}
            </ul>
          </div>

          {/* Official Resources */}
          <div>
            <h3 className="font-mono text-xs uppercase tracking-widest text-ink-300 mb-4">
              Official Resources
            </h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a
                  href="https://selling-guide.fanniemae.com/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-paper/80 hover:text-sage-400 transition-colors inline-flex items-center gap-1"
                >
                  <span className="w-2 h-2 bg-fannie rounded-sm"></span>
                  Fannie Mae Selling Guide
                  <ArrowSquareOut size={12} weight="thin" />
                </a>
              </li>
              <li>
                <a
                  href="https://guide.freddiemac.com/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-paper/80 hover:text-sage-400 transition-colors inline-flex items-center gap-1"
                >
                  <span className="w-2 h-2 bg-freddie rounded-sm"></span>
                  Freddie Mac Guide
                  <ArrowSquareOut size={12} weight="thin" />
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-ink-700 pt-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-xs text-ink-400 text-center md:text-left">
              For informational purposes only. Consult a licensed mortgage professional for advice.
            </p>
            <p className="text-xs text-ink-500">
              &copy; {currentYear} SAGE
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
