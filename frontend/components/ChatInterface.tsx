'use client';

import { useState } from 'react';
import type { ChatMessage, Citation } from '@/lib/types';

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
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800 mr-1">
      {citation.source}
    </span>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`
          max-w-[80%] rounded-lg px-4 py-3
          ${isUser
            ? 'bg-indigo-600 text-white'
            : 'bg-white border border-gray-200 text-gray-900'
          }
        `}
      >
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        {message.citations && message.citations.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-200">
            <p className="text-xs text-gray-500 mb-1">Sources:</p>
            <div className="flex flex-wrap gap-1">
              {message.citations.map((citation, index) => (
                <CitationBadge key={index} citation={citation} />
              ))}
            </div>
          </div>
        )}
      </div>
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
    <div className="flex flex-col h-[600px] bg-gray-50 rounded-lg border border-gray-200">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((message, index) => (
          <MessageBubble key={index} message={message} />
        ))}
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: '0.1s' }}
                />
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: '0.2s' }}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4">
        <div className="flex space-x-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={placeholder}
            disabled={isLoading}
            className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-2 rounded-lg font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
        <p className="mt-2 text-xs text-gray-500">
          Ask about eligibility requirements, income limits, property types, or any
          other guideline questions.
        </p>
      </form>
    </div>
  );
}
