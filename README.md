# VentCourse

Paediatric mechanical-ventilation course app for PICU trainees (KIMS / Cuddles, Bengaluru): Learn modules (7), ventilator simulator, cases, admin, plus three teaching decks.

This folder **is the live app**. There's no build step: what's here is what Railway serves.

## Run locally
```
npm start          # http://localhost:3000
```
- App → `/`
- Talks → `/talks/graphics.html`, `/talks/know-your-machine.html`, `/talks/complete.html`, `/talks/basics.html` (30-min basics), `/talks/disease-specific.html`, `/talks/difficult-scenarios.html` (the two Cases scenarios as a 75-slide case discussion), `/talks/cp-interactions.html` (Module 08, 131 slides, native SVG diagrams; case X-ray and echo in `assets/cp/`), `/talks/long-term-ventilation.html` (Module 09, 62 slides, native SVG diagrams), `/talks/rapid-cases.html` (Module 09 rapid cases, 15 min: OSA, Duchenne, SMA, GBS, BPD), and the three case-first live decks: `/talks/cp-part1.html` (CP interactions part 1, 30 min: Maya, Leo, the congenital heart · room CP1), `/talks/cp-part2.html` (part 2, 30 min: the 4-year-old, Suresh · room CP2), `/talks/ltv-cases.html` (long-term ventilation, five cases, 15 min · room LTV) (← → to move, F for full screen, N for notes, P for presenter window)
- Admin → sign in as `admin`

## Deploy
Push to GitHub `main` → Railway redeploys automatically. Users are stored in `/data/users.json` (Railway volume).
Railway variable `ADMIN_PASSWORD` sets the admin password (default `VentAdmin@2026`).

## Files
| Path | What it is |
|---|---|
| `index.html` | The whole app: screens, lesson text, cases, practice guide, simulator |
| `vent-graphics.js` | Waveform drawing (used by app and talks) |
| `talks/*.html` | Slide decks (1920×1080) |
| `server.js` | Static server + accounts API |
| `support.js` | Page runtime. **Don't edit** |
| `deck-stage.js` | Slide-deck shell |
| `image-slot.js` | Image placeholder helper used by the talks |
| `_ds/` | Solstice design system (colours, fonts, components) |
| `assets/` | Logos, X-rays, sounds, videos, textbook figures |
| `email/` | EmailJS template + setup notes |

## Case decks and the live session
The three case-first decks are built from the app, so the phone and the screen always match:
```
pip install segno                      # once, for the QR code on the Join slide
python3 tools/build_decks.py           # writes talks/cp-part1.html, cp-part2.html, ltv-cases.html and the LIVE block in index.html
python3 tools/bundle.py BASE.html talks/cp-part1.html "OUT.html"   # self-contained Present copy (BASE = any existing Present bundle)
```
Screen data for each stage (ventilator, monitor, short slide wording) is in `tools/deckdata.py`; the orders and the patient's
responses are each stage's `live` field in `index.html`. Candidates join by QR (`/#live-CP1`, `/#live-CP2`, `/#live-LTV`) without an account.

