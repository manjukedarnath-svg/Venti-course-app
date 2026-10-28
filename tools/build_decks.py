#!/usr/bin/env python3
"""Build the three case-first talk decks (CP part 1, CP part 2, LTV five cases) and the Live-session entries.

    python3 tools/build_decks.py      (then bundle each for Present with tools/bundle.py)

Reads the app (index.html, through tools/export.js), the screen data in deckdata.py and theory slides
from the existing talks; writes talks/cp-part1.html, talks/cp-part2.html, talks/ltv-cases.html and the LIVE block.
"""
import json, re, html, sys, hashlib, os, subprocess, tempfile
import segno  # pip install segno
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deckdata import MAYA, LEO, CHD, BOY, SURESH, LTV
_TH = {'mm1': ['Danger of intubation', 'Shock index'], 'mm3': ['Venous return', 'The crash', 'Three commands'], 'mm5': ['PPV', 'In children', 'ITP matrix'],
       'lv2': ['PVR U-curve', 'Interdependence', 'D-sign', 'Decode'], 'lv3': ['RV-protective ventilation'], 'lv4': ['Hyperinflation', 'Auto-PEEP on screen', 'Disconnection test'],
       'bo1': ['LV afterload', 'MV as VAD', 'POCUS'], 'bo3': ['ACPE cycle'], 'su3': ['Afterload and stroke volume'],
       'sd2': ['ltv:Road home', 'ltv:The team'], 'sg2': ['ltv:Defining PMV', 'ltv:Four indications', 'ltv:Timing', 'ltv:Go early or wait'], 'sp2': ['ltv:Assume the tube', 'ltv:The algorithm', 'ltv:False passage']}
for _d in MAYA + LEO + CHD + BOY + SURESH + LTV:
    if _d['id'] in _TH: _d['theory'] = list(dict.fromkeys(_TH[_d['id']] + [t for t in _d['theory'] if t not in ('Pre-induction',)] + (['Pre-induction'] if _d['id'] == 'mm2' else [])))

_HIDE = {'ch1': ('Child 1 of 5 · 4 months, 5 kg · intubated for bronchiolitis', 'Saturation 100%, lactate <em>rising</em>'),
         'ch2': ('Child 2 of 5 · 7 months, 7 kg · blue spells', 'A spell that needs the <em>tube</em>'),
         'ch3': ('Child 3 of 5 · newborn, 3.5 kg · day 1 after heart surgery', 'Saturation 90%, NIRS <em>falling</em>'),
         'ch4': ('Child 4 of 5 · 6 months, 6 kg · after heart surgery', 'Blue, with a plethoric <em>face</em>'),
         'ch5': ('Child 5 of 5 · 4 years, 16 kg · after heart surgery', 'Liver up, lactate <em>rising</em>'),
         'so1': ('Case 1 of 5 · 3 y, 14 kg · the night after tonsil surgery', None), 'sd1': ('Case 2 of 5 · 15 y, 45 kg · weak since early childhood', None),
         'sm1': ('Case 3 of 5 · 5 mo, 6 kg · floppy since birth, now a cold', None), 'sg1': ('Case 4 of 5 · 10 y, 30 kg · weak legs for a week, now arms', None),
         'sp1': ('Case 5 of 5 · 7 mo, 5 kg · born at 25 weeks, never off the ventilator', None),
         'su1': ('An 8-year-old · 24 kg', None)}
for _d in CHD + LTV + SURESH:
    if _d['id'] in _HIDE:
        ey, hd = _HIDE[_d['id']]; _d['eyebrow'] = ey
        if hd: _d['head'] = hd

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = 'https://venti-course-app-production.up.railway.app'
_tmp = os.path.join(tempfile.mkdtemp(), 'appdata.json')
subprocess.run(['node', os.path.join(APP, 'tools', 'export.js'), os.path.join(APP, 'index.html'), _tmp], check=True)
D = json.load(open(_tmp))
ST = D['stages']
FALLBACK_ILLUS = {'so1': 'rapid1_aarav_osa', 'so2': 'rapid1_aarav_osa', 'sd1': 'rapid2_rohan_duchenne', 'sd2': 'rapid2_rohan_duchenne',
                  'sm1': 'rapid3_meera_sma', 'sm2': 'rapid3_meera_sma', 'sg1': 'rapid4_diya_gbs', 'sg2': 'rapid4_diya_gbs',
                  'sp1': 'rapid5_kabir_bpd', 'sp2': 'rapid5_kabir_bpd', 'bo3': None, 'bo4': None}
SRC = {name: open(os.path.join(APP, 'talks', name)).read() for name in ['cp-interactions.html', 'rapid-cases.html', 'long-term-ventilation.html']}

e = lambda t: html.escape(str(t), quote=True)
MONO = "font-family:var(--font-mono); letter-spacing:.14em; text-transform:uppercase;"
LOGO = ('<div data-logo-plate="1" style="position:absolute; right:28px; bottom:16px; display:flex; align-items:center; gap:22px; background:#FFFFFF; border-radius:4px; padding:8px 16px; z-index:5; pointer-events:none;">'
        '<img src="../assets/logo-kims.png" alt="KIMS Hospitals Bengaluru" style="height:44px; width:auto; display:block;"><span style="width:1px; height:36px; background:#D2C5B1;"></span>'
        '<img src="../assets/logo-cuddles.png" alt="KIMS Cuddles Mother &amp; Child Centre" style="height:36px; width:auto; display:block;"></div>')


def illus_of(sid):
    s = ST.get(sid, {})
    n = s.get('illus') or FALLBACK_ILLUS.get(sid)
    return n


def ipath(n, rel='../'):
    return f'{rel}assets/illus/{n}.jpg' if n else ''


def plain(h):
    return re.sub(r'<[^>]+>', '', h)


def rot(sid):
    return int(hashlib.md5(sid.encode()).hexdigest(), 16) % 4


def orders(sid, short):
    """App orders for a stage, rotated so the right answer moves around; returns [(letter, label, ok, resp, short, cons)]."""
    live = ST[sid]['live']
    opts = list(zip(live['opts'], short))
    k = rot(sid)
    opts = opts[k:] + opts[:k]
    return [('ABCD'[i], o[0], o[1], o[2], s[0], s[1]) for i, (o, s) in enumerate(opts)]


# ------------------------------------------------------------------ slide parts --------------------------------------
def section(label, body, notes='', live=None, mode=None, results=None, chord=None, pad='56px 72px 64px', extra_style='', justify=''):
    a = [f'data-label="{e(label)}"']
    if live: a.insert(0, f'data-live="{e(live)}" data-live-mode="{mode or "info"}"' + (f' data-live-results="{e(results)}"' if results else ''))
    if chord: a.append(f'data-chord="{chord}"')
    a.append(f'data-speaker-notes="{e(notes)}"')
    st = f'background:var(--surface-page); color:var(--text-primary); padding:{pad}; box-sizing:border-box; display:flex; flex-direction:column; gap:28px;{justify}{extra_style}'
    return f'<section {" ".join(a)} style="{st}">\n{body}\n{LOGO}\n</section>\n'


def header(eyebrow, head, tag=''):
    return ('<div style="flex:none; display:flex; justify-content:space-between; align-items:flex-end; gap:40px;">'
            f'<div style="display:flex; flex-direction:column; gap:14px; min-width:0;"><span style="{MONO} font-size:22px; color:var(--text-secondary);">{e(eyebrow)}</span>'
            f'<h2 style="margin:0; font-family:var(--font-display); font-weight:400; font-size:76px; line-height:1; letter-spacing:-.01em; text-wrap:balance;">{head}</h2></div>'
            + (f'<span style="{MONO} font-size:20px; color:var(--text-accent); text-align:right; flex:none; padding-bottom:10px;">{tag}</span>' if tag else '') + '</div>')


FIG_AGE = {'bo3': 'toddler', 'bo4': 'toddler'}


def picture(n, h=320, sid=None):
    if not n:
        if sid in FIG_AGE:
            return (f'<div style="flex:none; height:{h}px; border-radius:6px; overflow:hidden; background:#F4EFE6; border:1px solid var(--border-subtle); padding:10px 20px; box-sizing:border-box;">'
                    f'<x-import component-from-global-scope="patient-figure" age="{FIG_AGE[sid]}" support="ett" style="width:100%; height:100%;" hint-size="100%,100%"></x-import></div>')
        return ''
    return (f'<div style="flex:none; height:{h}px; border-radius:6px; overflow:hidden; background:#F4EFE6; border:1px solid var(--border-subtle);">'
            f'<img src="{ipath(n)}" alt="The patient at the bedside" style="display:block; width:100%; height:100%; object-fit:cover;"></div>')


def monitor(vitals, zoom=1.42):
    return (f'<div style="flex:none; zoom:{zoom};"><x-import component-from-global-scope="bedside-monitor" vitals="{e(json.dumps(vitals, ensure_ascii=False))}" '
            'style="width:100%;" hint-size="100%,220px"></x-import></div>')


KNOB = ('<svg viewBox="0 0 60 60" width="54" height="54" aria-hidden="true"><circle cx="30" cy="30" r="27" fill="#2A2C2E" stroke="#141516" stroke-width="2"/>'
        '<circle cx="30" cy="30" r="21" fill="#1A1C1E"/><line x1="30" y1="30" x2="{x}" y2="{y}" stroke="#E9B54A" stroke-width="4" stroke-linecap="round"/></svg>')


def knob(i):
    import math
    a = math.radians(220 - 55 * (i % 5) - 17)
    return KNOB.format(x=round(30 + 17 * math.cos(a), 1), y=round(30 - 17 * math.sin(a), 1))


def device(scr, dim=False):
    """The app's ICU-1 ventilator: screen with waves and measured values, mode bar, knobs with set values."""
    wave = scr.get('wave')
    meas = scr.get('meas') or []
    mon = {k: v for k, v in (scr.get('mon') or [])}
    spo2 = re.sub(r'[^0-9]', '', str(mon.get('SpO₂', '--')))[:3] or '--'
    etco2 = re.sub(r'[^0-9]', '', str(mon.get('EtCO₂', '')))[:3] or '--'
    on = bool(wave)
    readouts = ''.join(f'<div style="display:flex; flex-direction:column; gap:3px;"><span style="font:500 13px/1 var(--font-mono); letter-spacing:.1em; text-transform:uppercase; color:#8A9096;">{e(k)}</span>'
                       f'<span style="font:500 30px/1 var(--font-mono); color:#F2EFE8; white-space:nowrap;">{e(v)}</span></div>' for k, v in meas)
    if on:
        screen_left = (f'<div style="flex:1; min-width:0; position:relative;"><x-import component-from-global-scope="vent-trace" scenario="{e(wave)}" lanes="pfv" theme="night" font="13" lw="2.4" marks="off" '
                       'style="position:absolute; inset:4px 0;" hint-size="100%,100%"></x-import></div>')
    else:
        screen_left = (f'<div style="flex:1; min-width:0; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:10px; color:#8A9096;">'
                       f'<span style="font:500 15px/1 var(--font-mono); letter-spacing:.16em; text-transform:uppercase;">Standby · not on the ventilator</span>'
                       f'<span style="font:400 26px/1.25 var(--font-sans); color:#D8D4CC; text-align:center; max-width:320px;">{e(scr.get("modeLong", ""))}</span></div>')
    knobs = ''.join(f'<div style="display:flex; flex-direction:column; align-items:center; gap:6px; min-width:0;"><span style="font:500 13px/1 var(--font-mono); letter-spacing:.1em; text-transform:uppercase; color:#3B3A36;">{e(k)}</span>'
                    f'{knob(i)}<span style="min-width:74px; text-align:center; background:#0E1012; color:#E9B54A; font:500 22px/1 var(--font-mono); padding:7px 8px; border-radius:3px; white-space:nowrap;">{e(v)}</span></div>'
                    for i, (k, v) in enumerate(scr.get('set') or []))
    note = scr.get('note') or scr.get('gas') or ''
    return ('<div style="height:100%; min-height:0; display:flex; flex-direction:column; gap:14px;' + (' opacity:.55;' if dim else '') + '">'
            '<div style="flex:1; min-height:0; background:#D9D4CB; border-radius:18px; padding:16px 18px 18px; box-shadow:inset 0 0 0 1px #BDB6A9, 0 18px 40px rgba(27,26,23,.18); display:flex; flex-direction:column; gap:12px;">'
            '<div style="flex:none; display:flex; justify-content:space-between; align-items:center;">'
            '<span style="font:500 14px/1 var(--font-mono); letter-spacing:.2em; color:#3B3A36;">ICU-1</span>'
            f'<div style="display:flex; gap:10px;"><span style="background:#0E1012; color:#3CC3CC; font:500 18px/1 var(--font-mono); padding:6px 10px; border-radius:3px;">{e(spo2)} <span style="font-size:10px; color:#6E6A63;">SpO₂</span></span>'
            f'<span style="background:#0E1012; color:#E9B54A; font:500 18px/1 var(--font-mono); padding:6px 10px; border-radius:3px;">{e(etco2)} <span style="font-size:10px; color:#6E6A63;">EtCO₂</span></span></div>'
            f'<span style="font:500 13px/1 var(--font-mono); letter-spacing:.14em; color:#3B3A36;"><span style="color:{"#3E9B5A" if on else "#C99A2E"};">●</span> {"ON" if on else "STANDBY"}</span></div>'
            '<div style="flex:1; min-height:0; background:#0E1012; border-radius:8px; border:2px solid #24272A; display:flex; gap:16px; padding:12px 16px;">'
            f'{screen_left}'
            + (f'<div style="flex:none; width:150px; display:flex; flex-direction:column; justify-content:space-around; border-left:1px solid #24272A; padding-left:14px;">{readouts}</div>' if readouts else '') +
            '</div>'
            '<div style="flex:none; display:flex; gap:10px;"><span style="flex:none; background:#E8E3DA; border-radius:6px; padding:9px 14px; font:500 14px/1 var(--font-mono); letter-spacing:.14em; color:#3B3A36; box-shadow:0 2px 0 #B5AEA1;">● MODES</span>'
            f'<span style="flex:1; background:#0E1012; color:#F2EFE8; border-radius:6px; padding:9px 16px; font:500 18px/1.1 var(--font-mono); letter-spacing:.04em;">{e(scr.get("modeLong", scr.get("mode", "")))}</span></div>'
            f'<div style="flex:none; display:flex; justify-content:space-around; gap:8px;">{knobs}</div>'
            '</div>'
            + (f'<span style="flex:none; font-size:24px; line-height:1.3; color:var(--text-secondary);">{e(note)}</span>' if note else '') +
            '</div>')


def order_cards(ords, reveal=False):
    out = []
    for L, label, ok, resp, short, cons in ords:
        good = reveal and ok
        border = '#3E7D4F' if good else 'var(--border-default)'
        bg = 'color-mix(in oklab, #3E7D4F 12%, var(--surface-page))' if good else 'transparent'
        dim = ' opacity:.62;' if reveal and not ok else ''
        tick = ('<span style="position:relative; flex:none; font:500 15px/1 var(--font-mono); letter-spacing:.14em; text-transform:uppercase; color:#3E7D4F;">Right order</span>' if good else '')
        cons_html = (f'<span style="position:relative; font-size:24px; line-height:1.3; color:{"var(--text-primary)" if good else "var(--text-secondary)"};">{e(cons)}</span>' if reveal else '')
        out.append(f'<div data-opt="{L}" style="position:relative; overflow:hidden; display:flex; flex-direction:column; gap:8px; padding:20px 24px; border-radius:4px; border:{"2px" if good else "1px"} solid {border}; background:{bg};{dim}">'
                   '<div data-bar style="position:absolute; left:0; top:0; bottom:0; width:0; background:rgba(176,68,40,.14); transition:width .7s cubic-bezier(.2,.7,.2,1);"></div>'
                   f'<div style="position:relative; display:flex; gap:18px; align-items:baseline;"><span style="font-family:var(--font-mono); font-size:24px; color:var(--text-secondary);">{L}</span>'
                   f'<span style="flex:1; font-size:30px; line-height:1.25; text-wrap:balance;">{e(short)}</span><span data-cnt style="flex:none; font-family:var(--font-mono); font-size:20px; color:var(--text-accent);"></span></div>'
                   + (f'<div style="position:relative; display:flex; justify-content:space-between; align-items:baseline; gap:12px; padding-left:42px;">{cons_html}{tick}</div>' if reveal else '') +
                   '</div>')
    return ''.join(out)


# ------------------------------------------------------------------ live entries ----------------------------------------
LIVE_OUT = {}


def live_vent(scr):
    v = {'mode': scr.get('modeLong') or scr.get('mode', ''), 'set': scr.get('set') or [], 'meas': scr.get('meas') or []}
    n = scr.get('note') or scr.get('gas')
    if n: v['note'] = n
    return v


def stage_slides(d, code):
    sid = d['id']
    st = ST[sid]
    ords = orders(sid, d['short'])
    n_before = illus_of(sid)
    scr, aft = d['scr'], d['after']
    title_plain = plain(d['head'])
    # phone
    LIVE_OUT[sid] = {'t': d['eyebrow'] + ' · ' + title_plain, 'illus': ipath(n_before, ''), 'mon': scr['mon'], 'vent': live_vent(scr),
                     'lines': [st['story']], 'q': st['live']['q'], 'opts': [[L, label] for L, label, *_ in ords]}
    if not n_before: LIVE_OUT[sid].pop('illus')
    n_after = aft.get('illus') or n_before
    aft_scr = {**scr, **{k: v for k, v in aft.items() if k in ('mode', 'set', 'meas', 'wave', 'mon')}}
    if 'set' in aft and 'modeLong' not in aft:
        aft_scr['modeLong'] = {'PC': 'AC · Pressure control', 'PRVC': 'AC · PRVC', 'VC': 'AC · Volume control', 'NIV': 'Bilevel by mask', 'ST': 'Bilevel ST', 'CPAP': 'CPAP by mask', 'PS': 'Pressure support + PEEP'}.get(aft.get('mode', ''), scr.get('modeLong'))
    aft_scr['note'] = ''
    aft_scr['gas'] = ''
    LIVE_OUT[sid + '_r'] = {'t': d['eyebrow'] + ' · the response', 'illus': ipath(n_after, ''), 'mon': aft['mon'], 'of': sid,
                            'reveal': [[L, label, ok, resp] for L, label, ok, resp, *_ in ords], 'lines': [aft['happen']]}
    if 'set' in aft: LIVE_OUT[sid + '_r']['vent'] = live_vent(aft_scr)
    if not n_after: LIVE_OUT[sid + '_r'].pop('illus')
    right = next(o for o in ords if o[2])
    # slide 1: the screen and the orders
    notes1 = st['story'] + ' Ask: ' + st['live']['q'] + ' Orders on the phones; the bars stay hidden until the response slide.'
    col1 = f'<div style="display:flex; flex-direction:column; gap:16px; min-width:0; min-height:0;">{picture(n_before, sid=sid)}{monitor(scr["mon"])}</div>'
    col3 = (f'<div style="display:flex; flex-direction:column; gap:16px; min-width:0;"><span style="{MONO} font-size:20px; color:var(--text-secondary);">Your order</span>{order_cards(ords)}'
            '</div>')
    body = header(d['eyebrow'], d['head'], 'Live · what do you do?') + \
        f'<div style="flex:1; min-height:0; display:grid; grid-template-columns:540px minmax(0,1fr) 470px; gap:30px;">{col1}{device(scr)}{col3}</div>'
    s1 = section(f'{title_plain}', body, notes1, live=sid, mode='ask')
    if sid in SET_WORD: s1 = set_slide(d) + s1
    # slide 2: the response
    notes2 = 'The response. ' + right[3] + ' ' + (st.get('event') or '')
    col1 = f'<div style="display:flex; flex-direction:column; gap:16px; min-width:0; min-height:0;">{picture(n_after, sid=sid)}{monitor(aft["mon"])}</div>'
    col3 = f'<div style="display:flex; flex-direction:column; gap:14px; min-width:0;"><span style="{MONO} font-size:20px; color:var(--text-secondary);">Each order · the response</span>{order_cards(ords, reveal=True)}</div>'
    foot = (f'<div style="flex:none; display:flex; gap:22px; align-items:baseline; border-top:1px solid var(--border-subtle); padding-top:18px;">'
            f'<span style="{MONO} font-size:20px; color:var(--text-accent); flex:none;">What happened</span><span style="font-size:32px; line-height:1.25;">{e(aft["happen"])}</span></div>')
    body = header(d['eyebrow'], d['head'], 'The response') + \
        f'<div style="flex:1; min-height:0; display:grid; grid-template-columns:540px minmax(0,1fr) 470px; gap:30px;">{col1}{device(aft_scr, dim=("set" not in aft))}{col3}</div>' + foot
    s2 = section(f'{title_plain} · response', body, notes2, live=sid + '_r', mode='show', results=sid)
    return s1 + s2


SET_WORD = {'mm2': 'NIV for pre-oxygenation', 'mm3': 'ventilator for the tube', 'ch1': 'ventilator', 'ch2': 'ventilator', 'ch3': 'ventilator', 'ch4': 'ventilator', 'ch5': 'ventilator',
            'bo1': 'support: high-flow, NIV or ventilator', 'bo2': 'ventilator for the tube', 'su2': 'ventilator before the drugs',
            'so1': 'support: high-flow, CPAP or bilevel', 'sd1': 'home support: CPAP or bilevel', 'sm1': 'support: high-flow, CPAP or bilevel', 'sg1': 'ventilator', 'sp1': 'ventilator'}


def set_slide(d):
    sid = d['id']; key = sid + '_set'; word = SET_WORD[sid]; scr = d['scr']
    n = illus_of(sid)
    LIVE_OUT[key] = {'t': d['eyebrow'] + ' · your settings', 'mon': scr['mon'], 'lines': [ST[sid]['story']],
                     'q': 'Set the ' + word + ': type mode and settings (e.g. EPAP 8, IPAP 14, FiO₂ 0.6)', 'text': True}
    if n: LIVE_OUT[key]['illus'] = ipath(n, '')
    col1 = f'<div style="display:flex; flex-direction:column; gap:16px; min-width:0; min-height:0;">{picture(n, sid=sid)}{monitor(scr["mon"])}</div>'
    wall = ('<div style="position:relative; min-height:0; border:1px dashed var(--border-default); border-radius:6px;">'
            '<div data-live-texts style="position:absolute; inset:18px; display:flex; flex-wrap:wrap; gap:14px; align-content:flex-start; overflow:hidden;"></div>'
            f'<div data-live-empty style="position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-family:var(--font-display); font-size:52px; color:var(--text-secondary); text-align:center; padding:40px;">Type your settings on the phone</div></div>')
    body = header(d['eyebrow'], 'You set the <em>' + e(word.split(':')[0]) + '</em>', 'Live · type your settings') + \
        f'<div style="flex:1; min-height:0; display:grid; grid-template-columns:540px minmax(0,1fr); gap:30px;">{col1}{wall}</div>'
    return section(plain(d['head']) + ' · your settings', body, ST[sid]['story'] + ' Before we show the screen: what would you set? Type it on the phones.', live=key, mode='text')


def opener(key, eyebrow, name, lines, n, notes, code):
    LIVE_OUT[key] = {'t': name, 'illus': ipath(n, ''), 'lines': lines}
    body = (f'<div style="flex:1; display:grid; grid-template-columns:minmax(0,1fr) 1040px; gap:56px; align-items:center;">'
            f'<div style="display:flex; flex-direction:column; gap:32px;"><span style="{MONO} font-size:24px; color:var(--text-secondary);">{e(eyebrow)}</span>'
            f'<h2 style="margin:0; font-family:var(--font-display); font-weight:400; font-size:104px; line-height:.98; letter-spacing:-.015em; text-wrap:balance;">{name}</h2>'
            + ''.join(f'<span style="font-size:38px; line-height:1.3; color:var(--text-secondary);">{e(l)}</span>' for l in lines) +
            f'<span style="{MONO} font-size:20px; color:var(--text-accent);">On your phones now · code {code}</span></div>'
            f'<div style="height:640px; border-radius:8px; overflow:hidden; background:#F4EFE6; border:1px solid var(--border-subtle);"><img src="{ipath(n)}" alt="" style="display:block; width:100%; height:100%; object-fit:cover;"></div></div>')
    return section('Case · ' + plain(name), body, notes, live=key, mode='info', pad='80px 96px 80px')


def reuse(src, label, new_label=None, strip_live=True):
    if label.startswith('ltv:'): src, label = 'long-term-ventilation.html', label[4:]
    s = SRC[src]
    i = s.index(f'data-label="{label}"')
    a = s.rfind('<section', 0, i)
    b = s.index('</section>', i) + len('</section>')
    sec = s[a:b]
    if strip_live:
        sec = re.sub(r' data-live="[^"]*" data-live-mode="[^"]*"', '', sec)
    sec = re.sub(r' data-screen-label="[^"]*"', '', sec)
    if new_label:
        sec = sec.replace(f'data-label="{label}"', f'data-label="{new_label}"', 1)
    return sec + '\n'


def title_slide(kicker, head, sub, notes):
    body = (f'<span style="{MONO} font-size:26px; color:var(--text-secondary);">{e(kicker)}</span>'
            f'<div style="display:flex; flex-direction:column; gap:36px;"><h1 style="margin:0; font-family:var(--font-display); font-weight:400; font-size:150px; line-height:.94; letter-spacing:-.02em;">{head}</h1>'
            f'<p style="margin:0; font-weight:300; font-size:48px; line-height:1.3; color:var(--text-secondary);">{e(sub)}</p></div>'
            f'<div style="display:flex; flex-direction:column; gap:12px;"><span style="{MONO} font-size:24px; color:var(--text-primary);">Dr Manju Kedarnath</span>'
            f'<span style="{MONO} font-size:24px; color:var(--text-secondary);">Senior consultant and clinical lead · Pediatrics, Peds ER and PICU</span>'
            f'<span style="{MONO} font-size:24px; color:var(--text-secondary);">KIMS Hospitals, Electronic City, Bangalore</span></div>')
    return section('Title', body, notes, chord='dusk', pad='120px 140px', justify=' justify-content:space-between;')


def qr_svg(url, px=520):
    q = segno.make(url, error='m')
    svg = q.svg_inline(scale=10, border=2, dark='#1B1A17', light='#FFFFFF')
    w = re.search(r'width="(\d+)"', svg).group(1)
    svg = re.sub(r'width="\d+" height="\d+"', f'width="{px}" height="{px}" viewBox="0 0 {w} {w}"', svg, count=1)
    return svg


def join_slide(code, notes):
    url = f'{HOST}/#live-{code}'
    body = (f'<div style="flex:1; display:grid; grid-template-columns:minmax(0,1fr) 600px; gap:80px; align-items:center;">'
            f'<div style="display:flex; flex-direction:column; gap:40px;"><span style="{MONO} font-size:28px; color:var(--text-secondary);">Live session · VentCourse</span>'
            f'<h2 style="margin:0; font-family:var(--font-display); font-weight:400; font-size:120px; line-height:.95; letter-spacing:-.02em;">Scan to <em>join</em></h2>'
            f'<div style="display:flex; flex-direction:column; gap:20px;"><span style="font-size:44px; line-height:1.3;">1 · Scan with the phone camera</span>'
            f'<span style="font-size:44px; line-height:1.3;">2 · The case comes to your phone</span><span style="font-size:44px; line-height:1.3;">3 · Tap your order</span></div>'
            f'<div style="display:flex; gap:40px; align-items:baseline;"><span style="{MONO} font-size:24px; color:var(--text-secondary);">Or enter the code</span>'
            f'<span style="font-family:var(--font-display); font-size:150px; line-height:.85; color:var(--text-accent); letter-spacing:.04em;">{code}</span></div>'
            f'<span style="font-family:var(--font-mono); font-size:22px; color:var(--text-secondary);">{e(HOST.replace("https://", ""))}</span></div>'
            f'<div style="background:#FFFFFF; border-radius:12px; padding:30px; display:flex; align-items:center; justify-content:center; box-shadow:0 0 0 1px var(--border-subtle);">{qr_svg(url)}</div></div>')
    LIVE_OUT.setdefault('join', {'t': 'Connected', 'lines': ['Watch the screen. The case comes to your phone as the speaker reaches it.']})
    return section('Join', body, notes, chord='dusk', pad='90px 120px')


def cards_slide(label, eyebrow, head, cards, notes):
    inner = ''.join(f'<div style="border:1px solid var(--border-default); border-radius:4px; padding:30px 32px; display:flex; flex-direction:column; gap:16px;">'
                    f'<span style="{MONO} font-size:22px; color:var(--text-secondary);">{e(t)}</span>'
                    + ''.join(f'<span style="font-size:32px; line-height:1.3; text-wrap:balance;">{e(x)}</span>' for x in lines) + '</div>' for t, lines in cards)
    body = header(eyebrow, head) + f'<div style="flex:1; min-height:0; display:grid; grid-template-columns:repeat({len(cards)},1fr); gap:24px; align-content:center;">{inner}</div>'
    return section(label, body, notes, pad='80px 120px')


def close_slide(head, sub, notes, code_hint):
    body = (f'<span style="{MONO} font-size:26px; color:var(--text-secondary);">VentCourse · {e(code_hint)}</span>'
            f'<h1 style="margin:0; font-family:var(--font-display); font-weight:400; font-size:140px; line-height:.95; letter-spacing:-.02em;">{head}</h1>'
            f'<p style="margin:0; font-size:44px; line-height:1.35; color:var(--text-secondary);">{e(sub)}</p>')
    return section('Close', body, notes, chord='dusk', pad='140px', justify=' justify-content:center; gap:44px;')


# ------------------------------------------------------------------ assemble ----------------------------------------
def shell(title, sections, code, thumb_from='cp-interactions.html'):
    s = SRC[thumb_from]
    head_end = s.index('<x-import component-from-global-scope="deck-stage"')
    head_end = s.index('>', head_end) + 1
    head = s[:head_end]
    tail = s[s.rindex('</section>') + len('</section>'):]
    head = re.sub(r'<title>.*?</title>', '', head)
    head = head.replace('<script src="../support.js"></script>', f'<title>{e(title)}</title>\n<meta name="vc-live-room" content="{code}">\n<script src="../support.js"></script>', 1)
    head = head.replace('<script src="../vent-graphics.js"></script>', '<script src="../vent-graphics.js"></script>\n  <script src="../bedside-monitor.js"></script>\n  <script src="../patient-figure.js"></script>', 1)
    notes = [html.unescape(m) for m in re.findall(r'data-speaker-notes="([^"]*)"', sections)]
    head = re.sub(r'<script type="application/json" id="speaker-notes">.*?</script>', lambda m: '<script type="application/json" id="speaker-notes">' + json.dumps(notes, ensure_ascii=False).replace('</', '<\\/') + '</script>', head, flags=re.S)
    # number the slides
    n = [0]
    def num(m):
        n[0] += 1
        return m.group(0).replace('<section ', f'<section data-screen-label="{n[0]:02d}" ', 1)
    sections = re.sub(r'<section ', lambda m: m.group(0), sections)
    sections = re.sub(r'<section [^>]*>', num, sections)
    # live room: fixed code from the meta tag; results may come from another question
    tail = tail.replace("if (!room) { try { const r = await post('create', {});",
                        "if (!room) { try { const r = await post('create', { code: ROOM });")
    tail = tail.replace("try { const sv = JSON.parse(localStorage.getItem('vc-live-room') || 'null');\n        if (sv && Date.now() - sv.at < 432e5)",
                        "try { const sv = JSON.parse(localStorage.getItem('vc-live-room') || 'null');\n        if (sv && sv.room === ROOM && Date.now() - sv.at < 432e5)")
    tail = tail.replace("let room = null, key = null, lastQ, timer = null;",
                        "const ROOM = ((document.querySelector('meta[name=vc-live-room]') || {}).content || '').toUpperCase() || undefined;\n    let room = null, key = null, lastQ, timer = null;")
    tail = tail.replace("const tick = async () => { try { const r = await post('results', { room, q });",
                        "const rq = s.getAttribute('data-live-results') || q;\n      const tick = async () => { try { const r = await post('results', { room, q: rq });")
    assert 'code: ROOM' in tail and 'data-live-results' in tail and 'sv.room === ROOM' in tail, 'tail patch failed'
    return head + '\n\n' + sections + tail


POCUS = {
  'maya': ('Maya · POCUS', 'Maya · before the next bolus', 'The IVC with each <em>breath</em>',
           [('ivc-variable', 'Subcostal IVC, M-mode: the diameter swings with each ventilator breath'), ('ivc-flat-vs-full', 'Flat and swinging (A) against full and fixed (B)')],
           'On controlled ventilation, in sinus rhythm and deeply sedated, an IVC whose diameter swings with each positive-pressure breath predicts a rise in output with fluid. A full, fixed IVC does not. Fluid responsiveness is not fluid need: pair it with the pressure, the lactate and the lung.'),
  'leo': ('Leo · POCUS', 'Leo · the probe on the heart', 'Full IVC, big right <em>heart</em>',
          [('ivc-plethoric', 'Subcostal IVC: wide, no change with the breath'), ('rv-dilated', 'Right ventricle: dilated, the septum pushed towards the LV')],
          'The IVC is plethoric and does not move with the breath; the right ventricle is dilated and pushes the septum into the left. This is a right heart failing against its load, not a tank running dry. No bolus.'),
  'suresh': ('Suresh · POCUS', 'Suresh · the echo on the tablet', 'How well does the LV <em>squeeze</em>?',
             [('lv-poor-psax', 'Short axis: a large LV, the walls barely move'), ('lv-poor-apical', 'Apical view: dilated chambers, poor contraction')],
             'Eyeball the function: how close do the walls come in systole, how close does the mitral leaflet come to the septum. Here they barely move. Fluid will not help this heart; an inotrope will.'),
  'views': ('POCUS · the views', 'POCUS · the views you need', 'Four views, one <em>question</em>',
            [('subcostal-normal', 'Subcostal four-chamber'), ('a4c-normal', 'Apical four-chamber'), ('ivc-normal', 'IVC entering the right atrium')],
            'The basic views: subcostal four-chamber, apical four-chamber and the IVC as it enters the right atrium. One question at a time: is the heart empty, is it squeezing, is the right side obstructed, is it compressed.'),
}


def pocus_slide(key):
    label, eyebrow, head, clips, notes = POCUS[key]
    tiles = ''.join(f'<div style="display:flex; flex-direction:column; gap:12px; min-width:0; min-height:0;"><div style="flex:1; min-height:0; position:relative; background:#000; border-radius:6px; overflow:hidden;">'
                    f'<video src="../assets/pocus/{f}.mp4" autoplay loop muted playsinline style="position:absolute; inset:0; width:100%; height:100%; object-fit:contain;"></video></div>'
                    f'<span style="font-size:26px; line-height:1.3; color:var(--text-secondary);">{e(c)}</span></div>' for f, c in clips)
    body = header(eyebrow, head, 'POCUS') + f'<div style="flex:1; min-height:0; display:grid; grid-template-columns:repeat({len(clips)},1fr); gap:28px;">{tiles}</div>'
    return section(label, body, notes, chord='night')


FULL = False
EXTRA = {'mm2': ['Golden rule', 'Neutral intubation'], 'mm3': ['Vasoactive matrix', 'Cuffed tube', 'Cognitive minefield'], 'mm5': ['Pair the changes', 'SVV and PPV', 'PPV caveats', 'Modalities'],
         'lv3': ['The spiral', 'Four pillars'], 'lv5': ['ARDS sweet spot', 'Side by side', 'Measuring coupling', 'Predicting failure'],
         'ch1': ['Left-to-right shunts'], 'ch2': ['Tet spell'], 'ch3': ['Single ventricle', 'Norwood trap'], 'ch4': ['Glenn'], 'ch5': ['Fontan', 'Post-op diagnostics', 'CHD weaning', 'PICU matrix'],
         'bo1': ['Laplace', 'Afterload and stroke volume', 'Master levers', 'Coupling', 'Quiz afterload', 'Quiz afterload · answer'], 'bo2': ['Golden rule MV'], 'bo4': ['Aryan', 'Quiz 3', 'Quiz 3 · answer'],
         'su3': ['Same drug, opposite ventricles']}
PRE = {'mm5': ['pocus:maya'], 'lv2': ['pocus:leo'], 'su1': ['pocus:suresh'], 'bo1': ['pocus:views']}


def theory_of(d, src='cp-interactions.html'):
    out = ''
    items = PRE.get(d['id'], []) + d['theory'] + (EXTRA.get(d['id'], []) if FULL else [])
    for t in dict.fromkeys(items):
        out += pocus_slide(t[6:]) if t.startswith('pocus:') else reuse(src, t)
    return out


def build_part1(body_only=False):
    code = 'CP1'
    out = '' if body_only else title_slide('VentCourse · Module 08 · Cardiopulmonary interactions · Part 1', 'Heart and lung, <em>at the bedside</em>',
                      'Three cases on the ventilator: the difficult airway, the failing right ventricle, the congenital heart.',
                      'Thirty minutes, three cases, and you run them. Every case starts at the bedside: the child, the monitor and the ventilator. You choose the order on your phone, and the screen shows what the child does next. The physiology comes in as the cases need it.')
    out += '' if body_only else join_slide(code, 'Scan the code with your phone camera. It opens the VentCourse app straight into this session; no account needed. If the camera will not scan, open the app, tap Live session and type CP1.')
    out += opener('maya_case', 'Case 1 · Maya', 'A 3-year-old <em>girl</em>',
                  ['15 kg · three days of fever, vomiting, lethargy', 'One 20 mL/kg bolus in the ED; arrives obtunded, mottled'], 'maya1_arrival',
                  'Maya, three years, fifteen kilos. Three days of fever, now obtunded and mottled to the thighs on one cannula. She needs a tube, and she has no reserve to survive one. VT 6 to 8 mL/kg is 90 to 120 mL.', code)
    for d in MAYA:
        out += stage_slides(d, code)
        out += theory_of(d)
    out += reuse('cp-interactions.html', 'Maya · debrief')
    out += opener('leo_case', 'Case 2 · Leo', 'A 6-year-old <em>boy</em>',
                  ['20 kg · flu-like illness, worsening breathing', 'Intubated 24 hours ago; desaturated when turned'], 'leo1_desat_on_turning',
                  'Leo, six years, twenty kilos, influenza A pneumonia, intubated twenty-four hours ago. He desaturates, the PEEP goes up, and the right ventricle fails. VT 6 mL/kg is 120 mL; he is running 110.', code)
    for d in LEO:
        out += stage_slides(d, code)
        out += theory_of(d)
    out += reuse('cp-interactions.html', 'Leo · debrief')
    out += opener('chd_case', 'Case 3 · five children', 'Five children, five <em>hearts</em>',
                  ['Infants and children with heart disease', 'Each one on a ventilator, each one different'], 'chd0_anatomy_normal',
                  'Five bedside vignettes, one ventilator screen each. FiO2, CO2, pH and mean airway pressure move PVR. The normal heart first, so each lesion can be compared against it.', code)
    out += reuse('cp-interactions.html', 'Two spigots')
    for d in CHD:
        out += stage_slides(d, code)
        out += theory_of(d)
    out += reuse('cp-interactions.html', 'The congenital heart · debrief')
    if body_only: return out
    out += close_slide('Every breath is a <em>haemodynamic</em> intervention', 'All three cases are in the app: Cases · Sim scenarios 08, 09 and 10.',
                       'Every breath the ventilator gives is a haemodynamic intervention. Maya, Leo and the five congenital hearts are simulator scenarios 08 to 10 in the app: run them on your own, with the monitor and the gas answering every change. Thank you.', 'Part 1')
    return shell('Cardiopulmonary interactions · Part 1', out, code)


def build_part2(body_only=False):
    code = 'CP2'
    out = '' if body_only else title_slide('VentCourse · Module 08 · Cardiopulmonary interactions · Part 2', 'The failing heart, <em>ventilated</em>',
                      'Myocarditis and cardiogenic shock: positive pressure as a treatment.',
                      'Thirty minutes, two children with failing left ventricles. Positive pressure is a treatment for this heart; the induction drugs are the danger. You run both cases on your phones.')
    out += '' if body_only else join_slide(code, 'Scan the code with your phone camera to join; no account needed. Or open the app, tap Live session and type CP2.')
    # the 4-year-old: bedside, investigations, then the ventilator
    LIVE_OUT['boy_case'] = {'t': 'A 4-year-old boy', 'illus': ipath('live1_arrival', ''), 'lines': ['Five days of fever, runny nose and cough', 'Fast breathing since yesterday', 'Lethargic since this morning, increased work of breathing', 'Received in the ER']}
    out += opener('boy_case', 'Case 1 · in the ER', 'A 4-year-old <em>boy</em>',
                  ['Five days of fever, runny nose, cough', 'Fast breathing, lethargic since morning'], 'live1_arrival',
                  'Five days of fever, runny nose and cough. Fast breathing since yesterday, lethargic since this morning, more work of breathing. Received in the ER. What do you see?', code)
    LIVE_OUT['boy_case']['lines'] = ['Five days of fever, runny nose and cough', 'Fast breathing since yesterday', 'Lethargic since this morning, increased work of breathing', 'Received in the ER']
    LIVE_OUT['er2'] = {**D['LIVE']['er'], 'illus': ipath('live2_er_abcd', '')}
    abcd = [('A · Airway', ['Open and maintainable']), ('B · Breathing', ['RR 65, retractions', 'Basal crepitations both sides', 'SpO₂ 92% on 5 L NRM']),
            ('C · Circulation', ['Cold, thready pulses', 'HR 165 · BP 94/58', 'CRT 3 s central · 5 s peripheral']), ('D · Disability', ['Drowsy, AVPU V–P', 'GRBS 96'])]
    cards = ''.join(f'<div style="border:1px solid {"var(--text-accent)" if t.startswith("C") else "var(--border-default)"}; border-radius:4px; padding:20px 24px; display:flex; flex-direction:column; gap:10px;">'
                    f'<span style="{MONO} font-size:20px; color:{"var(--text-accent)" if t.startswith("C") else "var(--text-secondary)"};">{e(t)}</span>'
                    + ''.join(f'<span style="font-size:28px; line-height:1.25;">{e(x)}</span>' for x in xs) + '</div>' for t, xs in abcd)
    body = header('A 4-year-old · in the ER', 'ER <em>assessment</em>', 'ABCD') + \
        (f'<div style="flex:1; min-height:0; display:grid; grid-template-columns:700px minmax(0,1fr); gap:40px;">'
         f'<div style="display:flex; flex-direction:column; gap:18px; min-height:0;">{picture("live2_er_abcd", 360)}{monitor(D["LIVE"]["er"]["mon"], 1.3)}</div>'
         f'<div style="display:grid; grid-template-columns:1fr 1fr; gap:18px; align-content:start;">{cards}</div></div>')
    out += section('ER assessment', body, 'Airway open and maintainable. Breathing: a rate of 65, suprasternal and subcostal retractions, basal crepitations both sides, saturation 88 in air and only 92 on a non-rebreather at 5 litres. Circulation: cold peripheries, heart rate 165 in sinus, thready pulses, pressure 94 over 58, capillary refill 3 seconds centrally and 5 peripherally. Disability: drowsy, responding to voice or pain. Sugar 96.', live='er2', mode='info')
    LIVE_OUT['inv2'] = {**D['LIVE']['inv'], 'illus': ipath('live3_investigations', '')}
    body = header('A 4-year-old · a minute later', 'What do you <em>need</em>?', 'Investigations') + \
        (f'<div style="flex:1; min-height:0; display:grid; grid-template-columns:1100px minmax(0,1fr); gap:56px; align-items:center;">{picture("live3_investigations", 600)}'
         f'<div style="display:flex; flex-direction:column; gap:30px;">' + ''.join(f'<span style="font-size:44px; line-height:1.25;">{e(x)}</span>' for x in ['Blood gas: arterial or venous?', 'Chest X-ray', 'Bedside ultrasound: echo?']) + '</div></div>')
    out += section('Investigations', body, 'Three things in the first minutes: a blood gas (venous is enough to start), a chest film, and the ultrasound on the heart before any fluid.', live='inv2', mode='info')
    for lab in ['Blood gas', 'Gas answer', 'Chest X-ray', 'Echo', 'Your diagnosis', 'Provisional diagnosis']:
        out += reuse('cp-interactions.html', lab, strip_live=False)
    for d in BOY:
        out += stage_slides(d, code)
        out += theory_of(d)
    out += cards_slide('Boy · debrief', 'The 4-year-old · debrief', 'Positive pressure as <em>treatment</em>',
                       [('Start', ['EPAP 8 is the treatment', 'Inotrope, no bolus']), ('The tube', ['The drugs are the danger', 'Pre-set, push-dose, ketamine']),
                        ('After', ['PEEP 8–10 while the BP holds', 'Closed suction only']), ('Weaning', ['A cardiac stress test', 'Extubate onto NIV'])],
                       'Positive pressure is a treatment for the failing LV: start it through a mask, EPAP 8. If the tube is needed, the danger is the induction drugs. After the tube keep the PEEP that unloads the LV. And wean onto NIV, not off it.')
    out += opener('suresh_case', 'Case 2 · KarPediCon Station D', 'An 8-year-old <em>boy</em>',
                  ['24 kg · five days of fever and fatigue', 'Referred after one fluid bolus; BP 68/40'], 'suresh1_bedside',
                  'Suresh, eight, twenty-four kilos, acute myocarditis, ejection fraction 15 per cent with moderate mitral regurgitation, in cardiogenic shock after one fluid bolus. Support the heart before the tube; set the ventilator before the drugs; protect preload after the tube; then PEEP for the LV.', code)
    for d in SURESH:
        out += stage_slides(d, code)
        out += theory_of(d)
    DEB = [('Shock Recognition', 'What distinguishes cardiogenic from distributive (septic) shock in this child?', 'Cardiogenic: raised JVP, hepatomegaly, cool peripheries, fluid-unresponsive, elevated BNP/troponin, low EF on ECHO; septic: warm peripheries, low SVR, flat JVP, fluid-responsive (early)'),
           ('Inotrope Choice', 'Why is fluid administration potentially harmful in cardiogenic shock and what is your first inotrope choice?', 'Fluid overloads a failing ventricle → worsens pulmonary oedema and MR; first choice: low-dose adrenaline (0.05–0.1 mcg/kg/min) or milrinone (reduces afterload, inotrope); avoid pure vasoconstrictors'),
           ('Safe Intubation', 'Why did you avoid ketamine for induction in cardiogenic shock?', 'Ketamine is a sympathomimetic — causes tachycardia and hypertension; in a failing myocardium with HR 168, this is dangerous; use etomidate (haemodynamically neutral) or low-dose fentanyl + midazolam'),
           ('Post-Intubation Management', 'Why did BP fall after intubation and how do you manage it?', 'IPPV reduces venous return (preload) → CO falls in volume-depleted/failing heart; cautious 5 mL/kg fluid; reduce PEEP; vasopressor uptitration; this is expected — anticipate before intubation, not react after'),
           ('Escalation', 'At what point would you consider mechanical circulatory support (ECMO/VAD)?', 'Refractory cardiogenic shock: MAP < 50 despite 2 vasopressors, lactate rising despite treatment, OI > 16, deteriorating ECHO function; early referral to centre with ECMO/VAD capability; Berlin Heart for chronic cardiomyopathy'),
           ('Communication', 'How do you communicate urgency to the cardiology team when calling for help?', 'SBAR + "I need you here now": state BP, lactate, EF; don\'t say "when you get a chance"; document time of call; escalate to attending if specialist delayed > 15 minutes')]
    for part, rows in (('1 of 2', DEB[:3]), ('2 of 2', DEB[3:])):
        trs = ''.join(f'<tr><td style="padding:16px; font-family:var(--font-display); font-size:32px; vertical-align:top; border-bottom:1px solid var(--border-subtle);">{e(a)}</td><td style="padding:16px; font-size:24px; line-height:1.3; vertical-align:top; border-bottom:1px solid var(--border-subtle);">{e(b)}</td><td style="padding:16px; font-size:24px; line-height:1.3; vertical-align:top; border-bottom:1px solid var(--border-subtle);">{e(c)}</td></tr>' for a, b, c in rows)
        body = header('Suresh · debrief · ' + part, 'Debrief <em>domains</em>', 'Station D') + f'<div style="flex:1; display:flex; align-items:center;"><table style="border-collapse:collapse; width:100%;"><tr><th style="text-align:left; padding:12px 16px; {MONO} font-size:18px;">Domain</th><th style="text-align:left; padding:12px 16px; {MONO} font-size:18px;">Question</th><th style="text-align:left; padding:12px 16px; {MONO} font-size:18px;">Key points</th></tr>{trs}</table></div>'
        out += section('Suresh · debrief ' + part, body, 'Debrief, station sheet.', pad='70px 100px')
    if body_only: return out
    out += close_slide('Preload first, then <em>PEEP</em>', 'Both cases are in the app: Cases · Sim scenarios 11 and 12.',
                       'For the failing left ventricle, positive pressure is a drug and the induction is the danger. Both children are simulator scenarios 11 and 12 in the app. Thank you.', 'Part 2')
    return shell('Cardiopulmonary interactions · Part 2', out, code)


def build_full():
    global FULL
    FULL = True
    code = 'CPF'
    out = title_slide('VentCourse · Module 08 · Cardiopulmonary interactions · complete', 'Heart and lung, <em>together</em>',
                      'Five children on the ventilator, and the physiology each one needs.',
                      'The complete talk: the same children as parts 1 and 2, with the physiology woven in where each case needs it. You run every case on your phones.')
    out += join_slide(code, 'Scan the code to join; no account needed. Or open the app, tap Live session and type CPF.')
    for t in ['Five interactions', 'Sealed chamber', 'Transmural pressure', 'Transmural example', 'Master key', 'Quiz 1', 'Quiz 1 · answer']:
        out += reuse('cp-interactions.html', t)
    out += build_part1(body_only=True) + build_part2(body_only=True)
    for t in ['Core principles', 'Summary', 'Takeaways']:
        out += reuse('cp-interactions.html', t)
    out += close_slide('Observe the physics. Predict the <em>crash</em>.', 'All five children are in the app: Cases · Sim scenarios 08 to 12.',
                       'Every breath is a haemodynamic intervention. All five children are simulator scenarios 08 to 12 in the app. Thank you.', 'Module 08')
    FULL = False
    return shell('Cardiopulmonary interactions · complete', out, code)


def build_ltv():
    code = 'LTV'
    out = title_slide('VentCourse · Module 09 · Long-term ventilation · 15 min', 'Five children, five <em>pumps</em>',
                      'How to ventilate them, stage by stage.',
                      'Fifteen minutes, five children who need ventilation for a long time. Each one starts at the bedside: commit to an order on your phone and see what the child does. Every child is a simulator scenario in the app, 03 to 07.')
    out += join_slide(code, 'Scan the code to join; no account needed. Or open the app, tap Live session and type LTV.')
    for d in LTV:
        out += stage_slides(d, code)
        for t in d['theory']: out += reuse('rapid-cases.html', t)
    out += reuse('rapid-cases.html', 'Map')
    out += reuse('rapid-cases.html', 'Summary')
    out += reuse('rapid-cases.html', 'Takeaways')
    out += close_slide('Oxygen is not <em>ventilation</em>', 'All five children are in the app: Cases · Sim scenarios 03 to 07.',
                       'Oxygen is not ventilation. All five children are simulator scenarios 03 to 07 in the app. Thank you.', 'Long-term ventilation')
    return shell('Long-term ventilation · five cases', out, code)


def write_live():
    p = os.path.join(APP, 'index.html')
    s = open(p).read()
    a = s.index('// LIVE-START')
    b = s.index('// LIVE-END')
    line = s[a:b]
    m = re.search(r'const LIVE = (\{.*\});', line, re.S)
    live = json.loads(m.group(1))
    live.update(LIVE_OUT)
    new = '// LIVE-START (generated from the CP interactions talk builder and tools/build_decks.py)\nconst LIVE = ' + json.dumps(live, ensure_ascii=False) + ';\n'
    s = s[:a] + new + s[b:]
    open(p, 'w').write(s)


if __name__ == '__main__':
    files = {'cp-part1.html': build_part1(), 'cp-part2.html': build_part2(), 'ltv-cases.html': build_ltv(), 'cp-complete.html': build_full()}
    for f, t in files.items():
        open(os.path.join(APP, 'talks', f), 'w').write(t)
        print(f, len(t), t.count('<section '), 'slides')
    write_live()
    print('LIVE entries', len(LIVE_OUT))
