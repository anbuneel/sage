# SAGE Design System
## "The Modern Ledger"

*Merged from Gemini + Claude concepts*

---

## Design Philosophy

SAGE is a **modern instrument for experts** — blending the authority of a legal library with the precision of a terminal. Not a cold SaaS dashboard. Not a generic fintech template.

**The Vibe:** Authoritative, Archival, Precise — "Old World Wisdom meets New World Intelligence"

**Inspiration:**
- The Economist / Monocle (editorial authority)
- Bloomberg Terminal (information density)
- Architectural blueprints (precision)
- Private banking materials (restrained luxury)

**Core Principles:**
1. **Gravitas without stuffiness** — Serious expertise, approachable delivery
2. **Warmth in finance** — Home = emotional. Reflect that.
3. **Precision over decoration** — Every element earns its place
4. **Two personas** — Manager sees engineering rigor; Underwriter sees familiar authority

---

## Color Palette: "Organic Authority"

Avoid the standard "Trust Blue." Use colors that evoke money, paper, and ink.

```css
:root {
  /* Backgrounds - The Canvas */
  --paper-light: #F9F8F4;      /* Alabaster - warm paper, not blinding white */
  --paper-dark: #1A1E23;       /* Deep Slate - rich charcoal, not pure black */
  --surface-light: #F0EDE5;    /* Card backgrounds in light mode */
  --surface-dark: #252A31;     /* Card backgrounds in dark mode */

  /* Primary - Sage Green (the name!) */
  --sage-900: #0D1F17;
  --sage-800: #1B4332;
  --sage-700: #2D6A4F;
  --sage-600: #3A6B56;         /* Primary brand color */
  --sage-500: #52B788;
  --sage-400: #74C69D;

  /* Ink - Text colors */
  --ink-900: #1C1917;          /* Headlines */
  --ink-700: #3D3833;          /* Body text */
  --ink-500: #6B6560;          /* Secondary text */
  --ink-300: #A8A29E;          /* Muted text */

  /* Accent - Amber Gold (highlights, focus states) */
  --gold-500: #E0A82E;
  --gold-600: #C4922A;
  --gold-700: #A67B23;

  /* Semantic */
  --success: #3A6B56;          /* Sage green */
  --warning: #E0A82E;          /* Amber gold */
  --error: #C05640;            /* Burnt sienna - like a red-ink correction */

  /* Code/Technical - Indigo Ink */
  --code-bg: #1E1E2E;          /* Dark panel for code, even in light mode */
  --code-text: #CDD6F4;
  --indigo: #3F47CC;           /* Code accents */

  /* GSE Brand (badges only) */
  --fannie-blue: #00447C;
  --freddie-red: #8B2332;
}
```

### Usage Guidelines
| Element | Light Mode | Dark Mode |
|---------|------------|-----------|
| Page background | `paper-light` | `paper-dark` |
| Card background | `surface-light` | `surface-dark` |
| Headlines | `ink-900` | `paper-light` |
| Body text | `ink-700` | `ink-300` |
| Primary button | `sage-600` | `sage-500` |
| Code blocks | `code-bg` (always dark) | `code-bg` |

---

## Typography: "Editorial & Code"

Contrast the feeling of a **Regulatory Document** (Serif) with an **Engineering Console** (Monospace).

### Font Stack

```css
/* Headlines - Fraunces: Variable serif with personality and authority */
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&display=swap');

/* Body - Public Sans: Clean, geometric, gets out of the way */
@import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600&display=swap');

/* Data & Code - JetBrains Mono: Precision for numbers and code */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --font-display: 'Fraunces', Georgia, serif;
  --font-body: 'Public Sans', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'Consolas', monospace;
}
```

### Type Scale

| Element | Font | Size | Weight | Notes |
|---------|------|------|--------|-------|
| Hero headline | Fraunces | 56px | 700 | The "Guide" voice |
| Page title | Fraunces | 36px | 600 | Authority |
| Section head | Fraunces | 24px | 600 | |
| Card title | Public Sans | 18px | 600 | Clean interface |
| Body | Public Sans | 16px | 400 | Highly legible |
| Caption | Public Sans | 14px | 400 | |
| Data/Numbers | JetBrains Mono | 16px | 500 | ALL numbers |
| Code | JetBrains Mono | 14px | 400 | |
| Badge/Label | JetBrains Mono | 11px | 500 | Uppercase, tracking |

### Typography Rules
- **Headlines are serif** — Conveys authority. When citing the Selling Guide, it should look like a legal citation.
- **Body is sans-serif** — Clean, gets out of the way for dense content.
- **ALL numbers in monospace** — DTI, LTV, dollar amounts, percentages. Non-negotiable.
- **No all-caps except badges** — Screaming is not professional.

---

## Iconography: Phosphor Icons (Thin)

**NOT** filled, bubbly icons. Use **stroke-based, fine-line icons** that feel like technical schematics.

### Icon Set: Phosphor Thin

```bash
npm install @phosphor-icons/react
```

```tsx
import { House, CheckCircle, Warning, FileText, Lightning } from '@phosphor-icons/react';

// Use "thin" weight throughout
<House size={24} weight="thin" />
```

### Icon Style Rules
```css
.icon {
  stroke-width: 1;
  stroke: currentColor;
  fill: none;
}
```

### Icon Mapping

| Concept | Phosphor Icon | Notes |
|---------|---------------|-------|
| Home/Property | `House` | Thin weight |
| Eligible | `CheckCircle` | Sage green |
| Ineligible | `XCircle` | Burnt sienna |
| Warning | `Warning` | Hexagon style, amber |
| Credit Score | `Gauge` | Not a number badge |
| Percentage (LTV/DTI) | `Percent` | |
| Income | `CurrencyDollar` | |
| Document/Policy | `FileText` | Or `Article` |
| Citation | `Quotes` | For guide references |
| Agent/AI | `Lightning` | Geometric, not robot |
| Fix Suggestion | `Lightbulb` | Amber gold color |
| Code | `Code` | |
| Changes/History | `ClockCounterClockwise` | |
| Chat/Ask | `ChatText` | |

### Custom: GSE Badges
Don't use logos. Use colored squares:
```tsx
// Fannie Mae
<span className="w-2 h-2 bg-fannie-blue rounded-sm" />

// Freddie Mac
<span className="w-2 h-2 bg-freddie-red rounded-sm" />
```

---

## Shape & Structure: "Structured Brutalism"

Avoid the "soft SaaS" look (large border radii, drop shadows, floating cards).

### Core Rules
- **Borders over shadows** — 1px solid borders define sections
- **Tight radii** — 2px corners, or sharp (0px) for stamps
- **Split views** — Vertical panes for comparison (Fannie vs Freddie, Old vs New)

### Border Tokens
```css
:root {
  --border-subtle: 1px solid #E8E0D0;    /* Light mode */
  --border-emphasis: 1px solid #3A6B56;  /* Active/focus */
  --radius-sm: 2px;
  --radius-none: 0px;                     /* For stamps */
}
```

---

## Component Patterns

### Cards
```
┌─────────────────────────────────────┐
│                                     │  ← 1px border (subtle)
│   Card Title                        │  ← Public Sans 600
│   ─────────────────────             │  ← Hairline divider
│                                     │
│   Content with generous padding     │  ← 24px padding
│   $350,000                          │  ← JetBrains Mono
│                                     │
└─────────────────────────────────────┘
```

```css
.card {
  background: var(--surface-light);
  border: 1px solid #E8E0D0;
  border-radius: 2px;
  padding: 24px;
}
.card:hover {
  border-color: var(--sage-600);
}
```

### Buttons

```css
/* Primary */
.btn-primary {
  background: var(--sage-600);
  color: white;
  font-family: var(--font-body);
  font-weight: 600;
  padding: 12px 24px;
  border-radius: 2px;
  border: none;
}
.btn-primary:hover {
  background: var(--sage-700);
}

/* Secondary */
.btn-secondary {
  background: transparent;
  color: var(--ink-900);
  border: 1px solid #D4C9B5;
  padding: 12px 24px;
  border-radius: 2px;
}
.btn-secondary:hover {
  border-color: var(--sage-600);
  color: var(--sage-600);
}
```

### Form Inputs

```css
.input {
  background: white;
  border: 1px solid #D4C9B5;
  border-radius: 2px;
  padding: 12px 16px;
  font-family: var(--font-body);
  font-size: 16px;
}
.input:focus {
  outline: none;
  border-color: var(--sage-600);
  box-shadow: 0 0 0 3px rgba(58, 107, 86, 0.1);
}

/* Numbers should use mono */
.input-currency,
.input-percentage {
  font-family: var(--font-mono);
}
```

---

## Key UI Moments

### 1. The "Stamp" — Eligibility Badge (Tab 4)

Don't use a colored pill. Design it like a **physical rubber stamp**.

```
┌─────────────────────────────┐
│                             │
│      ✓ ELIGIBLE             │  ← Sage green border, 0 radius
│      FNMA HOMEREADY         │  ← JetBrains Mono, uppercase
│                             │
└─────────────────────────────┘

┌─────────────────────────────┐
│                             │
│      ✗ INELIGIBLE           │  ← Burnt sienna border
│      FHLMC 4501.5           │  ← Citation in mono
│                             │
└─────────────────────────────┘
```

```css
.stamp {
  border: 3px solid var(--success);
  border-radius: 0;
  padding: 16px 24px;
  font-family: var(--font-mono);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  /* Optional: slight rotation for "stamped" feel */
  transform: rotate(-1deg);
}
.stamp--fail {
  border-color: var(--error);
}
```

### 2. The "Transcript" — Chat UI (Tab 1)

Don't make it look like iMessage. Make it look like a **legal transcript**.

```
USER                                           │
─────────────────────────────────────────────────
Is 50% DTI allowed for HomeReady?              │


SAGE                                           │  [1]
─────────────────────────────────────────────────
│ Per Selling Guide B3-6-02, the maximum       │
│ DTI ratio for HomeReady is 50% when the      │  ← Indented with sage
│ loan is underwritten through DU.             │     left border
│                                              │

                                    ┌──────────────────┐
                                    │ [1] B3-6-02      │
                                    │ DTI Requirements │
                                    └──────────────────┘
                                         ↑ Floating citation
```

```css
.message-user {
  font-family: var(--font-body);
  font-weight: 600;
  padding: 16px 0;
  border-top: 1px solid #E8E0D0;
}

.message-sage {
  padding: 16px;
  padding-left: 20px;
  border-left: 3px solid var(--sage-600);
  background: var(--surface-light);
  margin: 8px 0;
}

.citation-float {
  position: absolute;
  right: 0;
  font-family: var(--font-mono);
  font-size: 11px;
  background: var(--paper-light);
  border: 1px solid #E8E0D0;
  padding: 8px 12px;
}
```

### 3. The "Diff" — Code View (Tab 3)

Lean into the **IDE aesthetic**. Dark panel even in light mode.

```css
.code-panel {
  background: var(--code-bg);  /* Always dark */
  color: var(--code-text);
  font-family: var(--font-mono);
  font-size: 14px;
  padding: 24px;
  border-radius: 2px;
  overflow-x: auto;
}

/* Custom syntax colors matching brand */
.token-keyword { color: var(--indigo); }
.token-string { color: var(--gold-500); }
.token-comment { color: var(--ink-500); }
.token-added { color: var(--sage-400); }
.token-removed { color: var(--error); }
```

### 4. The Split Comparison

For Fannie vs Freddie comparison:

```
┌─────────────────────┬─────────────────────┐
│  ■ FANNIE MAE       │  ■ FREDDIE MAC      │
│                     │                     │
│  HomeReady          │  Home Possible      │
│  ─────────────────  │  ─────────────────  │
│                     │                     │
│  Credit: 620 min    │  Credit: 660 min    │
│  DTI: 50% max       │  DTI: 45% max       │
│  LTV: 97% max       │  LTV: 97% max       │
│                     │                     │
│  [STAMP: ELIGIBLE]  │  [STAMP: INELIGIBLE]│
│                     │                     │
└─────────────────────┴─────────────────────┘
```

---

## Layout

### Spacing Scale
```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;
  --space-16: 64px;
}
```

### Page Structure
```
┌────────────────────────────────────────────────────┐
│  SAGE                    [Ask] [Changes] [Code] [Check]   │
├────────────────────────────────────────────────────┤
│                                                    │
│     Page Title                     ← Fraunces     │
│     Subtitle description           ← Public Sans  │
│                                                    │
│     ┌──────────────────┬──────────────────┐       │
│     │                  │                  │       │
│     │  Split Pane L    │  Split Pane R    │       │
│     │                  │                  │       │
│     └──────────────────┴──────────────────┘       │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## Dark Mode

Full dark mode support, not just hero.

```css
@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: var(--paper-dark);
    --bg-surface: var(--surface-dark);
    --text-primary: var(--paper-light);
    --text-secondary: var(--ink-300);
    --border-subtle: 1px solid #3D3833;
  }
}
```

---

## Animation & Interaction

### Hover States
- Buttons: Background darkens (no scale/transform)
- Cards: Border color shifts to sage
- Links: Underline fades in

### Focus States
- 3px sage-tinted ring on all interactive elements
- High contrast for accessibility

### The "Stamp" Animation
When eligibility is determined, the stamp should feel like it's being pressed:

```css
@keyframes stamp {
  0% { transform: scale(1.1) rotate(-2deg); opacity: 0; }
  50% { transform: scale(0.98) rotate(-1deg); }
  100% { transform: scale(1) rotate(-1deg); opacity: 1; }
}

.stamp-animate {
  animation: stamp 0.3s ease-out forwards;
}
```

---

## What We're Avoiding

| ❌ Don't | ✅ Do Instead |
|---------|---------------|
| Purple/blue gradients | Sage green + amber accents |
| Inter, Roboto, system fonts | Fraunces + Public Sans + JetBrains |
| 16px+ rounded corners | 2px or sharp (0px for stamps) |
| Drop shadows everywhere | 1px borders |
| iMessage-style chat | Transcript with citations |
| Light code blocks | Dark code panels always |
| Filled chunky icons | Phosphor thin stroke icons |
| Generic "Success/Error" | Stamp metaphor with citations |

---

## Implementation Checklist

1. [ ] Install Phosphor icons: `npm install @phosphor-icons/react`
2. [ ] Add Google Fonts: Fraunces, Public Sans, JetBrains Mono
3. [ ] Create CSS variables in globals.css
4. [ ] Build base components: Button, Input, Card, Stamp
5. [ ] Implement dark mode toggle
6. [ ] Redesign navigation
7. [ ] Redesign landing page
8. [ ] Redesign Check My Loan with stamps + split view
9. [ ] Redesign Ask the Guide as transcript
10. [ ] Style code blocks with custom theme

---

## Next.js Font Setup

```tsx
// app/layout.tsx
import { Fraunces, Public_Sans, JetBrains_Mono } from 'next/font/google';

const fraunces = Fraunces({
  subsets: ['latin'],
  variable: '--font-display',
  display: 'swap',
});

const publicSans = Public_Sans({
  subsets: ['latin'],
  variable: '--font-body',
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
});

export default function RootLayout({ children }) {
  return (
    <html className={`${fraunces.variable} ${publicSans.variable} ${jetbrainsMono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
```

---

*This design system positions SAGE as a premium, authoritative tool for mortgage professionals. The serif headlines, thin-stroke icons, stamp metaphors, and transcript-style chat immediately differentiate it from the sea of purple-gradient fintech products.*
