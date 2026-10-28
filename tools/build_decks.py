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

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = 'https://venti-course-app-production.up.railway.app'
_tmp = os.path.join(tempfile.mkdtemp(), 'appdata.json')
subprocess.run(['node', os.path.join(APP, 'tools', 'export.js'), os.path.join(APP, 'index.html'), _tmp], check=True)
D = json.load(open(_tmp))
ST = D['stages']
FALLBACK_ILLUS = {'so1': 'rapid1_aarav_osa', 'so2': 'rapid1_aarav_osa', 'sd1': 'rapid2_rohan_duchenne', 'sd2': 'rapid2_rohan_duchenne',
                  'sm1': 'rapid3_meera_sma', 'sm2': 'rapid3_meera_sma', 'sg1': 'rapid4_diya_gbs', 'sg2': 'rapid4_diya_gbs',
                  'sp1': 'rapid5_kabir_bpd', 'sp2': 'rapid5_kabir_bpd', 'bo3': None, 'bo4': None}
SRC = {name: open(os.path.join(APP, 'talks', name)).read() for name in ['cp-interactions.html', 'rapid-cases.html']}

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


def build_part1():
    code = 'CP1'
    out = title_slide('VentCourse · Module 08 · Cardiopulmonary interactions · Part 1', 'Heart and lung, <em>at the bedside</em>',
                      'Three cases on the ventilator: the difficult airway, the failing right ventricle, the congenital heart.',
                      'Thirty minutes, three cases, and you run them. Every case starts at the bedside: the child, the monitor and the ventilator. You choose the order on your phone, and the screen shows what the child does next. The physiology comes in as the cases need it.')
    out += join_slide(code, 'Scan the code with your phone camera. It opens the VentCourse app straight into this session; no account needed. If the camera will not scan, open the app, tap Live session and type CP1.')
    out += opener('maya_case', 'Case 1 · the physiologically difficult airway', 'Maya: the haemodynamic <em>cliff</em>',
                  ['3 years · 15 kg · refractory septic shock', 'Needs a tube, no reserve to survive one'], 'maya1_arrival',
                  'Maya, three years, fifteen kilos. Three days of fever, now obtunded and mottled to the thighs on one cannula. She needs a tube, and she has no reserve to survive one. VT 6 to 8 mL/kg is 90 to 120 mL.', code)
    for d in MAYA:
        out += stage_slides(d, code)
        for t in d['theory']: out += reuse('cp-interactions.html', t)
    out += reuse('cp-interactions.html', 'Maya · debrief')
    out += opener('leo_case', 'Case 2 · the failing right ventricle', 'Leo: crashing on the <em>ventilator</em>',
                  ['6 years · 20 kg · influenza PARDS', 'Intubated 24 hours, deeply sedated'], 'leo1_desat_on_turning',
                  'Leo, six years, twenty kilos, influenza A pneumonia, intubated twenty-four hours ago. He desaturates, the PEEP goes up, and the right ventricle fails. VT 6 mL/kg is 120 mL; he is running 110.', code)
    for d in LEO:
        out += stage_slides(d, code)
        for t in d['theory']: out += reuse('cp-interactions.html', t)
    out += reuse('cp-interactions.html', 'Leo · debrief')
    out += opener('chd_case', 'Case 3 · the congenital heart', 'Five lesions, five <em>screens</em>',
                  ['PVR and SVR are the levers', 'Each lesion needs the opposite of the last'], 'chd0_anatomy_normal',
                  'Five bedside vignettes, one ventilator screen each. FiO2, CO2, pH and mean airway pressure move PVR. The normal heart first, so each lesion can be compared against it.', code)
    out += reuse('cp-interactions.html', 'Two spigots')
    for d in CHD:
        out += stage_slides(d, code)
    out += reuse('cp-interactions.html', 'The congenital heart · debrief')
    out += close_slide('Every breath is a <em>haemodynamic</em> intervention', 'All three cases are in the app: Cases · Sim scenarios 08, 09 and 10.',
                       'Every breath the ventilator gives is a haemodynamic intervention. Maya, Leo and the five congenital hearts are simulator scenarios 08 to 10 in the app: run them on your own, with the monitor and the gas answering every change. Thank you.', 'Part 1')
    return shell('Cardiopulmonary interactions · Part 1', out, code)


def build_part2():
    code = 'CP2'
    out = title_slide('VentCourse · Module 08 · Cardiopulmonary interactions · Part 2', 'The failing heart, <em>ventilated</em>',
                      'Myocarditis and cardiogenic shock: positive pressure as a treatment.',
                      'Thirty minutes, two children with failing left ventricles. Positive pressure is a treatment for this heart; the induction drugs are the danger. You run both cases on your phones.')
    out += join_slide(code, 'Scan the code with your phone camera to join; no account needed. Or open the app, tap Live session and type CP2.')
    # the 4-year-old: bedside, investigations, then the ventilator
    LIVE_OUT['boy_case'] = {'t': 'A 4-year-old boy', 'illus': ipath('live1_arrival', ''), 'lines': ['Five days of fever, runny nose and cough', 'Fast breathing since yesterday', 'Lethargic since this morning, increased work of breathing', 'Received in the ER']}
    out += opener('boy_case', 'Case 1 · the failing left ventricle', 'A 4-year-old <em>boy</em>',
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
        for t in d['theory']: out += reuse('cp-interactions.html', t)
    out += cards_slide('Boy · debrief', 'The 4-year-old · debrief', 'Positive pressure as <em>treatment</em>',
                       [('Start', ['EPAP 8 is the treatment', 'Inotrope, no bolus']), ('The tube', ['The drugs are the danger', 'Pre-set, push-dose, ketamine']),
                        ('After', ['PEEP 8–10 while the BP holds', 'Closed suction only']), ('Weaning', ['A cardiac stress test', 'Extubate onto NIV'])],
                       'Positive pressure is a treatment for the failing LV: start it through a mask, EPAP 8. If the tube is needed, the danger is the induction drugs. After the tube keep the PEEP that unloads the LV. And wean onto NIV, not off it.')
    out += opener('suresh_case', 'Case 2 · KarPediCon Station D', 'Suresh: the heart <em>first</em>',
                  ['8 years · 24 kg · acute myocarditis', 'EF 15%, moderate MR, BP 68/40'], 'suresh1_bedside',
                  'Suresh, eight, twenty-four kilos, acute myocarditis, ejection fraction 15 per cent with moderate mitral regurgitation, in cardiogenic shock after one fluid bolus. Support the heart before the tube; set the ventilator before the drugs; protect preload after the tube; then PEEP for the LV.', code)
    for d in SURESH:
        out += stage_slides(d, code)
        for t in d['theory']: out += reuse('cp-interactions.html', t)
    out += cards_slide('Suresh · debrief', 'Suresh · debrief', 'The order <em>matters</em>',
                       [('Recognise', ['JVP, liver, cold, low EF', 'No more fluid']), ('Support', ['Adrenaline or milrinone', 'No pure constrictor alone']),
                        ('Intubate', ['Ventilator set first', 'Ketamine reduced, pads on']), ('After', ['Preload, then the rate', 'Then PEEP for the LV'])],
                       'Cardiogenic shock: raised JVP, hepatomegaly, cool peripheries, fluid-unresponsive, low EF. Adrenaline or milrinone, not a pure vasoconstrictor. Set the ventilator before induction, ketamine at a reduced dose, push-dose adrenaline and pads on. After the tube: preload first, then match his minute ventilation, then PEEP for the LV. Escalate to ECMO or VAD early: I need you here now.')
    out += close_slide('Preload first, then <em>PEEP</em>', 'Both cases are in the app: Cases · Sim scenarios 11 and 12.',
                       'For the failing left ventricle, positive pressure is a drug and the induction is the danger. Both children are simulator scenarios 11 and 12 in the app. Thank you.', 'Part 2')
    return shell('Cardiopulmonary interactions · Part 2', out, code)


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
    files = {'cp-part1.html': build_part1(), 'cp-part2.html': build_part2(), 'ltv-cases.html': build_ltv()}
    for f, t in files.items():
        open(os.path.join(APP, 'talks', f), 'w').write(t)
        print(f, len(t), t.count('<section '), 'slides')
    write_live()
    print('LIVE entries', len(LIVE_OUT))
