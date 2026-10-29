// The scenarios on the faculty scoring sheet: each one is a single change from a scripted stage, run through the same code the phones use.
// Run: node tools/physio_review.js   (prints the table and writes tools/physio_review.json)
const fs = require('fs'), path = require('path');
const APP = path.join(__dirname, '..');
global.window = global; global.HTMLElement = class {}; global.customElements = { get: () => 1, define() {} };
eval(fs.readFileSync(path.join(APP, 'vent-graphics.js'), 'utf8'));
require(path.join(APP, 'physio.js'));
const html = fs.readFileSync(path.join(APP, 'index.html'), 'utf8');
const LIVE = JSON.parse(html.slice(html.indexOf('const LIVE = ') + 13, html.indexOf(';\n', html.indexOf('const LIVE = '))));
const LVK = html.slice(html.indexOf('const LV_IF = '), html.indexOf('// Branching live cases: grade'));
const PHY = html.slice(html.indexOf("// Each phone's own patient (branching"), html.indexOf('// Module 09 carries high-flow'));
eval((LVK + PHY).replace(/^const /gm, 'var ').replace(/^function (\w+)/gm, 'global.$1 = function $1'));

const V = (mode, v) => ({ iface: 'VENT', mode, v: { o: 100, ti: 0.7, ...v } });
const SC = [
  // [case, stage, what the candidate changes, settings]
  ['1 · ARDS, 2 y, 10 kg', 'ar0', 'ER on a non-rebreather 15 L/min → NIV 16/6, FiO₂ 0.85', { iface: 'NIV', mode: 'ST', v: { ip: 16, ep: 6, br: 20, ti: 0.7, o: 85 } }],
  ['1 · ARDS, 2 y, 10 kg', 'ar0', 'ER on a non-rebreather → high-flow 2 L/kg, FiO₂ 0.6', { iface: 'HFNC', mode: 'HFNC', v: { f: 20, o: 60 } }],
  ['1 · ARDS, 2 y, 10 kg', 'ar0', 'ER on a non-rebreather → simple mask 6 L/min', { iface: 'MASK', mode: 'Mask', v: { l: 6 } }],
  ['1 · ARDS, 2 y, 10 kg', 'ar3', 'PRVC VT 75, PEEP 7 → PEEP 12', V('PRVC', { vt: 75, pe: 12, rr: 30, ti: 0.67 })],
  ['1 · ARDS, 2 y, 10 kg', 'ar3', 'PRVC VT 75, PEEP 7 → PEEP 18', V('PRVC', { vt: 75, pe: 18, rr: 30, ti: 0.67 })],
  ['1 · ARDS, 2 y, 10 kg', 'ar3', 'PRVC VT 75 → VT 100 (10 mL/kg)', V('PRVC', { vt: 100, pe: 7, rr: 30, ti: 0.67 })],
  ['1 · ARDS, 2 y, 10 kg', 'ar3', 'Rate 30 → 40', V('PRVC', { vt: 75, pe: 7, rr: 40, ti: 0.67 })],
  ['1 · ARDS, 2 y, 10 kg', 'ar3', 'FiO₂ 1.0 → 0.6', V('PRVC', { vt: 75, pe: 7, rr: 30, ti: 0.67, o: 60 })],
  ['1 · ARDS, 2 y, 10 kg', 'ar3', 'PRVC → PC 30 above PEEP 5, rate 40', V('PC', { pi: 30, pe: 5, rr: 40, ti: 0.6 })],
  ['1 · ARDS, 2 y, 10 kg', 'ar5', 'At PEEP 12: Ti 0.67 → 0.9 s (I:E about 1:1.2)', V('PRVC', { vt: 75, pe: 12, rr: 30, ti: 0.9 })],
  ['2 · asthma, 5 y, 20 kg', 'as2', 'VC VT 140, rate 14, PEEP 4 → VT 200, rate 25, PEEP 8', V('VC', { vt: 200, pe: 8, rr: 25, ti: 0.8, o: 80 })],
  ['2 · asthma, 5 y, 20 kg', 'as2', 'Rate 14 → 20', V('VC', { vt: 140, pe: 4, rr: 20, ti: 0.86, o: 80 })],
  ['2 · asthma, 5 y, 20 kg', 'as2', 'Rate 14 → 10 (longer expiration)', V('VC', { vt: 140, pe: 4, rr: 10, ti: 0.86, o: 80 })],
  ['2 · asthma, 5 y, 20 kg', 'as2', 'Ti 0.86 → 1.4 s (shorter expiration)', V('VC', { vt: 140, pe: 4, rr: 14, ti: 1.4, o: 80 })],
  ['2 · asthma, 5 y, 20 kg', 'as4', 'Triggering, auto-PEEP about 8: PEEP 0 → 6', V('VC', { vt: 140, pe: 6, rr: 12, ti: 1, o: 50 })],
  ['2 · asthma, 5 y, 20 kg', 'as4', 'Triggering: PEEP 0 → 12', V('VC', { vt: 140, pe: 12, rr: 12, ti: 1, o: 50 })]
];
const pick = (arr, k) => { const r = (arr || []).find(([x]) => x.replace(/₂/g, '2').startsWith(k)); return r ? r[1] : '–'; };
const out = SC.map(([cs, sid, what, set], i) => {
  const P = LIVE[sid].phys, a = lvPatient(P, P.anc.set, 0), b = lvPatient(P, set, 0);
  const row = x => ({ SpO2: pick(x.mon, 'SpO2'), HR: pick(x.mon, 'HR'), BP: pick(x.mon, 'BP') !== '–' ? pick(x.mon, 'BP') : pick(x.mon, 'ABP'),
    pH: pick(x.meas, 'pH'), PaCO2: pick(x.meas, 'PaCO2'), PaO2: pick(x.meas, 'PaO2'), Plat: pick(x.meas, 'Plateau'), dP: pick(x.meas, 'ΔP'), Crs: pick(x.meas, 'Crs'), TotPEEP: pick(x.meas, 'Total PEEP') });
  return { n: i + 1, case: cs, stage: LIVE[sid].t.split(' · ').slice(-1)[0], what, before: row(a), after: row(b), alarm: b.alarm };
});
for (const o of out) console.log(o.n, o.case, '|', o.stage, '|', o.what, '\n   before', JSON.stringify(o.before), '\n   after ', JSON.stringify(o.after), o.alarm ? '\n   alarm  ' + o.alarm : '');
fs.writeFileSync(path.join(APP, 'tools', 'physio_review.json'), JSON.stringify(out, null, 1));
