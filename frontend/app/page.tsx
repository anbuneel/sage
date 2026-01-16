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

      <main>
        {/* Hero Section - Dark, typography-focused */}
        <section className="hero-gradient text-paper relative overflow-hidden">
          {/* Subtle grid pattern overlay */}
          <div className="absolute inset-0 opacity-[0.03]" style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
                             linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
            backgroundSize: '32px 32px'
          }} />

          <div className="max-w-6xl mx-auto px-6 lg:px-8 py-32 md:py-40 relative">
            <div className="max-w-3xl animate-stagger">
              <p className="text-sage-400 font-mono text-sm tracking-widest uppercase mb-6 animate-fade-up">
                Smart Agentic Guide Engine
              </p>
              <h1 className="font-display text-5xl md:text-7xl lg:text-8xl font-bold tracking-tighter mb-8 animate-fade-up" style={{ animationDelay: '50ms' }}>
                Policy intelligence
                <br />
                <span className="text-gold-500">that works for you.</span>
              </h1>
              <p className="text-xl md:text-2xl text-ink-300 leading-relaxed mb-12 max-w-2xl animate-fade-up" style={{ animationDelay: '100ms' }}>
                SAGE transforms Fannie Mae and Freddie Mac guidelines into an intelligent
                system that monitors changes, reasons about loans, and generates compliance updates.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 animate-fade-up" style={{ animationDelay: '150ms' }}>
                <Link
                  href="/check"
                  className="btn btn-lg inline-flex items-center justify-center gap-3 bg-paper text-sage-900 hover:bg-surface shadow-xl hover:shadow-2xl transition-all duration-200"
                >
                  Check Loan Eligibility
                  <ArrowRight size={20} weight="bold" />
                </Link>
                <Link
                  href="/ask"
                  className="btn btn-lg inline-flex items-center justify-center gap-2 border-2 border-sage-500/50 text-paper bg-transparent hover:bg-sage-800/50 hover:border-sage-400 transition-all duration-200"
                >
                  Ask the Guide
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Value Prop - The comparison angle */}
        <section className="border-b border-border section-paper">
          <div className="max-w-6xl mx-auto px-6 lg:px-8 py-20 md:py-24">
            <div className="flex items-center gap-3 mb-10">
              <Scales size={28} weight="thin" className="text-sage-600" />
              <h2 className="font-display text-2xl md:text-3xl font-semibold">
                Compare What Matters
              </h2>
            </div>
            <div className="grid md:grid-cols-2 gap-px bg-border border-ledger">
              {/* Fannie Mae */}
              <div className="bg-paper p-8 md:p-10 hover-lift">
                <div className="gse-badge gse-badge-fannie mb-5">Fannie Mae</div>
                <h3 className="font-display text-xl md:text-2xl font-semibold mb-3">HomeReady</h3>
                <p className="text-ink-500 mb-8 leading-relaxed">
                  Flexible underwriting for low-to-moderate income borrowers.
                </p>
                <dl className="space-y-4 font-mono text-sm">
                  <div className="flex justify-between py-2 border-b border-border/50">
                    <dt className="text-ink-500">Min Credit</dt>
                    <dd className="text-ink-900 font-medium">620</dd>
                  </div>
                  <div className="flex justify-between py-2 border-b border-border/50">
                    <dt className="text-ink-500">Max DTI</dt>
                    <dd className="text-ink-900 font-medium">50%</dd>
                  </div>
                  <div className="flex justify-between py-2 border-b border-border/50">
                    <dt className="text-ink-500">Max LTV</dt>
                    <dd className="text-ink-900 font-medium">97%</dd>
                  </div>
                  <div className="flex justify-between py-2">
                    <dt className="text-ink-500">Income Limit</dt>
                    <dd className="text-ink-900 font-medium">80% AMI</dd>
                  </div>
                </dl>
              </div>
              {/* Freddie Mac */}
              <div className="bg-paper p-8 md:p-10 hover-lift">
                <div className="gse-badge gse-badge-freddie mb-5">Freddie Mac</div>
                <h3 className="font-display text-xl md:text-2xl font-semibold mb-3">Home Possible</h3>
                <p className="text-ink-500 mb-8 leading-relaxed">
                  Low down payment options for qualified borrowers.
                </p>
                <dl className="space-y-4 font-mono text-sm">
                  <div className="flex justify-between py-2 border-b border-border/50">
                    <dt className="text-ink-500">Min Credit</dt>
                    <dd className="text-ink-900 font-medium">660</dd>
                  </div>
                  <div className="flex justify-between py-2 border-b border-border/50">
                    <dt className="text-ink-500">Max DTI</dt>
                    <dd className="text-ink-900 font-medium">45%</dd>
                  </div>
                  <div className="flex justify-between py-2 border-b border-border/50">
                    <dt className="text-ink-500">Max LTV</dt>
                    <dd className="text-ink-900 font-medium">97%</dd>
                  </div>
                  <div className="flex justify-between py-2">
                    <dt className="text-ink-500">Income Limit</dt>
                    <dd className="text-ink-900 font-medium">80% AMI</dd>
                  </div>
                </dl>
              </div>
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section className="bg-surface">
          <div className="max-w-6xl mx-auto px-6 lg:px-8 py-20 md:py-24">
            <h2 className="font-display text-2xl md:text-3xl font-semibold mb-12">
              Four Ways to Work Smarter
            </h2>

            <div className="grid md:grid-cols-2 gap-6 lg:gap-8">
              {/* Ask the Guide */}
              <Link href="/ask" className="card group p-8">
                <div className="flex items-start gap-5">
                  <div className="p-4 bg-sage-600/10 text-sage-600 transition-transform duration-200 group-hover:scale-110">
                    <ChatText size={28} weight="thin" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-display text-lg md:text-xl font-semibold mb-3 group-hover:text-sage-600 transition-colors">
                      Ask the Guide
                    </h3>
                    <p className="text-ink-500 leading-relaxed">
                      Chat with AI to get instant answers about mortgage guidelines.
                      Every response includes citations from official selling guides.
                    </p>
                  </div>
                </div>
              </Link>

              {/* What Changed */}
              <Link href="/changes" className="card group p-8">
                <div className="flex items-start gap-5">
                  <div className="p-4 bg-gold-500/10 text-gold-600 transition-transform duration-200 group-hover:scale-110">
                    <ClockCounterClockwise size={28} weight="thin" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-display text-lg md:text-xl font-semibold mb-3 group-hover:text-sage-600 transition-colors">
                      What Changed
                    </h3>
                    <p className="text-ink-500 leading-relaxed">
                      Track policy updates in real time. Monitor Lender Letters,
                      Bulletins, and guide changes as they happen.
                    </p>
                  </div>
                </div>
              </Link>

              {/* Code Updates */}
              <Link href="/code" className="card group p-8">
                <div className="flex items-start gap-5">
                  <div className="p-4 bg-indigo/10 text-indigo transition-transform duration-200 group-hover:scale-110">
                    <Code size={28} weight="thin" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-display text-lg md:text-xl font-semibold mb-3 group-hover:text-sage-600 transition-colors">
                      Code Updates
                    </h3>
                    <p className="text-ink-500 leading-relaxed">
                      Get auto-generated rule changes when policies update.
                      Export in Python, TypeScript, YAML, or JSON Logic.
                    </p>
                  </div>
                </div>
              </Link>

              {/* Check My Loan */}
              <Link href="/check" className="card group p-8">
                <div className="flex items-start gap-5">
                  <div className="p-4 bg-success/10 text-success transition-transform duration-200 group-hover:scale-110">
                    <CheckCircle size={28} weight="thin" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-display text-lg md:text-xl font-semibold mb-3 group-hover:text-sage-600 transition-colors">
                      Check My Loan
                    </h3>
                    <p className="text-ink-500 leading-relaxed">
                      Enter a scenario and instantly check eligibility for both
                      programs. Get specific fix suggestions when loans fail.
                    </p>
                  </div>
                </div>
              </Link>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-border bg-paper">
          <div className="max-w-6xl mx-auto px-6 lg:px-8 py-10 md:py-12">
            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-sage-600 flex items-center justify-center">
                  <span className="text-white font-display font-bold">S</span>
                </div>
                <span className="font-display text-lg font-semibold text-ink-900">SAGE</span>
              </div>
              <p className="text-sm text-ink-500 text-center md:text-right max-w-md">
                For informational purposes only. Not financial advice.
                Consult a licensed mortgage professional.
              </p>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
