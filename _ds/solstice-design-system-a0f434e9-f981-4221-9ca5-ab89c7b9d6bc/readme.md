# Solstice Design System

**Premise.** Solstice is built on one idea: *colour, type and image should come from the same light.* Every hue in the palette is sampled from late-afternoon sun — bone paper, ink, terracotta, ochre, sage, tide-blue, plum. Those hues are locked into **chords** (surface + text + accent + image duotone). Set `data-chord="dusk"` on any element and the surface, the typography, every component *and every photograph inside it* re-harmonise together — photos are mapped onto the chord's duotone via `ImageFrame`. That's how image, colour and text always match.

## Sources
None. The brief was: *"a design system where the match of colours and text and image is just mind blowing."* No codebase, Figma, logo, fonts or imagery were provided — everything here is an original from-scratch direction.
- **Name** "Solstice" is a working name chosen for this system, not a supplied brand.
- **Logo:** none supplied — the name is set in type (Instrument Serif + accent full stop). Do not draw a mark.
- **Photography:** placeholder images hot-linked from picsum.photos (ids 1015, 1016, 1018, 1036, 1039, 1043, 1044, 1050). Replace with real imagery; the duotone treatment will adapt anything.

## Index
- `styles.css` — entry point (imports only). Link this one file.
- `tokens/` — `fonts.css` (Google Fonts + Lucide font), `colors.css` (palette + semantic aliases), `chords.css` (7 theme scopes), `typography.css`, `spacing.css` (space, radii, controls), `effects.css` (shadows, motion, grain), `base.css` (resets, `.t-*` type classes), `components.css` (`sl-*` component classes).
- `guidelines/` — foundation specimen cards (Colors, Type, Spacing, Brand).
- `components/` — React primitives (below), each with `.jsx`, `.d.ts`, `.prompt.md`, one card per folder.
- `ui_kits/journal/` — Solstice Journal, an editorial reference site (home, article, subscribe dialog, toast).
- `thumbnail.html`, `SKILL.md`.

## Components
- **actions/** — Button, IconButton
- **forms/** — Input, Select, Checkbox, Radio, Switch
- **display/** — Card, Badge, Tag, ImageFrame, Icon
- **navigation/** — Tabs
- **feedback/** — Dialog, Toast, Tooltip

**Intentional additions** (beyond the standard set): **ImageFrame** — the duotone/grain engine that binds imagery to the chord; **Icon** — thin wrapper over the Lucide icon font.

---

## CONTENT FUNDAMENTALS
- **Voice:** a well-travelled friend writing a letter — observant, sensory, unhurried. Specific over grand ("the colour of weak tea", not "stunning vistas").
- **Person:** "you" to the reader; "we" sparingly for the publication; first-person "I" only inside bylined essays.
- **Casing:** Sentence case everywhere — headlines, buttons, nav ("Read the story", "Keep reading"). UPPERCASE only in mono eyebrows/meta ("FIELD NOTES · NO. 14").
- **Headlines:** short, concrete, often with one *italicised* word that carries the feeling — "Recent *light*", "What the tide *leaves* behind". One italic per headline, max.
- **Buttons:** verb-first, 1–3 words: Subscribe, Read the story, Save for later. No "Click here", no exclamation marks.
- **Metadata:** mono, middot-separated: `By M. Ortega · 8 min read`, `Fig. 2 — Channel at low water`. Figures are numbered.
- **Microcopy:** calm and human — "You're on the list", "The next letter lands on the solstice." Errors say what to do: "Use at least 2000px on the long edge."
- **Emoji:** never. Unicode used only for typographic punctuation (— · “ ” ×).
- **Numbers:** "No. 14", "8 min", numerals not words for data.

## VISUAL FOUNDATIONS
- **Colour:** warm neutrals (never #FFF / #000 — paper is `#F3EDE3`, ink `#1B1A17`). Ember `#B04428` is the one accent per view. Supporting hues (ochre, sage, tide, plum) share one saturation band so any two sit together. Status colours are borrowed from the palette (sage = success, ochre = warning, tide = info) plus a single crimson for danger.
- **Chords:** paper · dusk · ember · grove · ochre · plum · night. Each defines surface, text (primary/secondary/tertiary), accent + accent-fg, borders (as fg at 12/24% alpha), and `--duo-shadow/--duo-light`. All text pairings pass 4.5:1. Rhythm rule: on a page, alternate paper with at most one coloured chord per viewport; in grids, chord ≤ 1 in 3 cards.
- **Type:** Instrument Serif (display, 400, roman + italic, −0.02em, leading 0.92–1.05) for all headlines and pull quotes; Hanken Grotesk for UI and body (16px/1.65, 64ch measure, Light 300 for ledes); IBM Plex Mono for eyebrows, labels, captions (11–12px, uppercase, 0.14em). Scale ×1.333 from 16 → 118.
- **Imagery:** always through `ImageFrame`. Default *duotone* (grayscale → multiply over chord light, lighten with chord shadow) + film grain overlay (45%). *Tint* keeps natural colour washed in chord light; *natural* only for product shots. Vibe: warm, low-sun, grainy, landscape/still-life; no stock-office people. Missing images render a chord gradient field — never a grey box.
- **Backgrounds:** flat chord fields, full-bleed. No gradients as decoration (only the image-placeholder field). Texture = grain, applied to images only.
- **Layout:** 1240px container, 24px gutter, 12-col feel via asymmetric splits (5/7). Generous vertical rhythm (56–96px section padding). Sticky header is the only fixed element.
- **Corners:** near-square — 2px images/badges, 4px cards/inputs, 8px dialogs/toasts; pills for buttons, tags, pill-tabs only.
- **Cards:** three kinds — *flat* (no surface, image + text flush-left; default in grids), *outlined* (1px 10% ink hairline), *raised* (shadow-md, used with a chord). Never left-accent-border cards.
- **Borders:** hairlines at 10% (subtle) / 20% (default) of the chord's text colour; 1px ink for secondary buttons.
- **Shadows:** warm (43,39,35) low and soft: sm, md, lg, inset. Used only for raised cards, dialogs, toasts, switch thumb.
- **Transparency & blur:** header = page colour at 86% + 14px blur; dialog scrim = ink 48% + 6px blur. Nowhere else.
- **Motion:** ease-out `cubic-bezier(.2,.7,.2,1)`, 120/200/360/640ms. Fades and 10px rises; no bounce, no spring. Image zoom 4% over 640ms on card hover. Honour reduced-motion.
- **Hover:** primary → one step darker accent; secondary → inverts to ink fill; ghost → 10% ink wash; cards lift 3px; links shift to ink.
- **Press:** scale(.97) buttons, (.94) icon buttons; accent one more step darker.
- **Focus:** 2px tide-500 outline, 2px offset; inputs get ink border + 25% tide ring.

## ICONOGRAPHY
- **System:** [Lucide](https://lucide.dev) via the `lucide-static@0.460.0` icon font (CDN, imported in `tokens/fonts.css`). Use `<Icon name="sun" />` or `<i class="icon-sun"></i>`.
- **Style:** outline only, ~2px stroke at 24px, round caps — matches Hanken's stroke weight. Sizes 16 (dense), 18 (default), 22 (large); `currentColor`.
- **Usage:** functional only (search, save, share, close, arrows, chevrons). No decorative icon grids, no icons in headlines, no filled icons.
- **Emoji / unicode:** no emoji. Unicode only as punctuation.
- **Substitution flag:** Lucide was chosen (no brand icon set existed). No SVG/PNG icon assets are stored locally.

## Fonts (substitution flag)
All three families load from Google Fonts — no local font files were provided, so no `@font-face` binaries ship in this project. Supply licensed files to self-host.
