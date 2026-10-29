#!/usr/bin/env python3
"""Build the ARDS and asthma live branching deck (talks/ards-asthma.html, room ARDS) from the app's two case discussions.

    python3 tools/build_aa.py

Each stage: history and bedside (slide 1, phones set the support and order) → the room (word cloud of settings, percentages,
how many patients improve, stay, worsen or crash) → the response (right order, why). Every phone follows its own patient:
the severity of its orders and settings changes its monitor and carries into the next stage. Grades and ranges: tools/aadata.py.
"""
import os, re, sys, json, subprocess, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_decks as bd
from aadata import ARDS, ASTHMA

APP = bd.APP
e, MONO = bd.e, bd.MONO
bd.SRC['disease-specific.html'] = open(os.path.join(APP, 'talks', 'disease-specific.html')).read()
SC = json.loads(subprocess.run(['node', '-e', "const L=require('./tools/load.js')('index.html').__exp; process.stdout.write(JSON.stringify({S:L.SCENARIOS, I:null}))"],
                               cwd=APP, capture_output=True, text=True, check=True).stdout)['S']
SCB = {z['id']: z for z in SC}
ILL = {'sc-ards': ['a1_er_mask', 'a2_niv_failing', 'a3_just_intubated', 'a4_desaturating', 'a4_desaturating', 'a4_desaturating', 'a5_fighting', 'a6_day2_round', 'a7_day2_worse', 'a8_prone'],
       'sc-asthma': ['b1_er_quiet_chest', 'b2_induction_ready', 'b3_bagging_stiff', 'b4_ventilated_settled', 'b5_starts_to_trigger', 'b6_sudden_desat', 'b4_ventilated_settled']}

SET_KEYS = ('VT', 'RR', 'I:E', 'PEEP', 'FiO₂', 'PS', 'Pinsp', 'Ti')


def parse_vent(v):
    if not v:
        return None
    parts = [p.strip() for p in v.split('·')]
    mode = parts[0]
    st, ms = [], []
    for p in parts[1:]:
        m = re.match(r'(measured auto-PEEP|auto-PEEP|[A-Za-zÀ-ÿ₀-₉:]+(?:\s\(titrated\))?)\s+(.+)', p)
        if not m:
            ms.append(['', p]); continue
        k, val = m.group(1), m.group(2)
        k = k.replace('measured ', '')
        if not re.search(r'\d', val):  # 'intermittent Ppeak alarm', 'no auto-PEEP': words, not numbers
            ms.append(['', p]); continue
        if k.split()[0] in SET_KEYS:
            st.append([k.split()[0], val.replace(' mL', '').replace(' (titrated)', '')])
        else:
            ms.append([k.replace('Ppeak', 'Peak').replace('Pplat', 'Plateau'), val])
    long = {'PRVC': 'AC · PRVC', 'VC': 'AC · Volume control', 'PC': 'AC · Pressure control', 'NIV': 'NIV by mask'}.get(mode, mode)
    return {'mode': mode, 'modeLong': long, 'set': st, 'meas': [m for m in ms if m[0]][:3], 'extra': [m[1] for m in ms if not m[0]]}


def mon_of(vit):
    out, notes = [], []
    for k, v in vit or []:
        m = re.match(r'([\d.]+(?:[–-][\d.]+)?(?:/\d+)?)\s*%?\s*(.*)', v)
        if k in ('Temp', 'Fluid balance', 'CRT', 'OI', 'P/F') or not m:
            out.append([k, v]); continue
        out.append([k, m.group(1)])
        if m.group(2): notes.append(f'{k} {v}')
    return out, notes


def first_sentence(t):
    m = re.match(r'(.+?[.!?])(\s|$)', t or '')
    return m.group(1) if m else (t or '')


CXR = {}
_pic = bd.picture
def picture(n, h=320, sid=None):
    """The patient, and the X-ray beside it when the stage has one."""
    if sid in CXR:
        return (f'<div style="flex:none; height:{h}px; display:grid; grid-template-columns:1fr 1fr; gap:10px;">'
                f'<div style="border-radius:6px; overflow:hidden; background:#F4EFE6; border:1px solid var(--border-subtle);"><img src="{bd.ipath(n)}" alt="" style="display:block; width:100%; height:100%; object-fit:cover;"></div>'
                f'<div style="border-radius:6px; overflow:hidden; background:#0E1012;"><img src="../{CXR[sid]}" alt="Chest X-ray" style="display:block; width:100%; height:100%; object-fit:contain;"></div></div>')
    return _pic(n, h, sid)
bd.picture = picture


def table_html(tb):
    th = ''.join(f'<th style="{MONO} font-size:14px; color:var(--text-secondary); padding:6px 6px; text-align:center; border-bottom:1px solid var(--border-default);">{e(h)}</th>' for h in tb['head'])
    rows = ''.join('<tr>' + ''.join(f'<td style="font:500 20px/1.2 var(--font-mono); padding:6px; text-align:center; border-bottom:1px solid var(--border-subtle);">{e(c)}</td>' for c in r) + '</tr>' for r in tb['rows'][:5])
    return (f'<div style="flex:none; background:#FFFFFF; border:1px solid var(--border-subtle); border-radius:6px; padding:10px 12px;">'
            f'<table style="width:100%; border-collapse:collapse;"><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table>'
            f'<span style="display:block; margin-top:6px; font-size:15px; line-height:1.35; color:var(--text-secondary);">{e(tb.get("note", ""))}</span></div>')


VG = {}   # vent-graphics scenarios written for this deck: one per screen, from that screen's own settings


def num(x, d=None):
    m = re.search(r'-?\d+(?:\.\d+)?', str(x or ''))
    return float(m.group(0)) if m else d


def scenario(key, v, kg, kind='ards', extra=None):
    """A waveform that matches the settings and the measured numbers on the screen."""
    S = {k: val for k, val in v['set']}
    M = {k: val for k, val in v['meas']}
    rr = (extra or {}).get('rr') or num(S.get('RR'), 30)
    ie = re.match(r'1:(\d+(?:\.\d+)?)', S.get('I:E', '') or '')
    ti = round(60 / rr / (1 + float(ie.group(1))), 2) if ie else round(min(1.0, 60 / rr / 3), 2)
    peep = num(S.get('PEEP'), 5)
    vt = num(S.get('VT'), 7 * kg)
    plat = num(M.get('Plateau'), None)
    peak = num(M.get('Peak') or M.get('PIP'), None)
    if plat is None: plat = (peak - 4) if peak else peep + 16
    C = max(1.5, min(60, vt / max(4, plat - peep)))
    R = 25 if kind == 'ards' else 60
    mode = v['mode']
    sc = {'peep': peep, 'C': round(C, 1), 'R': R, 'rr': rr, 'window': round(3 * 60 / rr, 2), 'scale': {'v': round(vt * 1.6)}}
    if mode == 'NIV':
        sc.update({'mode': 'PS', 'ps': num(S.get('PS'), 10), 'rr': rr, 'efforts': [{'t': round(0.22 + i * 60 / rr, 3), 'amp': 7, 'dur': round(min(0.5, 25 / rr), 2)} for i in range(3)]})
    elif mode == 'VC':
        if peak and plat:
            fl = vt / 1000 / max(0.2, ti - 0.15)
            sc['R'] = round(max(10, (peak - plat) / fl))
        sc.update({'mode': 'VC', 'vt': vt, 'ti': ti, 'pause': 0.15})
    else:  # PRVC and PC: a decelerating, pressure-limited breath that delivers the set VT
        sc.update({'mode': 'PC', 'pinsp': round(plat - peep, 1), 'ti': ti})
    if extra: sc.update(extra)
    VG[key] = sc
    return key


def write_vg():
    p = os.path.join(APP, 'vent-graphics.js'); t = open(p).read()
    block = '    // AA-START (ARDS and asthma live deck: one screen each, from tools/build_aa.py)\n' + ''.join(f"    '{k}': {json.dumps(v)},\n" for k, v in VG.items()) + '    // AA-END\n'
    if '// AA-START' in t:
        t = t[:t.index('    // AA-START')] + block + t[t.index('    // AA-END') + len('    // AA-END\n'):]
    else:
        t = t.replace('    // VS-START', block + '    // VS-START', 1)
    open(p, 'w').write(t)


def bedside_slide(d, sid, ords, T, n, st, tag):
    pic = (f'<div style="flex:none; height:{390 if sid in CXR else 470}px; border-radius:6px; overflow:hidden; background:#F4EFE6; border:1px solid var(--border-subtle);"><img src="{bd.ipath(n)}" alt="The patient" style="display:block; width:100%; height:100%; object-fit:cover;"></div>')
    if sid in CXR:
        pic += f'<div style="flex:1; min-height:0; border-radius:6px; overflow:hidden; background:#0E1012;"><img src="../{CXR[sid]}" alt="Chest X-ray" style="display:block; width:100%; height:100%; object-fit:contain;"></div>'
    gas = ' · '.join(f'{k} {v}' for k, v in (st.get('abg') or []))
    exam = ''.join(f'<span style="font-size:24px; line-height:1.35; color:var(--text-secondary);">{e(x)}</span>' for x in (st.get('exam') or [])[:3])
    mid = (f'<div style="display:flex; flex-direction:column; gap:20px; min-width:0;">{bd.monitor(d["scr"]["mon"], 1.55)}'
           f'<span style="font-size:28px; line-height:1.35;">{e(d["hist"])}</span>{exam}'
           + (f'<span style="font-family:var(--font-mono); font-size:22px; color:var(--text-accent);">Gas · {e(gas)}</span>' if gas else '') + '</div>')
    foot = ''
    if T:
        foot = (f'<div style="flex:none; display:flex; flex-direction:column; gap:8px; border:1px dashed var(--text-accent); border-radius:6px; padding:14px 18px; margin-top:8px;">'
                f'<span style="{MONO} font-size:18px; color:var(--text-accent);">On your phone</span><span style="font-size:26px; line-height:1.3;">{e(T["ask"])}, then tap your order</span>'
                f'<span data-set-count style="{MONO} font-size:18px; color:var(--text-secondary);">Waiting for settings</span></div>')
    body = (bd.header(d['eyebrow'], d['head'], tag) +
            f'<div style="flex:1; min-height:0; display:grid; grid-template-columns:600px minmax(0,1fr) 470px; gap:36px;">'
            f'<div style="display:flex; flex-direction:column; gap:14px; min-height:0;">{pic}</div>{mid}'
            f'<div style="display:flex; flex-direction:column; gap:16px; min-width:0;"><span style="{MONO} font-size:20px; color:var(--text-secondary);">Your order</span>{bd.order_cards(ords)}' + foot + '</div></div>')
    return bd.section(bd.plain(d['head']), body, d['hist'] + ' ' + st['q'], live=sid, mode='ask', setq=T and T['q'])


def console_slide(d, sid, scr, T, label, tag, live, mode, extra=''):
    body = (bd.header(d['eyebrow'], d['head'], tag) +
            f'<div style="flex:1; min-height:0; display:flex; justify-content:center;"><div style="width:1500px; height:100%; min-height:0;">{bd.device(scr, foot=extra)}</div></div>')
    note = '; '.join(scr.get('extra') or [])
    return bd.section(label, body, 'The ventilator, full screen: mode, settings, the waveforms and the measured values.' + (' ' + note if note else ''), live=live, mode=mode, setq=T and T['q'], pad='56px 72px 120px')


def room_slide(d, sid, ords, T, rule, sevmap):
    left = ''
    if T:
        left = (f'<div style="display:flex; flex-direction:column; gap:18px; min-width:0;">'
                f'<span style="{MONO} font-size:20px; color:var(--text-secondary);">Settings the room sent · <span data-set-count>Waiting for settings</span></span>'
                f'<div data-set-cloud style="display:flex; flex-wrap:wrap; gap:12px; align-content:flex-start; min-height:300px;"></div>'
                f'<span style="{MONO} font-size:20px; color:var(--text-secondary);">Support chosen</span><div data-set-pct style="display:flex; flex-direction:column; gap:10px;"></div>'
                f'<span style="{MONO} font-size:20px; color:var(--text-secondary);">Their patients on these settings</span><div data-sev-set></div></div>')
    right = (f'<div style="display:flex; flex-direction:column; gap:14px; min-width:0;"><span style="{MONO} font-size:20px; color:var(--text-secondary);">Orders</span>{bd.order_cards(ords)}'
             f'<span style="{MONO} font-size:20px; color:var(--text-secondary); margin-top:10px;">Their patients after these orders</span><div data-sev-ord></div></div>')
    grid = f'<div style="flex:1; min-height:0; display:grid; grid-template-columns:{"minmax(0,1.15fr) minmax(0,1fr)" if T else "minmax(0,1fr)"}; gap:56px;">{left}{right}</div>'
    body = bd.header(d['eyebrow'], d['head'], 'The room')
    sec = bd.section(bd.plain(d['head']) + ' · the room', body + grid,
                     'The room, live: every setting the phones sent, the support chosen in percent, and how the patients are doing on what the room chose. We judge by how sick the patients got, not by who picked the right box. Each phone is already showing its own patient.',
                     live=sid, mode='cloud', setq=T and T['q'])
    attrs = f' data-sev="{e(json.dumps(sevmap))}"' + (f' data-rule="{e(json.dumps(rule))}"' if rule else '')
    return sec.replace('<section ', '<section' + attrs + ' ', 1)


def response_slide(d, sid, ords, after, T):
    body = (bd.header(d['eyebrow'], d['head'], 'The response') +
            f'<div style="flex:1; min-height:0; display:grid; grid-template-columns:minmax(0,1fr) 560px; gap:44px;">'
            f'<div style="display:flex; flex-direction:column; gap:14px; min-width:0;"><span style="{MONO} font-size:20px; color:var(--text-secondary);">Each order · the response</span>{bd.order_cards(ords, reveal=True)}</div>'
            f'<div style="display:flex; flex-direction:column; gap:18px; min-width:0;">{bd.monitor(after["mon"], 1.2)}'
            f'<span style="{MONO} font-size:20px; color:var(--text-accent);">What happened</span><span style="font-size:30px; line-height:1.3;">{e(after["happen"])}</span>'
            + (f'<span style="{MONO} font-size:20px; color:var(--text-secondary);">Why</span><span style="font-size:26px; line-height:1.35; color:var(--text-secondary);">{e(after["why"])}</span>' if after.get('why') else '') +
            '</div></div>')
    return bd.section(bd.plain(d['head']) + ' · response', body, 'The response. ' + after['happen'] + ' ' + after.get('why', ''), live=sid + '_r', mode='show', results=sid, setq=T and T['q'])


def table_slide(label, eyebrow, head, cols, rows, note, notes, tag=''):
    th = ''.join(f'<th style="{MONO} font-size:18px; color:var(--text-secondary); padding:10px 12px; text-align:center; border-bottom:2px solid var(--border-default);">{c}</th>' for c in cols)
    trs = ''.join('<tr>' + ''.join(f'<td style="font:500 30px/1.2 var(--font-mono); padding:12px; text-align:center; border-bottom:1px solid var(--border-subtle);{" color:var(--text-accent);" if j == 0 else ""}">{c}</td>' for j, c in enumerate(r)) + '</tr>' for r in rows)
    body = (bd.header(eyebrow, head, tag) + f'<table style="width:100%; border-collapse:collapse; table-layout:fixed;"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>'
            + (f'<span style="font-size:26px; line-height:1.4; color:var(--text-secondary);">{note}</span>' if note else ''))
    return bd.section(label, body, notes, pad='64px 96px')


def ardsnet():
    lo_f = ['0.3', '0.4', '0.4', '0.5', '0.5', '0.6', '0.7', '0.7', '0.7', '0.8', '0.9', '0.9', '0.9', '1.0']
    lo_p = ['5', '5', '8', '8', '10', '10', '10', '12', '14', '14', '14', '16', '18', '18–24']
    hi_f = ['0.3', '0.3', '0.3', '0.3', '0.3', '0.4', '0.4', '0.5', '0.5', '0.5–0.8', '0.8', '0.9', '1.0', '1.0']
    hi_p = ['5', '8', '10', '12', '14', '14', '16', '16', '18', '20', '22', '22', '22', '24']
    rows = [['Lower PEEP · FiO₂'] + lo_f, ['Lower PEEP · PEEP'] + lo_p, ['Higher PEEP · FiO₂'] + hi_f, ['Higher PEEP · PEEP'] + hi_p]
    th = ''.join(f'<th style="padding:0;"></th>' for _ in range(15))
    trs = ''.join('<tr>' + ''.join((f'<td style="{MONO} font-size:17px; color:var(--text-accent); padding:14px 10px; text-align:left; border-bottom:1px solid var(--border-subtle); width:250px;">{c}</td>' if j == 0 else
                                   f'<td style="font:500 26px/1.1 var(--font-mono); padding:14px 4px; text-align:center; border-bottom:1px solid var(--border-subtle);{" background:rgba(176,68,40,.07);" if "PEEP · PEEP" in r[0] else ""}">{c}</td>') for j, c in enumerate(r)) + '</tr>' for r in rows)
    body = (bd.header('PEEP titration · a starting point', 'The ARDSNet <em>tables</em>', 'ARDSNet 2000 · ALVEOLI 2004') +
            f'<table style="width:100%; border-collapse:collapse; table-layout:fixed;"><colgroup><col style="width:250px">' + '<col>' * 14 + f'</colgroup><tbody>{trs}</tbody></table>'
            '<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:24px;">'
            '<div style="border:1px solid var(--border-default); border-radius:4px; padding:20px 24px; font-size:26px; line-height:1.35;">Read across: the FiO₂ she needs gives the least PEEP to pair with it.</div>'
            '<div style="border:1px solid var(--border-default); border-radius:4px; padding:20px 24px; font-size:26px; line-height:1.35;">Our girl at FiO₂ 1.0: the lower table says 18–24. Her best compliance was at 12.</div>'
            '<div style="border:1px solid var(--border-default); border-radius:4px; padding:20px 24px; font-size:26px; line-height:1.35;">PALICC-2: use the table or higher, then titrate to compliance, oxygenation and the blood pressure.</div></div>')
    return bd.section('ARDSNet table', body, 'The ARDSNet lower and higher PEEP / FiO2 tables, as tables. A starting point, not a target: our girl on FiO2 1.0 would get PEEP 18 to 24 from the lower table, yet her best compliance was at 12. PALICC-2 accepts the table or higher, then titration.', pad='64px 96px')


def deadspace():
    rows = [['6', '50', '36', '(50 − 36) ÷ 50', '0.28'], ['12', '50', '45', '(50 − 45) ÷ 50', '0.10']]
    th = ''.join(f'<th style="{MONO} font-size:17px; color:var(--text-secondary); padding:10px; text-align:center; border-bottom:2px solid var(--border-default);">{c}</th>' for c in ['PEEP', 'PaCO₂', 'EtCO₂', 'AVDSf', 'Result'])
    trs = ''.join('<tr>' + ''.join(f'<td style="font:500 34px/1.2 var(--font-mono); padding:16px 10px; text-align:center; border-bottom:1px solid var(--border-subtle);{" color:var(--text-accent);" if j == 4 else ""}">{c}</td>' for j, c in enumerate(r)) + '</tr>' for r in rows)
    body = (bd.header('Our girl · before and after the titration', 'Dead space <em>fraction</em>', 'Calculate') +
            '<div style="display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1.2fr); gap:56px; flex:1; min-height:0;">'
            '<div style="display:flex; flex-direction:column; gap:22px;">'
            '<span style="font-family:var(--font-display); font-size:60px; line-height:1.1;">AVDSf = (PaCO₂ − EtCO₂) ÷ PaCO₂</span>'
            '<span style="font-size:28px; line-height:1.4;">Alveolar dead space fraction: the share of ventilated alveoli that get no blood flow.</span>'
            '<span style="font-size:28px; line-height:1.4;">Bohr–Enghoff (physiological): (PaCO₂ − PēCO₂) ÷ PaCO₂, with mixed expired CO₂ from volumetric capnography.</span>'
            '<span style="font-size:28px; line-height:1.4; color:var(--text-secondary);">Recruiting PEEP lowers it; over-distending PEEP raises it again. A high dead space fraction marks a sicker child (Ghuman, PCCM 2012).</span></div>'
            f'<div style="display:flex; flex-direction:column; gap:20px;"><table style="width:100%; border-collapse:collapse;"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>'
            '<span style="font-size:24px; line-height:1.4; color:var(--text-secondary);">PaCO₂ 50 on both gases; EtCO₂ from the titration sheet at the PEEP 6 and PEEP 12 steps. Same rate.</span></div></div>')
    return bd.section('Dead space fraction', body, 'Ask the room to calculate it before the answer. At PEEP 6: PaCO2 50, EtCO2 36, about 0.28. At PEEP 12: PaCO2 50, EtCO2 45, about 0.10. Recruitment cut the dead space; at PEEP 14 the EtCO2 gap would open again as she over-distends.', pad='64px 96px')


def pocus_day2():
    slots = ''.join(bd.video_slot(n, c, 520) for n, c in [('ivc-normal', 'IVC: normal size, varies with the breath'), ('a4c-normal', 'Apical four-chamber: normal squeeze'), ('subcostal-normal', 'Subcostal: no effusion')])
    body = bd.header('Case 1 · Day 2 · the echo on the round', 'POCUS before the <em>bolus</em>', 'Video') + f'<div style="flex:1; min-height:0; display:flex; gap:28px; align-items:center;">{slots}</div>'
    return bd.section('Day 2 · POCUS', body, 'The round echo: an adequate IVC and a normal heart. Perfusion is adequate, so the low-normal blood pressure does not need a bolus; more fluid goes into a wet lung. Lung ultrasound next: B-lines and consolidation, reassessed after every change.')


SPECIAL = {'#ardsnet': ardsnet, '#deadspace': deadspace, '#pocus-day2': pocus_day2}


def build_case(C, n_case, code):
    z = SCB[C['id']]
    kind = 'ards' if C['id'] == 'sc-ards' else 'asthma'
    stages = [s for s in z['stages'] if s.get('opts')]
    ids = [('ar' if kind == 'ards' else 'as') + str(i) for i in range(len(stages))]
    out = bd.opener(f"{C['id']}_case", f'Case {n_case} of 2', C['name'].split(' · ')[0] + ', <em>' + C['name'].split(' · ')[1] + '</em>', C['open'],
                    ILL[C['id']][0], ' '.join(C['open']) + '. History only: the room works out the rest. Every phone follows its own patient from here.', code)
    course, last_v, last_key, last_mon = [], None, None, None
    for i, (st, sid) in enumerate(zip(stages, ids)):
        A = C['stages'][i]
        nxt = stages[i + 1] if i + 1 < len(stages) else None
        mon, mnotes = mon_of(st.get('vit'))
        if not mon and last_mon: mon = last_mon  # no new vitals at this stage: the monitor keeps the last numbers
        if mon: last_mon = mon
        v = parse_vent(st.get('vent'))
        on_vent = i >= 2  # both children are intubated from stage 3 on
        if v:
            wx = dict(A.get('wave_extra') or {})
            if v['mode'] == 'NIV': wx['rr'] = num(dict(st.get('vit') or []).get('RR'), 30)
            key = scenario(f'aa-{sid}', v, C['kg'], kind, wx or None)
            last_v, last_key = v, key
        elif on_vent and last_v and not st['t'].startswith('Intubated'):
            v, key = last_v, last_key
        else:
            key = None
        if sid == 'as5' and last_v:  # sudden collapse: the same settings, the chest full of trapped gas
            key = scenario('aa-as5', last_v, C['kg'], kind, {'R': 160, 'C': 4, 'rr': 12})
        gas = st.get('abg') or []
        scr = {'mode': v['mode'] if v else 'MASK', 'modeLong': v['modeLong'] if v else st['t'], 'set': v['set'] if v else [],
               'meas': (v['meas'] if v else []) + [[k, val] for k, val in gas if k in ('pH', 'PaCO₂', 'PaO₂')][:2 if v else 3],
               'wave': key, 'mon': mon or [['Status', 'See the history']], 'note': '; '.join(v['extra']) if v else '', 'msg': ''}
        if not v:
            scr['msg'] = 'Waiting for your settings' if st['t'].startswith('Intubated') else 'Not on the ventilator'
        if sid == 'as5': scr['msg'] = 'High-pressure alarm'
        if st.get('img'): CXR[sid] = st['img']
        right = next(o for o in st['opts'] if o[1])
        nv = parse_vent(nxt.get('vent')) if nxt else None
        nmon = mon_of(nxt.get('vit'))[0] if nxt and nxt.get('vit') else mon
        after = {'mon': nmon or mon, 'happen': first_sentence(right[2]), 'why': first_sentence(st.get('teach', ''))}
        if nv:
            akey = scenario(f'aa-{sid}-a', nv, C['kg'], kind)
            after.update({'mode': nv['mode'], 'modeLong': nv['modeLong'], 'set': nv['set'], 'meas': nv['meas'], 'wave': akey})
        d = {'id': sid, 'eyebrow': f'Case {n_case} · ' + C['name'], 'head': re.sub(r'(\S+)$', r'<em>\1</em>', st['t']), 'hist': st['story'],
             'scr': scr, 'short': A['short'], 'after': after, 'theory': C['theory'][i] if i < len(C['theory']) else [], 'setq': A['setq']}
        bd.ST[sid] = {'story': st['story'], 'live': {'q': st['q'], 'opts': st['opts']}, 'illus': ILL[C['id']][min(i, len(ILL[C['id']]) - 1)]}
        k = bd.rot(sid)
        sevmap = {'ABCD'[(j - k) % 4]: A['sev'][j] for j in range(4)}
        ords = bd.orders(sid, A['short'])
        T = bd.set_task(d, sid)
        bd.stage_slides(d, code)  # phone entries only; the slides are laid out below
        vent_task = bool(T) and set(A['setq']['ifaces']) == {'VENT'}
        n_pic = ILL[C['id']][min(i, len(ILL[C['id']]) - 1)]
        out += bedside_slide(d, sid, ords, None if vent_task else T, n_pic, st, 'Live · the bedside')
        if v or vent_task:
            setfoot = ''
            if vent_task:
                setfoot = (f'<div style="flex:none; display:flex; justify-content:space-between; align-items:baseline; gap:16px; border:1px dashed var(--text-accent); border-radius:6px; padding:12px 18px;">'
                           f'<span style="font-size:28px;"><span style="{MONO} font-size:18px; color:var(--text-accent);">On your phone · </span>{e(T["ask"])}</span>'
                           f'<span data-set-count style="{MONO} font-size:18px; color:var(--text-secondary);">Waiting for settings</span></div>')
            if st.get('table'):
                setfoot = table_html(st['table']) + setfoot
            out += console_slide(d, sid, scr, T, bd.plain(d['head']) + ' · ventilator', 'Live · the ventilator', sid, 'ask', setfoot)
        j = None
        out += room_slide(d, sid, ords, T, A['rule'], sevmap)
        out += response_slide(d, sid, ords, after, T)
        if after.get('set'):
            ascr = {**scr, **{kk: after[kk] for kk in ('mode', 'modeLong', 'set', 'meas', 'wave') if kk in after}, 'mon': after['mon'], 'msg': ''}
            sumfoot = ''
            if T:
                sumfoot = (f'<div style="flex:none; border-top:1px solid var(--border-subtle); padding-top:10px; display:flex; gap:16px; align-items:baseline;">'
                           f'<span style="{MONO} font-size:17px; color:var(--text-accent); flex:none;">The room set</span>'
                           f'<span data-set-summary style="font-size:24px; line-height:1.35; color:var(--text-secondary);">No settings sent</span></div>')
            out += console_slide(d, sid, ascr, T, bd.plain(d['head']) + ' · the ventilator after', 'The settings · after', sid + '_r', 'show', sumfoot)
        bd.LIVE_OUT[sid].update({'sev': {L: [A['sev'][jj], st['opts'][jj][2]] for jj in range(4) for L in ['ABCD'[(jj - k) % 4]]},
                                 'monOk': after['mon'], 'kg': C['kg']})
        if A['rule']: bd.LIVE_OUT[sid]['rule'] = A['rule']
        if i: bd.LIVE_OUT[sid]['prev'] = ids[i - 1]
        course.append((sid, st['t'], sevmap, A['rule']))
        for t in d['theory']:
            out += SPECIAL[t]() if t in SPECIAL else bd.reuse('disease-specific.html', t)
    # the course: the room's patients stage by stage, and each phone's own
    key = f"{C['id']}_course"
    bd.LIVE_OUT[key] = {'t': "Your patient's course", 'lines': ['Each stage, how your patient did on your orders and settings.'], 'course': [[sid, t] for sid, t, *_ in course]}
    rows = ''.join(f'<div data-cq="{sid}" data-sev="{e(json.dumps(sm))}"' + (f' data-rule="{e(json.dumps(rl))}"' if rl else '') +
                   f' style="display:grid; grid-template-columns:420px minmax(0,1fr); gap:24px; align-items:start;"><span style="font-size:26px; line-height:1.25;">{e(t)}</span><div data-bar-sev></div></div>'
                   for sid, t, sm, rl in course)
    body = bd.header(f'Case {n_case} · ' + C['name'], "The room's <em>course</em>", 'Debrief') + f'<div style="flex:1; min-height:0; display:flex; flex-direction:column; gap:16px; overflow:hidden;">{rows}</div>'
    out += bd.section(f"Case {n_case} · the room's course", body, 'Stage by stage, how the room\'s patients did: improving, no change, worse, life-threatening, from the orders and the settings together. Each phone shows its own patient\'s course.', live=key, mode='course', pad='56px 72px 64px')
    deb = (z['stages'][-1].get('debrief') or [])
    if deb:
        items = ''.join(f'<li style="font-size:30px; line-height:1.35; margin-bottom:12px;">{e(x)}</li>' for x in deb)
        out += bd.section(f'Case {n_case} · take-aways', bd.header(f'Case {n_case} · ' + C['name'], 'What to <em>keep</em>', 'Debrief') + f'<ol style="margin:0; padding-left:34px;">{items}</ol>',
                          'The take-aways, one line each.', pad='56px 96px 64px')
    return out


def build():
    code = 'ARDS'
    out = bd.title_slide('VentCourse · Difficult ventilatory scenarios', 'Two children, two <em>lungs</em>',
                         'You set the support and give the orders on your phone. Your patient answers you; the room\'s patients answer us.',
                         'Two children on the ventilator. Every phone follows its own patient: the orders and settings each person chooses change that patient, and at fixed points the story moves on for everyone. We judge by how sick the patients got, not by who picked the right box.')
    out += bd.join_slide(code, 'Scan the code to join; no account needed. Or open the app, tap Live session and type ARDS. Late joiners: the code is on every slide.')
    out += build_case(ARDS, 1, code)
    out += build_case(ASTHMA, 2, code)
    for t in ['Side by side', 'Takeaways']:
        out += bd.reuse('disease-specific.html', t)
    out += bd.close_slide('Judge by the <em>patient</em>', 'Both children are in the app: Cases · Discuss the decisions.',
                          'The patient tells you how you did. Both children are in the app as case discussions. Thank you.', 'Difficult ventilatory scenarios')
    out += bd.appendix('disease-specific.html', 'PARDS definition', 'Part 8')
    return bd.shell('Difficult ventilatory scenarios · live', out, code)


if __name__ == '__main__':
    bd.USED.clear(); bd._POCUS_DONE.clear()
    t = build()
    # Instrument Serif has no subscript digits: in serif text, draw ₂ as a small lowered 2
    SUB = '<span style="font-size:.6em; vertical-align:-.12em;">2</span>'
    def _sub(m):
        return re.sub(r'>([^<]*)<', lambda x: '>' + x.group(1).replace('₂', SUB) + '<', m.group(0))
    t = re.sub(r'<(h1|h2)\b[^>]*>.*?</\1>', _sub, t, flags=re.S)
    t = re.sub(r'<(span|div)\b[^>]*font-family:var\(--font-display\)[^>]*>[^<]*(?:<em>[^<]*</em>[^<]*)*</\1>', _sub, t)
    write_vg()
    open(os.path.join(APP, 'talks', 'ards-asthma.html'), 'w').write(t)
    secs = re.findall(r'<section [^>]*>', t)
    print('ards-asthma.html', len([x for x in secs if 'data-deck-skip' not in x]), 'visible of', len(secs))
    # write only this deck's phone entries
    p = os.path.join(APP, 'index.html'); s = open(p).read()
    a, b = s.index('// LIVE-START'), s.index('// LIVE-END')
    m = re.search(r'const LIVE = (\{.*\});', s[a:b], re.S)
    live = json.loads(m.group(1))
    live.update({k: v for k, v in bd.LIVE_OUT.items() if re.match(r'(ar|as)\d|sc-(ards|asthma)_|xards\d', k)})
    s = s[:a] + '// LIVE-START (generated from the CP interactions talk builder and tools/build_decks.py)\nconst LIVE = ' + json.dumps(live, ensure_ascii=False) + ';\n' + s[b:]
    open(p, 'w').write(s)
    print('LIVE entries', len([k for k in bd.LIVE_OUT if re.match(r'(ar|as)\d|sc-(ards|asthma)_|xards\d', k)]))
