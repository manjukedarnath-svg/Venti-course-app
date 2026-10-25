# CLAUDE.md: VentCourse

This is a **live, working app**. Continue it; don't rebuild or migrate it.

## How the files work
- `index.html` holds the whole app. The top part is the template (HTML with `{{ name }}` holes, `<sc-if>`, `<sc-for>`, `<x-import>`). The bottom `<script type="text/x-dc">` is the logic: `class Component extends DCLogic { renderVals() {…} }`.
- Holes are plain names only. Compute values in `renderVals()` and expose them by name. No `{{ a + b }}`.
- Styling is **inline `style="…"` only**. No new CSS classes or stylesheets.
- Lesson, case and practice data are JS constants in the logic (`MODULES`, `LESSON_SETS`, `PRACTICE`, cases). Edit the text there.
- `SCENARIOS` holds the evolving simulation scenarios (Cases screen → "Start scenario", screen `scen`). One patient, several stages; each stage has the bedside picture (`vit`, `exam`, `vent`, `abg`, optional `img`, `table`, `trace`), one question (`q`, `opts` = [label, 1 if right, feedback]), a `teach` take-away and a `lesson` link [module, index]. The last stage is a `debrief` list. Answers are saved with lesson progress (`sc`).
- `support.js` is the runtime. Never edit it.
- `vent-graphics.js` draws all waveforms (`<vent-trace scenario="…">`).
- Talks in `talks/` use the same format; each slide is a `<section data-label>`.

## Design rules (Solstice, `_ds/`)
- Paper `#F3EDE3`, ink `#1B1A17`, single accent ember `#B04428`. Use `var(--…)` tokens.
- Instrument Serif headlines (one italic word), Hanken Grotesk body, IBM Plex Mono uppercase labels.
- Sentence case. No emoji. Lucide icons only.
- Mobile-first at 390px; tap targets ≥ 44px.

## Rules
- Clinical text is final. Don't reword it unless asked.
- Small, targeted edits. Don't restyle things you weren't asked to touch.
- After a change, run `npm start` and check `http://localhost:3000` at phone width.
- Commit with a plain-English message and push to `main` (Railway auto-deploys).
- Never commit passwords or keys beyond what's already in the files.

## Accounts API (`server.js`)
POST JSON: `/api/exists`, `/api/register`, `/api/login`, `/api/touch`, `/api/admin/list`, `/api/admin/role`, `/api/admin/delete`.
`/api/progress` (POST `{u, ph, prog?}`) saves and returns the user's lesson progress; the app also keeps a copy in localStorage (`vc-progress-<user>`). A lesson counts as done when its quiz is answered; Module 02 is done when its quiz is answered.
Eight modules, 49 lessons; Module 07 (Disease-specific ventilation) lives in `LESSON_SETS['07']`, Module 08 (Cardiopulmonary interactions) in `LESSON_SETS['08']`. A lesson may carry `vidCap` + `vidNote` (renders a video slot) and `vid` (path to an mp4 under `assets/`; until it is set the slot shows a placeholder).
Username 2–40 chars (trimmed, lower-cased), password ≥ 6. Admin re-seeded from `ADMIN_PASSWORD` on boot.
EmailJS sends the sign-up code (service `service_po89bsd`, template `template_ndn664u`).

## Author
Paediatric intensivist, not a developer. Explain plainly, keep answers short.
