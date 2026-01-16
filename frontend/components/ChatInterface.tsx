'use client';

import { useState } from 'react';
import type { ChatMessage, Citation } from '@/lib/types';
import { sendChatMessage } from '@/lib/api';
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
      className={`inline-flex items-center gap-1.5 px-3 py-1 text-xs font-mono hover:opacity-80 transition-all duration-200 hover:scale-105 ${
        isFannie
          ? 'bg-fannie/10 text-fannie border border-fannie/20'
          : 'bg-freddie/10 text-freddie border border-freddie/20'
      }`}
    >
      <BookOpen size={14} weight="thin" />
      {citation.source}
    </a>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';

  return (
    <div className={`animate-fade-up ${isUser ? 'message-user' : 'message-sage'}`}>
      {isUser ? (
        <p className="text-ink-900 text-lg">{message.content}</p>
      ) : (
        <>
          <p className="text-ink-700 whitespace-pre-wrap leading-relaxed text-[15px]">
            {message.content}
          </p>
          {message.citations && message.citations.length > 0 && (
            <div className="mt-5 pt-4 border-t border-border">
              <p className="text-xs font-mono uppercase tracking-widest text-ink-500 mb-3">
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
  const [conversationId, setConversationId] = useState<string | undefined>();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const messageText = input.trim();
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage({
        message: messageText,
        conversation_id: conversationId,
      });

      setConversationId(response.conversation_id);
      setMessages((prev) => [...prev, response.message]);
    } catch (err) {
      console.error('Error sending message:', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[650px] bg-surface border-2 border-border shadow-sm">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 md:p-8">
        {messages.map((message, index) => (
          <MessageBubble key={index} message={message} />
        ))}
        {isLoading && (
          <div className="message-sage animate-fade-up">
            <div className="flex items-center gap-3 text-ink-500">
              <CircleNotch size={18} weight="thin" className="animate-spin" />
              <span className="text-sm">Searching guidelines...</span>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="border-t-2 border-border p-5 md:p-6 bg-paper">
        <div className="flex gap-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={placeholder}
            disabled={isLoading}
            className="input flex-1 disabled:opacity-60 disabled:cursor-not-allowed text-base"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="btn btn-primary inline-flex items-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <PaperPlaneTilt size={20} weight="bold" />
            Send
          </button>
        </div>
        <p className="mt-3 text-xs text-ink-500">
          Ask about eligibility requirements, income limits, property types, or any
          other guideline questions.
        </p>
      </form>
    </div>
  );
}
