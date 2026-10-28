// Builds the scenario book HTML from scen.json; images are pre-shrunk into ./img.
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const REPO = process.argv[2], DIR = __dirname;
const D = JSON.parse(fs.readFileSync(DIR + '/scen.json', 'utf8'));
fs.mkdirSync(DIR + '/img', { recursive: true });
const thumb = p => { if (!p) return ''; const out = DIR + '/img/' + p.replace(/[\/]/g, '_').replace(/\.(png|jpe?g)$/i, '.jpg');
  if (!fs.existsSync(out)) execFileSync('python3', ['-I', '-c', 'import sys\nfrom PIL import Image\nim=Image.open(sys.argv[1]).convert("RGB"); im.thumbnail((700,700)); im.save(sys.argv[2], quality=78)', REPO + '/' + p, out]);
  return 'img/' + path.basename(out); };
const E = s => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const em = t => { const w = E(t).split(' '); if (w.length < 2) return E(t); const i = w.length - 1; w[i] = '<em>' + w[i] + '</em>'; return w.join(' '); };
const kv = rows => '<table class="kv">' + rows.map(([l, v]) => `<tr><th>${E(l)}</th><td>${E(v === 'live' ? 'live, from the simulator' : v)}</td></tr>`).join('') + '</table>';
const nStages = D.reduce((n, z) => n + z.stages.length, 0);
let body = '';
// ---------- cover ----------
body += `<section class="cover">
  <div class="mono dim">VentCourse · Paediatric ventilation · Simulator scenario book</div>
  <div class="cover-mid"><h1>Twenty children on the <em>ventilator</em></h1>
  <p class="lede">Every simulator scenario in the app, stage by stage: what the candidate sees, what they can ask for and do, what the patient does in response, the targets that close each stage, and what was going on.</p></div>
  <div class="mono">Dr Manju Kedarnath<br><span class="dim">Pediatrics, Peds ER and PICU · KIMS Hospitals, Electronic City, Bangalore</span><br><span class="dim">${D.length} scenarios · ${nStages} stages · October 2026</span></div>
</section>`;
// ---------- how they run ----------
body += `<section class="intro"><h2>How a scenario <em>runs</em></h2>
<ol class="steps">
<li><b>The cue.</b> The case opens with the story and a drawing of the patient only. Examination, chest X-ray, blood gas, handover, ventilator and chart are asked for, one by one, and the app records what was asked for and when.</li>
<li><b>Set up the ventilator.</b> Choose invasive or non-invasive, the mode, the patient type and the weight from the chart, run the self test, then Save &amp; close. The ventilator then waits on standby: the knobs are live, the screen is blank, and nothing runs until the candidate presses Start ventilation.</li>
<li><b>Ventilate.</b> Waveforms, readouts, SpO₂, EtCO₂ and every blood gas are calculated from the candidate’s settings and the patient’s physiology for that stage. In pressure modes the monitor shows no plateau or driving pressure.</li>
<li><b>Bedside actions.</b> Orders such as sedation, suction, ultrasound, a bolus, proning or a chest drain change the patient. Some must follow another (suction after disconnecting, a needle after the ultrasound); harmful orders are explained and logged.</li>
<li><b>Check targets.</b> Each stage closes when its targets are met. The settings carry into the next stage, where the patient has moved on. “Call a senior” shows the senior’s advice and counts towards the performance card.</li>
<li><b>Debrief.</b> After the last stage the app shows what was going on at every stage, the take-home points and a scored performance card: time, assessed before acting, information gathered, targets, senior called, harmful orders.</li>
</ol>
<p class="note">In this book, “live” vitals are calculated by the simulator. The gas reference settings are the settings at which the printed blood gas was drawn; the simulator recalculates the gas from whatever the candidate sets.</p>
<h2 class="toc-h">The <em>scenarios</em></h2>
<table class="toc">${D.map(z => `<tr><td class="mono">${E(z.eyebrow.replace('Sim scenario ', ''))}</td><td><b>${E(z.title)}</b><br><span class="dim">${E(z.setting)}</span></td><td class="mono r">${z.stages.length} stage${z.stages.length > 1 ? 's' : ''}</td></tr>`).join('')}</table>
</section>`;
// ---------- scenarios ----------
for (const z of D) {
  body += `<section class="scen"><div class="scen-head"><div class="mono dim">${E(z.eyebrow)} · ${z.stages.length} stage${z.stages.length > 1 ? 's' : ''}</div><h2>${em(z.title)}</h2><div class="mono acc">${E(z.setting)}</div><p class="lede">${E(z.blurb)}</p>
    <ol class="stagelist">${z.stages.map(s => `<li>${E(s.t)}</li>`).join('')}</ol></div>`;
  z.stages.forEach((s, i) => {
    const pics = [s.illus && `<figure><img src="${thumb(s.illus)}"><figcaption>Scene</figcaption></figure>`, s.cxrImg && `<figure class="xr"><img src="${thumb(s.cxrImg)}"><figcaption>Chest X-ray</figcaption></figure>`].filter(Boolean).join('');
    body += `<div class="stage">
      <div class="head-cue"><div class="stage-h"><span class="mono acc">Stage ${i + 1} of ${z.stages.length}${s.keep ? ' · settings carry over' : ' · fresh setup'}${s.niv ? ' · non-invasive' : ''}</span><h3>${E(s.t)}</h3><span class="mono dim">${E(s.setting)}</span></div>
      <div class="cue"><span class="lab">Cue</span><p>${E(s.story)}</p></div></div>
      <div class="grid ${pics ? '' : 'nopic'}"><div>
        ${s.vit.length ? `<span class="lab">Vitals</span>${kv(s.vit)}` : ''}
        ${s.exam.length ? `<span class="lab">Examination</span><ul class="ex">${s.exam.map(x => `<li>${E(x)}</li>`).join('')}</ul>` : ''}
        ${s.cxr ? `<span class="lab">Chest X-ray</span><p class="sm">${E(s.cxr)}</p>` : ''}
        ${s.abg.length ? `<span class="lab">Blood gas</span><p class="gas">${s.abg.map(([l, v]) => `${E(l)} <b>${E(v)}</b>`).join(' &nbsp; ')}</p>` : ''}
        ${s.vent ? `<span class="lab">Handover · ventilator</span><p class="sm mono2">${E(s.vent)}</p>` : ''}
      </div>${pics ? `<div class="pics">${pics}</div>` : ''}</div>
      ${s.task1 ? `<div class="blk"><span class="lab">Setup</span><p class="sm">${E(s.task1)}</p></div>` : ''}
      ${s.set.length ? `<div class="blk"><span class="lab">Changed by the team before the candidate arrives</span><p class="sm mono2">${E(s.setMode)} · ${s.set.map(([k, v]) => E(k) + ' ' + E(v)).join(' · ')}</p></div>` : ''}
      <div class="blk adv"><span class="lab">Senior’s advice · behind “Call a senior”</span><p>${E(s.brief)}</p></div>
      ${s.actions.length ? `<div class="blk"><span class="lab">Bedside actions and the patient’s response</span><table class="acts">${s.actions.map(x => `<tr class="${x.bad ? 'bad' : ''}"><th>${E(x.label)}${x.bad ? '<span class="tag">harmful</span>' : ''}${x.needs ? `<span class="tag soft">after: ${E(x.needs)}</span>` : ''}</th><td>${E(x.fb)}${x.needs && x.needsFb ? `<br><span class="dim">If ordered too early: ${E(x.needsFb)}</span>` : ''}${x.becomes ? `<br><span class="dim">Patient becomes: ${E(x.becomes)}</span>` : ''}</td></tr>`).join('')}</table></div>` : ''}
      <div class="blk"><span class="lab">Targets that close the stage</span><ul class="goals">${s.goals.map(g => `<li>${E(g)}</li>`).join('')}</ul></div>
      ${s.event ? `<div class="blk ev"><span class="lab">What was going on · shown at the debrief</span><p>${E(s.event)}</p></div>` : ''}
      <div class="blk two"><div><span class="lab">Diagnosis</span><p class="sm">${E(s.dx)}</p></div><div><span class="lab">Learn link</span><p class="sm">${E(s.lesson)}</p></div></div>
      <div class="blk fac"><span class="lab">For the facilitator · the simulator</span><p class="sm">Patient model: ${E(s.patient)} · ${E(s.physio)}</p>${s.start.length ? `<p class="sm">Gas reference settings: ${E(s.mode)} · ${s.start.map(([k, v]) => E(k) + ' ' + E(v)).join(' · ')}</p>` : ''}</div>
    </div>`;
  });
  const deb = (z.stages[z.stages.length - 1] || {}).debrief || [];
  if (deb.length) body += `<div class="deb"><span class="lab">Debrief · take-home points</span><ol>${deb.map(d => `<li>${E(d)}</li>`).join('')}</ol></div>`;
  body += `</section>`;
}
const css = `${fs.readFileSync(DIR + '/fonts-inline.css', 'utf8')}
@page { size: A4; margin: 14mm 15mm 16mm; }
:root { --ink:#1B1A17; --sec:#5E554B; --acc:#B04428; --rule:rgba(27,26,23,.14); --paper:#F3EDE3; --soft:#FAF6EF; }
* { box-sizing:border-box; } html { -webkit-print-color-adjust:exact; print-color-adjust:exact; }
body { margin:0; color:var(--ink); font:400 9.6pt/1.45 "Hanken Grotesk", Helvetica, sans-serif; }
h1,h2,h3 { font-family:"Instrument Serif", Georgia, serif; font-weight:400; margin:0; letter-spacing:-.01em; }
em { font-style:italic; } b { font-weight:600; }
.mono,.lab { font-family:"IBM Plex Mono", monospace; text-transform:uppercase; letter-spacing:.12em; font-size:7.2pt; }
.mono2 { font-family:"IBM Plex Mono", monospace; font-size:8.2pt; letter-spacing:0; }
.dim { color:var(--sec); } .acc { color:var(--acc); } .r { text-align:right; }
.lab { display:block; color:var(--acc); margin:7px 0 3px; }
p { margin:0 0 4px; } .sm { font-size:9pt; }
.cover { height:262mm; display:flex; flex-direction:column; justify-content:space-between; padding:18mm 14mm; background:var(--paper); border-radius:3px; break-after:page; }
.cover h1 { font-size:58pt; line-height:.95; margin-bottom:12px; } .cover .lede { font-size:13pt; font-weight:300; max-width:140mm; color:var(--sec); }
.cover .mono { line-height:1.9; }
.intro { break-after:page; } .intro h2 { font-size:26pt; margin:4px 0 10px; } .toc-h { margin-top:18px !important; }
.steps { padding-left:18px; margin:0 0 8px; } .steps li { margin:0 0 6px; }
.note { font-size:8.6pt; color:var(--sec); border-left:2px solid var(--acc); padding-left:8px; }
.toc { width:100%; border-collapse:collapse; } .toc td { border-top:1px solid var(--rule); padding:4px 6px 4px 0; vertical-align:top; font-size:9pt; }
.toc td:first-child { width:12mm; color:var(--acc); } .toc td:last-child { width:20mm; }
.scen { break-before:page; } .scen-head { background:var(--paper); padding:10px 12px 8px; border-radius:3px; margin-bottom:8px; break-inside:avoid; }
.scen-head h2 { font-size:28pt; line-height:1; margin:4px 0 4px; } .scen-head .lede { font-size:10pt; margin-top:6px; }
.stagelist { margin:4px 0 0; padding-left:18px; font-size:8.8pt; color:var(--sec); columns:2; column-gap:10mm; }
.stage { border-top:1.5px solid var(--ink); padding-top:6px; margin-top:12px; }
.head-cue { break-inside:avoid; } .stage-h { break-after:avoid; } .stage-h h3 { font-size:18pt; line-height:1.05; margin:2px 0 1px; }
.cue { background:var(--soft); border-left:3px solid var(--acc); padding:5px 9px; margin:6px 0; break-inside:avoid; } .cue .lab { margin-top:2px; } .cue p { font-size:10pt; }
.grid { display:grid; grid-template-columns:1fr 54mm; gap:9mm; break-inside:avoid; } .grid.nopic { grid-template-columns:1fr; }
.pics { display:flex; flex-direction:column; gap:6px; } figure { margin:0; } figure img { width:100%; border-radius:2px; display:block; } .xr img { background:#0E1012; }
figcaption { font:7pt "IBM Plex Mono", monospace; letter-spacing:.1em; text-transform:uppercase; color:var(--sec); margin-top:2px; }
.kv { border-collapse:collapse; width:100%; } .kv th,.kv td { text-align:left; font-size:8.8pt; padding:1.5px 8px 1.5px 0; border-bottom:1px solid var(--rule); vertical-align:top; }
.kv th { font:500 7.4pt "IBM Plex Mono", monospace; letter-spacing:.08em; color:var(--sec); width:28mm; }
.ex { margin:0; padding-left:14px; font-size:9pt; } .gas { font:8.8pt "IBM Plex Mono", monospace; }
.blk { break-inside:avoid; } .adv p { font-size:9.4pt; } .ev { background:var(--soft); padding:4px 9px 5px; margin-top:6px; border-radius:2px; }
.acts { border-collapse:collapse; width:100%; } .acts th,.acts td { text-align:left; vertical-align:top; padding:3px 8px 3px 0; border-bottom:1px solid var(--rule); font-size:8.8pt; }
.acts th { width:46mm; font-weight:600; } .acts tr { break-inside:avoid; } .acts tr.bad th { color:var(--acc); }
.tag { display:inline-block; margin:2px 4px 0 0; font:500 6.6pt "IBM Plex Mono", monospace; letter-spacing:.08em; text-transform:uppercase; padding:1px 4px; border-radius:2px; background:var(--acc); color:#FAF6EF; }
.tag.soft { background:transparent; color:var(--sec); border:1px solid var(--rule); }
.goals { margin:0; padding:0; list-style:none; columns:2; column-gap:8mm; } .goals li { font-size:8.8pt; padding-left:13px; position:relative; break-inside:avoid; margin-bottom:1px; }
.goals li:before { content:''; position:absolute; left:0; top:4px; width:7px; height:7px; border:1.3px solid var(--acc); border-radius:50%; }
.two { display:grid; grid-template-columns:1fr 1fr; gap:8mm; } .fac p { color:var(--sec); font-size:8.2pt; margin:0 0 2px; }
.deb { break-inside:avoid; margin-top:14px; background:var(--paper); padding:8px 12px; border-radius:3px; } .deb ol { margin:0; padding-left:18px; } .deb li { margin-bottom:3px; font-size:9.4pt; }
`;
fs.writeFileSync(DIR + '/book.html', `<!doctype html><html><head><meta charset="utf-8"><title>VentCourse · Simulator scenario book</title><style>${css}</style></head><body>${body}</body></html>`);
console.log('book.html', Math.round(fs.statSync(DIR + '/book.html').size / 1024), 'KB');
