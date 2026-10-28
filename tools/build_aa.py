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


def build_case(C, n_case, code):
    z = SCB[C['id']]
    stages = [s for s in z['stages'] if s.get('opts')]
    ids = [('ar' if C['id'] == 'sc-ards' else 'as') + str(i) for i in range(len(stages))]
    out = bd.opener(f"{C['id']}_case", f'Case {n_case} of 2', C['name'].split(' · ')[0] + ', <em>' + C['name'].split(' · ')[1] + '</em>', C['open'],
                    ILL[C['id']][0], ' '.join(C['open']) + '. History only: the room works out the rest. Every phone follows its own patient from here.', code)
    course = []
    for i, (st, sid) in enumerate(zip(stages, ids)):
        A = C['stages'][i]
        nxt = stages[i + 1] if i + 1 < len(stages) else None
        mon, mnotes = mon_of(st.get('vit'))
        v = parse_vent(st.get('vent'))
        gas = st.get('abg') or []
        meas = (v['meas'] if v else []) + [[k, val] for k, val in gas if k in ('pH', 'PaCO₂', 'PaO₂')][:3 if not v else 2]
        prev_v = parse_vent(stages[i - 1].get('vent')) if i else None
        scr = {'mode': v['mode'] if v else ('MASK' if i == 0 else 'TUBE'), 'modeLong': v['modeLong'] if v else st['t'],
               'set': v['set'] if v else [], 'meas': meas, 'wave': (st.get('trace') or {}).get('sc') if v else None,
               'mon': mon or [['Status', 'See the history']], 'note': '; '.join((st.get('exam') or [])[:2] + mnotes)[:160],
               'msg': 'Not on the ventilator' if not v else ''}
        if not v and (st.get('trace') or {}).get('sc'):  # tube in, the ventilator waiting: show the trace anyway
            scr['wave'] = st['trace']['sc']; scr['modeLong'] = 'Ventilator connected'
        elif not v and i >= 2:  # already on the ventilator: the last settings stay on the screen
            if prev_v and not st['t'].startswith('Intubated'):
                scr.update({'mode': prev_v['mode'], 'modeLong': prev_v['modeLong'], 'set': prev_v['set']})
            scr['msg'] = 'High-pressure alarm' if 'alarm' in st['story'].lower() else ('Waiting for your settings' if st['t'].startswith('Intubated') else 'Ventilator running')
        if st.get('img'): CXR[sid] = st['img']
        right = next(o for o in st['opts'] if o[1])
        nv = parse_vent(nxt.get('vent')) if nxt else None
        nmon = mon_of(nxt.get('vit'))[0] if nxt and nxt.get('vit') else mon
        after = {'mon': nmon or mon, 'happen': first_sentence(right[2]), 'why': first_sentence(st.get('teach', ''))}
        if nv: after.update({'mode': nv['mode'], 'modeLong': nv['modeLong'], 'set': nv['set'], 'meas': nv['meas'], 'wave': (nxt.get('trace') or {}).get('sc'),
                             'msg': '' if (nxt.get('trace') or {}).get('sc') else ('On NIV' if nv['mode'] == 'NIV' else 'Ventilator running')})
        d = {'id': sid, 'eyebrow': f'Case {n_case} · ' + C['name'], 'head': re.sub(r'(\S+)$', r'<em>\1</em>', st['t']), 'hist': st['story'],
             'scr': scr, 'short': A['short'], 'after': after, 'theory': C['theory'][i] if i < len(C['theory']) else [], 'setq': A['setq']}
        bd.ST[sid] = {'story': st['story'], 'live': {'q': st['q'], 'opts': st['opts']}, 'illus': ILL[C['id']][min(i, len(ILL[C['id']]) - 1)]}
        k = bd.rot(sid)
        sevmap = {'ABCD'[(j - k) % 4]: A['sev'][j] for j in range(4)}
        ords = bd.orders(sid, A['short'])
        T = bd.set_task(d, sid)
        s12 = bd.stage_slides(d, code)
        if st.get('table'):  # PEEP titration: the nurse's table in place of the monitor
            s12 = re.sub(r'<div style="flex:none; zoom:1\.42;"><x-import component-from-global-scope="bedside-monitor".*?</x-import></div>', table_html(st['table']).replace('\\', '\\\\'), s12, count=1)
        j = s12.index(f'<section data-live="{sid}_r"')
        out += s12[:j] + room_slide(d, sid, ords, T, A['rule'], sevmap) + s12[j:]
        bd.LIVE_OUT[sid].update({'sev': {L: [A['sev'][jj], st['opts'][jj][2]] for jj in range(4) for L in ['ABCD'[(jj - k) % 4]]},
                                 'monOk': after['mon'], 'kg': C['kg']})
        if A['rule']: bd.LIVE_OUT[sid]['rule'] = A['rule']
        if i: bd.LIVE_OUT[sid]['prev'] = ids[i - 1]
        course.append((sid, st['t'], sevmap, A['rule']))
        for t in d['theory']:
            out += bd.reuse('disease-specific.html', t)
    # the course: the room's patients stage by stage, and each phone's own
    key = f"{C['id']}_course"
    bd.LIVE_OUT[key] = {'t': "Your patient's course", 'lines': ['Each stage, how your patient did on your orders and settings.'], 'course': [[sid, t] for sid, t, *_ in course]}
    rows = ''.join(f'<div data-cq="{sid}" data-sev="{e(json.dumps(sm))}"' + (f' data-rule="{e(json.dumps(rl))}"' if rl else '') +
                   f' style="display:grid; grid-template-columns:420px minmax(0,1fr); gap:24px; align-items:start;"><span style="font-size:26px; line-height:1.25;">{e(t)}</span><div data-bar-sev></div></div>'
                   for sid, t, sm, rl in course)
    body = bd.header(f'Case {n_case} · ' + C['name'], "The room's <em>course</em>", 'Debrief') + f'<div style="flex:1; min-height:0; display:flex; flex-direction:column; gap:16px; overflow:hidden;">{rows}</div>'
    sec = bd.section(f"Case {n_case} · the room's course", body, 'Stage by stage, how the room\'s patients did: improving, no change, worse, life-threatening, from the orders and the settings together. Each phone shows its own patient\'s course.', live=key, mode='course', pad='56px 72px 64px')
    out += sec
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
