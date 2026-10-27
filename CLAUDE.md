# CLAUDE.md: VentCourse

This is a **live, working app**. Continue it; don't rebuild or migrate it.

## How the files work
- `index.html` holds the whole app. The top part is the template (HTML with `{{ name }}` holes, `<sc-if>`, `<sc-for>`, `<x-import>`). The bottom `<script type="text/x-dc">` is the logic: `class Component extends DCLogic { renderVals() {…} }`.
- Holes are plain names only. Compute values in `renderVals()` and expose them by name. No `{{ a + b }}`.
- Styling is **inline `style="…"` only**. No new CSS classes or stylesheets.
- Lesson, case and practice data are JS constants in the logic (`MODULES`, `LESSON_SETS`, `PRACTICE`, cases). Edit the text there.
- `SIM_SCEN` + `SIM_STAGES` are the simulator scenarios (Cases screen → "Take the ventilator"). Each stage is a `CASES` entry with `scen`/`stage`/`keep` (keep = carry the learner's settings over), its own `PATIENTS` physiology (`Cfn` = PEEP-dependent compliance, `autoBase` = baseline auto-PEEP, `fight` = asynchrony dips, `defs` = knob ranges), an `event` paragraph, a `brief`, bedside `actions` ([id, label, fb, optional `patient` switch, `needs` prerequisite, `bad`]), a `gas(m, acts, s, m0, c)` hook returning `{o2, co2}` multipliers, optional `vitals()`, and `goals(m, acts, s)`; the last stage carries a `debrief`. Action state lives in `state.acts[caseId]`.
- `SCENARIOS` holds the same two cases as question-and-answer walkthroughs ("Discuss the decisions", screen `scen`); `talks/difficult-scenarios.html` is generated from them. One patient, several stages; each stage has the bedside picture (`vit`, `exam`, `vent`, `abg`, optional `img`, `table`, `trace`), one question (`q`, `opts` = [label, 1 if right, feedback]), a `teach` take-away and a `lesson` link [module, index]. The last stage is a `debrief` list. Answers are saved with lesson progress (`sc`).
- **Simulation format (OPENPediatrics style).** Every case opens with only the case story and a drawing of the patient (`patient-figure.js`, `<patient-figure age="infant|toddler|child|teen" support="ett|bag|mask|niv|nc|trach|prone">`; age comes from the title via `AGE_BAND`, airway per stage: sim stages from `fig`/ventOn/prone, discussions from `SC_FIG`). Everything else (exam, X-ray, gas, handover, ventilator, monitor, chart) is asked for with chips. In sim stages the stage `story` is the cue; every stage `event` is held back until the last stage is solved, then shown together as "What was going on · stage by stage"; `brief` sits behind "Call a senior".
- **Free flow, no question-and-answer.** Case discussions (`SCENARIOS`) and wave cases (`WAVES`) show the `opts`/`fixes` as orders, shuffled per stage, given in any order; each order's feedback text is the patient's response, logged in the case log (`state.scLog[scenarioId]`, `state.wLog[i]`). The right order moves the case to the next stage in one continuous page (earlier stages stay above as "case so far"). `q` is no longer shown; `teach`/`teachList`/`lesson` appear only at the debrief, stage by stage. Wave cases reveal the right `names` entry as "What was going on" once fixed.
- **Vitals** render as a bedside monitor (`bedside-monitor.js`, `<bedside-monitor vitals='[["HR","145"],...]'>`): HR/SpO₂/RR as moving traces with big numbers, everything else as coloured tiles.
- **Performance.** `state.perf[key]` (key = case id, `w<i>` for wave cases, `<scenario>:<stage>` for discussions) logs open time, what was asked for and when (`req`), first action (`act`), senior call (`hint`), harmful orders (`bad`), checks and finish time. `perfReport()` turns it into the scored card (time, assessed before acting, information gathered, targets/decisions, senior, harmful orders).
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
Nine modules, 65 lessons; Module 07 (Disease-specific ventilation) lives in `LESSON_SETS['07']`, Module 08 (Cardiopulmonary interactions) in `LESSON_SETS['08']`, Module 09 (Long-term ventilation) in `LESSON_SETS['09']`. The lesson count also appears as text in `index.html` (home card, Learn header, admin list): update all three when adding lessons. A lesson may carry `vidCap` + `vidNote` (renders a video slot) and `vid` (path to an mp4 under `assets/`; until it is set the slot shows a placeholder).
Username 2–40 chars (trimmed, lower-cased), password ≥ 6. Admin re-seeded from `ADMIN_PASSWORD` on boot.
EmailJS sends the sign-up code (service `service_po89bsd`, template `template_ndn664u`).

## Author
Paediatric intensivist, not a developer. Explain plainly, keep answers short.
