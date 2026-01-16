'use client';

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

  return (
    <nav className="border-b border-border bg-paper">
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 bg-sage-600 flex items-center justify-center">
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
                    flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors
                    ${isActive
                      ? 'text-sage-600 bg-sage-600/5'
                      : 'text-ink-500 hover:text-ink-900 hover:bg-surface'
                    }
                  `}
                >
                  {tab.icon}
                  {tab.name}
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
        className="p-2 text-ink-500 hover:text-ink-900 hover:bg-surface transition-colors"
        aria-label="Open menu"
      >
        <List size={24} weight="thin" />
      </button>

      {/* Dropdown */}
      <div className="absolute right-0 mt-2 w-56 bg-paper border border-border opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-150 z-50">
        <div className="py-2">
          {tabs.map((tab) => {
            const isActive = currentPath === tab.href;
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={`
                  flex items-center gap-3 px-4 py-3 text-sm
                  ${isActive
                    ? 'text-sage-600 bg-sage-600/5'
                    : 'text-ink-700 hover:bg-surface'
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
