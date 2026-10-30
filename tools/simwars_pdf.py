#!/usr/bin/env python3
"""The live ventilation simulation as a SimWars-format scenario packet (PDF).

    python3 tools/build_sim.py && python3 tools/simwars_pdf.py [out.pdf]

Layout follows the SimWars semi-final packet: cover, Part I shared architecture, Part II and III round packets,
Part IV judge scoring, debrief, production checklist. Stage states and timings come from sim-data.js (the same data
the facilitator panel runs), so the paper and the screens cannot disagree.
"""
import os, sys, json, subprocess, html, re

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(APP, 'VentCourse Live Simulation - Scenario Packet.pdf')
src = open(os.path.join(APP, 'sim-data.js')).read()
D = json.loads(src[src.index('=') + 1:src.rindex(';')])
CS = {c['id']: c for c in D['cases']}
e = html.escape


def mmss(s):
    return f"{s // 60}:{s % 60:02d}"


def stage_state(st, extra=''):
    parts = []
    if st['vit']:
        parts.append('<b>' + ' · '.join(e(f'{k} {v}') for k, v in st['vit']) + '</b>')
    if st['exam']:
        parts.append(e('. '.join(st['exam'])) + '.')
    if st['vent']:
        parts.append('Ventilator: ' + e(st['vent']))
    if st['abg']:
        parts.append('Gas: <b>' + ' · '.join(e(f'{k} {v}') for k, v in st['abg']) + '</b>')
    return (e(st['story']) + '<br>' if st['story'] else '') + '<br>'.join(parts) + extra


def right(st):
    return next(o for o in st['opts'] if o[1])


SEVW = ['better', 'no change', 'worse', 'life-threatening']


def wrong_lines(st):
    return '<br>'.join(f'<i>{e(o[0])}</i> → {SEVW[o[3]]}' for o in st['opts'] if not o[1])


def table(head, rows, widths=None, cls=''):
    cg = ''.join(f'<col style="width:{w}">' for w in widths) if widths else ''
    return (f'<table class="{cls}"><colgroup>{cg}</colgroup><thead><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr></thead><tbody>'
            + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table>')


def box(t, red=False):
    return f'<div class="box{" red" if red else ""}">{t}</div>'


# ───────────────────────── the two rounds ─────────────────────────
A, S = CS['sc-ards'], CS['sc-asthma']
AS = {s['id']: s for s in A['stages']}
SS = {s['id']: s for s in S['stages']}

ROUNDS = [
    dict(n=1, key='A', C=A, name='The Wet Lung', who='2-year-old girl (10 kg)', short='ARDS',
         brief='You are the paediatric team on duty in the Emergency Department, with PICU cover. A 2-year-old girl is being referred from a nearby hospital with pneumonia and worsening breathing. Your task is to assess her, choose her respiratory support, and manage her ventilation. The ventilator and the patient monitor in front of you respond to what you set and order.',
         handover=['"This is the referring hospital. We are sending you a 2-year-old girl, 10 kilos. Cough, cold and fever for five days, fast breathing for two."',
                   '"We had her on 5 litres by face mask, IV fluids and IV ceftriaxone. She has needed more oxygen through the day."',
                   '"She is on a non-rebreathing mask at 15 litres now. Saturations low nineties. IV access is in. Arriving in one minute."'],
         act1='The child arrives on a non-rebreathing mask at 15 L/min with the transfer nurse. Mother is parking and arrives later.',
         exp60='designate a team leader · allocate airway, ventilator and drugs/IV roles · rapid ABCDE · apply monitoring · read the work of breathing and the oxygen requirement together · request a blood gas and chest X-ray · verbalise an initial support decision',
         hist='Previously well. Five days of cough, cold and fever; fast breathing for two days. Treated at the referring hospital with face-mask oxygen, IV fluids and ceftriaxone.',
         hidden='Bacterial pneumonia progressing to moderate–severe paediatric ARDS (bilateral opacities, PaO₂/FiO₂ falling below 100, oxygenation index rising to the high 20s). NIV will fail on the clock. The heart is normal.',
         trap='The early numbers look manageable: alert, drinking, pH 7.35, saturations 92%. The CO₂ of 56 on a 15-litre mask is the warning. The trap is a NIV trial with no stop rule, and a ventilator set to normalise numbers rather than to protect the lung.',
         stages=[
             ('1 — Arrival', 0, 180, AS['ar0'], 'No deterioration before 3:00, deliberately. The team should commit to a support and, if NIV, say what failure looks like.',
              ['ar0']),
             ('2 — NIV failing', 180, 300, AS['ar1'], '<b>Fires at 3:00 for every team</b>; the clock compresses two hours. If the team never started NIV, the child arrives here sicker (the panel carries a worse patient). Mother arrives 4:00.',
              ['ar1']),
             ('3 — Tube in, first settings', 300, 420, AS['ar2'], '<b>The tube is in at 5:00 for every team.</b> A team that has not decided to intubate by then is overtaken: the PICU consultant intubates, scored as a delay. Ventilator opens on standby; until they set it, the child is hand-bagged.',
              ['ar2']),
             ('4 — First ventilator gas', 420, 510, AS['ar3'], 'Release the gas on request from the panel (it reflects their settings). Oxygenation is poor on FiO₂ 1.0.',
              ['ar3']),
             ('5 — PEEP titration window', 510, 630, AS['ar4'], 'The ventilator lung behaves like the titration sheet: best compliance at PEEP 12, overdistension at 14 (plateau 30, BP falls). Release the sheet only if they titrate or ask.',
              ['ar4']),
             ('Acute event — 10:30', 630, 780, AS['ar6'], '<b>Scripted and unpreventable.</b> Sedation and paralysis wear off; she fights the ventilator, the high-pressure alarm sounds. Tap <i>Sedation / analgesia</i> when they deepen it: she settles. A blocker without sedation is scored, not prevented.',
              ['ar6']),
             ('6 — Endgame', 780, 900, AS['ar8'], 'Despite best PEEP, a longer Ti, sedation and a drier chart she is back on FiO₂ 1.0, OI 26. Rescue and handover. Hard stop 15:00.',
              ['ar8'])],
         res=[('Blood gas (arterial or venous)', '"Sending it now." Release from the panel: the numbers are the patient\'s at that moment, under the team\'s settings.'),
              ('Chest X-ray', '"Portable film is done." Release from the panel (the film for that stage).'),
              ('Lung ultrasound', 'Three views on the monitor: anterior B-lines with sliding, lateral coalescent B-lines, posterior consolidation with shred sign.'),
              ('Echo / POCUS heart, IVC, subcostal', 'Normal size and squeeze, IVC normal, no effusion. After 30 mL/kg the IVC turns plethoric.'),
              ('PICU consultant', '"On the phone. I can be there in ten minutes if you need hands for the tube." <b>Only</b> intubates at 5:00 if the team has not.'),
              ('Anaesthesia', '"Ten minutes away."'),
              ('Push-dose adrenaline, fluid bolus', '"Drawn up." / "Running." Tap Fluid 10 mL/kg or Inotrope on the panel when given.'),
              ('High-frequency oscillation', '"The oscillator is available. Fifteen minutes to set up and check." It does not arrive before 15:00.'),
              ('Inhaled nitric oxide', '"Available. Ten minutes to bring the cylinder." Tap Inhaled NO when started.'),
              ('ECMO centre', '"We\'ll take the call. Send us the OI trend and what you have tried." No retrieval within the scenario.'),
              ('Prone positioning', '"We have four people and the checklist." Tap Prone when they turn her.'),
              ('Additional staff', '"Two more nurses are five minutes away." Available from 5:00, not before.')],
         nurse=[(0.75, 'Doctor, what support do you want me to set up for her?', 'Only if no support decision yet'),
                (2, 'Shall I send a gas?', 'Only if no gas sent'),
                (5.5, 'The ventilator is on standby. What settings do you want?', 'Only if the ventilator is not yet set')],
         family=('Mother', '4:00', 'Calm, tired, worried. Arrives while the team is deciding on the tube.',
                 ['"She is so tired. Is she going to need a breathing tube?"', '12:00, if no one has spoken to her: "Why is it beeping all the time? Is she in pain?"'],
                 'She never obstructs care. She asks the same question again if ignored. One team member should speak to her without stopping the resuscitation.'),
         ),
    dict(n=2, key='B', C=S, name='The Quiet Chest', who='5-year-old boy (20 kg)', short='Asthma',
         brief='You are the paediatric team on duty in the Emergency Department, with PICU cover. A 5-year-old boy with acute severe asthma has been brought in by ambulance after an hour of treatment. Your task is to assess him, decide on his airway, and manage his ventilation. The ventilator and the patient monitor in front of you respond to what you set and order.',
         handover=['"Ambulance arriving. Five-year-old boy, 20 kilos, known asthmatic on an inhaled steroid he rarely takes. Two days of cough and wheeze, worse overnight."',
                   '"He has had three salbutamol nebs, ipratropium, IV hydrocortisone and IV magnesium over the last hour."',
                   '"He was wheezing a lot when we picked him up. He is quieter now, settling down. Saturations mid-eighties on the mask. One minute out."'],
         act1='The child arrives on a non-rebreathing mask at 15 L/min with the ambulance crew. Mother follows two minutes later.',
         exp60='designate a team leader · allocate airway, ventilator and drugs/IV roles · rapid ABCDE · apply monitoring · recognise the quiet chest and the drowsiness as exhaustion, not improvement · call for airway help · verbalise an initial airway decision',
         hist='Known asthmatic, poor adherence to an inhaled steroid. Two days of cough and wheeze, worse overnight. Three salbutamol nebulisers, ipratropium, IV hydrocortisone and IV magnesium in the last hour.',
         hidden='Life-threatening acute asthma with exhaustion. After intubation: severe gas trapping (measured auto-PEEP 8, peak–plateau gap from airway resistance). At 11:00, dynamic hyperinflation with circulatory collapse.',
         trap='The crew\'s "quieter now, settling down" and a chest that is barely wheezing. The quiet chest in a drowsy child is the loudest sign. Later the traps are a high CO₂ that tempts a faster rate, and a sudden collapse that tempts a needle before a disconnection.',
         stages=[
             ('1 — Arrival', 0, 150, SS['as0'], 'No deterioration before 2:30. The decision to intubate is clinical: credit a team that does not wait for a gas.',
              ['as0']),
             ('2 — Induction and the tube', 150, 240, SS['as1'], '<b>Fires at 2:30 for every team.</b> A team still giving nebulisers is told by the nurse: "He has stopped answering me." The panel carries a worse patient into the next stage.',
              ['as1']),
             ('3 — Tube in, first settings', 240, 390, SS['as2'], '<b>The tube is in at 4:00 for every team.</b> If the team has not decided to intubate, the PICU consultant intubates, scored as a delay. Ventilator opens on standby; until they set it, he is hand-bagged.',
              ['as2']),
             ('4 — First ventilator gas', 390, 540, SS['as3'], 'Release the gas from the panel. Peak is high, plateau is not: the gap is resistance. A team that raises the rate will see auto-PEEP climb and the BP fall on the screens.',
              ['as3']),
             ('5 — He starts to trigger', 540, 660, SS['as4'], 'Paralysis wears off at 9:00. With PEEP 0 each trigger costs 8 cmH₂O. Credit external PEEP about 6, never above the auto-PEEP.',
              ['as4']),
             ('Acute event — 11:00', 660, 780, SS['as5'], '<b>Scripted and unpreventable.</b> Dynamic hyperinflation. Tap <i>Disconnect the circuit</i> when they do, then <i>Reconnect</i>. Needle decompression without a pneumothorax is logged as such. Father/mother line at 12:00.',
              ['as5']),
             ('6 — Endgame', 780, 900, SS['as6'], 'If the team disconnected and restarted with a lower rate and VT, move the panel to stage 7 (stable) at 13:00; otherwise leave the event physiology running. Plan and handover. Hard stop 15:00.',
              ['as6'])],
         res=[('Blood gas (arterial or venous)', '"Sending it now." Release from the panel: the patient\'s numbers at that moment.'),
              ('Chest X-ray', '"Portable film in twenty minutes." No film inside the scenario.'),
              ('Lung ultrasound', 'Lung sliding with A-lines on both sides: no pneumothorax (unless the facilitator has fired one, which is not used in competition).'),
              ('Echo / POCUS heart, IVC, subcostal', 'Normal function, small underfilled ventricles; IVC normal; no effusion.'),
              ('Ketamine, rocuronium, cuffed tube', '"Drawn up." / "Cuffed 5.0 and 4.5 ready."'),
              ('Push-dose adrenaline, fluid bolus', '"Drawn up." / "Running." Tap Fluid or Inotrope on the panel when given.'),
              ('More nebulisers / salbutamol in the circuit', '"Running." Tap Bronchodilator each time (it lowers airway resistance a little each dose).'),
              ('IV salbutamol or aminophylline infusion', '"Pharmacy is making it up: ten minutes."'),
              ('Heliox', '"We don\'t have heliox in this unit."'),
              ('Inhalational anaesthetic', '"The anaesthetic machine can come from theatre in thirty minutes." Not inside the scenario.'),
              ('PICU consultant / anaesthesia', '"On the phone. Ten minutes." <b>Only</b> intubates at 4:00 if the team has not.'),
              ('Additional staff', '"Two more nurses are five minutes away." Available from 5:00, not before.')],
         nurse=[(0.75, 'Shall I set up another nebuliser?', 'Only if no airway decision yet. A deliberate distractor.'),
                (4.5, 'He is on the ventilator on standby. What settings do you want?', 'Only if the ventilator is not yet set'),
                (7, 'The CO₂ is 78. Do you want to change anything?', 'Only if the gas has not been discussed. Neutral delivery: the right answer is no.')],
         family=('Mother', '2:00', 'Anxious, familiar with asthma, used to nebulisers working.',
                 ['"He always gets better with the nebuliser. Why is it not working this time?"', '12:00, if no one has spoken to her: "What is happening? Why are all the alarms going?"'],
                 'She never obstructs care. During the acute event she escalates emotionally but stays at the bedside. One team member should speak to her.'),
         ),
]

SAFE = {  # the panel grades settings against these ranges (aim · harm beyond)
    'A': [('Intubated, first settings and onward', 'VT 60–80 mL (6–8 mL/kg) · PEEP 6–10 (9–12 after titration) · rate 25–35 · Ti 0.5–0.8 s · FiO₂ 0.8–1.0 · Pinsp 12–20',
           'VT < 50 or > 100 · PEEP < 5 or > 14 · rate < 20 or > 40 · Pinsp > 25'),
          ('NIV (stage 1)', 'CPAP/EPAP 5–8 · IPAP 10–16 · FiO₂ 0.6–1.0', 'Mask alone at stage 1 = worse; NIV at stage 2 onward = life-threatening')],
    'B': [('Intubated, first settings and onward', 'VT 120–160 mL (6–8 mL/kg) · rate 10–16 · Ti 0.6–1.0 s · expiratory time ≥ 3.5 s · PEEP 0–5 (5–7 once triggering) · plateau < 30',
           'VT > 200 · rate > 20 · expiratory time < 2 s · PEEP > 8 (> 9 once triggering)'),
          ('Stage 1', 'Intubation is the expected decision', 'NIV = life-threatening (drowsy, cannot protect the airway)')],
}


def round_packet(R):
    C = R['C']; n = R['n']; part = ['II', 'III'][n - 1]
    h = [f'<h1 class="part">PART {part} — ROUND {n} PACKET</h1>', f'<h2>"{R["name"]}"</h2>',
         f'<p><b>Clock:</b> {mmss(C["clock"]["stop"])} hard stop · <b>Patient:</b> {e(R["who"])} · <b>Diagnosis family:</b> {R["short"]} · '
         f'<b>Confederates:</b> Bedside nurse · {R["family"][0]} · PICU consultant (voice on the phone) · <b>Operator:</b> facilitator panel</p>',
         '<h3>Candidate brief</h3>', box(e(R['brief'])),
         '<h3>Pre-arrival call</h3>', box('<br>'.join(e(x) for x in R['handover'])),
         '<h3>Act I — The Golden Minute (0:00–1:00)</h3>', f'<p>{e(R["act1"])}</p>',
         f'<p><b>Expected within 60 seconds:</b> {e(R["exp60"])}.</p><p>No deterioration occurs in this window unless gross errors are made.</p>',
         f'<h2 class="sec">{n * 2 + 4}. The patient — {e(R["who"])}</h2>',
         f'<p><b>History:</b> {e(R["hist"])}</p><p><b>Hidden diagnosis:</b> {e(R["hidden"])}</p>',
         box('<b>The trap — read before judging.</b> ' + e(R['trap']), True)]
    rows = []
    for (lab, t0, t1, st, note, _ids) in R['stages']:
        r = right(st)
        rows.append([f'<b>{e(lab)}</b><br><span class="mono">{mmss(t0)}–{mmss(t1)}</span>',
                     stage_state(st),
                     f'<b>{e(r[0])}.</b> {e(r[2])}',
                     note + ('<br><br><span class="dim">Other choices on the panel:</span><br>' + wrong_lines(st) if len(st['opts']) > 1 else '')])
    h.append(table(['Stage', 'State', 'Expected behaviour', 'Operator notes'], rows, ['13%', '29%', '31%', '27%'], 'stages'))
    h.append(box('<b>What the screens do.</b> The stage moves on the clock. The team\'s settings and orders run through the physiology on every screen: '
                 'a good decision makes the child better within the stage, a harmful one makes the child worse, and a stage that ended worse or life-threatening '
                 'carries a sicker child into the next one. Settings are graded against the safe ranges below and shown to the operator only.'))
    h.append('<h3>Safe ranges the panel grades against</h3>')
    h.append(table(['When', 'Aim', 'Harm beyond'], [[e(a), e(b), e(c)] for a, b, c in SAFE[R['key']]], ['22%', '48%', '30%']))
    sec = n * 2 + 5
    h.append(f'<h2 class="sec">{sec}. Round {n} — Scripts and Scripted Answers</h2>')
    h.append(f'<h3>Nurse prompts — {len(R["nurse"])}, fixed</h3>')
    h.append(table(['Time', 'Prompt', 'Note'], [[mmss(int(t * 60)), f'<i>"{e(p)}"</i>', e(nt)] for t, p, nt in R['nurse']], ['10%', '50%', '40%']))
    fam = R['family']
    h.append(f'<h3>{fam[0]} — arrives {fam[1]}</h3><p>{e(fam[2])}</p>' + box('<br>'.join(f'<i>{e(x)}</i>' for x in fam[3])) + f'<p>{e(fam[4])}</p>')
    h.append('<h3>Resource requests — scripted answers</h3>')
    h.append(table(['Request', 'Response'], [[e(a), b] for a, b in R['res']], ['26%', '74%']))
    h.append('<p class="dim">Deliver every answer neutrally, with no hesitation and no hint. The same words for every team in the round.</p>')
    return '\n'.join(h)


# fixed timings, side by side
def timings():
    rows = [['0:00', 'Child arrives · Act I begins', 'Child arrives · Act I begins'],
            ['0:45', 'Nurse prompt (support)', 'Nurse prompt (another nebuliser?)'],
            ['1:00–3:00', 'Stage 1: support decision', 'Stage 1 to 2:30: airway decision'],
            ['2:00', 'Nurse prompt (gas)', '<b>Mother arrives</b>'],
            ['2:30', '', '<b>Stage 2: induction</b> (fires)'],
            ['3:00', '<b>Stage 2: NIV failing</b> (fires)', ''],
            ['4:00', '<b>Mother arrives</b>', '<b>Stage 3: tube in</b> · ventilator on standby'],
            ['4:30', '', 'Nurse prompt (settings)'],
            ['5:00', '<b>Stage 3: tube in</b> · ventilator on standby', 'Additional staff available'],
            ['5:30', 'Nurse prompt (settings) · additional staff available', ''],
            ['6:30', '', 'Stage 4: first gas'],
            ['7:00', 'Stage 4: first gas', 'Nurse prompt (CO₂ 78)'],
            ['8:30', 'Stage 5: PEEP titration window', ''],
            ['9:00', '', 'Stage 5: paralysis wears off'],
            ['10:30', '<b>Scripted acute event</b>: fighting the ventilator', ''],
            ['11:00', '', '<b>Scripted acute event</b>: sudden desaturation'],
            ['12:00', 'Mother (if not yet spoken to)', 'Mother (if not yet spoken to)'],
            ['13:00', 'Endgame: OI 26 · rescue and handover', 'Endgame: plan and handover (stage 7 only if resolved)'],
            ['<b>15:00</b>', '<b>Hard stop</b>', '<b>Hard stop</b>']]
    return table(['Time', 'Round 1 · The Wet Lung', 'Round 2 · The Quiet Chest'], rows, ['12%', '44%', '44%'])


def score_rows(items):
    return table(['Item', 'Max'], [[a, str(b)] for a, b in items] + [['<b>Section subtotal</b>', f'<b>/ {sum(b for _, b in items)}</b>']], ['88%', '12%'])


def crm(title, items):
    return f'<h3 class="plain">{title} (10)</h3>' + table(['Behaviour', 'Score (0–2)'], [[x, ''] for x in items] + [['<b>Subtotal</b>', '<b>/ 10</b>']], ['84%', '16%'])


SB1 = [('Recognises the indication to intubate and acts on it — <b>R1</b> NIV failure by the numbers and the shock, not waiting further · <b>R2</b> exhaustion and altered sensorium, without waiting for a gas', 2),
       ('Prepares intubation as a resuscitation: preoxygenation, fluid bolus, pressor drawn up, cuffed tube, most experienced hands — <b>R2</b> ketamine and rocuronium · 0 absent · 1–2 partial · 3 largely complete · 4 timely and comprehensive', 4),
       ('First ventilator settings within the safe ranges, set from the brief rather than by trial — <b>R1</b> VT 6–8 mL/kg, PEEP 7, rate 30, FiO₂ 1.0 · <b>R2</b> VT 6–8 mL/kg, rate 12–14, I:E 1:4, expiratory time 4–5 s, PEEP 0–5 · scored 0–4 as above', 4),
       ('Verifies the settings with measured values — plateau and driving pressure (<b>R1</b>), plateau and an expiratory hold for auto-PEEP (<b>R2</b>)', 2),
       ('Confirms the tube (EtCO₂, chest rise, equal air entry) and starts a sedation plan', 2),
       ('Hand-bags safely while the ventilator is on standby — <b>R2</b> slow, 8–10 breaths a minute with a long exhalation', 2)]


def scoring():
    h = ['<h1 class="part">PART IV — SHARED JUDGE SCORING MODEL</h1>',
         '<h2 class="sec">10. Structure</h2>',
         '<p><b>Clinical Judgement 40 · Crisis Resource Management 50 · Global Performance 10 = 100</b></p>',
         '<p><b>Item scoring rule:</b> 0 = absent / unsafe · 1 = partial, delayed, or inconsistent · 2 = timely, complete, and effective. Items carrying 4 marks are scored 0–4 using the same anchor, applied proportionally.</p>',
         '<p><b>Scored by:</b> Domain I — both clinical judges independently, <b>averaged</b>. Domain II — both non-clinical judges independently, <b>averaged</b>. Domain III — <b>collective agreed mark</b>, after each judge has privately recorded their own rating.</p>',
         box('<b>DO NOT SUM THE TWO SHEETS IN A DOMAIN. AVERAGE THEM.</b>', True),
         box('<b>Evidence the screens give you.</b> The facilitator panel keeps a time-stamped log of every setting, order, prompt and stage, with where each one was taking the patient (Debrief tab, downloadable as CSV). Judges may use it to settle a disputed time. It records what was done, not why: the judging is still yours.'),
         '<h2 class="sec">11. Domain I — Clinical Judgement (40)</h2>',
         '<h3>Section A — Initial assessment and support decision (8)</h3>',
         score_rows([('Rapid ABCDE; reads the severity from the work of breathing, mental state and oxygen requirement together', 2),
                     ('Recognises the cue in the handover — <b>R1</b> CO₂ 56 on a 15-litre mask · <b>R2</b> "quieter now" after maximal therapy, a quiet chest in a drowsy child', 2),
                     ('Makes the right support decision with a stated rationale — <b>R1</b> NIV with written failure criteria (time limit and numbers) · <b>R2</b> intubate on clinical grounds', 2),
                     ('Requests investigations without letting them delay care — gas, X-ray, ultrasound as indicated', 2)]),
         '<h3>Section B — Airway and first ventilator settings (16)</h3>', score_rows(SB1),
         '<h3>Section C — Ongoing ventilation (8)</h3>',
         '<p class="plain"><b>Round 1 — The Wet Lung</b></p>',
         score_rows([('Raises PEEP in steps for oxygenation, watching compliance, SpO₂ and blood pressure at each step', 2),
                     ('Settles on the best-compliance PEEP (12) and steps back from overdistension', 2),
                     ('Does not chase oxygen with tidal volume or rate; keeps plateau ≤ 28–30 and driving pressure ≤ 15', 2),
                     ('Reassesses the circulation; avoids a positive fluid creep once perfusing', 2)]),
         '<p class="plain"><b>Round 2 — The Quiet Chest</b></p>',
         score_rows([('Accepts the CO₂ while pH ≥ 7.20; does not raise the rate or the tidal volume', 2),
                     ('Reads peak − plateau as airway resistance and plateau − PEEP as stretch', 2),
                     ('Sets external PEEP at about 75–80% of the measured auto-PEEP once he triggers; never above it', 2),
                     ('Continues bronchodilators and steroids; keeps him sedated; no routine blocker', 2)]),
         '<h3>Section D — Acute event, reassessment and disposition (8)</h3>',
         score_rows([('Manages the scripted acute event — <b>R1</b> rules out the tube, secretions and pneumothorax, then deepens sedation; blocker only if she still fights · <b>R2</b> disconnects first, lets the chest fall, then DOPE', 2),
                     ('Reassesses after the event and modifies the ventilator — <b>R2</b> restarts with a lower rate and tidal volume', 2),
                     ('Plans the next step — <b>R1</b> prone with a checklist, HFOV and an early ECMO call, accepts SpO₂ 88–92% · <b>R2</b> prevents auto-PEEP: long expiration, bronchodilators, sedation, low VT', 2),
                     ('Gives a structured SBAR handover with the current settings, measured values and the plan', 2)]),
         box('<b>The acute event is scripted and occurs regardless of team performance. Do not score a prevention pathway — none exists.</b><br>'
             '<b>Branch neutrality.</b> Score Section D on what the team did <b>from where they were</b>. A team whose child is still critical at the handover earns the same disposition marks for a correct handover as a team handing over a stable child. The outcome is already captured in Section B, the penalty, and Domain III.', True),
         '<p><b>Penalty</b> — the consultant had to intubate on the clock because the team had not decided by the tube-in time: <b>−10</b></p>',
         '<p class="dim"><i>Two further penalties are proposed but not yet agreed: ventilator left on standby or the child hand-bagged for more than two minutes after the tube is in −4; plateau above 30 or VT above 10 mL/kg for more than two minutes −5.</i></p>',
         table(['CLINICAL JUDGEMENT TOTAL (A + B + C + D)', '/ 40'], [['', '']], ['88%', '12%']),
         '<h2 class="sec">12. Domain II — Crisis Resource Management (50)</h2>',
         '<p><i>All behaviours scored 0–2 using the general anchor at the top of this sheet.</i></p>',
         box('<b>Anti-double-counting rule — read before scoring.</b><br><b>Domain I scores the clinical recognition and its consequences, once. Domain II scores the process</b> — whether the team had a system for noticing, delegating, communicating and reassessing — <b>not the diagnosis.</b> A team that recognised NIV failure or the trapping does not earn credit again here for the same moment. Situational awareness asks whether they had a method for noticing (reading the ventilator\'s measured values and alarms, scheduled reassessment, findings said aloud), not whether they noticed.', True),
         crm('Leadership and command', ['Assumes a clearly identifiable leadership role early', 'Assigns airway, ventilator, drugs and family roles and confirms accountability',
                                        'Maintains a hands-off overview rather than taking over the ventilator or the airway', 'Reprioritises as the child deteriorates on the clock', 'Anticipates the next step: the tube, the first settings, the gas, the rescue']),
         crm('Communication', ['Uses clear, concise instructions and closed-loop communication — settings read back before Confirm', 'Verbalises priorities and maintains a shared mental model',
                               'Encourages team members to report changes, alarms and concerns', 'Communicates effectively and compassionately with the parent', 'Uses structured communication with the consultant and the receiving team']),
         crm('Situational awareness', ['Watches the monitor and the ventilator together, and says aloud what changed', 'Reassesses rather than relying on the first examination',
                                       'Has a system that surfaces the measured values (plateau, driving pressure, auto-PEEP, VTe)', 'Responds to alarms by cause, not by silencing them',
                                       'Anticipates the next threat — <b>R1</b> NIV failure, hypotension after the tube, overdistension · <b>R2</b> hypotension after the tube, trapping, collapse']),
         crm('Resource and workload management', ['Allocates people sensibly between the airway, the ventilator, drugs and the parent', 'Uses investigations and equipment purposefully without duplication',
                                                  'Calls for help in good time — consultant, anaesthesia; <b>R1</b> ECMO centre', 'Manages time efficiently within the 15:00 scenario', 'Maintains care continuity during intubation and the acute event']),
         crm('Decision-making and anticipation', ['Establishes the correct initial priority after rapid assessment', 'Distinguishes a reassuring number from a reassuring child',
                                                  'Escalates before catastrophic deterioration when clues were available', 'Changes one thing at a time on the ventilator and checks its effect', 'Makes a coherent plan for the next hours and the handover']),
         table(['CRM TOTAL', '/ 50'], [['', '']], ['88%', '12%']),
         '<h2 class="sec">13. Domain III — Global Performance and Final Adjudication</h2>',
         '<p><b>Entrustment question:</b> <i>Would you confidently entrust this team to ventilate this child in your PICU tonight?</i></p>',
         table(['Rating', 'Behavioural anchor', 'Marks'], [['<b>Unsafe</b>', 'Major threats missed; ventilator settings or delays place the child at risk', '0'],
                                                         ['<b>Poor</b>', 'Fragmented assessment, delayed decisions, substantial prompting required', '2'],
                                                         ['<b>Borderline</b>', 'Basic care delivered but inconsistent leadership, reassessment or anticipation', '4'],
                                                         ['<b>Competent</b>', 'Safe and generally organised management with some delays or omissions', '6'],
                                                         ['<b>Very good</b>', 'Timely decisions, lung-protective settings, effective reassessment with minor limitations', '8'],
                                                         ['<b>Outstanding</b>', 'Seamless leadership, anticipatory decisions and consistently safe ventilation', '10']], ['16%', '72%', '12%']),
         box('<b>Sequence — do not vary.</b> ① Each judge privately records their own rating the moment the scenario ends. ② The four judges confer and agree the collective mark. ③ <b>Only then</b> are domain totals calculated. A collective mark agreed after the arithmetic is read out is no longer independent information.', True),
         '<p><b>COLLECTIVE GLOBAL PERFORMANCE SCORE: ____ / 10</b></p>',
         '<h3>Safety red flags</h3>',
         '<p class="chk">☐ No identifiable leader ☐ NIV continued or escalated in a child who is failing it ☐ NIV in a drowsy asthmatic ☐ Waiting for a gas to decide on intubation in exhaustion ☐ VT above 10 mL/kg ☐ Plateau above 30 left uncorrected ☐ Rate raised to chase the CO₂ in asthma ☐ External PEEP above the auto-PEEP ☐ Needle before disconnection in the collapse ☐ Blocker without sedation ☐ Bicarbonate for a respiratory acidosis</p>',
         '<h3>Exceptional performance indicators</h3>',
         '<p class="chk">☐ States NIV failure criteria before starting ☐ Prepares the circulation before induction ☐ Reads back settings before Confirm ☐ Uses holds to measure plateau and auto-PEEP ☐ Titrates PEEP one step at a time against compliance and BP ☐ Disconnects within seconds of the collapse ☐ Speaks to the parent without stopping the resuscitation ☐ Leader remains consistently hands-off</p>',
         table(['Why should this team advance to the final?', 'What prevented a higher score?'], [['&nbsp;<br>&nbsp;', '']], ['50%', '50%']),
         table(['Domain', 'Maximum', 'Awarded'], [['Clinical Judgement <i>(mean of two clinical judges)</i>', '40', ''], ['Crisis Resource Management <i>(mean of two non-clinical judges)</i>', '50', ''],
                                                ['Global Performance <i>(collective)</i>', '10', ''], ['<b>FINAL TOTAL</b>', '<b>100</b>', '']], ['64%', '18%', '18%'])]
    return '\n'.join(h)


def debrief():
    return '\n'.join([
        '<h2 class="sec">14. Debrief — Both Rounds</h2>',
        '<p><b>No debrief runs until both teams in that round have played.</b></p>',
        '<p><b>Open with the design reveal.</b> State that every stage and the acute event fired on the clock, and that both teams faced the identical arc. Then show the panel\'s Debrief tab: their own settings, with where each one took the child.</p>',
        '<p><b>Then, by objective:</b></p><ul>' + ''.join(f'<li><b>{a}</b> — {b}</li>' for a, b in [
            ('Opening', 'how are you feeling? What was the hardest moment?'),
            ('Leadership', 'walk me through the first sixty seconds. Who led, who had the airway, who had the ventilator?'),
            ('Anchoring', '<i>R1:</i> she was alert and drinking with a pH of 7.35. What made you worry? <i>R2:</i> the crew said he was settling. What did the quiet chest tell you?'),
            ('The support decision', '<i>R1:</i> what were your NIV failure criteria, and when did you write them down? <i>R2:</i> what made intubation a clinical decision?'),
            ('The first settings', 'what did you set, and how did you check it was safe? What did the plateau and the driving pressure (R1), or the expiratory hold (R2), tell you?'),
            ('The middle', '<i>R1:</i> how did you choose the PEEP, and what told you to stop? <i>R2:</i> the CO₂ was 78. Why leave it?'),
            ('The acute event', '<i>R1:</i> the alarm and the fighting: what did you check before you sedated? <i>R2:</i> the collapse: what did you do in the first ten seconds, and why?'),
            ('Communication', 'the parent arrived at the worst moment. How did you manage that without stopping?'),
            ('Closing', 'one thing you would change about how you organised the team.')]) + '</ul>',
        '<h3>Take-aways the debrief should land</h3>',
        '<p class="plain"><b>Round 1</b></p><ul>' + ''.join(f'<li>{e(x)}</li>' for x in A['debrief']) + '</ul>',
        '<p class="plain"><b>Round 2</b></p><ul>' + ''.join(f'<li>{e(x)}</li>' for x in S['debrief']) + '</ul>'])


def checklist():
    return '\n'.join([
        '<h2 class="sec">15. Production Checklist</h2>',
        '<h3>Common to both rounds</h3><ul>' + ''.join(f'<li>{x}</li>' for x in [
            '<b>Three screens on one room code</b>, opened from <span class="mono">venti-course-app-production.up.railway.app/sim.html</span>: facilitator panel (operator laptop, out of the team\'s sight), ventilator (tablet or laptop at the bedside, the team touches it), patient monitor (large screen the team can see)',
            'Open the facilitator panel first on the operator laptop; the same laptop keeps control. Any other laptop can take over the room with one click if needed',
            'Choose the case, check the ventilator and monitor show the same child, then press <b>Start the clock</b> as the stretcher enters. Pause only for a technical failure, never for the team',
            'On the monitor, tap <b>Sound off</b> once so the alarms and tones play',
            '<b>Events the operator does not fire in competition:</b> pneumothorax, plug, tube dislodged, under-filled. The only acute event is the scripted one, on the clock, so both teams in a round face the same case',
            'Infant/child manikin with a cuffed tube in the airway trolley; bag-valve-mask with PEEP valve; laryngoscopes; suction',
            'Printed drug labels: ketamine, rocuronium, fentanyl, midazolam, push-dose adrenaline, fluid boluses',
            'Visible countdown clock for the Chief (the panel shows elapsed time against 15:00)',
            'One bedside nurse confederate, one parent actor, one consultant voice (phone)',
            '<b>Sequestration room</b> for teams not competing, with no feed']) + '</ul>',
        '<h3>Round 1 — The Wet Lung</h3><ul>' + ''.join(f'<li>{x}</li>' for x in [
            'Toddler manikin labelled <b>2-year-old girl, 10 kg</b>, on a non-rebreathing mask at arrival; NIV mask and circuit at the bedside',
            'Cuffed 4.0 and 4.5 tubes; 10 mL/kg bolus syringes',
            'Prone checklist card and four people available from 5:00 (the additional staff)',
            'Moulage: none needed beyond nasal flaring and indrawing described on examination']) + '</ul>',
        '<h3>Round 2 — The Quiet Chest</h3><ul>' + ''.join(f'<li>{x}</li>' for x in [
            'Child manikin labelled <b>5-year-old boy, 20 kg</b>, on a non-rebreathing mask at arrival; nebuliser running',
            'Cuffed 5.0 and 4.5 tubes; ketamine and rocuronium labelled; 20 mL/kg fluid running at stage 2',
            'Inline salbutamol adaptor for the circuit',
            'Simulated chest compression for the disconnection manoeuvre (hands on the chest)']) + '</ul>'])


def part1():
    return '\n'.join([
        '<h1 class="part">PART I — SHARED ARCHITECTURE</h1>',
        '<h2 class="sec">1. Competition Structure</h2>',
        '<p><b>Two rounds, one child each, played on the live simulation: a ventilator screen the team touches and a patient monitor the team watches, both driven by the same physiology and run from the facilitator panel.</b></p>',
        '<p>Comparison is within-round only. The two teams playing the same round must face precisely the same scenario — identical stages at identical minutes, identical prompts, identical scripted answers, identical information released at identical moments. This is why the clock now drives the case, and why the resource-answer tables in §7 and §9 exist.</p>',
        '<h3>Sequestration</h3><ul><li>Teams not currently competing are held in a sealed room with no feed and phones surrendered.</li><li><b>No debrief for either team until both teams in that round have played.</b></li></ul>',
        '<h2 class="sec">2. The Two Rounds</h2>',
        table(['', 'Round 1 · The Wet Lung', 'Round 2 · The Quiet Chest'], [
            ['Child', '2-year-old girl, 10 kg', '5-year-old boy, 20 kg'],
            ['Condition', 'Pneumonia progressing to ARDS', 'Life-threatening acute asthma'],
            ['Reassuring front', 'Alert, drinking, pH 7.35', '"Quieter now, settling down"'],
            ['Real threat', 'NIV failure, then a stiff lung that punishes large breaths', 'Exhaustion, then gas trapping that punishes fast breaths'],
            ['Scripted acute event', '10:30 fighting the ventilator', '11:00 sudden desaturation (dynamic hyperinflation)'],
            ['Ventilator lesson', 'Small VT, titrated PEEP, plateau and driving pressure', 'Low rate, long expiration, plateau and auto-PEEP']], ['20%', '40%', '40%']),
        '<p>The two rounds are mirror images: one lung is too stiff to stretch, the other too obstructed to empty. Both test reading the ventilator\'s measured values rather than its alarms.</p>',
        '<h2 class="sec">3. How the Clock Runs the Case</h2>',
        box('<b>Governing principle.</b> Every stage and scripted event fires on the clock for both teams. Team decisions modulate <b>severity</b> and <b>resolution</b> — never <b>occurrence</b>.', True),
        '<ul><li><b>Start the clock</b> on the facilitator panel as the stretcher enters. From then on the panel moves the stages, fires the acute event and shows each confederate line in a <b>Say now</b> box at its minute.</li>'
        '<li><b>Severity:</b> the team\'s settings and orders run through the physiology on all screens. A child who reaches a stage after a worse or life-threatening decision arrives sicker. A child on lung-protective settings looks better within the same stage.</li>'
        '<li><b>Resolution:</b> the acute event resolves only through the team\'s actions (sedation in Round 1, disconnection and a lower rate in Round 2).</li>'
        '<li><b>Overtaking:</b> intubation happens at the tube-in minute for every team. A team that has not decided is overtaken by the consultant, scored as a delay.</li>'
        '<li><b>Pause</b> only for a technical failure. <b>Clock off</b> returns the panel to manual stages (teaching, not competition).</li></ul>',
        '<h3>Fixed timings — both rounds</h3>', timings(),
        '<h3>Confederate behavioural ceilings</h3><ul>'
        '<li><b>Never make a clinical decision or offer a diagnosis.</b> The nurse does not say "her CO₂ is going up" or "should we intubate". She reports only what she is asked, and the fixed prompts.</li>'
        '<li><b>The nurse sets the ventilator only when told, and reads back.</b> The ventilator screen is the team\'s: the nurse may press Confirm for them, never choose a value.</li>'
        '<li><b>The parent never obstructs care.</b> She escalates emotionally if ignored and does not leave, but never physically interferes or refuses.</li>'
        '<li><b>The consultant on the phone advises only when asked</b>, and acts only at the overtaking minute.</li>'
        '<li><b>No unprompted findings.</b> Every examination finding and result is available when asked for, and volunteered by nobody.</li></ul>',
        '<h3>Safety valve</h3>',
        '<p>If by <b>8:00</b> a team has become non-functional and no meaningful care is happening, the Chief Judge signals the nurse to escalate prompts heavily. No team should score near zero because of a coordination failure in the opening minutes; the value lies in what they do once oriented.</p>',
        '<h2 class="sec">4. Judging Model</h2>',
        '<p><b>Four judges: two clinical, two non-clinical. One non-scoring Chief.</b></p>',
        table(['Domain', 'Marks', 'Scored by', 'Method'], [['<b>I — Clinical Judgement</b>', '40', 'Both clinical judges, independently', '<b>Mean of the two sheets</b>'],
                                                          ['<b>II — Crisis Resource Management</b>', '50', 'Both non-clinical judges, independently', '<b>Mean of the two sheets</b>'],
                                                          ['<b>III — Global Entrustment</b>', '10', 'All four judges', '<b>Collective agreed mark</b>'], ['<b>TOTAL</b>', '<b>100</b>', '', '']], ['36%', '10%', '30%', '24%']),
        box('<b>DO NOT SUM THE TWO SHEETS IN A DOMAIN. AVERAGE THEM.</b> Two judges each scoring Domain I out of 40 produce a domain mark out of 40, not 80.', True),
        '<p><b>Disagreement signal.</b> If the two judges in a domain differ by more than <b>6 marks in Domain I</b> or <b>8 marks in Domain II</b>, hold a thirty-second conference before totals are locked.</p>',
        '<p><b>The Chief does not score.</b> The role is: hold the flat 15:00 clock, watch that the panel fires on time, trigger the safety valve, adjudicate the tiebreaker, and preside over both rounds so one standard applies throughout.</p>',
        '<h3>Tiebreaker</h3><p>Pre-declared. 60 seconds. Team leader only, no conferring.</p>',
        '<p><b>Round 1:</b> <i>"Your PEEP is 12, FiO₂ 1.0, OI 26. Tell me the order of your next three steps, and what would make you skip straight to the last one."</i></p>',
        '<p><b>Round 2:</b> <i>"The blood pressure falls to 60 systolic, two minutes after intubation. Tell me what you do in the first thirty seconds, and the five causes you work through after that."</i></p>',
        '<h2 class="sec">5. Outstanding Items for Co-Hosts</h2><ol>'
        '<li><b>Confirm who holds the non-scoring Chief role</b>, and who operates the facilitator panel (not a judge).</li>'
        '<li><b>Book the technical dry run</b> of both rounds on the three screens: confederates and operator only, full 15:00 with the clock.</li>'
        '<li><b>Decide on the two proposed penalties</b> in §11 (standby or hand-bagging beyond two minutes; plateau above 30 or VT above 10 mL/kg).</li>'
        '<li><b>Confirm the tiebreaker</b>, or whether ties are broken on Domain III alone.</li>'
        '<li><b>Decide whether Part I is removed</b> before anything is distributed to competing teams.</li></ol>'])


CSS = """
@page { size: A4; margin: 18mm 16mm 18mm 16mm; }
* { box-sizing: border-box; }
body { font-family: 'DejaVu Sans', sans-serif; font-size: 8.6pt; line-height: 1.45; color: #1b1b1b; margin: 0; }
.cover { height: 250mm; display: flex; flex-direction: column; justify-content: center; page-break-after: always; }
.kick { color: #8B1E1E; font-weight: 700; letter-spacing: .22em; font-size: 8.4pt; }
.cover h1 { font-size: 24pt; margin: 14px 0 10px; }
.cover .sub { font-size: 11pt; color: #444; line-height: 1.5; }
.rule { width: 150px; height: 3px; background: #8B1E1E; margin: 30px 0; }
.meta p { margin: 4px 0; font-size: 8.4pt; } .meta b { margin-right: 6px; }
.toc { margin-top: 60px; color: #888; font-size: 7.4pt; line-height: 1.6; }
h1.part { color: #8B1E1E; font-size: 13pt; border-bottom: 2px solid #8B1E1E; padding-bottom: 6px; margin: 0 0 14px; page-break-before: always; }
h2 { font-size: 10.5pt; margin: 14px 0 6px; }
h2.sec { border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-top: 20px; }
h3 { color: #8B1E1E; font-size: 8.8pt; margin: 14px 0 6px; }
h2, h3, p.plain { break-after: avoid; page-break-after: avoid; } table, .box { break-before: avoid-page; } h3.plain { color: #1b1b1b; }
p { margin: 5px 0; } p.plain { margin-top: 10px; } .dim { color: #666; } .mono { font-family: 'DejaVu Sans Mono', monospace; font-size: 7.6pt; }
ul, ol { margin: 4px 0 8px; padding-left: 18px; } li { margin: 3px 0; }
.box { border-left: 3px solid #8B1E1E; background: #FDF3F1; padding: 8px 12px; margin: 8px 0; }
.box:not(.red) { background: #FBF6F5; }
table { width: 100%; border-collapse: collapse; margin: 6px 0 10px; font-size: 7.6pt; page-break-inside: auto; }
th { background: #EFE9E4; text-align: left; padding: 6px 7px; border: 1px solid #d6cfc8; font-weight: 700; }
td { padding: 6px 7px; border: 1px solid #d6cfc8; vertical-align: top; }
tr { page-break-inside: avoid; } tbody tr:nth-child(even) td { background: #FAFAF8; }
table.stages td { font-size: 7.3pt; }
.chk { line-height: 1.8; }
"""


def main():
    cover = f"""<div class="cover"><div class="kick">VENTCOURSE · LIVE VENTILATION SIMULATION · SIMWARS FORMAT</div>
<h1>Two Children on the Ventilator</h1>
<div class="sub">Round 1 — The Wet Lung<br>Round 2 — The Quiet Chest</div><div class="rule"></div>
<div class="meta"><p><b>Scenario clock</b> 15:00 hard stop, both rounds · every stage fires on the clock</p>
<p><b>Round 1</b> 2-year-old girl, 10 kg · pneumonia to ARDS</p><p><b>Round 2</b> 5-year-old boy, 20 kg · life-threatening asthma</p>
<p><b>Screens</b> Facilitator panel · Ventilator · Patient monitor (one room code)</p>
<p><b>Confederates</b> Bedside nurse · Mother · PICU consultant (phone)</p><p><b>Judges</b> Clinical · CRM · Chief</p>
<p><b>Weighting</b> Clinical 40 · CRM 50 · Global Entrustment 10</p></div>
<div class="toc">Part I — Shared architecture and the clock<br>Part II — Round 1 packet · Part III — Round 2 packet<br>Part IV — Shared judge scoring model · Debrief · Production checklist</div></div>"""
    body = cover + part1() + round_packet(ROUNDS[0]) + round_packet(ROUNDS[1]) + scoring() + debrief() + checklist()
    # renumber the round packet sections to follow Part I (6.. in packet II, 9.. in packet III) — already numbered by n
    doc = f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>'
    hp = os.path.join(APP, 'tools', 'simwars_packet.html'); open(hp, 'w').write(doc)
    subprocess.run(['node', '-e', f"""
const {{ chromium }} = require('playwright');
(async () => {{ const b = await chromium.launch(); const p = await b.newPage(); await p.goto('file://{hp}');
 await p.pdf({{ path: {json.dumps(OUT)}, format: 'A4', printBackground: true, displayHeaderFooter: true,
  headerTemplate: '<span></span>', margin: {{ top: '18mm', bottom: '20mm', left: '16mm', right: '16mm' }},
  footerTemplate: '<div style="width:100%; margin:0 16mm; border-top:1px solid #333; padding-top:4px; font-family:DejaVu Sans; font-size:7px; color:#666; display:flex; justify-content:space-between;"><span>Live Ventilation Simulation | VentCourse · SimWars format</span><span><span class=pageNumber></span> / <span class=totalPages></span></span></div>' }});
 await b.close(); }})();"""], check=True, cwd=APP)
    print(OUT)


if __name__ == '__main__':
    main()
