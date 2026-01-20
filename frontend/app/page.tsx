import Link from 'next/link';
import TabNav from '@/components/TabNav';
import {
  ChatText,
  ClockCounterClockwise,
  Code,
  CheckCircle,
  ArrowRight,
  Scales,
} from '@phosphor-icons/react/dist/ssr';

export default function Home() {
  return (
    <div className="min-h-screen bg-paper">
      <TabNav />

      {/* Compact Hero */}
      <section className="bg-ink-900 text-paper">
        <div className="max-w-6xl mx-auto px-6 lg:px-8 py-10 md:py-12">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sage-400 font-mono text-xs tracking-widest uppercase mb-2">
                Smart Agentic Guide Engine
              </p>
              <h1 className="font-display text-2xl md:text-3xl font-bold">
                <span className="text-paper">Fannie Mae</span>
                <span className="text-gold-500"> & </span>
                <span className="text-paper">Freddie Mac</span>
                <span className="text-sage-400"> Guidelines</span>
              </h1>
            </div>
            <div className="hidden md:flex gap-3">
              <Link
                href="/check"
                className="btn bg-paper text-ink-900 hover:bg-surface text-sm px-5 py-2"
              >
                Check Loan
              </Link>
              <Link
                href="/ask"
                className="btn border border-sage-500/50 text-paper bg-transparent hover:bg-sage-800/50 text-sm px-5 py-2"
              >
                Ask a Question
              </Link>
            </div>
          </div>
        </div>
      </section>

      <main className="max-w-6xl mx-auto px-6 lg:px-8 py-10 md:py-12">
        {/* Quick Access Cards */}
        <div className="grid md:grid-cols-2 gap-5 mb-12">
          {/* Check My Loan */}
          <Link href="/check" className="card group p-6 md:p-8">
            <div className="flex items-start gap-5">
              <div className="p-3 bg-success/10 text-success transition-transform duration-200 group-hover:scale-110">
                <CheckCircle size={24} weight="thin" />
              </div>
              <div className="flex-1">
                <h2 className="font-display text-lg font-semibold mb-2 group-hover:text-sage-600 transition-colors">
                  Check My Loan
                </h2>
                <p className="text-ink-500 text-sm leading-relaxed">
                  Check eligibility for HomeReady and Home Possible programs.
                </p>
              </div>
              <ArrowRight size={20} weight="thin" className="text-ink-400 group-hover:text-sage-600 transition-colors" />
            </div>
          </Link>

          {/* Ask the Guide */}
          <Link href="/ask" className="card group p-6 md:p-8">
            <div className="flex items-start gap-5">
              <div className="p-3 bg-sage-600/10 text-sage-600 transition-transform duration-200 group-hover:scale-110">
                <ChatText size={24} weight="thin" />
              </div>
              <div className="flex-1">
                <h2 className="font-display text-lg font-semibold mb-2 group-hover:text-sage-600 transition-colors">
                  Ask the Guide
                </h2>
                <p className="text-ink-500 text-sm leading-relaxed">
                  Chat with AI to get answers about mortgage guidelines with citations.
                </p>
              </div>
              <ArrowRight size={20} weight="thin" className="text-ink-400 group-hover:text-sage-600 transition-colors" />
            </div>
          </Link>

          {/* What Changed */}
          <Link href="/changes" className="card group p-6 md:p-8">
            <div className="flex items-start gap-5">
              <div className="p-3 bg-gold-500/10 text-gold-600 transition-transform duration-200 group-hover:scale-110">
                <ClockCounterClockwise size={24} weight="thin" />
              </div>
              <div className="flex-1">
                <h2 className="font-display text-lg font-semibold mb-2 group-hover:text-sage-600 transition-colors">
                  What Changed
                </h2>
                <p className="text-ink-500 text-sm leading-relaxed">
                  Track policy updates, Lender Letters, and Bulletins.
                </p>
              </div>
              <ArrowRight size={20} weight="thin" className="text-ink-400 group-hover:text-sage-600 transition-colors" />
            </div>
          </Link>

          {/* Code Updates hidden - not needed for demo */}
        </div>

        {/* Program Comparison */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-5">
            <Scales size={20} weight="thin" className="text-ink-500" />
            <h2 className="font-mono text-xs uppercase tracking-widest text-ink-500">
              Program Comparison
            </h2>
          </div>
          <div className="grid md:grid-cols-2 gap-px bg-border border-2 border-border">
            {/* Fannie Mae */}
            <div className="bg-paper p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="gse-badge gse-badge-fannie">Fannie Mae</div>
                <span className="font-display font-semibold">HomeReady</span>
              </div>
              <dl className="space-y-2 font-mono text-sm">
                <div className="flex justify-between py-1.5 border-b border-border/50">
                  <dt className="text-ink-500">Min Credit</dt>
                  <dd className="text-ink-900">620</dd>
                </div>
                <div className="flex justify-between py-1.5 border-b border-border/50">
                  <dt className="text-ink-500">Max DTI</dt>
                  <dd className="text-ink-900">50%</dd>
                </div>
                <div className="flex justify-between py-1.5 border-b border-border/50">
                  <dt className="text-ink-500">Max LTV</dt>
                  <dd className="text-ink-900">97%</dd>
                </div>
                <div className="flex justify-between py-1.5">
                  <dt className="text-ink-500">Income Limit</dt>
                  <dd className="text-ink-900">80% AMI</dd>
                </div>
              </dl>
            </div>
            {/* Freddie Mac */}
            <div className="bg-paper p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="gse-badge gse-badge-freddie">Freddie Mac</div>
                <span className="font-display font-semibold">Home Possible</span>
              </div>
              <dl className="space-y-2 font-mono text-sm">
                <div className="flex justify-between py-1.5 border-b border-border/50">
                  <dt className="text-ink-500">Min Credit</dt>
                  <dd className="text-ink-900">660</dd>
                </div>
                <div className="flex justify-between py-1.5 border-b border-border/50">
                  <dt className="text-ink-500">Max DTI</dt>
                  <dd className="text-ink-900">45%</dd>
                </div>
                <div className="flex justify-between py-1.5 border-b border-border/50">
                  <dt className="text-ink-500">Max LTV</dt>
                  <dd className="text-ink-900">97%</dd>
                </div>
                <div className="flex justify-between py-1.5">
                  <dt className="text-ink-500">Income Limit</dt>
                  <dd className="text-ink-900">80% AMI</dd>
                </div>
              </dl>
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}
