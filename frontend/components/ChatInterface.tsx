'use client';

import { useState } from 'react';
import type { ChatMessage, Citation } from '@/lib/types';
import { PaperPlaneTilt, CircleNotch, BookOpen } from '@phosphor-icons/react';

interface ChatInterfaceProps {
  placeholder?: string;
}

// Mock initial message
const initialMessages: ChatMessage[] = [
  {
    role: 'assistant',
    content:
      'Hello! I\'m your mortgage guidelines assistant. Ask me anything about Fannie Mae HomeReady or Freddie Mac Home Possible programs. For example, you can ask about credit score requirements, income limits, or eligible property types.',
    citations: undefined,
  },
];

function CitationBadge({ citation }: { citation: Citation }) {
  const isFannie = citation.source.toLowerCase().includes('fannie');

  return (
    <a
      href={citation.url}
      target="_blank"
      rel="noopener noreferrer"
      className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-mono hover:opacity-80 transition-opacity ${
        isFannie
          ? 'bg-fannie/10 text-fannie'
          : 'bg-freddie/10 text-freddie'
      }`}
    >
      <BookOpen size={12} weight="thin" />
      {citation.source}
    </a>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';

  return (
    <div className={`${isUser ? 'message-user' : 'message-sage'}`}>
      {isUser ? (
        <p className="text-ink-900">{message.content}</p>
      ) : (
        <>
          <p className="text-ink-700 whitespace-pre-wrap leading-relaxed">
            {message.content}
          </p>
          {message.citations && message.citations.length > 0 && (
            <div className="mt-4 pt-3 border-t border-border">
              <p className="text-xs font-mono uppercase tracking-wider text-ink-500 mb-2">
                Sources
              </p>
              <div className="flex flex-wrap gap-2">
                {message.citations.map((citation, index) => (
                  <CitationBadge key={index} citation={citation} />
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default function ChatInterface({
  placeholder = 'Ask a question about mortgage guidelines...',
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Simulate API response (mock for now)
    setTimeout(() => {
      const mockResponse: ChatMessage = {
        role: 'assistant',
        content:
          'This is a placeholder response. The RAG chat functionality will be implemented when the backend is ready. The system will search through Fannie Mae and Freddie Mac guidelines to provide accurate, cited answers to your questions.',
        citations: [
          {
            text: 'Example citation',
            source: 'Fannie Mae Selling Guide B5-6-01',
            url: 'https://example.com',
          },
        ],
      };
      setMessages((prev) => [...prev, mockResponse]);
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-[600px] bg-surface border border-border">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6">
        {messages.map((message, index) => (
          <MessageBubble key={index} message={message} />
        ))}
        {isLoading && (
          <div className="message-sage">
            <div className="flex items-center gap-2 text-ink-500">
              <CircleNotch size={16} weight="thin" className="animate-spin" />
              <span className="text-sm">Searching guidelines...</span>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="border-t border-border p-4 bg-paper">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={placeholder}
            disabled={isLoading}
            className="input flex-1 disabled:opacity-60 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="btn btn-primary inline-flex items-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <PaperPlaneTilt size={18} weight="bold" />
            Send
          </button>
        </div>
        <p className="mt-2 text-xs text-ink-500">
          Ask about eligibility requirements, income limits, property types, or any
          other guideline questions.
        </p>
      </form>
    </div>
  );
}
