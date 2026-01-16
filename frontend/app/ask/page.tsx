'use client';

import TabNav from '@/components/TabNav';
import ChatInterface from '@/components/ChatInterface';
import { ChatText, Books, Info } from '@phosphor-icons/react';

export default function AskPage() {
  const exampleQuestions = [
    'What is the minimum credit score for HomeReady?',
    'Can I use Home Possible for a condo?',
    'What are the income limits for HomeReady in California?',
    'Is homeownership education required for Home Possible?',
    'What property types are eligible for HomeReady?',
    'Can I use gift funds for the down payment?',
  ];

  return (
    <div className="min-h-screen bg-paper">
      <TabNav />

      <main className="max-w-4xl mx-auto px-6 lg:px-8 py-16 md:py-20">
        {/* Page Header */}
        <div className="mb-12 animate-fade-up">
          <h1 className="font-display text-4xl md:text-5xl font-bold text-ink-900 mb-4">
            Ask the Guide
          </h1>
          <p className="text-ink-500 text-lg md:text-xl max-w-2xl leading-relaxed">
            Chat with AI to get instant answers about Fannie Mae and Freddie Mac
            mortgage guidelines. All responses include citations from official
            selling guides.
          </p>
        </div>

        {/* Chat Interface */}
        <div className="animate-fade-up" style={{ animationDelay: '50ms' }}>
          <ChatInterface placeholder="e.g., What is the maximum DTI for HomeReady?" />
        </div>

        {/* Example Questions */}
        <div className="mt-12 animate-fade-up" style={{ animationDelay: '100ms' }}>
          <h2 className="flex items-center gap-2 text-sm font-mono uppercase tracking-widest text-ink-500 mb-5">
            <ChatText size={18} weight="thin" />
            Example Questions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {exampleQuestions.map((question, index) => (
              <button
                key={index}
                className="text-left px-5 py-4 bg-surface border border-border hover:border-sage-600 hover:shadow-sm transition-all duration-200 text-ink-700 hover:text-ink-900"
              >
                {question}
              </button>
            ))}
          </div>
        </div>

        {/* Info Section */}
        <div className="mt-12 bg-sage-600/5 border-2 border-sage-600/20 p-6 md:p-8 animate-fade-up" style={{ animationDelay: '150ms' }}>
          <div className="flex gap-5">
            <Info size={28} weight="thin" className="text-sage-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-display text-lg font-semibold text-ink-900 mb-3">
                About This Feature
              </h3>
              <p className="text-ink-500 leading-relaxed">
                This RAG (Retrieval-Augmented Generation) chat searches through the
                complete Fannie Mae Selling Guide and Freddie Mac Seller/Servicer
                Guide to find relevant information for your questions. Every answer
                includes citations so you can verify the source.
              </p>
              <div className="mt-5 flex items-center gap-6">
                <div className="flex items-center gap-2">
                  <div className="gse-badge gse-badge-fannie">Fannie Mae</div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="gse-badge gse-badge-freddie">Freddie Mac</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sources */}
        <div className="mt-12 border-t border-border pt-10 animate-fade-up" style={{ animationDelay: '200ms' }}>
          <h2 className="flex items-center gap-2 text-sm font-mono uppercase tracking-widest text-ink-500 mb-5">
            <Books size={18} weight="thin" />
            Indexed Sources
          </h2>
          <div className="grid md:grid-cols-2 gap-px bg-border border-2 border-border">
            <div className="bg-paper p-5 md:p-6">
              <div className="gse-badge gse-badge-fannie mb-3">Fannie Mae</div>
              <p className="text-ink-700 font-medium">Selling Guide (Full)</p>
              <p className="text-xs text-ink-500 mt-2 font-mono">Last updated: Jan 2025</p>
            </div>
            <div className="bg-paper p-5 md:p-6">
              <div className="gse-badge gse-badge-freddie mb-3">Freddie Mac</div>
              <p className="text-ink-700 font-medium">Seller/Servicer Guide</p>
              <p className="text-xs text-ink-500 mt-2 font-mono">Last updated: Jan 2025</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
