'use client';

import { useState, useRef, useEffect } from 'react';
import TabNav from '@/components/TabNav';
import type { ChatMessage, Citation } from '@/lib/types';
import { sendChatMessage } from '@/lib/api';
import {
  MagnifyingGlass,
  PaperPlaneTilt,
  CircleNotch,
  BookOpen,
  ArrowRight,
  Sparkle,
  Books,
  CaretRight
} from '@phosphor-icons/react';

// Sample questions that users can click
const sampleQuestions = [
  { text: 'What is the minimum credit score for HomeReady?', category: 'Credit' },
  { text: 'Can I use gift funds for the down payment?', category: 'Assets' },
  { text: 'What are the income limits for HomeReady?', category: 'Income' },
  { text: 'Is homeownership education required?', category: 'Requirements' },
  { text: 'What property types are eligible?', category: 'Property' },
  { text: 'Compare HomeReady vs Home Possible', category: 'Comparison' },
];

// Build deep link URL for a GSE section
function buildSectionUrl(sectionId: string, isFannie: boolean): { url: string; isDirect: boolean } {
  if (isFannie) {
    // Fannie Mae: Use their Selling Guide search with section ID as query
    // This is more reliable than guessing the exact URL structure
    const searchQuery = encodeURIComponent(sectionId);
    return {
      url: `https://singlefamily.fanniemae.com/search?keys=${searchQuery}`,
      isDirect: false,
    };
  } else {
    // Freddie Mac: Direct deep link works!
    // Section format from our files: "5501-4" -> need "5501.4"
    const normalizedSection = sectionId.replace(/-/g, '.');
    return {
      url: `https://guide.freddiemac.com/app/guide/section/${normalizedSection}`,
      isDirect: true,
    };
  }
}

// Citation component with GSE branding and deep linking
function CitationCard({ citation, index }: { citation: Citation; index: number }) {
  const isFannie = citation.source.toLowerCase().includes('fannie');
  const sectionId = citation.source.replace('Fannie Mae - ', '').replace('Freddie Mac - ', '');

  // Build link URL
  const { url, isDirect } = buildSectionUrl(sectionId, isFannie);

  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className={`
        group flex flex-col p-4 border-2 transition-all duration-200
        hover:shadow-md hover:-translate-y-0.5
        ${isFannie
          ? 'border-fannie/20 bg-fannie/5 hover:border-fannie/40'
          : 'border-freddie/20 bg-freddie/5 hover:border-freddie/40'
        }
      `}
    >
      {/* Header with index and GSE */}
      <div className="flex items-center gap-3 mb-2">
        <div className={`
          flex-shrink-0 w-7 h-7 flex items-center justify-center text-xs font-mono font-bold
          ${isFannie ? 'bg-fannie text-white' : 'bg-freddie text-white'}
        `}>
          {index + 1}
        </div>
        <span className={`text-xs font-mono uppercase tracking-wider ${isFannie ? 'text-fannie' : 'text-freddie'}`}>
          {isFannie ? 'Fannie Mae' : 'Freddie Mac'}
        </span>
      </div>

      {/* Section ID - the main reference */}
      <p className="text-sm font-semibold text-ink-800 mb-2 font-mono">
        {sectionId}
      </p>

      {/* Snippet preview if available */}
      {citation.text && (
        <p className="text-xs text-ink-500 line-clamp-2 mb-3 leading-relaxed">
          &ldquo;{citation.text.substring(0, 120)}...&rdquo;
        </p>
      )}

      {/* Link with context-appropriate text */}
      <div className={`
        inline-flex items-center gap-1.5 text-xs font-medium mt-auto
        ${isFannie ? 'text-fannie' : 'text-freddie'}
        group-hover:underline
      `}>
        <span>{isDirect ? 'View Section →' : 'Search in Guide →'}</span>
      </div>
    </a>
  );
}

// Format response content with proper markdown-like rendering
function FormattedResponse({ content }: { content: string }) {
  // Split content into sections and format
  const sections = content.split(/\n(?=##\s)/);

  return (
    <div className="prose-sage">
      {sections.map((section, sectionIndex) => {
        const lines = section.split('\n');

        return (
          <div key={sectionIndex} className={sectionIndex > 0 ? 'mt-6' : ''}>
            {lines.map((line, lineIndex) => {
              // Main headers (##)
              if (line.startsWith('## ')) {
                return (
                  <h2 key={lineIndex} className="font-display text-xl font-semibold text-ink-900 mt-6 mb-3 pb-2 border-b border-border">
                    {line.replace('## ', '')}
                  </h2>
                );
              }

              // Sub-headers (###) or bold sections (**)
              if (line.startsWith('### ') || line.match(/^\*\*[^*]+\*\*$/)) {
                const text = line.replace('### ', '').replace(/\*\*/g, '');
                return (
                  <h3 key={lineIndex} className="font-display text-lg font-semibold text-ink-800 mt-5 mb-2">
                    {text}
                  </h3>
                );
              }

              // Bullet points
              if (line.match(/^[-•]\s/) || line.match(/^\d+\.\s/)) {
                const text = line.replace(/^[-•]\s/, '').replace(/^\d+\.\s/, '');
                // Handle inline bold
                const formattedText = text.split(/(\*\*[^*]+\*\*)/).map((part, i) => {
                  if (part.startsWith('**') && part.endsWith('**')) {
                    return <strong key={i} className="font-semibold text-ink-900">{part.slice(2, -2)}</strong>;
                  }
                  return part;
                });

                return (
                  <div key={lineIndex} className="flex gap-3 my-2 ml-1">
                    <span className="text-sage-600 mt-1.5 flex-shrink-0">
                      <div className="w-1.5 h-1.5 bg-sage-600 rounded-full" />
                    </span>
                    <p className="text-ink-700 leading-relaxed">{formattedText}</p>
                  </div>
                );
              }

              // Regular paragraphs
              if (line.trim()) {
                // Handle inline bold and citations
                const formattedText = line.split(/(\*\*[^*]+\*\*|\[\d+\])/).map((part, i) => {
                  if (part.startsWith('**') && part.endsWith('**')) {
                    return <strong key={i} className="font-semibold text-ink-900">{part.slice(2, -2)}</strong>;
                  }
                  if (part.match(/^\[\d+\]$/)) {
                    return (
                      <sup key={i} className="text-sage-600 font-mono text-xs ml-0.5">
                        {part}
                      </sup>
                    );
                  }
                  return part;
                });

                return (
                  <p key={lineIndex} className="text-ink-700 leading-relaxed my-3">
                    {formattedText}
                  </p>
                );
              }

              return null;
            })}
          </div>
        );
      })}
    </div>
  );
}

// Question/Answer pair component
function QAPair({ question, answer, citations }: {
  question: string;
  answer: string;
  citations?: Citation[];
}) {
  return (
    <div className="animate-fade-up">
      {/* Question */}
      <div className="flex items-start gap-4 mb-6">
        <div className="flex-shrink-0 w-10 h-10 bg-sage-600 flex items-center justify-center">
          <span className="text-white font-display font-bold text-sm">Q</span>
        </div>
        <p className="text-xl font-display font-semibold text-ink-900 pt-1.5">
          {question}
        </p>
      </div>

      {/* Answer */}
      <div className="ml-14 pb-8 border-b-2 border-border mb-8">
        <FormattedResponse content={answer} />

        {/* Citations */}
        {citations && citations.length > 0 && (
          <div className="mt-8 pt-6 border-t border-dashed border-border">
            <div className="flex items-start justify-between gap-4 mb-4">
              <h4 className="flex items-center gap-2 text-sm font-mono uppercase tracking-widest text-ink-500">
                <BookOpen size={16} weight="bold" />
                Sources ({citations.length})
              </h4>
              <p className="text-xs text-ink-400 text-right">
                Click to view in official GSE guides
              </p>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              {citations.map((citation, index) => (
                <CitationCard key={index} citation={citation} index={index} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function AskPage() {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [qaPairs, setQaPairs] = useState<Array<{
    question: string;
    answer: string;
    citations?: Citation[];
  }>>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Scroll to results when new answer arrives
  useEffect(() => {
    if (qaPairs.length > 0 && resultsRef.current) {
      resultsRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [qaPairs.length]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const question = input.trim();
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage({
        message: question,
        conversation_id: conversationId,
      });

      setConversationId(response.conversation_id);
      // Prepend new Q&A to show latest at top
      setQaPairs((prev) => [{
        question,
        answer: response.message.content,
        citations: response.message.citations,
      }, ...prev]);
    } catch (err) {
      console.error('Error sending message:', err);
      // Prepend error response to show at top too
      setQaPairs((prev) => [{
        question,
        answer: 'Sorry, I encountered an error while searching the guidelines. Please try again.',
      }, ...prev]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSampleClick = (question: string) => {
    setInput(question);
    inputRef.current?.focus();
  };

  return (
    <div className="min-h-screen bg-paper">
      <TabNav />

      {/* Hero Section with Search */}
      <div className="relative bg-gradient-to-b from-sage-900 via-sage-800 to-sage-900 text-white overflow-hidden">
        {/* Decorative grid pattern */}
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)
            `,
            backgroundSize: '32px 32px',
          }}
        />

        {/* Decorative glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-sage-500/20 rounded-full blur-3xl" />

        <div className="relative max-w-4xl mx-auto px-6 lg:px-8 py-16 md:py-24">
          {/* Title */}
          <div className="text-center mb-10 animate-fade-up">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 border border-white/20 text-sm font-mono uppercase tracking-wider mb-6">
              <Sparkle size={14} weight="fill" className="text-gold-500" />
              RAG-Powered Search
            </div>
            <h1 className="font-display text-4xl md:text-5xl lg:text-6xl font-bold mb-4 tracking-tight">
              Ask the Guide
            </h1>
            <p className="text-sage-300 text-lg md:text-xl max-w-2xl mx-auto leading-relaxed">
              Search across 4,800+ pages of Fannie Mae and Freddie Mac guidelines.
              Every answer includes citations you can verify.
            </p>
          </div>

          {/* Search Input */}
          <form onSubmit={handleSubmit} className="animate-fade-up" style={{ animationDelay: '100ms' }}>
            <div className="relative">
              <div className="absolute left-5 top-1/2 -translate-y-1/2 text-ink-500">
                <MagnifyingGlass size={24} weight="bold" />
              </div>
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask anything about mortgage guidelines..."
                disabled={isLoading}
                className="
                  w-full pl-14 pr-36 py-5 text-lg
                  bg-white text-ink-900 placeholder-ink-400
                  border-2 border-transparent
                  focus:outline-none focus:border-sage-500
                  shadow-xl
                  disabled:opacity-70 disabled:cursor-not-allowed
                  transition-all duration-200
                "
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="
                  absolute right-2 top-1/2 -translate-y-1/2
                  px-6 py-3 bg-sage-600 text-white font-semibold
                  hover:bg-sage-700 disabled:opacity-50 disabled:cursor-not-allowed
                  transition-all duration-200 hover:shadow-lg
                  flex items-center gap-2
                "
              >
                {isLoading ? (
                  <>
                    <CircleNotch size={20} weight="bold" className="animate-spin" />
                    <span className="hidden sm:inline">Searching...</span>
                  </>
                ) : (
                  <>
                    <PaperPlaneTilt size={20} weight="bold" />
                    <span className="hidden sm:inline">Search</span>
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Sample Questions */}
          <div className="mt-8 animate-fade-up" style={{ animationDelay: '200ms' }}>
            <p className="text-center text-sage-400 text-sm mb-4">Try asking:</p>
            <div className="flex flex-wrap justify-center gap-2">
              {sampleQuestions.map((q, index) => (
                <button
                  key={index}
                  onClick={() => handleSampleClick(q.text)}
                  className="
                    group px-4 py-2 bg-white/10 border border-white/20
                    text-sm text-white/90 hover:text-white
                    hover:bg-white/20 hover:border-white/30
                    transition-all duration-200
                    flex items-center gap-2
                  "
                >
                  <span className="text-sage-400 text-xs font-mono">{q.category}</span>
                  <span className="text-white/30">|</span>
                  <span>{q.text}</span>
                  <ArrowRight size={14} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Results Section */}
      <main className="max-w-4xl mx-auto px-6 lg:px-8 py-12 md:py-16">
        {/* Loading State */}
        {isLoading && qaPairs.length === 0 && (
          <div className="text-center py-16 animate-fade-up">
            <CircleNotch size={48} weight="thin" className="animate-spin text-sage-600 mx-auto mb-4" />
            <p className="text-ink-500 text-lg">Searching through guidelines...</p>
            <p className="text-ink-400 text-sm mt-2">This may take a few seconds</p>
          </div>
        )}

        {/* Q&A Results */}
        {qaPairs.length > 0 && (
          <div ref={resultsRef}>
            {/* Loading indicator at top for follow-up questions */}
            {isLoading && (
              <div className="flex items-center gap-3 text-ink-500 animate-fade-up mb-8 pb-8 border-b-2 border-border">
                <CircleNotch size={20} weight="bold" className="animate-spin" />
                <span>Searching guidelines...</span>
              </div>
            )}

            {qaPairs.map((qa, index) => (
              <QAPair
                key={index}
                question={qa.question}
                answer={qa.answer}
                citations={qa.citations}
              />
            ))}
          </div>
        )}

        {/* Empty State */}
        {qaPairs.length === 0 && !isLoading && (
          <div className="animate-fade-up">
            {/* Info Section */}
            <div className="bg-surface border-2 border-border p-8 mb-8">
              <div className="flex items-start gap-5">
                <div className="w-12 h-12 bg-sage-600/10 flex items-center justify-center flex-shrink-0">
                  <Books size={24} weight="thin" className="text-sage-600" />
                </div>
                <div>
                  <h3 className="font-display text-xl font-semibold text-ink-900 mb-3">
                    How it works
                  </h3>
                  <p className="text-ink-600 leading-relaxed mb-4">
                    SAGE uses RAG (Retrieval-Augmented Generation) to search through the complete
                    Fannie Mae Selling Guide and Freddie Mac Seller/Servicer Guide. Every answer
                    includes citations so you can verify the information.
                  </p>
                  <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-fannie" />
                      <span className="text-sm font-mono text-ink-600">Fannie Mae</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-freddie" />
                      <span className="text-sm font-mono text-ink-600">Freddie Mac</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-px bg-border border-2 border-border">
              <div className="bg-paper p-6 text-center">
                <p className="font-mono text-3xl font-bold text-sage-600">4,866</p>
                <p className="text-sm text-ink-500 mt-1">Pages Indexed</p>
              </div>
              <div className="bg-paper p-6 text-center">
                <p className="font-mono text-3xl font-bold text-sage-600">1,203</p>
                <p className="text-sm text-ink-500 mt-1">Guide Sections</p>
              </div>
              <div className="bg-paper p-6 text-center">
                <p className="font-mono text-3xl font-bold text-sage-600">2</p>
                <p className="text-sm text-ink-500 mt-1">GSEs Covered</p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
