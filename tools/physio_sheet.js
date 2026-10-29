// Faculty scoring sheet for the live-case physiology (round 1 of a Delphi review).
// Run after tools/physio_review.js and tools/physio_test.js:  node tools/physio_sheet.js <out.docx>
const fs = require('fs'), path = require('path');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, AlignmentType,
  PageOrientation, HeadingLevel, LevelFormat, PageBreak, Footer, PageNumber, TableLayoutType } = require('docx');
const APP = path.join(__dirname, '..');
const SC = JSON.parse(fs.readFileSync(path.join(APP, 'tools', 'physio_review.json'), 'utf8'));
const TESTS = JSON.parse(fs.readFileSync(path.join(APP, 'tools', 'physio_test.json'), 'utf8'));
const OUT = process.argv[2] || path.join(APP, 'VentCourse physiology - faculty scoring sheet.docx');

const INK = '1B1A17', ACC = 'B04428', SUB = '6E6A63', LINE = 'D2C5B1', PAPER = 'F3EDE3', FONT = 'Arial';
const W = 16838 - 2 * 1000;   // A4 landscape width minus 1000-DXA margins: 14838
const t = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size || 20, bold: o.bold, italics: o.it, color: o.color || INK });
const p = (runs, o = {}) => new Paragraph({ children: Array.isArray(runs) ? runs : [t(runs, o)], spacing: { before: o.before ?? 60, after: o.after ?? 60 }, alignment: o.align, keepNext: o.keepNext, heading: o.heading });
const h1 = s => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: s, font: FONT, size: 32, bold: true, color: INK })], spacing: { before: 120, after: 120 } });
const h2 = s => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: s, font: FONT, size: 24, bold: true, color: ACC })], spacing: { before: 200, after: 80 }, keepNext: true });
const label = s => new TextRun({ text: s.toUpperCase(), font: FONT, size: 15, bold: true, color: SUB, characterSpacing: 20 });
const bullet = (s, lvl = 0) => new Paragraph({ numbering: { reference: 'b', level: lvl }, children: [t(s)], spacing: { before: 30, after: 30 } });
const border = { style: BorderStyle.SINGLE, size: 4, color: LINE }, borders = { top: border, bottom: border, left: border, right: border };
const cell = (children, w, o = {}) => new TableCell({ width: { size: w, type: WidthType.DXA }, borders, shading: o.fill ? { type: ShadingType.CLEAR, color: 'auto', fill: o.fill } : undefined,
  margins: { top: 50, bottom: 50, left: 90, right: 90 }, columnSpan: o.span, verticalAlign: o.v, children: Array.isArray(children) ? children : [p(children, { size: o.size, bold: o.bold, color: o.color, align: o.align, before: 0, after: 0 })] });
const table = (widths, rows) => new Table({ width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED, rows });
const fillLine = (lab, w = 4200) => new Paragraph({ spacing: { before: 140, after: 40 }, children: [t(lab + '  ', { color: SUB }), t('_'.repeat(Math.round(w / 110)), { color: LINE })] });
const BOX = '☐';

// ── the scenarios ──
const COLS = [['SpO2', 'SpO₂ %'], ['HR', 'HR'], ['BP', 'BP'], ['pH', 'pH'], ['PaCO2', 'PaCO₂'], ['PaO2', 'PaO₂'], ['Plat', 'Plateau'], ['dP', 'ΔP'], ['Crs', 'Crs'], ['TotPEEP', 'Total PEEP']];
function scenario(o) {
  const w0 = 1500, wc = Math.floor((W - w0) / COLS.length), widths = [w0, ...COLS.map(() => wc)], tw = widths.reduce((a, b) => a + b, 0);
  const head = new TableRow({ tableHeader: true, children: [cell('', w0, { fill: PAPER }), ...COLS.map(([, l]) => cell(l, wc, { fill: PAPER, size: 16, bold: true, color: SUB, align: AlignmentType.CENTER }))] });
  const row = (lab, x, bold) => new TableRow({ cantSplit: true, children: [cell(lab, w0, { size: 18, bold: true, color: bold ? ACC : SUB }), ...COLS.map(([k]) => cell(x[k] === '–' ? '·' : x[k], wc, { size: 20, bold, align: AlignmentType.CENTER }))] });
  const rate = new TableRow({ children: [cell([p([t('Rate it', { bold: true, size: 18, color: ACC })], { before: 0, after: 0 })], w0, { v: 'center' }),
    cell([p([t('Direction of each change is right?   ', { size: 18 }), t(`${BOX} Yes   ${BOX} No   ${BOX} Unsure`, { size: 20 })], { before: 0, after: 20 }),
          p([t('Size of the change:   ', { size: 18 }), t(`${BOX} Too small   ${BOX} About right   ${BOX} Too large`, { size: 20 })], { before: 0, after: 20 }),
          p([t('Believable at the bedside:   ', { size: 18 }), t(`1 ${BOX}    2 ${BOX}    3 ${BOX}    4 ${BOX}    5 ${BOX}`, { size: 20 }), t('     (1 not at all · 5 entirely)', { size: 16, color: SUB })], { before: 0, after: 0 })],
      tw - w0, { span: COLS.length })] });
  const expect = new TableRow({ children: [cell('What would you expect instead?', w0, { size: 16, color: SUB }), cell([p(' ', { before: 260, after: 260 })], tw - w0, { span: COLS.length })] });
  return [
    new Paragraph({ keepNext: true, spacing: { before: 220, after: 40 }, children: [t(String(o.n).padStart(2, '0') + '  ', { bold: true, size: 24, color: ACC }), t(o.what, { bold: true, size: 24 })] }),
    new Paragraph({ keepNext: true, spacing: { before: 0, after: 80 }, children: [label('Case ' + o.case + '  ·  stage: ' + o.stage)] }),
    table(widths, [head, row('Before', o.before, false), row('After', o.after, true), ...(o.alarm ? [new TableRow({ children: [cell('Alarms', w0, { size: 16, color: SUB }), cell(o.alarm, tw - w0, { span: COLS.length, size: 18, color: ACC })] })] : []), rate, expect])
  ];
}

// ── the document ──
const kids = [];
kids.push(p([label('VentCourse · live cases · faculty review, round 1')], { after: 40 }));
kids.push(h1('Does the simulated patient respond like a real child?'));
kids.push(p('In the live ARDS and asthma cases, each trainee sets the support on their own phone and sees their own patient respond: ventilator waveforms, plateau and driving pressure, blood gas and bedside monitor. This sheet asks you, as an experienced PICU clinician, to judge whether those responses are believable. Your ratings are the expert (face and content) validation of the model before it is used for teaching.', { after: 120 }));
kids.push(h2('How to rate'));
['Rate on your own, without discussing with other reviewers. The group result is shared in round 2.',
 'Each scenario is one change a trainee might make. "Before" is the scripted state of the case at that stage; "After" is what the phone shows once the patient has settled (a few minutes, shown sped up on the phone).',
 'Judge three things: whether each number moves the right way, whether the size of the change is right for this child, and how believable the whole picture is.',
 'If something is wrong, write what you would expect instead, with numbers if you can. That is the most useful part of the sheet.',
 'There are 16 scenarios; it takes about 25 minutes.'].forEach(s => kids.push(bullet(s)));
kids.push(h2('The two children'));
kids.push(bullet('Case 1 · ARDS: a 2-year-old girl, 10 kg, pneumonia progressing to severe PARDS (oxygenation index about 20–26). Lung-protective ventilation, PEEP titration, proning.'));
kids.push(bullet('Case 2 · asthma: a 5-year-old boy, 20 kg, near-fatal asthma, intubated. Low rate, long expiration, auto-PEEP, permissive hypercapnia.'));
kids.push(h2('Reviewer'));
kids.push(fillLine('Name'), fillLine('Designation and unit'), fillLine('Years in paediatric critical care'), fillLine('Date'));
kids.push(new Paragraph({ children: [new PageBreak()] }));
kids.push(p([label('Part 1 · scenarios')], { after: 40 }));
kids.push(h1('Sixteen changes, before and after'));
kids.push(p('Units: SpO₂ %, HR /min, BP mmHg, PaCO₂ and PaO₂ mmHg, pressures cmH₂O, Crs (respiratory compliance) mL/cmH₂O. A dot means not measured at that stage (no hold on a mask, for example). Total PEEP is what an expiratory hold would read.', { color: SUB, size: 18 }));
SC.forEach((o, i) => { if (i && i % 2 === 0) kids.push(new Paragraph({ children: [new PageBreak()] })); kids.push(...scenario(o)); });   // two whole scenarios per page
kids.push(new Paragraph({ children: [new PageBreak()] }));
kids.push(p([label('Part 2 · overall')], { after: 40 }));
kids.push(h1('Overall judgement'));
const q = s => [p([t(s, { bold: true })], { before: 200, after: 60, keepNext: true })];
kids.push(...q('1. Overall, how realistic are the patient responses for teaching ventilation to PICU trainees?'), p(`1 ${BOX}  not realistic      2 ${BOX}      3 ${BOX}      4 ${BOX}      5 ${BOX}  very realistic`));
kids.push(...q('2. Could any response teach a trainee a wrong lesson? Which scenario, and why?'), p(' ', { before: 600 }));
kids.push(...q('3. On the phone, oxygen settles over about 25 seconds and CO₂ over about a minute after a change (time is sped up). Is that a sensible teaching compromise?'), p(`${BOX} Yes    ${BOX} Oxygen should settle faster    ${BOX} Slower    ${BOX} CO₂ faster    ${BOX} CO₂ slower`));
kids.push(...q('4. Would you be comfortable using this simulated patient with your own trainees?'), p(`${BOX} Yes, as it is    ${BOX} Yes, after the changes I have suggested    ${BOX} No`));
kids.push(...q('5. Anything missing that a real child would show? (for example, a falling urine output, a rising lactate, a pneumothorax with high pressures)'), p(' ', { before: 600 }));

kids.push(new Paragraph({ children: [new PageBreak()] }));
kids.push(p([label('Appendix · for reviewers who want the detail')], { after: 40 }));
kids.push(h1('How the simulated patient works'));
kids.push(h2('The model, in plain words'));
['Lungs: two compartments. A "baby lung" that is always open, and a recruitable compartment that opens as PEEP and mean airway pressure rise. In ARDS about 45% of the lung is consolidated and never opens. Both compartments overstretch at high end-inspiratory pressure: compliance falls, those units are squeezed of blood flow and become dead space.',
 'Oxygen: shunt through closed units (reduced by hypoxic vasoconstriction), mixed with oxygenated blood using the mixed venous oxygen content, so a falling cardiac output also lowers the PaO₂. SpO₂ from the standard oxygen dissociation curve.',
 'CO₂: from alveolar ventilation (rate × (VT − dead space)). Anatomical dead space about 2.5 mL/kg on the ventilator; alveolar dead space rises with overstretch and with a low cardiac output.',
 'Asthma: expiration is slower than inspiration (the time-constant ratio is set so the script\'s measured auto-PEEP comes out right). Gas trapped at the end of each breath builds auto-PEEP; external PEEP below about 80% of it does not raise the total (flow limitation).',
 'Circulation: right atrial pressure rises with the pressure transmitted from the airway (a stiff ARDS lung transmits about 15%, the hyperinflated asthmatic chest about 40%), which reduces venous return; the right ventricle is loaded by overstretch, hypoxia and acidosis; the baroreflex makes up about half of any fall in pressure.',
 'Each stage of the case calibrates the model: the script\'s own settings give back the script\'s own gas, blood pressure and compliance. A trainee\'s different settings move the numbers from there.'].forEach(s => kids.push(bullet(s)));
kids.push(h2('What it has already been checked against'));
const groups = {};
TESTS.forEach(([res, g, what, det]) => { (groups[g] = groups[g] || []).push([res, what, det]); });
const gw = [2500, 6800, 5538];
const trows = [new TableRow({ tableHeader: true, children: ['Area', 'Check', 'Model result'].map((h, i) => cell(h, gw[i], { fill: PAPER, size: 16, bold: true, color: SUB })) })];
for (const [g, list] of Object.entries(groups)) {
  if (g === 'Script') { const ok = list.filter(x => x[0] === 'PASS').length; trows.push(new TableRow({ children: [cell(g, gw[0], { size: 17, bold: true }), cell('Every scripted stage: its own settings reproduce its own blood gas', gw[1], { size: 17 }), cell(ok + ' of ' + list.length + ' stages', gw[2], { size: 17 })] })); continue; }
  list.forEach(([res, what, det], i) => trows.push(new TableRow({ children: [cell(i ? '' : g, gw[0], { size: 17, bold: true }), cell(what, gw[1], { size: 17 }), cell((res === 'PASS' ? '✓  ' : '✗  ') + det, gw[2], { size: 16, color: res === 'PASS' ? INK : ACC })] })));
}
kids.push(table(gw, trows));
kids.push(p(`${TESTS.filter(x => x[0] === 'PASS').length} of ${TESTS.length} checks pass. The ARDS constants were fitted to the PEEP titration sheet in case 1 (SpO₂, blood pressure and compliance at PEEP 6 to 14).`, { before: 120, color: SUB, size: 18 }));
kids.push(h2('Known limits'));
['It is one average child per stage, not a population: the same settings always give the same numbers.',
 'Disease does not progress by itself between stages; the script moves the story on.',
 'Fluid status is fixed per case; a bolus, inotropes and sedation act only through the order\'s severity grade, not through the physiology.',
 'High-flow and NIV are simplified (a pressure effect and an FiO₂; no leak or asynchrony).',
 'It has not been compared with real patient data. That is the next step (round 3 below).'].forEach(s => kids.push(bullet(s)));

kids.push(new Paragraph({ children: [new PageBreak()] }));
kids.push(p([label('For the course director')], { after: 40 }));
kids.push(h1('Collating the reviews'));
['Round 1 (this sheet): three to five PICU consultants, each rating independently.',
 'Consensus: a scenario is accepted when at least 80% of reviewers rate direction "Yes", size "About right" and believability 4 or 5.',
 'Scenarios that miss consensus are changed using the reviewers\' "what would you expect" answers; the model is re-run and re-checked.',
 'Round 2: reviewers see the group\'s median ratings, the changed scenarios and their own previous rating, and rate again. Usually two rounds are enough.',
 'Round 3 (for publication): with ethics approval, de-identified PICU records of setting changes with blood gases before and after; the model\'s predictions are compared with what happened, against error limits agreed beforehand (for example PaCO₂ within ±5 mmHg).'].forEach(s => kids.push(bullet(s)));
const cw = [800, 6638, 1480, 1480, 1480, 1480, 1480];
kids.push(p(' ', { before: 120 }));
kids.push(table(cw, [new TableRow({ tableHeader: true, children: ['No.', 'Scenario', 'Reviewer 1', 'Reviewer 2', 'Reviewer 3', 'Reviewer 4', 'Reviewer 5'].map((h, i) => cell(h, cw[i], { fill: PAPER, size: 16, bold: true, color: SUB })) }),
  ...SC.map(o => new TableRow({ children: [cell(String(o.n), cw[0], { size: 17 }), cell(o.what, cw[1], { size: 17 }), ...[0, 1, 2, 3, 4].map(i => cell('D  S  B', cw[2 + i], { size: 14, color: LINE, align: AlignmentType.CENTER }))] }))]));
kids.push(p('D: direction (Y/N) · S: size (−, ✓, +) · B: believability 1–5. Accepted when at least 80% of reviewers give Y, ✓ and 4–5.', { color: SUB, size: 16 }));

const doc = new Document({
  creator: 'VentCourse', title: 'VentCourse physiology · faculty scoring sheet',
  styles: { default: { document: { run: { font: FONT, size: 20 } } },
    paragraphStyles: [{ id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 32, bold: true, font: FONT }, paragraph: { outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 24, bold: true, font: FONT, color: ACC }, paragraph: { outlineLevel: 1 } }] },
  numbering: { config: [{ reference: 'b', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 260 } } } }] }] },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838, orientation: PageOrientation.LANDSCAPE }, margin: { top: 900, bottom: 900, left: 1000, right: 1000 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [t('VentCourse · physiology review · round 1 · page ', { size: 16, color: SUB }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: SUB, bold: false })] })] }) },
    children: kids }]
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(OUT, b); console.log('wrote', OUT); });
