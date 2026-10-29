// Checks the live-case physiology (physio.js) against textbook behaviour and against the case scripts.
// Run: node tools/physio_test.js   (prints a table; exit code 1 if any check fails)
const fs = require('fs'), path = require('path');
const APP = path.join(__dirname, '..');
require(path.join(APP, 'physio.js'));
const V = globalThis.VCPhysio;
const html = fs.readFileSync(path.join(APP, 'index.html'), 'utf8');
const LIVE = JSON.parse(html.slice(html.indexOf('const LIVE = ') + 13, html.indexOf(';\n', html.indexOf('const LIVE = '))));

const anc = P => { const m = P.anc.mon || [], f = k => (m.find(([x]) => x.replace(/₂/g, '2').startsWith(k)) || [])[1];
  return { set: P.anc.set, gas: P.anc.gas, bp: f('BP') || f('ABP') || '', spo2: parseFloat(f('SpO2')) || null }; };
const vent = (mode, v) => ({ iface: 'VENT', mode, v: { o: 100, ti: 0.7, ...v } });
const cal = P => V.calibrate(P, anc(P));
const rows = []; let fails = 0;
const check = (group, what, ok, detail) => { rows.push([ok ? 'PASS' : 'FAIL', group, what, detail]); if (!ok) fails++; };
const r1 = x => Math.round(x * 10) / 10;

// 1 · oxygen dissociation curve (Severinghaus): P50 about 27, 90% near 60, 97–98% near 100
check('O2 curve', 'P50 ≈ 27 mmHg', Math.abs(V.so2(26.8) - 50) < 2, 'SaO2 at 26.8 = ' + r1(V.so2(26.8)) + '%');
check('O2 curve', 'PaO2 60 → SaO2 ≈ 90%', Math.abs(V.so2(60) - 90.5) < 1.5, r1(V.so2(60)) + '%');
check('O2 curve', 'PaO2 100 → SaO2 ≈ 97–98%', V.so2(100) > 97 && V.so2(100) < 98.5, r1(V.so2(100)) + '%');

// a normal 10 kg child for the clean textbook relationships
const N = { kind: 'normal', kg: 10, C: 15, R: 20, own: 30, anc: { set: vent('VC', { vt: 70, pe: 5, rr: 25, o: 21 }), mon: [['HR', '120'], ['SpO₂', '98'], ['BP', '95/60']], gas: { pH: 7.4, 'PaCO₂': 40, 'PaO₂': 95 } } };
const cN = cal(N), base = V.run(N, cN, N.anc.set);
// 2 · CO2 is inversely proportional to alveolar ventilation
const half = V.run(N, cN, vent('VC', { vt: 70, pe: 5, rr: 12.5, o: 21 }));
check('CO2', 'Halving the rate roughly doubles PaCO2', half.paco2 / base.paco2 > 1.8 && half.paco2 / base.paco2 < 2.3, 'PaCO2 ' + r1(base.paco2) + ' → ' + r1(half.paco2));
const bigVT = V.run(N, cN, vent('VC', { vt: 90, pe: 5, rr: 25, o: 21 }));
check('CO2', 'A bigger VT lowers PaCO2 more than in proportion (dead space is fixed)', base.paco2 / bigVT.paco2 > 90 / 70, 'PaCO2 ' + r1(base.paco2) + ' → ' + r1(bigVT.paco2) + ' (VT ×' + r1(90 / 70) + ')');
// 3 · hypoventilation on air lowers PaO2 (alveolar gas equation)
check('O2', 'Hypoventilating on room air lowers PaO2', half.pa < base.pa - 15, 'PaO2 ' + r1(base.pa) + ' → ' + r1(half.pa));
// 4 · the normal lung answers FiO2; a shunted lung barely does
const nO2 = V.run(N, cN, vent('VC', { vt: 70, pe: 5, rr: 25, o: 60 }));
check('O2', 'Normal lung: FiO2 0.21 → 0.6 raises PaO2 several-fold', nO2.pa / base.pa > 2.5, 'PaO2 ' + r1(base.pa) + ' → ' + r1(nO2.pa));

const A3 = LIVE.ar3.phys, c3 = cal(A3), a3 = V.run(A3, c3, A3.anc.set);
const fi60 = V.run(A3, c3, vent('PRVC', { vt: 75, pe: 7, rr: 30, ti: 0.67, o: 60 }));
check('Shunt', 'ARDS (large shunt): FiO2 0.6 → 1.0 raises PaO2 only modestly', a3.pa / fi60.pa < 2, 'PaO2 ' + r1(fi60.pa) + ' → ' + r1(a3.pa) + ' · shunt ' + Math.round(a3.qs * 100) + '%');
check('Shunt', 'ARDS shunt fraction in the severe range (> 25%)', a3.qs > 0.25, Math.round(a3.qs * 100) + '%');

// 5 · PEEP in ARDS: recruitment, best compliance, then overdistension and a falling cardiac output
const peeps = [5, 7, 8, 10, 12, 14, 16, 18, 20].map(pe => ({ pe, r: V.run(A3, c3, vent('PRVC', { vt: 60, pe, rr: 30, ti: 0.67, o: 100 })) }));
const best = peeps.reduce((a, b) => (b.r.C > a.r.C ? b : a));
check('PEEP · ARDS', 'Compliance is best at a middle PEEP (10–14)', best.pe >= 10 && best.pe <= 14, 'best compliance at PEEP ' + best.pe + ' (' + peeps.map(x => x.pe + ':' + r1(x.r.C)).join(' ') + ')');
const dP = peeps.map(x => x.r.sup.pEnd - x.r.sup.peep - x.r.sup.auto), low = peeps[dP.indexOf(Math.min(...dP))];
check('PEEP · ARDS', 'Driving pressure is lowest at the best-compliance PEEP', Math.abs(low.pe - best.pe) <= 2, 'lowest ΔP at PEEP ' + low.pe + ' (' + peeps.map((x, i) => x.pe + ':' + r1(dP[i])).join(' ') + ')');
const pa = peeps.map(x => x.r.pa);
check('PEEP · ARDS', 'PaO2 rises with PEEP from 5 to 12', pa[4] > pa[0] * 1.3, 'PaO2 ' + peeps.map(x => x.pe + ':' + Math.round(x.r.pa)).join(' '));
check('PEEP · ARDS', 'PaO2 stops improving beyond best PEEP (overdistension)', pa[8] <= Math.max(...pa) * 1.02 && pa[8] < pa[6] * 1.1, 'PEEP 16: ' + Math.round(pa[6]) + ' · PEEP 20: ' + Math.round(pa[8]));
check('PEEP · ARDS', 'Cardiac output falls at high PEEP', peeps[8].r.coRel < 0.85 && peeps[4].r.coRel > peeps[8].r.coRel, 'CO PEEP 12: ' + Math.round(peeps[4].r.coRel * 100) + '% · PEEP 20: ' + Math.round(peeps[8].r.coRel * 100) + '% of baseline');
check('PEEP · ARDS', 'Blood pressure falls at high PEEP', peeps[8].r.sys < peeps[4].r.sys - 5, 'systolic PEEP 12: ' + peeps[4].r.sys + ' · PEEP 20: ' + peeps[8].r.sys);

// 6 · big breaths in ARDS
const vt10 = V.run(A3, c3, vent('PRVC', { vt: 100, pe: 7, rr: 30, ti: 0.67, o: 100 }));
check('VT · ARDS', '10 mL/kg: plateau above 30', vt10.sup.pEnd > 30, 'plateau ' + r1(vt10.sup.pEnd) + ' (VT 75: ' + r1(a3.sup.pEnd) + ')');
check('VT · ARDS', '10 mL/kg: compliance falls (overstretch)', vt10.C < a3.C, 'C ' + r1(a3.C) + ' → ' + r1(vt10.C) + ' mL/cmH2O');
check('VT · ARDS', '10 mL/kg: alveolar dead space rises', vt10.vdAlv / vt10.sup.vt > a3.vdAlv / a3.sup.vt, 'VDalv/VT ' + r1(a3.vdAlv / a3.sup.vt * 100) + '% → ' + r1(vt10.vdAlv / vt10.sup.vt * 100) + '%');

// 7 · asthma: trapping depends on expiratory time
const S2 = LIVE.as2.phys, c2 = cal(S2);
const as = rr => V.run(S2, c2, vent('VC', { vt: 140, pe: 0, rr, ti: 0.86, o: 80 }));
const s12 = as(12), s20 = as(20), s28 = as(28);
check('Asthma', 'Auto-PEEP rises as the rate rises (shorter expiration)', s12.sup.auto < s20.sup.auto && s20.sup.auto < s28.sup.auto, 'auto-PEEP RR 12: ' + r1(s12.sup.auto) + ' · 20: ' + r1(s20.sup.auto) + ' · 28: ' + r1(s28.sup.auto));
const vtBig = V.run(S2, c2, vent('VC', { vt: 200, pe: 0, rr: 20, ti: 0.86, o: 80 }));
check('Asthma', 'Auto-PEEP rises with a bigger VT', vtBig.sup.auto > s20.sup.auto, 'VT 140: ' + r1(s20.sup.auto) + ' · VT 200: ' + r1(vtBig.sup.auto));
check('Asthma', 'Blood pressure falls with auto-PEEP', s28.sys < s12.sys - 10, 'systolic RR 12: ' + s12.sys + ' · RR 28: ' + s28.sys);
check('Asthma', 'A faster rate does not clear CO2 once gas traps', s28.paco2 > s20.paco2 * 0.9, 'PaCO2 RR 20: ' + r1(s20.paco2) + ' · RR 28: ' + r1(s28.paco2));

// 8 · heart–lung: PEEP costs more cardiac output in the dry child
const dry = { ...A3, k: { pms: 9 } }, wet = { ...A3, k: { pms: 15 } };
const coAt = (P, pe) => { const c = cal(P); return V.run(P, c, vent('PRVC', { vt: 60, pe, rr: 30, ti: 0.67, o: 100 })).coRel; };
check('Heart–lung', 'PEEP 18 lowers cardiac output more when the child is dry', coAt(dry, 18) < coAt(wet, 18), 'CO at PEEP 18: dry ' + Math.round(coAt(dry, 18) * 100) + '% · filled ' + Math.round(coAt(wet, 18) * 100) + '%');

// 9 · the case's own PEEP titration sheet (nurse's record, case 1): SpO2 within 2 and systolic within 8 at each step
{ const sheet = [[6, 75, 90, 110], [8, 60, 92, 110], [10, 60, 94, 110], [12, 60, 96, 110], [14, 60, 96, 100]];
  const P = { ...A3, anc: { ...A3.anc, set: vent('PRVC', { vt: 75, pe: 6, rr: 30, ti: 0.67 }), gas: { pH: 7.30, 'PaCO₂': 50 }, mon: [['SpO₂', '90'], ['BP', '110/70']] } };
  const c = cal(P);
  for (const [pe, vt, sp, sys] of sheet) { const r = V.run(P, c, vent('PRVC', { vt, pe, rr: 30, ti: 0.67 }));
    const m = Math.round(90 + r.dSat); check('Sheet · ARDS', 'PEEP ' + pe + ': SpO2 ' + sp + ', systolic ' + sys + ' on the sheet', Math.abs(m - sp) <= 2 && Math.abs(r.sys - sys) <= 8, 'model SpO2 ' + m + ', systolic ' + r.sys); } }

// 9 · every scripted stage: its own settings give its own numbers back
for (const [k, E] of Object.entries(LIVE)) { if (!/^(ar|as)\d+$/.test(k) || !E.phys) continue;
  const P = E.phys, c = cal(P), r = V.run(P, c, P.anc.set), g = P.anc.gas || {};
  const okC = !g['PaCO₂'] || Math.abs(r.paco2 - g['PaCO₂']) < 1, okO = !g['PaO₂'] || Math.abs(r.pa - g['PaO₂']) < 1.5;
  check('Script', k + ': anchor settings reproduce the scripted gas', okC && okO, 'PaCO2 ' + r1(r.paco2) + (g['PaCO₂'] ? ' (script ' + g['PaCO₂'] + ')' : '') + ' · PaO2 ' + r1(r.pa) + (g['PaO₂'] ? ' (script ' + g['PaO₂'] + ')' : '')); }

const w = [5, 13, 62];
console.log(rows.map(r => r[0].padEnd(w[0]) + r[1].padEnd(w[1]) + r[2].padEnd(w[2]) + r[3]).join('\n'));
console.log(`\n${rows.length - fails} of ${rows.length} checks pass`);
fs.writeFileSync(path.join(APP, 'tools', 'physio_test.json'), JSON.stringify(rows, null, 1));
process.exit(fails ? 1 : 0);
