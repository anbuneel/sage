'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  ChatText,
  ClockCounterClockwise,
  Code,
  CheckCircle,
  List,
} from '@phosphor-icons/react';

interface Tab {
  name: string;
  href: string;
  icon: React.ReactNode;
}

const tabs: Tab[] = [
  {
    name: 'Ask the Guide',
    href: '/ask',
    icon: <ChatText size={20} weight="thin" />,
  },
  {
    name: 'What Changed',
    href: '/changes',
    icon: <ClockCounterClockwise size={20} weight="thin" />,
  },
  {
    name: 'Code Updates',
    href: '/code',
    icon: <Code size={20} weight="thin" />,
  },
  {
    name: 'Check My Loan',
    href: '/check',
    icon: <CheckCircle size={20} weight="thin" />,
  },
];

export default function TabNav() {
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav
      className={`
        sticky top-0 z-50 border-b bg-paper transition-all duration-200
        ${scrolled ? 'border-transparent shadow-md' : 'border-border'}
      `}
    >
      <div className="max-w-6xl mx-auto px-6 lg:px-8">
        <div className="flex items-center justify-between h-18">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 bg-sage-600 flex items-center justify-center transition-transform duration-200 group-hover:scale-105">
              <span className="text-white font-display font-bold text-lg">S</span>
            </div>
            <span className="font-display text-xl font-semibold text-ink-900 tracking-tight">
              SAGE
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {tabs.map((tab) => {
              const isActive = pathname === tab.href;
              return (
                <Link
                  key={tab.href}
                  href={tab.href}
                  className={`
                    relative flex items-center gap-2 px-4 py-2.5 text-sm font-medium transition-all duration-200
                    ${isActive
                      ? 'text-sage-600'
                      : 'text-ink-500 hover:text-ink-900'
                    }
                  `}
                >
                  <span className={`transition-transform duration-200 ${isActive ? '' : 'group-hover:scale-110'}`}>
                    {tab.icon}
                  </span>
                  {tab.name}
                  {/* Active indicator line */}
                  <span
                    className={`
                      absolute bottom-0 left-4 right-4 h-0.5 bg-sage-600 transition-transform duration-200
                      ${isActive ? 'scale-x-100' : 'scale-x-0'}
                    `}
                  />
                </Link>
              );
            })}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <MobileMenu tabs={tabs} currentPath={pathname} />
          </div>
        </div>
      </div>
    </nav>
  );
}

function MobileMenu({
  tabs,
  currentPath,
}: {
  tabs: Tab[];
  currentPath: string;
}) {
  return (
    <div className="relative group">
      <button
        className="p-2.5 text-ink-500 hover:text-ink-900 hover:bg-surface transition-all duration-200 rounded-sm"
        aria-label="Open menu"
      >
        <List size={24} weight="thin" />
      </button>

      {/* Dropdown */}
      <div className="absolute right-0 mt-2 w-60 bg-paper border border-border shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
        <div className="py-2">
          {tabs.map((tab) => {
            const isActive = currentPath === tab.href;
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={`
                  flex items-center gap-3 px-5 py-3.5 text-sm transition-all duration-200
                  ${isActive
                    ? 'text-sage-600 bg-sage-600/5 border-l-2 border-sage-600'
                    : 'text-ink-700 hover:bg-surface hover:translate-x-1 border-l-2 border-transparent'
                  }
                `}
              >
                {tab.icon}
                <span className="font-medium">{tab.name}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
