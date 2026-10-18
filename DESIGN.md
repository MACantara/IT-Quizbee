# Design — Answer Sheet

IT Quizbee renders as the OMR answer sheet contestants already know: bond paper, graphite ink, hairline rules, letter bubbles, and red-pencil marking. Direction chosen via the Impeccable decision board (seed `8a45a085`); the previous pastel-gradient UI is anti-reference, not authority.

## Palette

| Token | Value | Use |
| --- | --- | --- |
| `paper` | `#fbfaf6` | page ground |
| `ink` | `#211f1c` | text, borders, rules |
| `ink-soft` | `#57544c` | secondary text |
| `line` | `#dcd8cb` | hairline rules, cell borders |
| `pencil` | `#2e5aac` | actions, links, selected state, focus ring |
| `pencil-deep` | `#254e93` | primary hover |
| `pencil-wash` | `#f0f4fb` | selected/soft highlight fill |
| `mark` | `#c4392e` | incorrect answers, errors, expired timer |
| `pass` | `#2e7d46` | correct answers |
| `warn` | `#a86e00` | caution, low-but-live timer |
| `*-wash` | pale tints | marked feedback fills |

## Type

- Public Sans (`--font-public-sans` via `next/font/google`) — all text.
- Roboto Mono (`--font-roboto-mono`) — every numeral via `.num`; tabular figures.
- Section heads and field labels are small-caps tracked (`field-label`, `tracking-[0.14em]`).

## Surfaces and structure

- `.sheet`: white stock, 1px `line` border, square corners. Hairline rules and fields separate content — no shadows, no gradients, no radius past `rounded-sm`.
- Masthead and footer close the form with a 2px ink rule; `FORM Q-1` sits top-right in mono.
- Topic/subtopic indexes read as ruled rows with `divide-y divide-line`.

## Signature controls

- **Answer options** are `.choice` rows holding a real `sr-only` radio and a `.bubble` letter cell; shading (pencil fill) marks the choice, `:has(:focus-visible)` keeps keyboard focus visible.
- **Progress** is a shaded-cell strip: one 3×3px cell per question, pencil-filled when answered (`role="progressbar"` on the container).
- **Timer/counts/score** are `.num` figures; the timer sits in a `.readout` box and turns `warn` then `mark` as it runs down.
- **Buttons** are rectangular: `.btn-pencil` primary, `.btn-ink` dark, `.btn-line` outlined; `:active` shades to scale(0.97); 150ms ease-out on named properties only.
- **Results** read as a marked scorecard: `pass` green for correct, `mark` red for incorrect, verdict icon in an ink-bordered box.

## Icons

lucide-react only (`Trophy`, `Zap`, `CircleCheck`, `CircleX`, `TriangleAlert`, `Hourglass`, `RotateCcw`, `House`, `Book`, `Tag`, topic glyphs). No emoji, no icon fonts.

## Motion

One entrance (`animate-fade-in`, 180ms ease-out) plus color/transform transitions on controls. `prefers-reduced-motion` collapses both. No scale-on-hover, no `transition-all`, nothing that blocks answering.

## Product invariants

The IT Quizbee name, competition framing, local-only attempt storage, quiz modes, scoring, and routing are untouched. Browser chrome (selection, caret, focus rings, scrollbars) inherits the palette.
