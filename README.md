# VentCourse

Paediatric mechanical-ventilation course app for PICU trainees (KIMS / Cuddles, Bengaluru): Learn modules (7), ventilator simulator, cases, admin, plus three teaching decks.

This folder **is the live app**. There's no build step: what's here is what Railway serves.

## Run locally
```
npm start          # http://localhost:3000
```
- App → `/`
- Talks → `/talks/graphics.html`, `/talks/know-your-machine.html`, `/talks/complete.html`, `/talks/basics.html` (30-min basics), `/talks/disease-specific.html`, `/talks/difficult-scenarios.html` (the two Cases scenarios as a 75-slide case discussion), `/talks/cp-interactions.html` (Module 08, 131 slides, native SVG diagrams; case X-ray and echo in `assets/cp/`) (← → to move, F for full screen, N for notes, P for presenter window)
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
