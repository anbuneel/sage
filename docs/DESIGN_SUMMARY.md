# SAGE Design System Summary

## The Concept: "The Modern Ledger"

*Merged from Gemini + Claude design concepts*

**The Vibe:** Authoritative, Archival, Precise — "Old World Wisdom meets New World Intelligence"

---

## What We Merged

| From Gemini | From Claude | Final Decision |
|-------------|-------------|----------------|
| Phosphor thin icons | Lucide icons | ✅ **Phosphor thin** |
| Transcript-style chat | Standard chat | ✅ **Legal transcript with floating citations** |
| Rubber stamp eligibility | Left-border accent | ✅ **Stamp with animation** |
| Dark code panels always | Light code panels | ✅ **Dark panels: `#1E1E2E`** |
| Indigo for code accents | Not specified | ✅ **Indigo: `#3F47CC`** |
| Public Sans body | Source Serif body | ✅ **Public Sans** (cleaner for UI) |
| Full dark mode | Hero only | ✅ **Full dark mode support** |
| Newsreader headlines | Fraunces headlines | ✅ **Fraunces** (more character) |
| Concept sketches | Detailed component specs | ✅ **Both combined** |

---

## The Distinctive Elements

| Element | What Makes It Different |
|---------|------------------------|
| 🖋️ **Serif headlines** | Fraunces font — almost no fintech does this |
| 📝 **Transcript chat** | Legal transcript with floating citations — not iMessage bubbles |
| 🔖 **Rubber stamps** | Eligibility shown as physical stamps — not colored pills |
| 🎯 **Phosphor thin icons** | Fine-line technical schematics — not chunky filled icons |
| 🌲 **Sage green + amber** | Organic authority palette — not purple/blue gradients |
| 📐 **Sharp corners** | 2px radius, 1px borders — not soft shadows and rounded cards |
| 🌙 **Dark code panels** | IDE aesthetic always — even in light mode |

---

## Color Palette

```
Backgrounds
├── Light: #F9F8F4 (Alabaster - warm paper)
└── Dark:  #1A1E23 (Deep Slate - rich charcoal)

Primary
└── Sage Green: #3A6B56 (trust, stability, the name!)

Accents
├── Amber Gold:    #E0A82E (highlights, focus)
├── Burnt Sienna:  #C05640 (errors, like red-ink corrections)
└── Indigo Ink:    #3F47CC (code, technical elements)

GSE Brands
├── Fannie Mae: #00447C (blue square badge)
└── Freddie Mac: #8B2332 (red square badge)
```

---

## Typography

```
Headlines  → Fraunces (serif, authority, "the Guide voice")
Body/UI    → Public Sans (clean, gets out of the way)
Data/Code  → JetBrains Mono (precision, ALL numbers)
```

**Rule:** Every dollar amount, percentage, and score uses monospace.

---

## Key UI Patterns

### 1. The Stamp (Eligibility)
```
┌─────────────────────────────┐
│      ✓ ELIGIBLE             │  ← 3px sage border
│      FNMA HOMEREADY         │  ← Mono, uppercase
└─────────────────────────────┘   ← Slight rotation (-1deg)
```

### 2. The Transcript (Chat)
```
USER
─────────────────────────────────
Is 50% DTI allowed?

SAGE                              [1]
─────────────────────────────────
│ Per Selling Guide B3-6-02...   │  ← Sage left border
│                                │
                      ┌─────────────┐
                      │ [1] B3-6-02 │  ← Floating citation
                      └─────────────┘
```

### 3. The Split View (Comparison)
```
┌─────────────────┬─────────────────┐
│ ■ FANNIE MAE    │ ■ FREDDIE MAC   │
│ HomeReady       │ Home Possible   │
│                 │                 │
│ [✓ ELIGIBLE]    │ [✗ INELIGIBLE]  │
└─────────────────┴─────────────────┘
```

### 4. The Dark Code Panel
```css
.code-panel {
  background: #1E1E2E;  /* Always dark, even in light mode */
  color: #CDD6F4;
}
```

---

## What We're Avoiding

| ❌ Generic AI Slop | ✅ Modern Ledger |
|-------------------|------------------|
| Purple/blue gradients | Sage green + amber gold |
| Inter, Roboto fonts | Fraunces + Public Sans + JetBrains |
| 16px rounded corners | 2px sharp corners |
| Drop shadows on cards | 1px borders |
| iMessage chat bubbles | Legal transcript |
| Light code blocks | Dark code panels |
| Filled chunky icons | Phosphor thin strokes |
| "Success" green pills | Rubber stamp metaphor |

---

## Implementation Priority

1. Install Phosphor icons
2. Set up fonts (Fraunces, Public Sans, JetBrains Mono)
3. Create CSS variables
4. Build base components (Button, Input, Card, Stamp)
5. Redesign navigation
6. Redesign landing page
7. Redesign Check My Loan (stamps + split view)
8. Redesign Ask the Guide (transcript)
9. Add dark mode support

---

*Full specifications in [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md)*
