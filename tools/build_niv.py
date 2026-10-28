#!/usr/bin/env python3
"""Build the NIV talks (Module 04) and the joint NIV + long-term ventilation case talk.

    python3 tools/build_niv.py      (then bundle for Present with tools/bundle.py)

Writes:
  talks/niv.html        the full NIV talk: five parts, quizzes, native SVG figures, speaker notes (theory source)
  talks/niv-cases.html  three NIV cases at the bedside, live room NIV (sim scenarios 13–15), theory woven in
  talks/niv-ltv.html    the three NIV cases, then the five long-term ventilation cases, live room NLV
and adds the NIV stages to the LIVE block in index.html.

Sources: Chang ch. 7; Tobin 3e ch. 16–18 (Hill); Rabec, Thorax 2011 (modes); Cammarota, Front Med 2022 (comfort);
Tonelli, AJRCCM 2020 (oesophageal pressure); PEMVECC, Intensive Care Med 2017; BPICC manual, Pedicriticon 2026, ch. 6–7.
"""
import os, re, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_decks as bd
from talkkit import (title, divider, bullets, numbers, cards, two, table, figure, quiz, ending, head,
                     ln, pth, poly, rc, circ, tx, axes, e, MONO)
from nivdata import NIV_CASES

APP = bd.APP
SRC_LTV = 'long-term-ventilation.html'


# ------------------------------------------------------------------ figures ---------------------------------------------
def fig_ladder():
    steps = [('Low-flow', 'Cannula, mask', 'FiO₂ varies'), ('High-flow', '2 L/kg/min', 'Set FiO₂'), ('CPAP', '6–8 cmH₂O', 'One set pressure'),
             ('Bilevel', 'IPAP / EPAP', 'Plus a breath'), ('Tube', 'Invasive', 'When NIV fails')]
    out = ''
    for i, (a, b, c) in enumerate(steps):
        x = 80 + i * 310
        y = 560 - i * 105
        acc = i in (1, 2, 3)
        out += rc(x, y, 280, 760 - y - 60, fill='var(--surface-raised, transparent)' if not acc else 'color-mix(in oklab, var(--text-accent) 9%, transparent)',
                  c='var(--text-accent)' if acc else 'var(--text-primary)', sw=3 if acc else 2, r=4)
        out += tx(x + 24, y + 62, a, 46, 'var(--text-primary)', font='disp')
        out += tx(x + 24, y + 104, b, 24, 'var(--text-accent)' if acc else 'var(--text-secondary)')
        out += tx(x + 24, y + 142, c, 24, 'var(--text-secondary)', font='body')
    out += ln(80, 60, 1580, 60, arrow='arr', w=3) + tx(80, 40, 'More support, more risk', 24, 'var(--text-secondary)')
    out += tx(1580, 40, 'Reassess at every step: 1–2 hours', 24, 'var(--text-accent)', anchor='end')
    return out


def fig_flow_demand():
    X0, X1, Y0, Y1 = 180, 1560, 640, 90
    xm = lambda t: X0 + (X1 - X0) * t / 2.0
    ym = lambda f: Y0 - (Y0 - Y1) * f / 40.0
    out = axes(X0, Y0, X1, Y1, 'Time · one breath (s)', 'Flow L/min', yticks=[0, 10, 20, 30, 40], xticks=[(0, '0'), (0.5, '0.5'), (1, '1.0'), (1.5, '1.5'), (2, '2.0')], ymap=ym, xmap=xm)
    import math
    pts = [(xm(t), ym(28 * math.sin(math.pi * t / 0.8))) for t in [i / 100 for i in range(0, 81)]] + [(xm(0.8), ym(0)), (xm(2.0), ym(0))]
    out += poly(pts, w=5)
    out += tx(xm(0.4), ym(31), 'The child&#x27;s inspiratory flow', 26, 'var(--text-primary)', 'middle', 'body')
    out += ln(xm(0), ym(4), xm(2), ym(4), 'var(--danger)', 4, dash='14 10') + tx(xm(1.95), ym(4) - 16, 'Low-flow 4 L/min', 24, 'var(--danger)', 'end')
    out += ln(xm(0), ym(34), xm(2), ym(34), 'var(--text-accent)', 5) + tx(xm(1.95), ym(34) - 16, 'High-flow above the peak', 24, 'var(--text-accent)', 'end')
    out += rc(xm(0.12), ym(25), xm(0.68) - xm(0.12), ym(4) - ym(25), fill='color-mix(in oklab, var(--danger) 12%, transparent)', c='none', sw=0)
    out += tx(xm(0.4), ym(14), 'Room air drawn in: FiO₂ falls', 24, 'var(--danger)', 'middle', 'body')
    out += tx(xm(1.4), ym(20), 'Above demand: no room air,', 26, 'var(--text-primary)', 'middle', 'body')
    out += tx(xm(1.4), ym(20) + 36, 'the set FiO₂ is the FiO₂ she gets', 26, 'var(--text-primary)', 'middle', 'body')
    return out


def fig_prongs():
    out = ''
    for cx, lab, ok in [(480, 'Right', True), (1200, 'Wrong', False)]:
        out += f'<ellipse cx="{cx - 110}" cy="360" rx="95" ry="130" fill="none" stroke="var(--text-primary)" stroke-width="3"/>'
        out += f'<ellipse cx="{cx + 110}" cy="360" rx="95" ry="130" fill="none" stroke="var(--text-primary)" stroke-width="3"/>'
        r = 52 if ok else 92
        col = 'var(--text-accent)' if ok else 'var(--danger)'
        out += circ(cx - 110, 360, r, f'color-mix(in oklab, {col} 25%, transparent)', col, 4)
        out += circ(cx + 110, 360, r, f'color-mix(in oklab, {col} 25%, transparent)', col, 4)
        out += tx(cx, 560, lab, 48, col, 'middle', 'disp')
        out += tx(cx, 610, 'Visible gap · gas escapes in expiration' if ok else 'Fills the nostril · no way out', 26, 'var(--text-secondary)', 'middle', 'body')
    out += tx(840, 120, 'Seen from below: two nostrils, two prongs', 26, 'var(--text-secondary)', 'middle')
    out += tx(840, 690, 'About 2 mm from the septum · never cut to fit · nasal care every 4 hours', 26, 'var(--text-primary)', 'middle', 'body')
    return out


def fig_ipap_epap():
    X0, X1, Y0, Y1 = 200, 1500, 620, 100
    ym = lambda p: Y0 - (Y0 - Y1) * p / 20
    out = axes(X0, Y0, X1, Y1, '', 'Mask pressure cmH₂O', yticks=[0, 5, 10, 15, 20], ymap=ym)
    d = []
    x = X0
    for k in range(3):
        d += [(x, ym(6)), (x + 60, ym(6)), (x + 100, ym(14)), (x + 300, ym(14)), (x + 330, ym(6)), (x + 430, ym(6))]
        x += 430
    out += poly(d, w=5)
    out += ln(X0, ym(6), X1, ym(6), 'var(--text-accent)', 2, dash='6 8')
    out += tx(X1 + 20, ym(6) + 8, 'EPAP 6', 28, 'var(--text-accent)')
    out += tx(X1 + 20, ym(14) + 8, 'IPAP 14', 28, 'var(--text-primary)')
    bx = X0 + 430 + 380
    out += ln(bx, ym(6), bx, ym(14), 'var(--text-accent)', 4, arrow='arra') + ln(bx, ym(14), bx, ym(6), 'var(--text-accent)', 4, arrow='arra')
    out += ln(bx - 30, ym(14), bx + 30, ym(14), 'var(--text-accent)', 2, dash='4 6')
    out += tx(bx, ym(16), 'Support = IPAP − EPAP = 8', 28, 'var(--text-accent)', 'middle', 'body')
    out += tx(X0 + 40, ym(3), 'EPAP: holds alveoli and the upper airway open → oxygen, obstruction', 26, 'var(--text-primary)', font='body')
    out += tx(X0 + 40, ym(18.5), 'IPAP − EPAP: helps every breath → CO₂, work of breathing', 26, 'var(--text-primary)', font='body')
    return out


def fig_circuit():
    out = ''
    # single limb
    out += tx(80, 90, 'Single limb · intentional leak', 30, 'var(--text-accent)')
    out += rc(80, 140, 200, 140, c='var(--text-primary)', sw=3, r=10) + tx(180, 222, 'Blower', 26, 'var(--text-primary)', 'middle', 'body')
    out += pth('M280,210 C420,210 470,210 600,210', w=6)
    out += f'<ellipse cx="660" cy="210" rx="60" ry="70" fill="none" stroke="var(--text-primary)" stroke-width="3"/>' + tx(660, 320, 'Mask', 24, anchor='middle')
    for k in range(4):
        out += ln(700 + k * 6, 160 + k * 4, 760 + k * 14, 120 + k * 10, 'var(--text-accent)', 3, arrow='arra')
    out += tx(800, 120, 'Port in the mask: CO₂ flushed out', 24, 'var(--text-accent)', font='body')
    out += tx(80, 380, 'One tube: exhaled gas washes back up it unless EPAP keeps a flow going.', 26, 'var(--text-primary)', font='body')
    out += tx(80, 420, 'EPAP at least 4 cmH₂O · port in the mask beats port in the circuit.', 26, 'var(--text-primary)', font='body')
    # dual limb
    y = 470
    out += tx(80, y + 20, 'Dual limb · ICU ventilator', 30, 'var(--text-primary)')
    out += rc(80, y + 60, 200, 140, sw=3, r=10) + tx(180, y + 142, 'Ventilator', 26, 'var(--text-primary)', 'middle', 'body')
    out += pth(f'M280,{y + 100} C420,{y + 100} 470,{y + 110} 600,{y + 120}', w=6, arrow='arr')
    out += pth(f'M600,{y + 160} C470,{y + 170} 420,{y + 180} 280,{y + 180}', w=6, arrow='arr')
    out += f'<ellipse cx="660" cy="{y + 140}" rx="60" ry="70" fill="none" stroke="var(--text-primary)" stroke-width="3"/>'
    out += tx(800, y + 130, 'Expiratory valve: no rebreathing', 24, 'var(--text-primary)', font='body')
    out += tx(800, y + 170, 'Blender: any FiO₂ to 1.0', 24, 'var(--text-primary)', font='body')
    out += rc(1160, 140, 440, 330, c='var(--text-accent)', sw=2, r=4)
    out += tx(1190, 200, 'Oxygen bled into', 28, 'var(--text-accent)', font='body') + tx(1190, 240, 'a home bilevel', 28, 'var(--text-accent)', font='body')
    out += tx(1190, 340, '≈ 0.45–0.5', 76, 'var(--text-accent)', font='disp') + tx(1190, 400, 'Maximum FiO₂', 24)
    out += tx(1190, 440, 'Hypoxaemia: use an ICU ventilator', 22, 'var(--text-primary)', font='body')
    return out


def fig_leak_cycle():
    X0, X1, Y0, Y1 = 180, 1520, 620, 110
    xm = lambda t: X0 + (X1 - X0) * t / 2.0
    ym = lambda f: Y0 - (Y0 - Y1) * f / 60
    out = axes(X0, Y0, X1, Y1, 'Time (s)', 'Inspiratory flow L/min', yticks=[0, 20, 40, 60], xticks=[(0, '0'), (0.5, '0.5'), (1, '1.0'), (1.5, '1.5'), (2, '2.0')], ymap=ym, xmap=xm)
    import math
    nol = [(xm(t), ym(55 * math.exp(-t / 0.28))) for t in [i / 100 for i in range(0, 46)]]
    out += poly(nol, w=5)
    tcyc = 0.28 * math.log(4)
    out += ln(xm(tcyc), ym(13.75), xm(tcyc), Y0, 'var(--text-primary)', 2, dash='4 6')
    out += tx(xm(tcyc) + 12, ym(18), 'Cycles at 25% of peak', 24, 'var(--text-primary)', font='body')
    lk = [(xm(t), ym(22 + 33 * math.exp(-t / 0.28))) for t in [i / 100 for i in range(0, 151)]]
    out += poly(lk, c='var(--danger)', w=5)
    out += ln(X0, ym(13.75), X1, ym(13.75), 'var(--text-secondary)', 2, dash='14 10') + tx(X1, ym(13.75) - 12, 'Cycle threshold', 22, anchor='end')
    out += ln(xm(1.5), Y1, xm(1.5), Y0, 'var(--danger)', 3, dash='4 6') + tx(xm(1.5) + 14, Y1 + 30, 'Ti max cuts it off', 26, 'var(--danger)', font='body')
    out += tx(xm(1.05), ym(48), 'With a leak, flow never falls to the threshold:', 26, 'var(--danger)', 'middle', 'body')
    out += tx(xm(1.05), ym(48) + 36, 'the breath runs on into her expiration', 26, 'var(--danger)', 'middle', 'body')
    return out


def fig_async():
    out = ''
    rows = [('Her breathing · rate 40', 'var(--text-primary)', [(0.0, 0.55), (1.5, 0.55), (3.0, 0.55)], 1.5),
            ('Machine · Ti 1.2 s', 'var(--danger)', [(0.05, 1.2), (1.55, 1.2), (3.05, 1.2)], 1.5),
            ('Machine · Ti 0.7 s', 'var(--text-accent)', [(0.05, 0.7), (1.55, 0.7), (3.05, 0.7)], 1.5)]
    X0, W = 360, 1240
    xm = lambda t: X0 + W * t / 4.5
    for i, (lab, col, bars, _) in enumerate(rows):
        y = 130 + i * 190
        out += tx(60, y + 50, lab, 26, col, font='body')
        out += ln(X0, y + 90, X0 + W, y + 90, 'var(--text-secondary)', 1)
        for t0, d in bars:
            out += rc(round(xm(t0), 1), y, round(xm(t0 + d) - xm(t0), 1), 80, fill=f'color-mix(in oklab, {col} 22%, transparent)', c=col, sw=2, r=4)
        out += tx(X0 + W, y + 125, 'inspiration' if i == 0 else '', 20, anchor='end')
    for t in (0.55, 2.05, 3.55):
        out += rc(round(xm(t), 1), 300, round(xm(t + 0.7) - xm(t), 1), 110, fill='color-mix(in oklab, var(--danger) 18%, transparent)', c='none', sw=0)
    out += tx(xm(0.9), 290, 'She is breathing out; the machine still blows in', 24, 'var(--danger)', 'start', 'body')
    out += tx(X0, 700, 'Ti no more than 0.15–0.25 s longer than hers, and never more than half the breath cycle (1.5 s at a rate of 40).', 26, 'var(--text-primary)', font='body')
    return out


def fig_window():
    X0, X1, Y0, Y1 = 180, 1560, 600, 100
    xm = lambda t: X0 + (X1 - X0) * t / 10
    ym = lambda v: Y0 - (Y0 - Y1) * v / 10
    out = axes(X0, Y0, X1, Y1, 'Time', 'Severity', ymap=ym, xmap=xm)
    out += ln(X0, ym(8), X1, ym(8), 'var(--danger)', 3, dash='14 10') + tx(X1, ym(8) - 14, 'Needs a tube', 24, 'var(--danger)', 'end')
    out += ln(X0, ym(4), X1, ym(4), 'var(--text-secondary)', 2, dash='6 8') + tx(X1, ym(4) - 14, 'Needs help breathing', 22, anchor='end')
    out += rc(xm(1.6), Y1, xm(4.6) - xm(1.6), Y0 - Y1, fill='color-mix(in oklab, var(--text-accent) 9%, transparent)', c='none', sw=0)
    out += tx(xm(3.1), Y1 + 30, 'Window for NIV', 26, 'var(--text-accent)', 'middle')
    rev = [(xm(t), ym(v)) for t, v in [(0, 2), (1.5, 4), (3, 6.4), (4.5, 6.8), (6, 5.5), (7.5, 3.6), (10, 2)]]
    out += pth('M' + ' '.join(f'{x},{y}' for x, y in rev[:1]) + ' C' + ' '.join(f'{x},{y}' for x, y in rev[1:4]) + ' S' + ' '.join(f'{x},{y}' for x, y in rev[4:6]), 'var(--success)', 5)
    out += tx(xm(6.2), ym(3.2), 'Reversible: NIV carries her over the top', 26, 'var(--success)', font='body')
    rel = [(xm(t), ym(v)) for t, v in [(0, 2), (2, 4.5), (4, 7), (6, 9), (7, 9.8)]]
    out += poly(rel, c='var(--danger)', w=5)
    out += tx(xm(6.9), ym(9.6), 'Relentless: NIV only delays the tube', 26, 'var(--danger)', 'end', 'body')
    return out


def fig_pes():
    X0, X1, Y0, Y1 = 300, 1300, 620, 110
    ym = lambda v: Y0 - (Y0 - Y1) * v / 40
    out = axes(X0, Y0, X1, Y1, '', 'Oesophageal pressure swing cmH₂O', yticks=[0, 10, 20, 30, 40], ymap=ym)
    a, b = X0 + 220, X0 + 720
    out += tx(a, Y0 + 44, 'Start', 26, anchor='middle') + tx(b, Y0 + 44, 'At 2 hours', 26, anchor='middle')
    out += poly([(a, ym(34)), (b, ym(11))], c='var(--success)', w=6) + circ(a, ym(34), 12, 'var(--text-primary)', 'var(--text-primary)') + circ(b, ym(11), 12, 'var(--success)', 'var(--success)')
    out += poly([(a, ym(34)), (b, ym(31.5))], c='var(--danger)', w=6) + circ(b, ym(31.5), 12, 'var(--danger)', 'var(--danger)')
    out += tx(b + 30, ym(11) + 8, 'Success · 11', 28, 'var(--success)', font='body') + tx(b + 30, ym(31.5) + 8, 'Failure · 31.5', 28, 'var(--danger)', font='body')
    out += tx(a - 30, ym(34) + 8, '34', 28, 'var(--text-primary)', 'end')
    out += rc(1340, 150, 300, 380, c='var(--text-accent)', r=4)
    out += tx(1370, 260, '≥ 10', 96, 'var(--text-accent)', font='disp')
    out += tx(1370, 320, 'Fall by 2 h', 22) + tx(1370, 370, 'predicted success', 24, 'var(--text-primary)', font='body') + tx(1370, 410, 'AUC 0.97 (adults)', 24, 'var(--text-primary)', font='body')
    out += tx(1370, 470, 'P/F did not', 24, 'var(--danger)', font='body') + tx(1370, 504, 'separate them', 24, 'var(--danger)', font='body')
    return out


# ------------------------------------------------------------------ the full talk -----------------------------------------
def full_talk():
    T = ''
    T += title('VentCourse · Module 04 · Non-invasive ventilation · 50 min', 'Pressure without a <em>tube</em>',
               'High-flow, CPAP and bilevel in the PICU',
               'This talk is about the children we try hard not to intubate: the infant with bronchiolitis, the child with pneumonia, the child just extubated. High-flow, CPAP and bilevel: what each does, how to set them, how to make the mask fit the child, who should and should not have them, and how to know within the hour whether it is working. Sources: Chang chapter 7, Tobin chapters 16 to 18 by Hill, the BPICC manual from Pedicriticon 2026, PEMVECC 2017, and three papers on modes, comfort and effort.')
    T += bullets('Plan', 'Five <em>parts</em>', 'Today', ['What NIV does', 'The tools: high-flow, CPAP, bilevel', 'The mask and the child', 'Who to start, who not to', 'Is it working?'],
                 'Five parts. What positive pressure through a mask does to the lungs, the muscles and the heart. The three tools and how to set them. The interface, comfort and asynchrony, which is where most NIV fails. Selection and contraindications. And the first hour: how to tell success from failure, and why failing late is worse than failing early.')
    # ---------------- Part 1
    T += divider('Part 1', 'Part 1 · Physiology', 'What NIV <em>does</em>', 'Unload, open, splint, and the heart',
                 'Part one. What positive pressure without a tube actually does.')
    T += two('Two things', 'CPAP is not <em>ventilation</em>', 'Tobin ch. 18 · Chang ch. 7',
             ('CPAP', ['One pressure, all breath long', 'The child does all the work', 'Splints airway and alveoli']),
             ('Bilevel · NIPPV', ['A higher pressure in inspiration', 'The machine shares the work', 'EPAP below, IPAP above']),
             'Tobin separates two things. CPAP is a pressure that does not change through the breath: it holds the airway and the alveoli open, but strictly it is not ventilatory assistance because the patient does all the work of breathing. Non-invasive positive-pressure ventilation adds an active breath: a higher pressure in inspiration that inflates the lung and takes over part of the work. On a bilevel machine CPAP is simply IPAP equal to EPAP.')
    T += cards('Four effects', 'What the pressure <em>does</em>', 'Tobin ch. 18 · Rabec 2011',
               [('Unloads', ['Inspiratory pressure does part of the work']), ('Opens', ['EPAP raises FRC, reopens alveoli']), ('Splints', ['EPAP holds a floppy upper airway']), ('Offsets', ['EPAP cancels intrinsic PEEP'])],
               'Four effects. Inspiratory pressure raises transpulmonary pressure, increases the tidal volume and unloads the inspiratory muscles; with enough support the work of the diaphragm can be abolished. EPAP raises the functional residual capacity, reopens collapsed alveoli, reduces shunt and moves the lung onto a steeper part of its pressure–volume curve. EPAP splints a collapsible upper airway. And in a child with gas trapping, EPAP offsets intrinsic PEEP, so a smaller effort triggers the machine. In COPD, pressure support plus PEEP reduced diaphragmatic effort more than either alone.',
               big=['1', '2', '3', '4'], size=36)
    T += two('The heart', 'And the <em>heart</em>', 'Tobin ch. 16 and 18 · PEMVECC',
             ('A normal heart, dry', ['Venous return falls', 'Output can fall', 'Watch in sepsis, hypovolaemia']),
             ('A failing left ventricle', ['Afterload falls', 'Output rises', 'NIV is a treatment']),
             'Raising intrathoracic pressure reduces venous return and reduces left ventricular afterload. Which wins depends on the heart. In a dilated, poorly contracting left ventricle the afterload effect dominates and output rises: positive pressure is a treatment, which is why CPAP works in cardiogenic pulmonary oedema. In a normal heart that is underfilled, the fall in venous return dominates. Hypovolaemia, septic shock and gas trapping make the fall more likely. PEMVECC adds that positive pressure may raise afterload on a failing right ventricle.')
    T += numbers('Why not a tube', 'Why avoid the <em>tube</em>?', 'Tobin ch. 18', [('4×', 'Fewer pneumonias', 'Hospital-acquired, matched patients'), ('Own', 'Airway', 'Cough, swallow, talk, eat'), ('Fewer', 'Lines and catheters', 'Less sedation, less harm')],
                 'Because the airway stays the patient\'s own, the airway defences keep working: he can cough, swallow, talk and eat. Hospital-acquired pneumonia was about four times less common on non-invasive ventilation than with a tube in physiologically matched patients, and fewer lines and catheters were used.',
                 foot='NIV is used to avoid intubation, not to replace it.')
    T += quiz(1, 'Raise the <em>EPAP</em>', 'On a home bilevel device, EPAP is raised from 5 to 8 to treat obstruction. IPAP stays at 14. What happens to the support?',
              [('A', 'It rises'), ('B', 'It falls from 9 to 6'), ('C', 'It is unchanged'), ('D', 'Only oxygenation changes')], 'B',
              'Support is IPAP − EPAP. On a home bilevel device, raising EPAP alone lowers the support. Raise IPAP with it to keep the same help.',
              'First check. EPAP up from five to eight, IPAP left at fourteen. What happens to the support?',
              'B. Support is the difference. On ICU ventilators you set PEEP and pressure support separately, so PEEP adds on top; on home bilevel devices you set IPAP and EPAP, so raising EPAP alone takes support away. Raise them together.')
    # ---------------- Part 2
    T += divider('Part 2', 'Part 2 · The tools', 'High-flow, CPAP, <em>bilevel</em>', 'What each gives, how to set it, how to step up',
                 'Part two. The tools, in the order we reach for them.')
    T += figure('The ladder', 'One step at a <em>time</em>', 'BPICC · PEMVECC', fig_ladder(),
                'The ladder. BPICC names three PICU modes of non-invasive support: high-flow nasal cannula, mask CPAP or BiPAP, and bubble CPAP. High-flow is usually first-line for children with a high oxygen need or a raised work of breathing; mask CPAP or bilevel is for children who need more than high-flow when we would rather avoid a tube. PEMVECC draws the same ladder by severity and puts a question mark over NIV in severe disease. At each step, reassess within one to two hours.')
    T += numbers('High-flow', 'High-flow: the <em>numbers</em>', 'BPICC ch. 6, p. 29', [('2 L/kg/min', 'Start', 'Maximum 40 L/min'), ('3 L/kg/min', 'If worsening', 'Maximum 50 L/min, intensivist'), ('92–95%', 'SpO₂ target', 'Flow first, then FiO₂')],
                 'The BPICC protocol. Start at two litres per kilogram per minute, to a maximum of forty litres per minute. In a worsening child the duty intensivist may go to three litres per kilogram, to a maximum of fifty. Fix the flow first, then titrate the FiO2 to a saturation of 92 to 95 per cent. Note that the oxygen chapter of the same manual quotes two to eight litres for neonates and four to ten for children; use the weight-based PICU protocol.')
    T += figure('Flow meets demand', 'Why the <em>flow</em> matters', 'BPICC ch. 7', fig_flow_demand(),
                'Why high flow. A breathless child pulls in far more than four litres a minute at the peak of inspiration. On low-flow oxygen the rest is room air, so the FiO2 falls and varies breath to breath. When the flow meets or exceeds her peak inspiratory flow, no room air is drawn in: the FiO2 you set is the FiO2 she gets, and the dead space of the nose and pharynx is flushed. High-flow also creates some positive end-expiratory pressure, but how much depends on the flow, the leak and whether the mouth is open; it is not measured or set.')
    T += figure('Prong fit', 'The prongs must not <em>seal</em>', 'BPICC pp. 29–31', fig_prongs(),
                'The cannula must not be occlusive. BPICC asks for a visible gap around the prongs in the nostrils, about two millimetres between the base of the prongs and the septum, and never to cut the cannula to fit. The gap is the way out for exhaled gas. Check the nares for pressure areas and give nasal care at least every four hours, and oral care every three.')
    T += bullets('Reassess at two hours', 'Reassess at <em>two</em> hours', 'BPICC · Tobin ch. 18',
                 ['Rate and work: falling?', 'Pauses: gone?', 'SpO₂ on what FiO₂?', 'Gas: CO₂ falling?', 'No better: step up'],
                 'High-flow has one to two hours to show it is working. Look at the rate and the work of breathing, any pauses, the saturation and the FiO2 needed for it, and a gas. Improvement in heart rate, rate and gas exchange in the first one to two hours is the strongest predictor of success on any non-invasive support. If she is no better, step up to CPAP: do not leave a child to tire on a step that has not worked.')
    T += two('High-flow or CPAP', 'High-flow or <em>CPAP</em>?', 'BPICC · PEMVECC',
             ('High-flow', ['Set flow and FiO₂', 'Pressure unmeasured', 'Comfortable, easy to start']),
             ('CPAP', ['Set pressure, 6–8 to start', 'Holds alveoli open', 'Next step when high-flow fails']),
             'The difference is the pressure. High-flow sets a flow and an FiO2; whatever pressure it makes depends on the flow, the leak and the mouth. CPAP sets a pressure and holds it through expiration. PEMVECC found no randomised paediatric trials of either and no evidence that one beats the other, so it makes no recommendation for high-flow and suggests CPAP may be considered as initial support in mixed disease and mild to moderate cardiorespiratory failure. In practice: high-flow first, CPAP when high-flow has had its chance.')
    T += cards('Bubble CPAP', 'Bubble <em>CPAP</em>', 'BPICC pp. 36–39',
               [('Who', ['Babies under 5 kg', 'Needing more than high-flow']), ('Flow', ['6–8 L/min to start', 'Up to 10 for a leak']), ('Seal', ['Bubbling = pressure delivered', 'No bubbles = leak']), ('Wean', ['FiO₂ to 0.4', 'PEEP down to 6', 'Then low-flow'])],
               'Bubble CPAP, per BPICC, for babies under five kilograms who need more than high-flow. The pressure is the depth of the expiratory limb under water. Flow six to eight litres a minute, up to ten to compensate for a leak. Bubbling in the chamber shows a seal and that CPAP is being delivered; no bubbling means a leak. Leak test before use: test elbow, PEEP ten, flow one litre, gentle bubbling. Use a pacifier to keep the mouth closed. Wean the FiO2 to 0.4, then the PEEP step by step to six, then a trial of low-flow oxygen.', size=34)
    T += table('Terms', 'The <em>words</em> on the machine', 'Chang table 7-1',
               ['Term', 'What it means'],
               [['CPAP', 'One pressure in spontaneous breaths; no machine breaths; IPAP = EPAP'], ['EPAP', 'Pressure at the end of expiration: PEEP on a mask'], ['IPAP', 'Pressure in inspiration: the peak'],
                ['Support', 'IPAP − EPAP: the help each breath gets'], ['S · ST · T', 'Who starts the breath: the child, the child or a backup rate, the machine']],
               'The vocabulary, from Chang. CPAP: positive pressure during spontaneous breaths with no machine breaths, the same as IPAP equal to EPAP. EPAP is the PEEP of non-invasive ventilation. IPAP is the inspiratory peak. The difference is the support. And the mode letters say who starts the breath.', widths=['300px', None], size=34)
    T += figure('EPAP and IPAP', 'Two pressures, two <em>jobs</em>', 'Chang ch. 7 · Tobin ch. 18', fig_ipap_epap(),
                'Two pressures, two jobs. EPAP holds the alveoli and the upper airway open: raise it for oxygenation and for obstruction. The difference between IPAP and EPAP is the help each breath gets: raise IPAP for tidal volume, CO2 and the work of breathing. Chang titrates both in steps of one to two centimetres of water against the saturation and the CO2.')
    T += cards('Three questions', 'Three <em>questions</em> for any mode', 'Rabec, Thorax 2011',
               [('Controlled', ['Pressure or volume?']), ('Starts', ['Child or machine?']), ('Ends', ['Flow falling or time?'])],
               'More than thirty manufacturers use different names for the same mode and the same name for different modes. Rabec and the SomnoNIV group cut through it with three questions. What is controlled, pressure or volume? What starts inspiration, the patient or a timer? What ends it, the flow falling to a set fraction of its peak, or a set time? Pressure-targeted modes are used in more than nine of ten acute applications: they are better tolerated and they compensate for a moderate leak.', big=['1', '2', '3'])
    T += bd.reuse(SRC_LTV, 'S, ST, T')
    T += table('Starting settings', 'Where to <em>start</em>', 'Chang · Tobin · BPICC',
               ['Child', 'Start', 'Then'],
               [['Infant, bronchiolitis', 'Nasal CPAP 6–7', 'Up to 8; FiO₂ for SpO₂ 92–95%'], ['Hypercapnic, weak pump', 'ST · IPAP 8–10 / EPAP 4–5', 'IPAP up 1–2 at a time; backup near her rate'],
                ['Hypoxaemic, pneumonia', 'ST · EPAP 6–8, IPAP + 6–8', 'Oronasal mask; review at 1 hour'], ['Upper airway, OSA', 'CPAP 4–6', 'EPAP up for obstruction, IPAP for hypoventilation']],
               'Starting points. Chang starts adults at IPAP eight and EPAP four in S/T, and Hill at IPAP eight to twelve and EPAP four to five. For hypoxaemic failure the EPAP matters more: six to eight to start. For an infant with bronchiolitis, nasal CPAP six to seven. Raise EPAP for obstructive events and IPAP for hypoventilation. These are starting points; the child decides the end point.', widths=['380px', '520px', None], size=30)
    T += bullets('Titrate', 'Come up <em>fast</em>', 'Tobin ch. 18 · Chang table 7-6',
                 ['Start low so she accepts it', 'Steps of 1–2 cmH₂O', 'Most reach 12–20 within the hour', 'Too little, too slowly: the common error'],
                 'Hill describes a low-high approach: start at IPAP eight to ten so the patient accepts the mask, then raise it, usually to twelve to twenty within the first hour. The commonest mistake is not raising the pressure quickly enough, so the patient fails on inadequate support. The opposite, high-low, starts at twenty to twenty-five and comes down; it may suit the hypoxaemic patient with a very high minute ventilation.')
    T += figure('Circuits', 'Where does the CO₂ <em>go</em>?', 'Rabec 2011 · Tobin ch. 18', fig_circuit(),
                'Circuits. Home and dedicated NIV machines use a single limb with an intentional leak: exhaled gas leaves through a port, and unless EPAP keeps flow going, CO2 washes back up the tube and is rebreathed. Keep EPAP at least four and use a port in the mask, which flushes better than one in the circuit. ICU ventilators use two limbs with an expiratory valve: no rebreathing, and a blender for any FiO2. Oxygen bled into a home bilevel reaches only about 0.45 to 0.5, so a hypoxaemic child belongs on an ICU ventilator or a machine with a blender. PEMVECC: a single-limb circuit for NIV, and no home ventilators for invasive ventilation in the acute phase.')
    T += quiz(2, 'Six <em>kilograms</em>', 'A 6 kg infant with bronchiolitis is tiring on 2 L/min nasal oxygen. You start high-flow. Which flow?',
              [('A', '2 L/min'), ('B', '6 L/min'), ('C', '12 L/min'), ('D', '40 L/min')], 'C',
              'Two litres per kilogram per minute: 12 L/min for 6 kg. Then titrate the FiO₂ to SpO₂ 92–95%.',
              'Second check. Six kilograms, starting high-flow.',
              'C. Twelve litres a minute. Fix the flow, then the FiO2.')
    # ---------------- Part 3
    T += divider('Part 3', 'Part 3 · The mask and the child', 'Make it <em>fit</em> the child', 'Interfaces, leak, asynchrony, comfort',
                 'Part three. Most NIV that fails, fails here: at the interface, in the stomach, in the timing, and in a frightened child.')
    T += table('Interfaces', 'Six <em>interfaces</em>', 'Cammarota 2022 · Tobin ch. 18',
               ['Interface', 'For', 'Against'],
               [['Nasal mask or prongs', 'Infants, long-term, can talk and cough', 'Mouth leak'], ['Oronasal', 'Acute failure: the first choice', 'Claustrophobia, aspiration, asphyxia risk'],
                ['Total face', 'Odd anatomy, sore bridge', 'Claustrophobic'], ['Helmet', 'Longest tolerance, no bridge', 'Noise over 100 dB, clears CO₂ less well'], ['Mouthpiece', 'Daytime, neuromuscular', 'Largest leak']],
               'The interfaces. Nasal masks and prongs suit infants, who breathe through the nose, and long-term use. The oronasal mask is the first choice in acute failure, because breathless patients mouth-breathe: in one trial intolerance was 34 per cent with a nasal mask against 12 per cent with a full-face mask, and mouth leaks occur in up to 94 per cent of hypercapnic patients on NIV. Helmets are tolerated longest but are noisy and clear CO2 less well. PEMVECC makes no recommendation on the best paediatric interface: use the one with the least leak.', widths=['340px', '640px', None], size=30)
    T += cards('Fit the mask', 'Fit the <em>mask</em>', 'Chang ch. 7 · Tobin ch. 18 · Cammarota',
               [('Size', ['Use the gauge', 'Too big is the usual error']), ('Tension', ['Least that controls the leak', 'Two fingers under the straps']), ('Skin', ['Cushion the bridge', 'Rotate interfaces', 'Check every 4 h']), ('Safety', ['Anti-asphyxia valve', 'Alarms on'])],
               'Fitting. Use the sizing gauge; the commonest error is a mask that is too big. Use the least strap tension that controls the leak: too loose and there is leak, asynchrony, eye irritation and noise; too tight and there are pressure ulcers. Cushion the bridge, rotate between interfaces, and check the skin every four hours. Any oronasal mask needs an anti-asphyxia valve that opens to room air if the machine or the gas fails. Keep a bag of different masks at the bedside.', size=34)
    T += figure('Leak and cycling', 'A leak keeps the breath <em>going</em>', 'Rabec 2011, fig. 7', fig_leak_cycle(),
                'What a leak does to the breath. In S or ST mode the breath ends when inspiratory flow falls to a set fraction of its peak, classically twenty-five per cent. With a leak the machine keeps pouring flow in to hold the pressure, the flow never falls to the threshold, and the breath runs on into the child\'s expiration until Ti max cuts it off. Leaks also hide the child\'s efforts, causing ineffective triggers, or mimic them, causing autotriggering. Dedicated NIV machines handle leak better than ICU ventilators.')
    T += figure('Asynchrony on NIV', 'Out of <em>step</em>', 'Chang table 7-6', fig_async(),
                'Asynchrony in a fast-breathing child. At a rate of forty her whole breath lasts one and a half seconds and she breathes in for about half a second. A machine Ti of 1.2 seconds keeps blowing while she breathes out: she fights it, and the gas left in at the end of the long breath makes her next effort too weak to trigger. Chang sets the inspiratory time no more than 0.15 to 0.25 seconds longer than the patient\'s own, and never more than half the cycle. Keep the backup rate below her own so she leads.')
    T += cards('Five asynchronies', 'Five ways to be out of <em>step</em>', 'Rabec 2011 · Cammarota 2022',
               [('Ineffective effort', ['Leak, trapping, weak effort']), ('Double trigger', ['Ti too short, rise too fast']), ('Autotrigger', ['Leak mimics her effort']), ('Premature cycle', ['Stiff lungs']), ('Delayed cycle', ['Leak, obstruction, long Ti'])],
               'Five patterns. Ineffective efforts: the child tries and nothing happens, from leak, trapping or a weak effort. Double triggering: the breath ends before she has finished, often with too fast a rise. Autotriggering: breaths with no effort behind them, usually a leak. Premature cycling, typical of stiff lungs, and delayed cycling, typical of obstruction and leak. Detection by eye is poor and gets worse as asynchrony becomes common: look at the child as well as the screen.', size=34)
    T += bullets('Care of the child on NIV', 'Care of the child on <em>NIV</em>', 'BPICC ch. 6, p. 28',
                 ['Continuous monitoring, hourly observations', 'NG or OG tube: decompress', 'Suction nose and mouth as needed', 'Skin every 4 h; document each shift', 'Check the humidifier water'],
                 'BPICC nursing care. Continuous monitoring with observations at least hourly and alarms set. An NG or OG tube for gastric decompression, or the gastrostomy if there is one, with feeds as the condition allows. Suction the nose and mouth as needed for comfort, saturation and effort. Check pressure areas every four hours and document the skin every shift; comfort dressings on any red area. Check the water in the humidifier and the CPAP generator.', size=46)
    T += two('NG or not', 'The stomach: two <em>views</em>', 'BPICC · Tobin ch. 18',
             ('Adult guidance', ['No routine NG tube', 'Distension in 5–10%', 'Treat when it happens']),
             ('PICU protocol', ['NG or OG for every child', 'Infants swallow air', 'The diaphragm needs room']),
             'The sources disagree, and it is worth saying so. Tobin reports gastric insufflation in five to ten per cent of adults and says routine nasogastric tubes are no longer recommended. BPICC decompresses every child on non-invasive ventilation with an NG or OG tube. Infants swallow air, depend on the diaphragm and aspirate easily, so in the PICU we decompress. Remember that the tube can break a mask seal.')
    T += cards('Comfort and sedation', 'Comfort before <em>drugs</em>', 'Cammarota 2022 · Tobin ch. 18',
               [('First', ['Parent, explanation, calm room', 'Right mask, right settings']), ('If needed', ['Dexmedetomidine', 'No respiratory depression']), ('Careful', ['Benzodiazepines', 'Delirium, paradoxical agitation']), ('Warning', ['Agitation that will not settle', 'Is a reason to intubate'])],
               'Up to forty per cent of NIV fails, mostly from discomfort. Non-drug measures first: a parent at the bedside, an explanation, a calm room, the right mask and the right settings. If sedation is needed, dexmedetomidine sedates and relieves anxiety without depressing breathing and worked better than midazolam in adults; watch for bradycardia and hypotension. Benzodiazepines cause delirium and paradoxical agitation. Sedate only where the airway can be managed, and remember Tobin\'s warning: unremitting agitation on NIV is an indication to intubate.', size=34)
    T += table('Complications', 'What goes <em>wrong</em>', 'Tobin ch. 18, table 18-9',
               ['Problem', 'How often', 'Fix'],
               [['Leak', '80–100%', 'Close the mouth, chin support, oronasal mask'], ['Mask discomfort', '30–50%', 'Refit, new type'], ['Skin redness', '20–34%', 'Loosen, cushion, rotate'],
                ['Nasal bridge ulcer', '5–10%', 'Artificial skin, change mask'], ['Gastric distension', '5–10%', 'NG decompression, lower pressure'], ['Hypotension, pneumothorax', 'Under 5%', 'Lower pressure; drain']],
               'Complications from Tobin. Some leak is almost universal. Mask discomfort in a third to a half, skin redness in a fifth to a third, nasal bridge ulcers in five to ten per cent (up to forty in early series). Gastric distension five to ten. Hypotension and pneumothorax are uncommon but real. And in children on long-term mask ventilation, mid-face flattening was seen in nearly half.', widths=['420px', '260px', None], size=30)
    T += quiz(3, 'The <em>leak</em>', 'A crying 4-year-old on bilevel through a small adult mask: air at the bridge, abdomen distended, SpO₂ 88%. First step?',
              [('A', 'Raise IPAP to beat the leak'), ('B', 'Tighten the straps'), ('C', 'Midazolam bolus'), ('D', 'A mask that fits, NG tube, parent')], 'D',
              'Fix the interface and the stomach first. More IPAP feeds the leak and the stomach; tight straps injure skin; a benzodiazepine bolus quietens the alarms at the cost of her breathing.',
              'Third check. Wrong-size mask, leak, full stomach, crying child.', 'D. Interface, stomach, comfort, then the settings.')
    # ---------------- Part 4
    T += divider('Part 4', 'Part 4 · Selection', 'Who to start, who <em>not</em> to', 'Need, exclude, reversible',
                 'Part four. Who should have non-invasive ventilation, and who should not.')
    T += cards('Who to start', 'Three <em>steps</em>', 'Tobin ch. 18, table 18-3',
               [('Need', ['Distress, high rate, accessory muscles', 'CO₂ up with pH down, or low P/F']), ('Exclude', ['Arrest, shock, cannot protect airway', 'Copious secretions, agitation, no mask fit']), ('Reversible', ['Will the cause turn in hours to days?', 'NIV is a crutch, not a cure'])],
               'Hill\'s three steps. First, does the patient need ventilatory help: moderate to severe distress, a high rate, accessory muscles or paradox, a CO2 above forty-five with an acidosis, or a P/F below two hundred. Second, exclude those at high risk: respiratory arrest, shock or uncontrolled arrhythmia, an airway that cannot be protected, excessive secretions, agitation, and anatomy that prevents a fit. Third, is the cause reversible? NIV is a crutch that carries the patient while treatment works.', big=['1', '2', '3'], size=34)
    T += cards('Contraindications', 'Not by <em>mask</em>', 'BPICC ch. 6, p. 28',
               [('Face and head', ['Maxillofacial trauma', 'Complete nasal block', 'Base-of-skull fracture']), ('Chest', ['Undrained pneumothorax', 'Unrepaired CDH']), ('Gut', ['TOF, fresh anastomosis', 'Perforation, button battery', 'Upper GI bleed']), ('Circulation', ['Shock needing high or rising support'])],
               'BPICC contraindications for children: maxillofacial trauma, complete nasal obstruction, suspected base-of-skull fracture, an untreated pneumothorax (NIV may be considered once a drain is in), unrepaired congenital diaphragmatic hernia, oesophageal problems such as a tracheo-oesophageal fistula, a recent oesophageal anastomosis, perforation or a swallowed button battery, an upper GI bleed, and haemodynamic instability needing high or escalating support. NIV may still be used at the treating physician\'s discretion, or as a bridge to intubation.', size=32)
    T += table('By disease', 'Child by <em>child</em>', 'Tobin ch. 18 · PEMVECC · BPICC',
               ['Child', 'Support', 'Watch'],
               [['Bronchiolitis', 'High-flow, then CPAP 6–8', 'Nose, pauses, stomach'], ['Pneumonia, mild–moderate PARDS', 'Bilevel, oronasal, EPAP 6–8', 'One-hour review; not severe PARDS'], ['Acute asthma', 'Bilevel trial if not responding', 'Exhaustion, drowsiness'],
                ['Failing LV, myocarditis', 'CPAP or bilevel', 'Induction is the danger'], ['Weak pump: SMA, Duchenne', 'Bilevel ST + cough assist', 'Backup rate, secretions'], ['After extubation, high-risk', 'Planned bilevel', 'Not routine for all']],
               'Disease by disease. Bronchiolitis: high-flow, then CPAP. Pneumonia and mild to moderate PARDS: bilevel by oronasal mask with an hour to prove itself; PEMVECC advises against NIV in severe PARDS. Asthma: a trial is reasonable if the child is not responding, with the evidence called promising but controversial. The failing left ventricle: positive pressure is a treatment. Neuromuscular weakness: bilevel with a backup rate and cough assist. After extubation: planned NIV for the high-risk child, not for every child.', widths=['420px', '560px', None], size=30)
    T += figure('Window', 'The window of <em>opportunity</em>', 'Tobin ch. 18, fig. 18-3', fig_window(),
                'Hill\'s picture. The window for NIV opens when the patient needs help breathing and closes when a tube becomes unavoidable. Start early, before severe acidosis. In a reversible illness NIV carries the patient over the top of the curve while treatment works. In a relentless illness, such as severe ARDS or multi-organ failure, it only delays the tube, and the delay costs.')
    T += numbers('After extubation', 'After the <em>tube</em>', 'Tobin ch. 18 · PEMVECC',
                 [('25 vs 15%', 'ICU mortality', 'Rescue NIV for all, adults'), ('≈ 10 h', 'Later re-intubation', 'In the NIV group'), ('High-risk', 'Who benefits', 'Planned, not rescue')],
                 'After extubation. Used for everyone, as a rescue once failure has begun, NIV did not help: in Esteban\'s trial of 221 adults, ICU mortality was 25 per cent with NIV against 15 per cent, and re-intubation came about ten hours later. Planned NIV in high-risk patients reduced re-intubation. PEMVECC: no routine post-extubation NIV, but consider it early with cough assist in neuromuscular disease, and in other high-risk children.')
    T += bullets('Children', 'What we know in <em>children</em>', 'PEMVECC 2017 · Tobin ch. 18',
                 ['No paediatric trials of high-flow or CPAP', 'Two NIV trials, opposite results', 'Mild to moderate disease, not severe', 'NIV must not delay the tube'],
                 'The paediatric evidence is thin. PEMVECC found no randomised trials of high-flow or CPAP in children and only two of NIV, with opposite results for preventing intubation. Its consensus: consider NIV in mild to moderate disease, not severe, and do not let it delay intubation. Tobin\'s paediatric series mirror adult experience: in one series of children with hypoxaemic failure on nasal bilevel, only three of twenty-eight were intubated.')
    T += quiz(4, 'Which <em>child</em>?', 'Which child should not go on mask NIV?',
              [('A', 'Bronchiolitis tiring on high-flow'), ('B', 'Swallowed button battery, stridor'), ('C', 'Duchenne with morning headaches'), ('D', 'Pneumonia, alert, SpO₂ 87% on a mask')], 'B',
              'Oesophageal injury is a contraindication: mask pressure drives gas into the oesophagus. The others are good candidates.',
              'Fourth check. One of these children should not have mask NIV.', 'B. The button battery. An oesophageal injury is a contraindication.')
    # ---------------- Part 5
    T += divider('Part 5', 'Part 5 · The first hour', 'Is it <em>working</em>?', 'The review, the warnings, and failing well',
                 'Part five. How to know within the hour, and what to do when the answer is no.')
    T += cards('The one-hour review', 'The one-hour <em>review</em>', 'PEMVECC · Tobin ch. 18',
               [('Oxygen', ['SpO₂ on what FiO₂?', 'Rising FiO₂ = failing']), ('Breathing', ['Rate, work, paradox', 'Exhaled VT']), ('Gas', ['CO₂ falling or rising?', 'pH']), ('Child', ['Heart rate', 'Conscious level', 'Comfort'])],
               'PEMVECC asks for an assessment of NIV success at one hour: heart rate, respiratory rate, SpO2 over FiO2, pH, conscious level and other organ failure, so that intubation is not delayed. Tobin: falling rate and heart rate, less sternocleidomastoid activity, no abdominal paradox, synchrony and little leak predict success. Transcutaneous CO2 is more useful than end-tidal on a leaking mask.', size=34)
    T += figure('Effort tells first', 'Effort tells you <em>first</em>', 'Tonelli, AJRCCM 2020', fig_pes(),
                'Tonelli measured the oesophageal pressure swing, the patient\'s own effort, in thirty adults with new hypoxaemic respiratory failure on NIV. At the start both groups swung about thirty-four centimetres of water. At two hours the successes had fallen to eleven; the failures stayed at thirty-one. A fall of at least ten by two hours predicted success with an area under the curve of 0.97, while the P/F ratio, the rate and the tidal volume only separated the groups at about twelve hours. Effort tells you first, and you can see effort at the bedside: the neck, the abdomen, the paradox.')
    T += numbers('Big breaths on NIV', 'Big breaths are a <em>warning</em>', 'Tonelli 2020 · Cammarota 2022',
                 [('> 9.5', 'mL/kg exhaled VT', 'Predicted failure, adults'), ('P-SILI', 'Self-inflicted injury', 'Her own effort stretches the lung'), ('?', 'Children', 'No paediatric threshold yet')],
                 'Large tidal volumes on NIV are not a sign of success. In adults with hypoxaemic failure an exhaled tidal volume above 9.5 millilitres per kilogram independently predicted failure. Those breaths are the patient\'s own huge effort on top of the support, and they may injure an already injured lung: patient self-inflicted lung injury, through large swings in transpulmonary pressure, pendelluft and negative-pressure oedema. There is no paediatric threshold in our sources; treat a big exhaled volume in a breathless child as a warning.')
    T += numbers('Delayed intubation', 'Failing <em>late</em> costs', 'Tobin ch. 18 · Esteban',
                 [('29%', 'Mortality', 'NIV first, then the tube'), ('53 vs 6%', 'ARDS mortality', 'NIV failure vs success'), ('25 vs 15%', 'ICU mortality', 'Rescue NIV after extubation')],
                 'Failing late is worse than failing early. In US national data, patients moved from non-invasive to invasive ventilation had a 29 per cent mortality, higher than those intubated from the start. In ARDS, mortality was 53 per cent in NIV failures against 6 per cent in successes. After extubation, rescue NIV delayed re-intubation by about ten hours with higher mortality. PEMVECC: NIV should not delay endotracheal intubation.')
    T += bullets('Fail well', 'When it fails, fail <em>well</em>', 'Tobin ch. 18 · Cammarota',
                 ['Do not chase it with pressure', 'Do not sedate it into silence', 'Call help, pre-oxygenate on the NIV', 'Gentle induction, ventilator pre-set'],
                 'When the review says failure, do not chase it with more pressure, and do not sedate the child into silence on the mask: sedation on failing NIV unmasks the failure. Call help, pre-oxygenate on the NIV itself with FiO2 1.0 and the EPAP kept on, choose a haemodynamically gentle induction, and have the ventilator pre-set for lung protection. NIV as pre-oxygenation reduced desaturation during intubation.')
    T += quiz(5, 'The one-hour <em>review</em>', 'One hour on bilevel: FiO₂ up from 0.6 to 0.7, RR 52, HR 165, PaCO₂ 34 → 44, answering in single words. Exhaled VT 15 mL/kg.',
              [('A', 'IPAP to 22'), ('B', 'Another hour'), ('C', 'Intubate now, planned'), ('D', 'Midazolam to settle him')], 'C',
              'Every sign is going the wrong way at one hour: oxygen, rate, heart rate, CO₂, conscious level, and a big exhaled volume. The trial has answered; delay makes it worse.',
              'Last check. The one-hour review.', 'C. Intubate now, planned.')
    T += bullets('Takeaways', 'Take <em>home</em>', 'Five lines',
                 ['High-flow 2 L/kg/min; review at 1–2 h', 'EPAP opens, IPAP − EPAP ventilates', 'Fit the mask before the pressure', 'Start early, in mild to moderate disease', 'At one hour, decide: fail early, not late'], 'Five lines to take home. High-flow at two litres per kilogram, reviewed at one to two hours. EPAP opens the lung and the airway; the difference between IPAP and EPAP ventilates. Fix the mask, the leak, the stomach and the child before you touch the pressures. Start early, in mild to moderate disease, in a child who can protect the airway. And at the one-hour review, decide: failing early is safer than failing late.', size=46)
    T += bullets('Try it', 'Replay it in the <em>app</em>', 'VentCourse', ['Learn · Module 04 · 11 lessons', 'Cases · Sim scenarios 13–15', 'Home NIV: Sim scenarios 03–07'],
                 'Everything in this talk is in VentCourse. Module 04 now has eleven lessons, six of them on NIV. Sim scenarios thirteen to fifteen put you on the machine: the infant with bronchiolitis, the boy with pneumonia, and the girl just extubated. Scenarios three to seven take NIV home.')
    T += ending('Thank you', 'VentCourse · Module 04', 'Make the mask fit the <em>child</em>.', 'Then the pressures. Then the hour. · Thank you',
                'Fit the mask to the child, then set the pressures, then watch the hour. Thank you.')
    return T


# ------------------------------------------------------------------ case decks -----------------------------------------
ST = bd.ST
_FIG = {d['id']: (d['fig'], d['sup']) for d in NIV_CASES}
_orig_picture = bd.picture


def picture(n, h=320, sid=None):
    if not n and sid in _FIG:
        age, sup = _FIG[sid]
        return (f'<div style="flex:none; height:{h}px; border-radius:6px; overflow:hidden; background:#F4EFE6; border:1px solid var(--border-subtle); padding:10px 20px; box-sizing:border-box;">'
                f'<x-import component-from-global-scope="patient-figure" age="{age}" support="{sup}" style="width:100%; height:100%;" hint-size="100%,100%"></x-import></div>')
    return _orig_picture(n, h, sid)


bd.picture = picture


def opener_fig(key, eyebrow, name, lines, age, sup, notes):
    bd.LIVE_OUT[key] = {'t': name.replace('<em>', '').replace('</em>', ''), 'lines': lines}
    body = (f'<div style="flex:1; display:grid; grid-template-columns:minmax(0,1fr) 1040px; gap:56px; align-items:center;">'
            f'<div style="display:flex; flex-direction:column; gap:32px;"><span style="{MONO} font-size:24px; color:var(--text-secondary);">{e(eyebrow)}</span>'
            f'<h2 style="margin:0; font-family:var(--font-display); font-weight:400; font-size:104px; line-height:.98; letter-spacing:-.015em; text-wrap:balance;">{name}</h2>'
            + ''.join(f'<span style="font-size:38px; line-height:1.3; color:var(--text-secondary);">{e(l)}</span>' for l in lines) +
            f'<span style="{MONO} font-size:20px; color:var(--text-accent);">On your phones now</span></div>'
            f'<div style="height:640px; border-radius:8px; overflow:hidden; background:#F4EFE6; border:1px solid var(--border-subtle); padding:40px; box-sizing:border-box;">'
            f'<x-import component-from-global-scope="patient-figure" age="{age}" support="{sup}" style="width:100%; height:100%;" hint-size="100%,100%"></x-import></div></div>')
    return bd.section('Case · ' + bd.plain(name), body, notes, live=key, mode='info', pad='80px 96px 80px')


OPENERS = {
    'nb1': ('anaya_case', 'Anaya, <em>3 months</em>', ['5 kg · day 3 of a cold, cough and poor feeds', 'Two hours on high-flow in the ER'], 'infant', 'nc',
            'Anaya, three months, five kilos, day three of a cold and cough with poor feeds; RSV positive. She has been on high-flow at two litres per kilogram for two hours. History only; the room decides what comes next.'),
    'np1': ('ishaan_case', 'Ishaan, <em>6 years</em>', ['20 kg · four days of fever and cough', 'On IV antibiotics; breathless tonight'], 'child', 'mask',
            'Ishaan, six years, twenty kilos. Four days of fever and cough, on intravenous antibiotics on the ward since yesterday, and tonight he is breathless and saturating eighty-seven per cent on a non-rebreather. Alert, frightened, talking in short phrases.'),
    'nx1': ('zara_case', 'Zara, <em>4 years</em>', ['15 kg · six days on the ventilator', 'Extubated this morning onto bilevel'], 'toddler', 'niv',
            'Zara, four years, fifteen kilos. Six days on the ventilator for pneumonia with sepsis; two borderline breathing trials, so she was extubated this morning straight onto bilevel ST by an oronasal mask.'),
}
CASE_NO = {'nb1': 1, 'np1': 2, 'nx1': 3}
DEBRIEF = {
    'nb2': ('Anaya · debrief', 'Anaya · debrief', 'High-flow, then <em>CPAP</em>',
            [('Start', ['High-flow 2 L/kg/min', 'SpO₂ 92–95%']), ('Review', ['At 1–2 hours', 'No better: CPAP 6–8']), ('Keep it working', ['Nose, NG, pacifier', 'Not more pressure']), ('Skin', ['Gap at the septum', 'Check every 4 h'])],
            'High-flow first at two litres per kilogram, reviewed at one to two hours, CPAP six to eight when it has not worked. Keep it working with the child, not the pressure: a clear nose, an empty stomach, a closed mouth, the right size. Anaya is sim scenario thirteen.'),
    'np2': ('Ishaan · debrief', 'Ishaan · debrief', 'A trial with a <em>deadline</em>',
            [('Start', ['Awake, stable, reversible', 'Oronasal, EPAP 6–8']), ('Review', ['At one hour', 'FiO₂, rate, CO₂, mind']), ('Warning', ['Exhaled VT 15 mL/kg', 'Her own effort']), ('Fail well', ['No chasing, no midazolam', 'Planned intubation'])],
            'An NIV trial in hypoxaemic failure has a deadline, and it should be written before the mask goes on. At one hour every sign said failure: the oxygen need, the rate, the heart rate, the CO2, the conscious level and a big exhaled volume. Intubate planned. Ishaan is sim scenario fourteen.'),
    'nx2': ('Zara · debrief', 'Zara · debrief', 'Make it fit the <em>child</em>',
            [('Interface', ['The right size', 'Seal without blanching']), ('Stomach', ['NG on free drainage']), ('Timing', ['Ti ≤ half her cycle', 'Backup below her rate']), ('Comfort', ['Parent first', 'Dexmedetomidine'])],
            'Planned NIV after extubation suits the high-risk child, but only if it fits her: the mask, the stomach, the timing and her fear. More pressure, restraint and benzodiazepines make each of those worse. Zara is sim scenario fifteen.'),
}


def niv_cases_body(code, skip_used=True):
    out = ''
    for d in NIV_CASES:
        sid = d['id']
        if sid in OPENERS:
            key, name, lines, age, sup, notes = OPENERS[sid]
            out += opener_fig(key, f'Case {CASE_NO[sid]} of 3', name, lines, age, sup, notes)
        out += bd.stage_slides(d, code)
        for t in d['theory']:
            if ('niv.html', t) not in bd.USED:
                out += bd.reuse('niv.html', t)
        if sid in DEBRIEF:
            lab, eb, h, cs, notes = DEBRIEF[sid]
            out += bd.cards_slide(lab, eb, h, cs, notes)
    return out


def build_cases():
    code = 'NIV'
    out = bd.title_slide('VentCourse · Module 04 · Non-invasive ventilation · 25 min', 'Three children, <em>no</em> tube',
                         'You set the support on your phone; the child answers.',
                         'Twenty-five minutes, three children we are trying not to intubate: an infant with bronchiolitis, a boy with pneumonia, a girl just extubated. Each starts at the bedside: set the support on your phone, commit to an order, and see what the child does. The physiology comes in as the cases need it.')
    out += bd.join_slide(code, 'Scan the code with your phone camera to join; no account needed. Or open the app, tap Live session and type NIV.')
    out += niv_cases_body(code)
    out += bd.reuse('niv.html', 'Takeaways')
    out += bd.close_slide('Fit the mask to the <em>child</em>', 'All three children are in the app: Cases · Sim scenarios 13, 14 and 15.',
                          'Fit the mask to the child, then set the pressures, then watch the hour. Anaya, Ishaan and Zara are simulator scenarios thirteen to fifteen in the app. Thank you.', 'NIV')
    out += bd.appendix('niv.html', 'Part 1', 'Takeaways', drop=('Title', 'Plan', 'Try it', 'Thank you', 'Part 1', 'Part 2', 'Part 3', 'Part 4', 'Part 5'))
    return bd.shell('Non-invasive ventilation · three cases', out, code)


def ltv_body(code):
    """The five long-term ventilation cases, as in talks/ltv-cases.html, with the LTV theory woven in."""
    out = ''
    for d in bd.LTV2:
        if d['id'] == 'ry0':
            out += bd.opener('riya_case', 'Case 8 of 8', 'Riya: two failed <em>extubations</em>',
                             ['Born at 28 weeks · 9 months, 6 kg', 'Ventilated 22 days; stridor after each extubation'], 'riya1_ward_round',
                             'Riya, nine months, born at twenty-eight weeks. Ventilated since admission with a respiratory infection; two extubations, both failed with stridor and a rising CO2. She carries us through the tracheostomy: the decision, the emergencies, and home.', code)
        out += bd.stage_slides(d, code)
        for t in d['theory']:
            if (SRC_LTV, t) not in bd.USED:
                out += bd.reuse(SRC_LTV, t)
    return out


def build_joint():
    code = 'NLV'
    out = bd.title_slide('VentCourse · Modules 04 and 09 · NIV and long-term ventilation · 45 min', 'From the mask in the PICU to the <em>home</em>',
                         'Eight children at the bedside. You set the support; the child answers.',
                         'Forty-five minutes, eight children. The first three are acute: the infant with bronchiolitis, the boy with pneumonia, the girl just extubated. Then five who need ventilation for weeks, months or for life: the baby with BPD, the boy with Duchenne, the baby with SMA, the girl with Guillain–Barré and Riya with her tracheostomy. The same masks and machines, a different question each time: will this child need it tomorrow?')
    out += bd.join_slide(code, 'Scan the code to join; no account needed. Or open the app, tap Live session and type NLV.')
    body = niv_cases_body(code)
    body = body.replace('Case 1 of 3', 'Case 1 of 8').replace('Case 2 of 3', 'Case 2 of 8').replace('Case 3 of 3', 'Case 3 of 8')
    out += body
    out += divider('Bridge', 'From acute to long term', 'When the mask goes <em>home</em>', 'Same machine, a different question',
                   'The same masks and the same bilevel machines, but a different question. In the PICU we ask whether NIV will carry the child for hours or days until the cause turns. In the next five children the cause will not turn quickly: the pump is weak, the airway floppy, the lungs chronically scarred. Then the questions are how long, through which airway, and how to get home.')
    ltv = ltv_body(code)
    for a, b in [('Case 1 of 5', 'Case 4 of 8'), ('Case 2 of 5', 'Case 5 of 8'), ('Case 3 of 5', 'Case 6 of 8'), ('Case 4 of 5', 'Case 7 of 8'), ('Case 5 of 5', 'Case 8 of 8')]:
        ltv = ltv.replace(a, b)
    out += ltv
    out += bullets('Takeaways', 'Take <em>home</em>', 'Six lines',
                   ['High-flow, review at 1–2 h, then CPAP', 'Fit the mask, the stomach, the timing', 'At one hour, decide: fail early', 'Oxygen is not ventilation', 'PMV: 21 days, NIV counts', 'Tracheostomy: for whom, not when'],
                   'Six lines. High-flow first, reviewed at one to two hours, then CPAP. Make NIV fit the child: the mask, the stomach, the timing, the fear. At the one-hour review, decide; failing early is safer than failing late. Oxygen is not ventilation, in the PICU or at home. Prolonged ventilation is twenty-one days at six hours a day, and NIV counts. And decide the tracheostomy on trajectory: for whom, not when.', size=44)
    out += bd.close_slide('Oxygen is not <em>ventilation</em>', 'All eight children are in the app: Cases · Sim scenarios 03 to 07 and 13 to 15, and the tracheostomy case discussion.',
                          'Eight children, one thread: support the breathing the child cannot do, through an interface that fits, for as long as the illness needs, and know when the answer has changed. All eight are in the app. Thank you.', 'NIV and long-term ventilation')
    out += bd.appendix('niv.html', 'Part 1', 'Takeaways', drop=('Title', 'Plan', 'Try it', 'Thank you', 'Takeaways', 'Part 1', 'Part 2', 'Part 3', 'Part 4', 'Part 5'))
    out += bd.appendix(SRC_LTV, 'Plan', 'Riya')
    return bd.shell('NIV and long-term ventilation · eight cases', out, code)


def write_live(entries):
    p = os.path.join(APP, 'index.html')
    s = open(p).read()
    a = s.index('// LIVE-START'); b = s.index('// LIVE-END')
    m = re.search(r'const LIVE = (\{.*\});', s[a:b], re.S)
    live = json.loads(m.group(1))
    live.update(entries)
    new = '// LIVE-START (generated from the CP interactions talk builder and tools/build_decks.py)\nconst LIVE = ' + json.dumps(live, ensure_ascii=False) + ';\n'
    open(p, 'w').write(s[:a] + new + s[b:])


if __name__ == '__main__':
    talks = os.path.join(APP, 'talks')
    full = bd.shell('Non-invasive ventilation', full_talk(), 'NIVT', thumb_from='cp-interactions.html')
    open(os.path.join(talks, 'niv.html'), 'w').write(full)
    bd.SRC['niv.html'] = full
    print('niv.html', len(full), full.count('<section '), 'slides')
    bd.USED.clear(); cases = build_cases()
    open(os.path.join(talks, 'niv-cases.html'), 'w').write(cases)
    print('niv-cases.html', len(cases), cases.count('<section '), 'slides')
    bd.USED.clear(); joint = build_joint()
    open(os.path.join(talks, 'niv-ltv.html'), 'w').write(joint)
    print('niv-ltv.html', len(joint), joint.count('<section '), 'slides')
    keep = {k: v for k, v in bd.LIVE_OUT.items() if k[:3] in ('nb1', 'nb2', 'np1', 'np2', 'nx1', 'nx2') or k in ('anaya_case', 'ishaan_case', 'zara_case')}
    write_live(keep)
    print('LIVE entries added', len(keep))
