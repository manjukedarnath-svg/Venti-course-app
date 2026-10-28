// Pulls every simulator scenario out of the live app's index.html into scen.json for the PDF.
const fs = require('fs');
const REPO = process.argv[2], OUT = process.argv[3];
const src = fs.readFileSync(REPO + '/index.html', 'utf8');
const a = src.indexOf('<script type="text/x-dc"'), j = src.indexOf('>', a) + 1, code = src.slice(j, src.indexOf('class Component', j));
const stub = 'const React={createElement:()=>null};const window={};const document={};const localStorage={getItem(){},setItem(){}};';
new Function(stub + code + ";globalThis.X={SIM_SCEN,CASES,PATIENTS,LESSON_SETS,MODULES,DEFS,STAGE_ILLUS,VMODES};")();
const { SIM_SCEN, CASES, PATIENTS, LESSON_SETS, MODULES, DEFS, STAGE_ILLUS, VMODES } = X;
const zero = new Proxy({}, { get: (t, k) => k === Symbol.toPrimitive ? () => 0 : 0 });
const goalLabels = c => { try { return c.goals(zero, {}, zero).map(g => g[0]); } catch (e) { return ['(targets could not be listed: ' + e.message + ')']; } };
const LAB = { vt: ['VT', 'mL'], rr: ['RR', '/min'], peep: ['PEEP', 'cmH₂O'], ti: ['Ti', 's'], fio2: ['FiO₂', '%'], pinsp: ['Pinsp', 'cmH₂O'], ps: ['PS', 'cmH₂O'], cpap: ['CPAP', 'cmH₂O'], ipap: ['IPAP', 'cmH₂O'], epap: ['EPAP', 'cmH₂O'], vtt: ['Target VT', 'mL'], ipmax: ['IPAP max', 'cmH₂O'], phigh: ['P high', 'cmH₂O'], plow: ['P low', 'cmH₂O'], thigh: ['T high', 's'], tlow: ['T low', 's'], nava: ['NAVA', 'cmH₂O/µV'] };
const MODE_NAME = Object.fromEntries((VMODES || []).map(v => [v[0], v[1]]));
const modeOf = st => { const v = st.vmode || ({ VC: 'AC-VC', PC: 'AC-PC', PS: 'PS', NAVA: 'NAVA' })[st.mode] || st.mode; return MODE_NAME[v] || v || ''; };
const usedKeys = st => { const v = st.vmode || ({ VC: 'AC-VC', PC: 'AC-PC', PS: 'PS' })[st.mode] || st.mode;
  const K = { 'AC-VC': ['vt', 'rr', 'peep', 'ti', 'fio2'], 'SIMV-VC': ['vt', 'rr', 'peep', 'ti', 'fio2'], 'AC-PC': ['pinsp', 'rr', 'peep', 'ti', 'fio2'], 'SIMV-PC': ['pinsp', 'rr', 'peep', 'ti', 'fio2'], 'AC-PRVC': ['vt', 'rr', 'peep', 'ti', 'fio2'], PS: ['ps', 'peep', 'fio2'], CPAP: ['peep', 'fio2'] };
  return K[v] || Object.keys(st).filter(k => LAB[k]); };
const settings = st => st ? usedKeys(st).filter(k => st[k] != null && LAB[k]).map(k => [LAB[k][0], (k === 'fio2' ? (st[k] / 100).toFixed(2) : String(st[k])) + (k === 'fio2' ? '' : ' ' + LAB[k][1])]) : [];
const physio = p => { if (!p) return ''; const parts = [];
  if (p.Cfn) parts.push('compliance depends on PEEP (' + [5, 8, 10, 12, 14, 16].map(x => 'PEEP ' + x + ': ' + p.Cfn(x).toFixed(1)).join(', ') + ' mL/cmH₂O)');
  else if (p.C != null) parts.push('compliance ' + p.C + ' mL/cmH₂O');
  if (p.Rfn) parts.push('upper-airway resistance falls with EPAP/CPAP'); else if (p.R != null) parts.push('resistance ' + p.R + ' cmH₂O/L/s');
  if (p.C != null && p.R != null && !p.Cfn) parts.push('time constant ' + (p.C * p.R / 1000).toFixed(2) + ' s');
  if (p.autoBase) parts.push('baseline auto-PEEP ' + p.autoBase + ' cmH₂O'); if (p.fight) parts.push('fighting the ventilator');
  if (p.eff != null) parts.push('own effort ' + p.eff + (p.rrOwn ? ', own rate ' + p.rrOwn : '')); if (p.trig === false) parts.push('cannot trigger'); if (p.leak) parts.push('leak ' + Math.round(p.leak * 100) + '% of VT');
  return parts.join(' · '); };
const lessonName = l => { if (!l) return ''; const mod = l[2] || '01', L = (LESSON_SETS[mod] || [])[l[0]]; const md = (MODULES || []).find(m => m.no === mod);
  return 'Module ' + mod + (md && md.title ? ' · ' + md.title : '') + ' · ' + (L ? L.h.join('').trim() : l[1]); };
const img = p => p && fs.existsSync(REPO + '/' + p) ? p : '';
const out = SIM_SCEN.map(z => ({ id: z.id, eyebrow: z.eyebrow, title: z.title, setting: z.setting, blurb: z.blurb,
  stages: z.stages.map(id => { const c = CASES.find(x => x.id === id); if (!c) return { id, missing: true }; const p = PATIENTS[c.patient] || {};
    return { id, n: c.stage, t: c.t || c.title, setting: c.setting, keep: !!c.keep, niv: !!c.niv, story: c.story, event: c.event || '', dx: c.dx || '', brief: c.brief || '', task1: c.task1 || '',
      lesson: lessonName(c.learn), vit: (c.assess || {}).vit || [], exam: (c.assess || {}).exam || [], cxr: (c.assess || {}).cxr || '', cxrImg: img((c.assess || {}).img), abg: (c.assess || {}).abg || [], vent: (c.assess || {}).vent || '',
      illus: img(c.illus ? 'assets/illus/' + c.illus + '.jpg' : STAGE_ILLUS[c.id] ? 'assets/illus/' + STAGE_ILLUS[c.id] + '.jpg' : ''),
      patient: p.label || c.patient, physio: physio(p), mode: modeOf(c.start || {}), start: settings(c.start), set: c.set ? settings(c.set) : [], setMode: c.set ? modeOf(c.set) : '',
      actions: (c.actions || []).map(x => ({ label: x.label, fb: x.fb, bad: !!x.bad, needs: x.needs ? ((c.actions.find(y => y.id === x.needs) || {}).label || x.needs) : '', needsFb: x.needsFb || '', becomes: x.patient ? ((PATIENTS[x.patient] || {}).label || x.patient) : '' })),
      goals: goalLabels(c), debrief: c.debrief || [] }; }) }));
fs.writeFileSync(OUT, JSON.stringify(out, null, 1));
console.log(out.length, 'scenarios,', out.reduce((n, z) => n + z.stages.length, 0), 'stages; missing:', out.flatMap(z => z.stages.filter(s => s.missing).map(s => s.id)).join(',') || 'none');
