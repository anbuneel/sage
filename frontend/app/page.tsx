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
        <section className="bg-sage-900 text-paper">
          <div className="max-w-6xl mx-auto px-6 py-24">
            <div className="max-w-3xl">
              <p className="text-sage-400 font-mono text-sm tracking-wider uppercase mb-4">
                Smart Agentic Guide Engine
              </p>
              <h1 className="font-display text-5xl md:text-6xl font-bold tracking-tight mb-6">
                Policy intelligence
                <br />
                <span className="text-gold-500">that works for you.</span>
              </h1>
              <p className="text-xl text-ink-300 leading-relaxed mb-10 max-w-2xl">
                SAGE transforms Fannie Mae and Freddie Mac guidelines into an intelligent
                system that monitors changes, reasons about loans, and generates compliance updates.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link
                  href="/check"
                  className="btn btn-primary inline-flex items-center justify-center gap-2 bg-paper text-sage-900 hover:bg-surface"
                >
                  Check Loan Eligibility
                  <ArrowRight size={18} weight="bold" />
                </Link>
                <Link
                  href="/ask"
                  className="btn inline-flex items-center justify-center gap-2 border border-sage-600 text-paper bg-transparent hover:bg-sage-800"
                >
                  Ask the Guide
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Value Prop - The comparison angle */}
        <section className="border-b border-border">
          <div className="max-w-6xl mx-auto px-6 py-16">
            <div className="flex items-center gap-3 mb-8">
              <Scales size={24} weight="thin" className="text-sage-600" />
              <h2 className="font-display text-2xl font-semibold">
                Compare What Matters
              </h2>
            </div>
            <div className="grid md:grid-cols-2 gap-px bg-border">
              {/* Fannie Mae */}
              <div className="bg-paper p-8">
                <div className="gse-badge gse-badge-fannie mb-4">Fannie Mae</div>
                <h3 className="font-display text-xl font-semibold mb-2">HomeReady</h3>
                <p className="text-ink-500 mb-6">
                  Flexible underwriting for low-to-moderate income borrowers.
                </p>
                <dl className="space-y-3 font-mono text-sm">
                  <div className="flex justify-between">
                    <dt className="text-ink-500">Min Credit</dt>
                    <dd className="text-ink-900">620</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-ink-500">Max DTI</dt>
                    <dd className="text-ink-900">50%</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-ink-500">Max LTV</dt>
                    <dd className="text-ink-900">97%</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-ink-500">Income Limit</dt>
                    <dd className="text-ink-900">80% AMI</dd>
                  </div>
                </dl>
              </div>
              {/* Freddie Mac */}
              <div className="bg-paper p-8">
                <div className="gse-badge gse-badge-freddie mb-4">Freddie Mac</div>
                <h3 className="font-display text-xl font-semibold mb-2">Home Possible</h3>
                <p className="text-ink-500 mb-6">
                  Low down payment options for qualified borrowers.
                </p>
                <dl className="space-y-3 font-mono text-sm">
                  <div className="flex justify-between">
                    <dt className="text-ink-500">Min Credit</dt>
                    <dd className="text-ink-900">660</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-ink-500">Max DTI</dt>
                    <dd className="text-ink-900">45%</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-ink-500">Max LTV</dt>
                    <dd className="text-ink-900">97%</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-ink-500">Income Limit</dt>
                    <dd className="text-ink-900">80% AMI</dd>
                  </div>
                </dl>
              </div>
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section className="bg-surface">
          <div className="max-w-6xl mx-auto px-6 py-16">
            <h2 className="font-display text-2xl font-semibold mb-10">
              Four Ways to Work Smarter
            </h2>

            <div className="grid md:grid-cols-2 gap-6">
              {/* Ask the Guide */}
              <Link href="/ask" className="card group hover:border-sage-600 transition-colors">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-sage-600/10 text-sage-600">
                    <ChatText size={24} weight="thin" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-display text-lg font-semibold mb-2 group-hover:text-sage-600 transition-colors">
                      Ask the Guide
                    </h3>
                    <p className="text-ink-500 text-sm leading-relaxed">
                      Chat with AI to get instant answers about mortgage guidelines.
                      Every response includes citations from official selling guides.
                    </p>
                  </div>
                </div>
              </Link>

              {/* What Changed */}
              <Link href="/changes" className="card group hover:border-sage-600 transition-colors">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-gold-500/10 text-gold-600">
                    <ClockCounterClockwise size={24} weight="thin" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-display text-lg font-semibold mb-2 group-hover:text-sage-600 transition-colors">
                      What Changed
                    </h3>
                    <p className="text-ink-500 text-sm leading-relaxed">
                      Track policy updates in real time. Monitor Lender Letters,
                      Bulletins, and guide changes as they happen.
                    </p>
                  </div>
                </div>
              </Link>

              {/* Code Updates */}
              <Link href="/code" className="card group hover:border-sage-600 transition-colors">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-indigo/10 text-indigo">
                    <Code size={24} weight="thin" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-display text-lg font-semibold mb-2 group-hover:text-sage-600 transition-colors">
                      Code Updates
                    </h3>
                    <p className="text-ink-500 text-sm leading-relaxed">
                      Get auto-generated rule changes when policies update.
                      Export in Python, TypeScript, YAML, or JSON Logic.
                    </p>
                  </div>
                </div>
              </Link>

              {/* Check My Loan */}
              <Link href="/check" className="card group hover:border-sage-600 transition-colors">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-success/10 text-success">
                    <CheckCircle size={24} weight="thin" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-display text-lg font-semibold mb-2 group-hover:text-sage-600 transition-colors">
                      Check My Loan
                    </h3>
                    <p className="text-ink-500 text-sm leading-relaxed">
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
        <footer className="border-t border-border">
          <div className="max-w-6xl mx-auto px-6 py-8">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 bg-sage-600 flex items-center justify-center">
                  <span className="text-white font-display font-bold text-sm">S</span>
                </div>
                <span className="font-display font-semibold text-ink-900">SAGE</span>
              </div>
              <p className="text-sm text-ink-500 text-center">
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
