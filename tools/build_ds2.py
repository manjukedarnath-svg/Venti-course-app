#!/usr/bin/env python3
"""Build the disease-specific ventilation talk, Part 2 (after ARDS): asthma, obstructive sleep apnoea, bronchiolitis, and
neuromuscular disease with home ventilation. One live case for each, run on the candidates' phones (room DS2).

    python3 tools/build_ds2.py      (then bundle for Present with tools/bundle.py)

Writes talks/disease-specific-2.html and adds its stages to the LIVE block in index.html.
Theory slides are reused from talks/disease-specific.html (Module 07), talks/niv.html and talks/long-term-ventilation.html;
the three new-evidence slides (asthma, OSA, bronchiolitis) are new (evidence checked 3 Nov 2026).

Live cases: asthma = sim scenario 02 stages 1 and 4 (orders in index.html), OSA = sim scenario 03, bronchiolitis = Anaya
(sim scenario 13), Duchenne = sim scenario 04.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_decks as bd
import build_niv as bn                     # patches bd.picture so the infant shows as a drawn figure
from talkkit import title, divider, bullets, table, figure, cards, e
import ds2figs as F
from deckdata import S, V
from nivdata import NIV_CASES

APP = bd.APP
DS, NIV, LTV, CP = 'disease-specific.html', 'niv.html', 'long-term-ventilation.html', 'cp-interactions.html'
for f in (DS, NIV, LTV, CP):
    bd.SRC[f] = open(os.path.join(APP, 'talks', f)).read()
CODE = 'DS2'
VENT = ['VENT']
bn._FIG.update({'sb1': ('child', 'bag'), 'sb4': ('child', 'ett')})   # drawn patient beside the monitor (no scene illustration yet)

# ------------------------------------------------------------------ case data -------------------------------------------
ASTHMA = [
  S(id='sb1', head='Intubated: the bag is <em>stiff</em>', eyebrow='Asthma · 5 years, 20 kg',
    scr=S(mode='VC', modeLong='VC · the ER settings', set=[['VT', '200'], ['RR', '24'], ['PEEP', '5'], ['Ti', '0.8'], ['FiO₂', '1.0']],
          meas=[['Peak', '49'], ['Auto-PEEP', '6'], ['pH', '7.24'], ['PaCO₂', '68']], wave='ds2-a1p',
          mon=[['HR', '160'], ['SpO₂', '88'], ['BP', '92/55'], ['EtCO₂', '54']], note='Hyperinflated, almost silent chest; the bag was stiff'),
    short=[['The ER settings: VT 200, rate 24, PEEP 5', 'Auto-PEEP 6, BP 78/44'], ['VT 140, rate 12, Ti 1.0, PEEP 4', 'Flow back to zero, BP 95/58'],
           ['PC 30 over 5, rate 20', 'VT shrinks as gas stacks'], ['Rate 30 for the CO₂', 'More trapping, CO₂ rises']],
    setq=S(ifaces=VENT, start=V('VENT', 'VC', vt=200, rr=24, pe=5, ti=0.8, o=100), ask='Set the ventilator'),
    after=S(mode='VC', modeLong='VC · slow and small', set=[['VT', '140'], ['RR', '12'], ['PEEP', '4'], ['Ti', '1.0'], ['FiO₂', '1.0']],
            meas=[['Plateau', '12'], ['Auto-PEEP', '1'], ['Te', '4 s'], ['PaCO₂', '78']], wave='ds2-a1f',
            mon=[['HR', '150'], ['SpO₂', '95'], ['BP', '95/58'], ['EtCO₂', '62']],
            happen='VT 140, rate 12, Ti 1.0 s: four seconds to breathe out',
            why='Time to empty, not pressure to fill. Accept the CO₂ while the pH is above 7.2.')),
  S(id='sb4', head='Hour 9: the alarm will not <em>stop</em>', eyebrow='Asthma · hour 9',
    scr=S(mode='VC', modeLong='VC · your settings', set=[['VT', '140'], ['RR', '12'], ['PEEP', '6'], ['Ti', '1.0'], ['FiO₂', '0.5']],
          meas=[['Peak', '> 50'], ['Plateau', '36'], ['PaCO₂', '95'], ['PaO₂', '48']], wave='ds2-a4p',
          mon=[['HR', '170'], ['SpO₂', '78'], ['BP', '70/40'], ['EtCO₂', '30']], note='Chest hyperexpanded and still; neck veins full'),
    short=[['Disconnect: let the chest empty', 'BP 92/55 in 40 s'], ['Needle the chest now', 'Makes the pneumothorax'],
           ['Bag at 40 a minute', 'Stacks more gas'], ['FiO₂ 1.0 and PEEP 10', 'BP 60/35']],
    setq=S(ifaces=VENT, start=V('VENT', 'VC', vt=140, rr=12, pe=6, ti=1.0, o=50), ask='Set the ventilator after your order'),
    after=S(mode='VC', modeLong='VC · restarted lower', set=[['VT', '120'], ['RR', '10'], ['PEEP', '0'], ['Ti', '1.0'], ['FiO₂', '0.5']],
            meas=[['Plateau', '9'], ['Auto-PEEP', '1'], ['Te', '5 s']], wave='ds2-a4f',
            mon=[['HR', '130'], ['SpO₂', '92'], ['BP', '92/55'], ['EtCO₂', '48']],
            happen='Disconnected; chest fell, BP back in 40 s; sliding on both sides; restarted at rate 10, VT 120',
            why='In asthma, stacked breaths are the cause that comes first. Disconnect, then DOPE.')),
]


def renamed(d, eyebrow, **k):
    x = dict(d); x['eyebrow'] = eyebrow; x.update(k)
    return x


_NB = {d['id']: d for d in NIV_CASES}
_LTV2 = {d['id']: d for d in bd.LTV2}
ALL = ['MASK', 'HFNC', 'NIV', 'VENT']
OSA = [renamed(bd._BY['so1'], 'OSA · 3 years, 14 kg', setq=S(ifaces=ALL, start=V('MASK', 'Mask', l=10))),
       renamed(bd._BY['so2'], 'OSA · night one', setq=S(ifaces=['NIV', 'VENT'], start=V('NIV', 'CPAP', cp=8, o=30)))]
BRONCH = [renamed(_NB['nb1'], 'Bronchiolitis · 3 months, 5 kg'), renamed(_NB['nb2'], 'Bronchiolitis · night one')]
NMD = [renamed(_LTV2['sd1'], 'Duchenne · 15 years, 45 kg'), renamed(bd._BY['sd2'], 'Duchenne · night two', setq=S(ifaces=['NIV', 'VENT'], start=V('NIV', 'ST', ip=16, ep=5, br=14, ti=1.2, o=30)))]


# ------------------------------------------------------------------ new slides ------------------------------------------
def evidence(label, h, rows, notes):
    return table(label, h, "New evidence · 2017–2026", ['Source', 'What it found', 'At the bedside'], rows, notes, widths=['27%', '43%', '30%'], size=26)


EV_ASTHMA = evidence('Asthma · new evidence', 'Asthma: what the new <em>evidence</em> says', [
    ['GINA 2026<br><span style="font-size:20px; color:var(--text-secondary);">May 2026</span>', 'SABA-only reliever dropped for ages 6–11; ICS–formoterol an option for a mild attack from age 6', 'Check the reliever before discharge'],
    ['Abu-Sultaneh · Pediatr Pulmonol 2025<br><span style="font-size:20px; color:var(--text-secondary);">network meta-analysis · 12 RCTs · 852 children</span>', 'IV magnesium ranked first: shorter hospital and ICU stay, fewer ICU admissions', 'Magnesium is the first IV adjunct'],
    ['WHO reviews · Arch Dis Child 2025<br><span style="font-size:20px; color:var(--text-secondary);">2 × 9 RCTs</span>', 'Magnesium: fewer admissions (RR 0.70), less NIV. Aminophylline: more vomiting, no shorter stay', 'Aminophylline last, with an antiemetic'],
    ['Rogerson · Pediatr Pulmonol 2024<br><span style="font-size:20px; color:var(--text-secondary);">443 matched pairs</span>', 'High-flow: slower improvement, PICU stay 1.5 vs 1.2 days (observational)', 'HFNC and NIV are a bridge with a deadline']],
    'Four pieces of new evidence. GINA 2026 removes SABA-only relievers for six to eleven year olds. The 2025 network meta-analysis of twelve trials ranks intravenous magnesium first as the add-on. The two WHO-commissioned reviews agree on magnesium and find aminophylline mostly adds nausea and vomiting. And a large matched study found high-flow in asthma was associated with slower improvement and a longer PICU stay: observational, but there is still no trial showing that high-flow changes the course of asthma. Certainty for all of these is low.')

EV_OSA = evidence('OSA · new evidence', 'OSA: who comes to the <em>PICU</em>', [
    ['AAO-HNS tonsillectomy guideline 2019', 'PSG first if under 2, obese, Down syndrome, craniofacial, neuromuscular, sickle cell, MPS. Inpatient monitoring if under 3 or severe OSA. No codeine', 'Know the high-risk list'],
    ['AAP OSAS guideline 2012', 'Admit high-risk children after surgery: abnormal baseline PSG, complications of OSA, obesity', 'Monitored bed, CPAP ready'],
    ['ATS guideline 2024 · Ehsan, AJRCCM', 'Persistent OSA after surgery (obstructive AHI > 1): CPAP, weight, sleep endoscopy-directed surgery, montelukast with a nasal steroid. All conditional', 'Persistent OSA: think Down syndrome, obesity'],
    ['PATS trial · JAMA 2023<br><span style="font-size:20px; color:var(--text-secondary);">459 children, mild sleep-disordered breathing</span>', 'Surgery did not improve attention or executive function; it did improve behaviour, symptoms and quality of life', 'Mild disease: not every child needs the knife']],
    'Who reaches the PICU after the tonsils. The 2019 AAO-HNS guideline asks for a sleep study first in the high-risk groups and inpatient monitoring for children under three or with severe OSA, and says no codeine. The AAP 2012 guideline lists the high-risk children to admit. The 2024 ATS guideline covers the child who still obstructs after surgery: CPAP, weight, endoscopy-directed surgery and montelukast with a nasal steroid, all conditional. And the PATS trial showed that in mild sleep-disordered breathing surgery helps behaviour and symptoms but not attention.')

EV_BRONCH = evidence('Bronchiolitis · new evidence', 'Bronchiolitis: the 2025 <em>guideline</em>', [
    ['Australasian guideline 2025 · PREDICT', 'Oxygen if SpO₂ persistently < 90% (< 92% under 6 weeks or with a comorbidity). High-flow only after low-flow fails (no better in 4–5 h). CPAP for impending failure', 'Escalate on the child, not one number'],
    ['TRAMONTANE · Intensive Care Med 2017<br><span style="font-size:20px; color:var(--text-secondary);">142 infants under 6 months</span>', 'High-flow 2 L/kg/min was not non-inferior to CPAP 7 as the first support', 'The sicker infant: CPAP'],
    ['FIRST-ABC Step-Up · JAMA 2022<br><span style="font-size:20px; color:var(--text-secondary);">600 children, half bronchiolitis</span>', 'High-flow non-inferior to CPAP 7–8 for time to liberation; intubation 15% in both', 'High-flow first is reasonable'],
    ['RSV prevention · 2025 guideline', 'Consider nirsevimab for high-risk infants or for all; consider the maternal RSV vaccine', 'Ask about it in the history']],
    'Bronchiolitis. The 2025 Australasian guideline lowers the oxygen threshold to ninety per cent, ninety-two under six weeks or with a comorbidity, uses high-flow only after low-flow oxygen has failed, and keeps CPAP for impending failure. TRAMONTANE found CPAP better than high-flow as the first support in young infants with moderate to severe bronchiolitis; FIRST-ABC Step-Up, across all PICU children, found high-flow non-inferior. Read together: high-flow first is reasonable, CPAP for the sicker, younger infant. And RSV prevention, nirsevimab and the maternal vaccine, is changing who we see.')


# ------------------------------------------------------------------ added 3 Nov: hyperinflation, BP, Tasker -------------
DHI = figure('Dynamic hyperinflation · why it happens', 'Why the lung cannot <em>empty</em>', 'Dynamic hyperinflation', F.fig_dhi(),
             'Why it happens. On the left, one breath going out. Passive expiration is exponential: after one time constant, resistance times compliance, 37 per cent of the breath is still in the lung; after three, 5 per cent. In asthma the resistance is high, so the time constant is long. If the next breath arrives at one and a half time constants, 22 per cent of the last breath is still inside. On the right, breath after breath: each one starts from a higher volume, until the volume trapped is large enough that the faster flow out at that volume lets each breath out equal each breath in. That new end-expiratory volume above FRC is the trapped volume, and divided by compliance it is the auto-PEEP. Bigger breaths, a faster rate, a longer Ti or more resistance all raise it; only time to breathe out lowers it.')
DHI_FIX = cards('Dynamic hyperinflation · what drives it', 'What raises the trapped <em>volume</em>', 'Dynamic hyperinflation',
                [('VT', ['Bigger breath, more left behind']), ('Rate', ['Less time to breathe out']), ('Ti', ['Takes time from expiration']), ('R', ['Longer time constant'])],
                'The trapped volume rises with the tidal volume, the rate, the inspiratory time and the resistance. The fix is the same four in reverse: a smaller breath, a slower rate, a short inspiration with a fast flow, and bronchodilators for the resistance. PEEP does not empty the lung. Expiratory time is the treatment; check that the flow trace returns to zero.', size=34)
BP_ASTHMA = figure('Asthma · why the BP falls', 'Why the blood pressure <em>falls</em> in asthma', 'Heart–lung interaction', F.fig_bp_asthma(),
                   'The heart–lung interaction in asthma. Top row: trapped gas keeps the chest full; pleural and right atrial pressure rise, venous return falls, preload and blood pressure fall. Middle row: a lung near total lung capacity squeezes the alveolar vessels, so pulmonary vascular resistance rises; the right ventricle dilates and pushes the septum into the left, which fills less. Bottom row, before the tube: huge negative pleural swings raise left ventricular afterload and fill the right heart more in inspiration, which is pulsus paradoxus. After the tube, sedation removes the sympathetic drive, positive pressure adds to the trapping and the child is dry: the crash comes in minutes. Disconnect first, then fluid, then a slower rate and smaller breaths, then a vasopressor.')

TASKER_SRC = 'Tasker · Rimensberger 2015, ch. 50'
TASKER_TABLE = table('Bronchiolitis · Tasker mechanics', 'Four lungs in a 5 kg <em>infant</em>', TASKER_SRC,
                     ['Lung', 'Compliance mL/cmH₂O', 'Resistance cmH₂O/mL/s', 'Time constant', 'What it means'],
                     [['Control', '5.0', '0.06', '0.30 s', 'Empties easily at rate 30'],
                      ['Bronchiolitis<br><span style="font-size:20px; color:var(--text-secondary);">Derish 1998 · 25 cases</span>', '2.8', '0.08', '0.23 s', 'Compliance halves; resistance near normal'],
                      ['Obstructive<br><span style="font-size:20px; color:var(--text-secondary);">Hammer 1997 · 27 cases</span>', '2.85', '0.37', '1.05 s', 'Compliance down and resistance ×6: traps at rate 30'],
                      ['Restrictive<br><span style="font-size:20px; color:var(--text-secondary);">Hammer 1997 · ARDS pattern</span>', '1.9', '0.10', '0.19 s', 'About 1 in 5 ventilated: stiff, empties fast, needs PEEP']],
                     'Tasker models a five-kilogram infant from published mechanics. Controls: compliance 5 mL per cmH2O, resistance 0.06, time constant 0.3 seconds. Unselected ventilated bronchiolitis, from Derish: compliance falls to 2.8, but resistance is barely raised, so the time constant is actually shorter. The more severe obstructive cases in Hammer\'s series have the same low compliance plus six times the resistance: a time constant over a second. And about one in five ventilated infants has a restrictive, ARDS-like lung: compliance 1.9, time constant 0.19 seconds, and two weeks or more on the ventilator.',
                     widths=['24%', '15%', '15%', '13%', '33%'], size=26)
TASKER_WHY = bullets('Bronchiolitis · compliance not resistance', 'A stiff lung more than a narrow <em>airway</em>', TASKER_SRC,
                     ['Compliance falls by half; measured resistance is often near normal (Otis: equal time constants)',
                      'Fast, shallow breathing saves elastic work when compliance is low',
                      'Exhaustion: hyperinflation puts the diaphragm at a mechanical disadvantage',
                      'Ventilated infants: 73% of the pressure is elastic, 22% resistive, 5% auto-PEEP (Cruces 2017)',
                      '<span style="color:var(--text-accent);">The same child can show both patterns: which predominates depends on the infant\'s drive and the physiology of the airway and terminal bronchioles</span>'],
                     'The same infant can move between both patterns; which predominates depends on the infant\'s respiratory drive and on the airway and terminal bronchioles. Tasker\'s point: we expect bronchiolitis to be a resistance disease, but infants do not prolong expiration, and measured non-elastic resistance is often near normal. When flow is fast through unequally obstructed airways, the resistance you measure is that of the larger pathways: Otis\'s equality of time constants. What is consistently abnormal is compliance, halved by inflammation, fast breathing and above all hyperinflation. Rapid shallow breathing is the economical answer to a stiff lung. The infant tires not because the work is extreme but because a hyperinflated chest leaves the diaphragm flat and unable to shorten. Cruces and colleagues confirmed it in 16 ventilated infants in 2017: almost three quarters of the working pressure was elastic, a fifth resistive, and auto-PEEP only 5 per cent; inspiratory and expiratory time constants were equal, 0.18 seconds.', size=34)
TASKER_FIG = figure('Bronchiolitis · Tasker curves', 'Same ventilator, four <em>lungs</em>', TASKER_SRC + ' · recalculated', F.fig_tasker(),
                    'Tasker\'s inflation and deflation curves, recalculated here for a five-kilogram infant on pressure control with passive expiration. The control lung fills to 8 mL per kg in a Ti of 0.21 seconds. In bronchiolitis, with compliance halved, the same pressure needs a Ti of 0.5 seconds to reach 8 mL per kg, and PaCO2 is about 46. The trap: answering that CO2 with more pressure and a faster rate gives 10 mL per kg and a PaCO2 of 31, overventilation. In the obstructive lung, time constant a second, rate 30 leaves gas behind at end-expiration and the tidal volume is under 4 mL per kg: PaCO2 about 109. Slowing to 20 with a Ti of one second, the dashed line, improves the tidal volume: PaCO2 93, still high, but heading the right way. The restrictive lung empties fast; it needs PEEP and recruitment, not time.')
TASKER_PLAN = cards('Bronchiolitis · ventilate the phenotype', 'Ventilate the <em>phenotype</em>', TASKER_SRC,
                    [('Targets', ['SpO₂ > 88%, PaO₂ > 60, any PaCO₂ with pH > 7.25']), ('Volume', ['VT 6–8 mL/kg; do not chase the CO₂']),
                     ('Obstructive', ['Rate under 30, slower (10–15) with a long expiration']), ('Restrictive', ['MAP > 10 and AaDO₂ > 400 in 48 h: recruit with PEEP, VT < 8'])],
                    'Tasker\'s two guiding principles. Adequate, not normal, gases: oxygen above 60, saturation above 88, and any CO2 that keeps the pH above 7.25. And no overdistension of a hyperinflated lung: tidal volume 6 to 8 mL per kg, the rate under 30, and in the obstructive child as slow as 10 to 15 with a long expiration. If the mean airway pressure is above 10 and the alveolar–arterial gradient above 400 in the first 48 hours, think restrictive disease or ARDS, about one ventilated infant in five, and recruit with PEEP. Uncomplicated cases need 4 to 5 days on the ventilator; longer means another process, often bacterial co-infection.', size=32)


def debrief(lab, h, cs, notes):
    return bd.cards_slide(lab, lab, h, cs, notes)


# ------------------------------------------------------------------ the talk --------------------------------------------
def build():
    r = bd.reuse
    out = bd.title_slide('VentCourse · Module 07 · Disease-specific ventilation · Part 2', 'After ARDS: the <em>other</em> lungs',
                         'Asthma, OSA, bronchiolitis, the weak pump and home. Four children, live on your phones.',
                         'Part two of disease-specific ventilation. Part one was the small, stiff lung of ARDS. Today four other lungs: the full lung of asthma, the airway that closes in sleep, the infant whose bronchiolitis changes from day to day, and the strong lung with a weak pump that may go home on a ventilator. One child for each, run live on your phones.')
    out += bd.join_slide(CODE, 'Scan the code to join; no account needed. Or open the app, tap Live session and type DS2.')
    out += bullets('Plan', 'Four <em>lungs</em>', 'Today',
                   ['1 · Asthma: the full lung', '2 · OSA: the closing airway', '3 · Bronchiolitis: which day is it?', '4 · Neuromuscular disease: the weak pump, and home'],
                   'Four parts, one child each. Asthma, where the lung cannot empty. OSA, where the airway closes in sleep. Bronchiolitis, obstructive on day one and stiff by day four. And neuromuscular disease, a normal lung with a failing pump, which takes us to home ventilation.', size=48)

    # 1 · asthma
    out += divider('Part 1', 'Part 1 · Asthma', 'The <em>full</em> lung', 'Time to empty, not pressure to fill',
                   'Asthma: the lung that cannot empty. Every setting is about expiratory time.')
    for t in ['Time constant', 'Expiration']:
        out += r(DS, t)
    out += DHI + r(DS, 'Dynamic hyperinflation') + DHI_FIX
    for t in ['Measure it', 'Asthma on screen', 'When to intubate', 'Before the tube']:
        out += r(DS, t)
    out += bn.opener_fig('ds2_asthma', 'Case 1 of 4', 'Arjun, <em>5 years</em>', ['20 kg · known asthma, rarely takes his preventer', 'Silent chest after nebulisers, magnesium and steroids; just intubated'], 'child', 'bag',
                         'A five-year-old, twenty kilos, known asthma, rarely takes his preventer. Two days of wheeze; three salbutamol nebulisers, ipratropium, hydrocortisone and magnesium, then drowsy with a silent chest. Just intubated with ketamine and rocuronium, and the bag is stiff. History only: set the ventilator on your phones.')
    out += bd.stage_slides(ASTHMA[0], CODE)
    for t in ['Initial settings', 'PC in asthma', 'Fixing auto-PEEP', 'PEEP in asthma', 'Hypotension']:
        out += r(DS, t)
    out += BP_ASTHMA + r(CP, 'Pulsus paradoxus')
    out += bd.stage_slides(ASTHMA[1], CODE)
    out += r(DS, 'Drugs') + EV_ASTHMA
    out += debrief('Arjun · debrief', 'Let the lung <em>empty</em>',
                   [('Set it', ['VT 6–8 mL/kg', 'Rate 10–14, Te ≥ 4 s']), ('Accept', ['pH above 7.2', 'Plateau under 30']), ('Crash', ['Disconnect first', 'Then DOPE']), ('Adjuncts', ['Magnesium first', 'Ketamine, salbutamol in circuit'])],
                   'Small breaths, a slow rate and a long expiration; accept the CO2 while the pH holds above 7.2 and the plateau stays under 30. When he crashes, disconnect first: stacked breaths come before DOPE. Magnesium is the best-supported intravenous adjunct. Arjun is sim scenario 02 in the app.')
    out += r(DS, 'Quiz 3') + r(DS, 'Quiz 3 · answer')

    # 2 · OSA
    out += divider('Part 2', 'Part 2 · Obstructive sleep apnoea', 'The <em>closing</em> airway', 'A tube that collapses in sleep',
                   'Obstructive sleep apnoea: a normal lung behind an airway that collapses when the child sleeps.')
    out += r(DS, 'OSA') + r(DS, 'OSA numbers')
    out += bd.opener('ds2_osa', 'Case 2 of 4', 'Aarav, <em>3 years</em>', ['14 kg · severe OSA, adenotonsillectomy today', 'Extubated in recovery; obstructing on the ward'], 'rapid1_aarav_osa',
                     'Aarav, three years, fourteen kilos, severe OSA on his sleep study, adenotonsillectomy this morning. Extubated in recovery; now on the ward, snoring, then silent, with paradoxical breathing. History only: choose the support on your phones.', CODE)
    for d in OSA:
        out += bd.stage_slides(d, CODE)
    out += r(LTV, 'Home modes') + EV_OSA
    out += debrief('Aarav · debrief', 'Open the airway, then <em>ventilate</em>',
                   [('Night one', ['Under 3, severe, syndromes', 'Monitored bed']), ('Obstructing', ['CPAP 8–10', 'Not oxygen alone']), ('REM', ['Bilevel ST, backup rate', 'Stop the morphine']), ('After', ['Persistent OSA', 'Sleep study, CPAP'])],
                   'The first night after the tonsils is the risk: children under three, severe OSA and the syndromes go to a monitored bed. Obstruction needs CPAP, not more oxygen. In REM sleep, on opioids, he stops breathing as well as obstructing: EPAP keeps the airway open, IPAP minus EPAP and a backup rate ventilate. Aarav is sim scenario 03 in the app.')

    # 3 · bronchiolitis
    out += divider('Part 3', 'Part 3 · Bronchiolitis', 'Which <em>day</em> is it?', 'Obstructed first, stiff later',
                   'Bronchiolitis: obstructive on day one, stiff by day four. The support follows the day.')
    out += r(DS, 'Bronchiolitis phases') + TASKER_TABLE + TASKER_WHY + TASKER_FIG + TASKER_PLAN + r(DS, 'Bronchiolitis traces') + r(DS, 'Bronchiolitis support')
    key, name, lines, age, sup, notes = bn.OPENERS['nb1']
    out += bn.opener_fig(key, 'Case 3 of 4', name, lines, age, sup, notes)
    out += bd.stage_slides(BRONCH[0], CODE)
    out += r(NIV, 'High-flow or CPAP')
    out += bd.stage_slides(BRONCH[1], CODE)
    out += EV_BRONCH
    lab, eb, h, cs, notes = bn.DEBRIEF['nb2']
    out += bd.cards_slide(lab, lab, h, cs, notes)

    # 4 · neuromuscular disease and home ventilation
    out += divider('Part 4', 'Part 4 · Neuromuscular disease and home ventilation', 'The <em>weak</em> pump', 'A normal lung, failing muscles, and the road home',
                   'Neuromuscular disease: the lung is normal, the pump is not. Night comes first, and many of these children go home on the ventilator.')
    for t in ['Weak pump', 'Neuromuscular thresholds', 'Neuromuscular settings']:
        out += r(DS, t)
    for t in ['Drive, pump, load', 'Night comes first', 'Duchenne']:
        out += r(LTV, t)
    out += bd.opener('ds2_dmd', 'Case 4 of 4', 'Rohan, <em>15 years</em>', ['45 kg · Duchenne, off his feet for 4 years', 'Months of morning headaches; drowsy today'], 'rapid2_rohan_duchenne',
                     'Rohan, fifteen, forty-five kilos, Duchenne, in a wheelchair for four years. Months of morning headaches and poor sleep; today he is drowsy and on two litres of oxygen. History only: set the support on your phones.', CODE)
    out += bd.stage_slides(NMD[0], CODE)
    for t in ['S, ST, T', 'Setting bilevel', 'Volume target']:
        out += r(LTV, t)
    out += bd.stage_slides(NMD[1], CODE)
    for t in ['Interfaces', 'Ready to step down', 'Home equipment', 'The prescription', 'The risks']:
        out += r(LTV, t)
    out += debrief('Rohan · debrief', 'Ventilate the <em>night</em>',
                   [('Spot it', ['Morning headache, poor sleep', 'Daytime CO₂ comes last']), ('Support', ['Bilevel ST, big IPAP − EPAP', 'Backup rate, cough assist']), ('Not oxygen', ['Oxygen alone', 'raises the CO₂']), ('Home', ['A mask that fits, chin strap', 'Trained carers, a written plan'])],
                   'Hypoventilation starts at night: morning headaches and poor sleep come years before a daytime CO2. Oxygen alone drives the CO2 up. Bilevel ST with a big pressure difference and a backup rate, cough assist twice a day, and a mask that seals. Home needs trained carers, the right machine and a written prescription. Rohan is sim scenario 04 in the app.')

    # close
    out += r(DS, 'Side by side') + r(DS, 'DOPE-S')
    out += bullets('Takeaways', 'Take <em>home</em>', 'Four lines',
                   ['Asthma: slow, small, long expiration; disconnect first', 'OSA: CPAP opens the airway; IPAP − EPAP ventilates', 'Bronchiolitis: which day is it? High-flow, then CPAP', 'Weak pump: ventilate the night, never oxygen alone'],
                   'Four lines. Asthma: a slow rate, small breaths, a long expiration, and when it crashes disconnect first. OSA: CPAP opens the airway, the pressure difference and a backup rate ventilate. Bronchiolitis: ask which day it is; high-flow, then CPAP for the sicker infant. The weak pump: ventilate the night, and never give oxygen alone.', size=44)
    out += bd.close_slide('Which lung do you have <em>today</em>?', 'All four children are in the app: Cases · Sim scenarios 02, 03, 04 and 13. The theory is Learn · Modules 07 and 09.',
                          'Four lungs, one question: which lung do you have today? Arjun, Aarav, Anaya and Rohan are all in the app as simulator scenarios. Thank you.', 'Disease-specific ventilation · Part 2')
    out += bd.appendix(DS, 'Part 5', 'Side by side', drop=('Title', 'Join', 'Close', 'Try it', 'Thank you', 'Part 5', 'Part 6', 'Part 7', 'Part 8', 'Part 9', 'Part 10', 'Part 11'))
    return bd.shell('Disease-specific ventilation · Part 2', out, CODE)


if __name__ == '__main__':
    bd.USED.clear()
    deck = build()
    open(os.path.join(APP, 'talks', 'disease-specific-2.html'), 'w').write(deck)
    print('disease-specific-2.html', len(deck), deck.count('<section '), 'slides')
    ids = {d['id'] for d in ASTHMA + OSA + BRONCH + NMD}
    keep = {k: v for k, v in bd.LIVE_OUT.items() if k.split('_r')[0] in ids or k in ('ds2_asthma', 'ds2_osa', 'ds2_dmd', 'anaya_case') or re.match(r'xds2\d+$', k)}
    bn.write_live(keep)
    print('LIVE entries written', len(keep))
