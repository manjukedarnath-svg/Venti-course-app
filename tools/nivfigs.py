"""Native SVG drawings for the NIV lessons and talks: the interface gallery, fitting a mask, nostril fill
(high-flow cannula, RAM cannula, binasal prongs), the three kinds of machine, and where to put the nebuliser.

Each figure is drawn once with a palette, so the same drawing serves the talks (CSS tokens, 1680 x 760 canvas)
and the app lessons (hex colours, written to assets/niv/*.svg and shown as <img>).
    python3 tools/nivfigs.py      writes assets/niv/*.svg
"""
import os

DECK = dict(ink='var(--text-primary)', sec='var(--text-secondary)', acc='var(--text-accent)', danger='var(--danger)', ok='var(--success)',
            paper='var(--surface-page)', skin='color-mix(in oklab, var(--text-primary) 6%, var(--surface-page))',
            fm='font-family:var(--font-mono); letter-spacing:.08em; text-transform:uppercase;',
            fb='font-family:var(--font-body, Hanken Grotesk, sans-serif); letter-spacing:0; text-transform:none;',
            fd='font-family:var(--font-display); letter-spacing:-.01em; text-transform:none;')
FILE = dict(ink='#1B1A17', sec='#6E6A63', acc='#B04428', danger='#B42318', ok='#3E7D4F', paper='#F3EDE3', skin='#EAE3D8',
            fm="font-family:'IBM Plex Mono', ui-monospace, monospace; letter-spacing:.08em; text-transform:uppercase;",
            fb="font-family:'Hanken Grotesk', system-ui, sans-serif;",
            fd="font-family:'Instrument Serif', Georgia, serif;")


def T(P, x, y, s, size=22, c='sec', anchor='start', f='fb'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{P[c]}" text-anchor="{anchor}" style="{P[f]}">{s}</text>'


def L(P, d, c='ink', w=3, fill='none', dash=None, op=1):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    fc = P.get(fill, fill)
    return f'<path d="{d}" fill="{fc}" stroke="{P[c]}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{da} opacity="{op}"/>'


def tint(P, c, pct):
    return f'color-mix(in oklab, {P[c]} {pct}%, transparent)'


# ------------------------------------------------------------------ heads (300 x 300 box, facing right) ------------------
CHILD = ('M70 292 C70 262 52 240 46 205 C36 150 52 78 110 48 C160 22 222 44 226 100 C228 116 230 124 232 132 '
         'C236 146 246 160 262 176 C266 182 260 190 248 191 C244 192 242 196 244 202 C248 206 246 212 238 214 '
         'C246 218 246 226 238 230 C238 244 236 252 222 258 C206 262 196 262 188 270 L186 292')
INFANT = ('M84 292 C84 266 62 250 52 214 C36 150 58 72 130 48 C192 30 238 72 238 120 C238 134 238 140 242 150 '
          'C248 158 256 166 260 172 C262 178 256 182 248 182 C246 186 248 192 250 196 C252 202 246 206 242 206 '
          'C250 210 250 218 242 222 C244 236 238 248 224 252 C210 256 200 258 194 266 L192 292')


def head(P, infant=False):
    p = INFANT if infant else CHILD
    ear = 'M126 150 C142 150 148 176 138 194 C130 202 120 194 122 184' if not infant else 'M128 156 C142 156 148 180 138 196 C130 204 120 196 122 186'
    eye = (228, 134) if infant else (206, 132)
    out = L(P, p + ' Z', 'ink', 3, fill=P['skin'])
    out += L(P, ear, 'ink', 2.5)
    out += L(P, f'M{eye[0] - 10} {eye[1]} Q{eye[0]} {eye[1] - 7} {eye[0] + 9} {eye[1]}', 'ink', 2.5)
    out += f'<circle cx="{eye[0]}" cy="{eye[1] - 1}" r="3" fill="{P["ink"]}"/>'
    return out


def straps(P, pts, w=5):
    return ''.join(L(P, d, 'sec', w) for d in pts)


# ------------------------------------------------------------------ each interface ---------------------------------------
def i_nasal(P):
    o = head(P)
    o += straps(P, ['M236 84 C200 60 120 70 52 140', 'M230 186 C190 196 120 210 50 222'])
    o += L(P, 'M228 128 C246 140 270 164 272 176 C274 190 264 200 252 202 L228 200 C220 186 220 150 228 128 Z', 'acc', 3, fill=tint(P, 'acc', 22))
    o += L(P, 'M232 130 L244 88', 'ink', 4) + f'<rect x="228" y="74" width="20" height="18" rx="5" fill="{P["paper"]}" stroke="{P["ink"]}" stroke-width="2.5"/>'
    o += L(P, 'M272 182 C286 186 292 196 292 214 L292 300', 'ink', 10) + L(P, 'M272 182 C286 186 292 196 292 214 L292 300', 'paper', 5)
    o += ''.join(f'<circle cx="{280 + k * 5}" cy="{186 + k * 3}" r="1.8" fill="{P["ink"]}"/>' for k in range(3))
    return o


def i_pillows(P):
    o = head(P)
    o += straps(P, ['M234 194 C206 184 170 166 150 136 C138 116 112 100 50 150', 'M232 200 C190 210 120 214 52 222'])
    o += f'<ellipse cx="250" cy="196" rx="13" ry="8" transform="rotate(-25 250 196)" fill="{tint(P, "acc", 30)}" stroke="{P["acc"]}" stroke-width="3"/>'
    o += L(P, 'M244 204 C252 214 262 222 270 232 L278 300', 'ink', 8) + L(P, 'M244 204 C252 214 262 222 270 232 L278 300', 'paper', 4)
    return o


def i_oronasal(P):
    o = head(P)
    o += straps(P, ['M236 84 C200 60 120 70 52 140', 'M224 226 C190 236 120 240 56 236'])
    o += L(P, 'M228 126 C248 140 274 166 276 182 C278 210 268 232 252 240 L236 240 C220 236 216 220 216 200 C216 170 220 146 228 126 Z', 'acc', 3, fill=tint(P, 'acc', 22))
    o += L(P, 'M232 128 L244 88', 'ink', 4) + f'<rect x="228" y="74" width="20" height="18" rx="5" fill="{P["paper"]}" stroke="{P["ink"]}" stroke-width="2.5"/>'
    o += L(P, 'M276 196 C288 200 294 212 294 228 L294 300', 'ink', 10) + L(P, 'M276 196 C288 200 294 212 294 228 L294 300', 'paper', 5)
    o += f'<circle cx="286" cy="206" r="6" fill="{P["paper"]}" stroke="{P["ok"]}" stroke-width="2.5"/>'
    return o


def i_totalface(P):
    o = head(P)
    o += straps(P, ['M218 70 C170 30 90 50 46 150', 'M226 252 C180 266 110 260 56 240'])
    o += L(P, 'M216 66 C252 72 286 120 288 168 C290 222 262 262 230 264 C214 264 206 250 206 230 L204 100 C204 80 206 68 216 66 Z', 'acc', 3, fill=tint(P, 'acc', 18))
    o += L(P, 'M288 172 L298 176 L298 300', 'ink', 10) + L(P, 'M288 172 L298 176 L298 300', 'paper', 5)
    return o


def i_helmet(P):
    o = L(P, 'M40 300 C40 286 70 278 110 276 L200 276 C240 278 270 286 270 300', 'ink', 3, fill=P['skin'])
    o += head(P)
    o += f'<circle cx="150" cy="150" r="128" fill="{tint(P, "acc", 8)}" stroke="{P["acc"]}" stroke-width="3"/>'
    o += f'<rect x="60" y="256" width="182" height="22" rx="10" fill="{tint(P, "acc", 30)}" stroke="{P["acc"]}" stroke-width="3"/>'
    o += L(P, 'M80 276 L70 300', 'sec', 5) + L(P, 'M222 276 L232 300', 'sec', 5)
    o += L(P, 'M30 200 L52 206', 'ink', 9) + L(P, 'M30 200 L52 206', 'paper', 4)
    o += L(P, 'M248 206 L276 200', 'ink', 9) + L(P, 'M248 206 L276 200', 'paper', 4)
    return o


def i_hfnc(P, infant=False):
    o = head(P, infant)
    y = 186 if infant else 196
    o += f'<rect x="{196 if infant else 194}" y="{y + 2}" width="26" height="16" rx="4" fill="{P["paper"]}" stroke="{P["sec"]}" stroke-width="2"/>'
    o += L(P, f'M250 {y} C240 {y + 6} 230 {y + 8} 210 {y + 10} C180 {y + 12} 150 {y + 4} 136 {y - 10}', 'ink', 9) + L(P, f'M250 {y} C240 {y + 6} 230 {y + 8} 210 {y + 10} C180 {y + 12} 150 {y + 4} 136 {y - 10}', 'paper', 4)
    o += L(P, f'M136 {y - 10} C126 {y + 20} 120 {y + 60} 114 300', 'ink', 11) + L(P, f'M136 {y - 10} C126 {y + 20} 120 {y + 60} 114 300', 'paper', 6)
    o += f'<ellipse cx="{250 if not infant else 248}" cy="{y - 2}" rx="5" ry="4" fill="{P["acc"]}"/>'
    return o


def i_ram(P):
    o = head(P, True)
    y = 186
    o += f'<rect x="200" y="{y + 3}" width="26" height="15" rx="4" fill="{tint(P, "ok", 25)}" stroke="{P["ok"]}" stroke-width="2"/>'
    o += L(P, f'M248 {y} C238 {y + 6} 226 {y + 8} 206 {y + 10} C176 {y + 12} 150 {y} 138 {y - 14} C128 {y - 30} 112 {y - 30} 100 {y - 20} L60 300', 'ink', 7) + \
        L(P, f'M248 {y} C238 {y + 6} 226 {y + 8} 206 {y + 10} C176 {y + 12} 150 {y} 138 {y - 14} C128 {y - 30} 112 {y - 30} 100 {y - 20} L60 300', 'paper', 3)
    o += f'<ellipse cx="248" cy="{y - 3}" rx="6.5" ry="5" fill="{P["acc"]}"/>'
    return o


def i_prongs(P):
    o = head(P, True)
    o += L(P, 'M226 104 C222 66 186 40 132 48 C76 58 48 112 52 200 C58 214 74 214 80 200 C76 132 96 86 134 76 C172 68 204 84 212 108 Z', 'sec', 2.5, fill=tint(P, 'sec', 22))
    o += f'<rect x="250" y="176" width="26" height="22" rx="5" fill="{tint(P, "acc", 25)}" stroke="{P["acc"]}" stroke-width="3"/>'
    o += f'<rect x="242" y="182" width="12" height="9" rx="3" fill="{P["acc"]}"/>'
    d = 'M252 180 C234 176 212 172 192 164 C172 156 162 138 164 112'
    o += L(P, d, 'ink', 11) + L(P, d, 'paper', 6)
    return o


GALLERY = [
    ('Nasal mask', 'Infants, long term, can talk', i_nasal),
    ('Nasal pillows', 'Small, least claustrophobic', i_pillows),
    ('Oronasal mask', 'Acute failure: first choice', i_oronasal),
    ('Total face mask', 'Odd anatomy, sore bridge', i_totalface),
    ('Helmet', 'Longest tolerance; noisy', i_helmet),
    ('High-flow cannula', 'Leaks by design; set FiO₂', lambda P: i_hfnc(P, False)),
    ('RAM cannula', 'Infant CPAP/NIPPV, off-label', i_ram),
    ('Binasal prongs', 'Infant CPAP, bonnet', i_prongs),
]


def gallery(P, cols=4, W=1680, H=760, label=True):
    rows = (len(GALLERY) + cols - 1) // cols
    cw, ch = W / cols, H / rows
    s = min(cw / 330, (ch - 70) / 300)
    out = ''
    for k, (name, use, fn) in enumerate(GALLERY):
        cx, cy = (k % cols) * cw, (k // cols) * ch
        ox = cx + (cw - 300 * s) / 2
        out += f'<g transform="translate({ox:.1f},{cy + 4:.1f}) scale({s:.3f})">{fn(P)}</g>'
        if label:
            out += T(P, cx + cw / 2, cy + 300 * s + 34, name, 30 if W > 1000 else 26, 'ink', 'middle', 'fd')
            out += T(P, cx + cw / 2, cy + 300 * s + 60, use, 19 if W > 1000 else 18, 'sec', 'middle', 'fb')
    return out


# ------------------------------------------------------------------ fitting the mask ---------------------------------------
FIT = [((228, 120), (192, 100), '1', 'Top of the cushion on the bridge, below the eyes'), ((242, 242), (250, 268), '2', 'Bottom edge in the crease below the lower lip'),
       ((240, 82), (270, 62), '3', 'Forehead arm set so the cushion sits evenly'), ((140, 70), (140, 44), '4', 'Least strap tension that stops the leak'),
       ((220, 140), (178, 150), '5', 'Hydrocolloid on the bridge before it reddens'), ((286, 206), (316, 230), '6', 'Port open; anti-asphyxia valve on an oronasal mask')]
BIG = 'M212 96 C252 108 286 150 288 190 C290 240 266 268 236 270 L220 268 C204 260 202 220 202 180 C202 140 204 112 212 96 Z'
TINY = 'M236 150 C250 158 266 172 268 182 C270 196 262 208 252 210 L236 210 C230 200 230 172 236 150 Z'


def _fitdraw(P, x0, y0, s):
    out = f'<g transform="translate({x0},{y0}) scale({s})">{i_oronasal(P)}</g>'
    for (x, y), (lx, ly), n, _ in FIT:
        X, Y, LX, LY = x0 + x * s, y0 + y * s, x0 + lx * s, y0 + ly * s
        out += L(P, f'M{X:.0f} {Y:.0f} L{LX:.0f} {LY:.0f}', 'acc', 2)
        out += f'<circle cx="{X:.0f}" cy="{Y:.0f}" r="5" fill="{P["acc"]}"/><circle cx="{LX:.0f}" cy="{LY:.0f}" r="17" fill="{P["acc"]}"/>' + T(P, LX, LY + 7, n, 20, 'paper', 'middle', 'fm')
    return out


def _wrong(P, x0, y0, s, path, label):
    g = f'<g transform="translate({x0},{y0}) scale({s})">{head(P)}{L(P, path, "danger", 3, fill=tint(P, "danger", 18))}</g>'
    return g + T(P, x0 + 150 * s, y0 + 300 * s + 30, label, 20, 'danger', 'middle', 'fm')


def fitting(P, W=1680, H=760, portrait=False):
    if portrait:
        out = _fitdraw(P, 20, 40, 2.3)
        for i, (_, _, n, t) in enumerate(FIT):
            ty = 790 + i * 56
            out += f'<circle cx="46" cy="{ty - 8}" r="16" fill="none" stroke="{P["acc"]}" stroke-width="2.5"/>' + T(P, 46, ty - 1, n, 18, 'acc', 'middle', 'fm') + T(P, 76, ty, t, 26, 'ink', 'start', 'fb')
        out += _wrong(P, 60, 1150, 0.95, BIG, 'Too big: eyes, past chin') + _wrong(P, 430, 1150, 0.95, TINY, 'Too small: pinches nose')
        return out
    out = _fitdraw(P, 30, 30, 2.25)
    for i, (_, _, n, t) in enumerate(FIT):
        ty = 70 + i * 66
        out += f'<circle cx="790" cy="{ty - 8}" r="15" fill="none" stroke="{P["acc"]}" stroke-width="2.5"/>' + T(P, 790, ty - 1, n, 18, 'acc', 'middle', 'fm') + T(P, 820, ty, t, 26, 'ink', 'start', 'fb')
    out += _wrong(P, 860, 470, 0.7, BIG, 'Too big: eyes, past chin') + _wrong(P, 1260, 470, 0.7, TINY, 'Too small: pinches nose')
    return out


# ------------------------------------------------------------------ nostril fill -----------------------------------------
NOS = [('High-flow cannula', 0.45, 'Visible gap', ['Visible gap around each prong', 'Leaks by design: gas escapes', 'Flow and FiO₂ are set, not pressure']),
       ('RAM cannula', 0.72, '60–80% fill', ['Prongs fill 60–80% of the nostril', 'Delivers far less pressure than set', 'Keep the mouth closed']),
       ('Binasal CPAP prongs', 1.0, 'Fills · seals', ['Prongs fill the nostril and seal', 'Pressure close to what is set', 'Septum injury: check every 4 h'])]


def _nos(P, cx, cy, f, k=1.0):
    out = ''
    for dx in (-62 * k, 62 * k):
        out += f'<ellipse cx="{cx + dx}" cy="{cy}" rx="{52 * k}" ry="{78 * k}" fill="{P["skin"]}" stroke="{P["ink"]}" stroke-width="3"/>'
        out += f'<ellipse cx="{cx + dx}" cy="{cy}" rx="{52 * k * f ** .5 * .96:.1f}" ry="{78 * k * f ** .5 * .96:.1f}" fill="{tint(P, "acc", 35)}" stroke="{P["acc"]}" stroke-width="3"/>'
    return out + L(P, f'M{cx - 4} {cy - 80 * k} L{cx - 4} {cy + 80 * k} M{cx + 4} {cy - 80 * k} L{cx + 4} {cy + 80 * k}', 'sec', 2)


def nostrils(P, W=1680, H=640, portrait=False):
    out = T(P, W / 2, 50, 'Seen from below: two nostrils, two prongs', 22, 'sec', 'middle', 'fm')
    for k, (name, f, tag, lines) in enumerate(NOS):
        if portrait:
            y0 = 110 + k * 300
            out += _nos(P, 150, y0 + 110, f, 0.85)
            out += T(P, 300, y0 + 50, name, 36, 'ink', 'start', 'fd') + T(P, 300, y0 + 84, tag, 20, 'acc', 'start', 'fm')
            out += ''.join(T(P, 300, y0 + 130 + j * 36, ln, 24, 'ink' if j == 0 else 'sec', 'start', 'fb') for j, ln in enumerate(lines))
        else:
            cx = W / 3 * k + W / 6
            out += _nos(P, cx, 210, f)
            out += T(P, cx, 360, name, 36, 'ink', 'middle', 'fd') + T(P, cx, 396, tag, 22, 'acc', 'middle', 'fm')
            out += ''.join(T(P, cx, 450 + j * 40, ln, 25, 'ink' if j == 0 else 'sec', 'middle', 'fb') for j, ln in enumerate(lines))
    return out


# ------------------------------------------------------------------ three machines ---------------------------------------
MACH = [('ICU ventilator', ['Wall air and oxygen', 'Two limbs, expiratory valve', 'Any FiO₂ to 1.0, full alarms', 'NIV mode: check it copes with leak'], 'icu'),
        ('Standalone NIV', ['Own turbine, oxygen blender', 'One limb, leak port', 'Built to chase leak', 'Graphics, alarms, battery'], 'niv'),
        ('Home bilevel', ['Own turbine, small, battery', 'One limb, leak port', 'O₂ bled in: FiO₂ ≈ 0.45–0.5', 'Few alarms: not for hypoxaemia'], 'home')]


def _machine(P, x0, base, kind):
    out = ''
    bw, bh = (230, 190) if kind == 'icu' else ((210, 150) if kind == 'niv' else (170, 110))
    by = base - bh
    out += f'<rect x="{x0}" y="{by}" width="{bw}" height="{bh}" rx="14" fill="{P["skin"]}" stroke="{P["ink"]}" stroke-width="3"/>'
    out += f'<rect x="{x0 + 18}" y="{by + 18}" width="{bw - 36}" height="{bh * .45:.0f}" rx="6" fill="{P["ink"]}"/>'
    out += L(P, f'M{x0 + 30} {by + 18 + bh * .3:.0f} l18 -14 l14 18 l18 -22 l16 16 l20 -10', 'paper', 2.5)
    if kind == 'icu':
        for j, g in enumerate(['O₂', 'Air']):
            out += L(P, f'M{x0 + 40 + j * 60} {base} L{x0 + 40 + j * 60} {base + 40} L{x0 + 20 + j * 60} {base + 60}', 'sec', 4) + T(P, x0 + 6 + j * 60, base + 86, g, 18, 'sec', 'start', 'fm')
        out += L(P, f'M{x0 + bw} {by + 60} C{x0 + bw + 70} {by + 60} {x0 + bw + 100} {by + 120} {x0 + bw + 110} {base + 40}', 'ink', 9)
        out += L(P, f'M{x0 + bw} {by + 130} C{x0 + bw + 40} {by + 130} {x0 + bw + 70} {by + 170} {x0 + bw + 100} {base + 40}', 'ink', 9)
        out += f'<circle cx="{x0 + bw + 106}" cy="{base + 50}" r="14" fill="{tint(P, "acc", 25)}" stroke="{P["acc"]}" stroke-width="3"/>'
        out += T(P, x0 + bw + 30, by - 10, 'Two limbs', 18, 'sec', 'start', 'fm')
    else:
        fx, fy = x0 + bw - 40, by + bh - 32
        out += f'<circle cx="{fx}" cy="{fy}" r="20" fill="none" stroke="{P["sec"]}" stroke-width="2.5"/>' + ''.join(
            L(P, f'M{fx} {fy} q{8 * dx} {-10 * dy} {16 * dx} {-4 * dy}', 'sec', 2.5) for dx, dy in ((1, 1), (-1, -1), (1, -1), (-1, 1)))
        out += L(P, f'M{x0 + bw} {by + 40} C{x0 + bw + 70} {by + 40} {x0 + bw + 90} {by + 100} {x0 + bw + 110} {base + 40}', 'ink', 9)
        out += ''.join(f'<circle cx="{x0 + bw + 98 + d * 7}" cy="{base + 12 + d * 3}" r="2.5" fill="{P["acc"]}"/>' for d in range(3))
        out += T(P, x0 + bw + 30, by - 10, 'One limb · leak', 18, 'sec', 'start', 'fm')
        if kind == 'home':
            out += f'<rect x="{x0 + 18}" y="{by + bh - 30}" width="34" height="16" rx="3" fill="none" stroke="{P["ok"]}" stroke-width="2.5"/>'
    return out


def machines(P, W=1680, H=660, portrait=False):
    out = ''
    for k, (name, lines, kind) in enumerate(MACH):
        if portrait:
            y0 = 30 + k * 560
            out += _machine(P, 60, y0 + 230, kind)
            out += T(P, 60, y0 + 360, name, 38, 'ink', 'start', 'fd') + ''.join(T(P, 60, y0 + 404 + j * 36, ln, 25, 'ink' if j < 2 else 'sec', 'start', 'fb') for j, ln in enumerate(lines))
        else:
            x0 = W / 3 * k + 50
            out += _machine(P, x0, 250, kind)
            out += T(P, x0, 410, name, 40, 'ink', 'start', 'fd') + ''.join(T(P, x0, 460 + j * 44, ln, 25, 'ink' if j < 2 else 'sec', 'start', 'fb') for j, ln in enumerate(lines))
    return out


# ------------------------------------------------------------------ where the nebuliser goes -------------------------------
def _box(P, x, y, w, h, t, sub=''):
    r = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{P["skin"]}" stroke="{P["ink"]}" stroke-width="3"/>' + T(P, x + w / 2, y + h / 2 + 8, t, 24, 'ink', 'middle', 'fb')
    return r + (T(P, x + w / 2, y + h + 26, sub, 17, 'sec', 'middle', 'fm') if sub else '')


def _neb(P, x, y, ok=True, label='', anchor='middle'):
    c = 'ok' if ok else 'danger'
    r = f'<path d="M{x - 16} {y - 30} L{x + 16} {y - 30} L{x + 10} {y - 4} L{x - 10} {y - 4} Z" fill="{tint(P, c, 30)}" stroke="{P[c]}" stroke-width="3"/>'
    r += (L(P, f'M{x - 10} {y - 52} l20 14 M{x + 10} {y - 52} l-20 14', c, 4) if not ok else L(P, f'M{x - 12} {y - 46} l8 9 l16 -18', c, 4))
    return r + (T(P, x, y - 62, label, 18, c, anchor, 'fm') if label else '')


def nebs(P, W=1680, H=660, portrait=False):
    if portrait:
        out = T(P, 30, 50, 'High-flow', 36, 'acc', 'start', 'fd')
        out += _box(P, 30, 130, 170, 64, 'Blender', 'Flow · FiO₂') + _box(P, 290, 130, 200, 64, 'Humidifier', '37 °C') + _box(P, 580, 130, 190, 64, 'Cannula', 'Nose')
        out += L(P, 'M200 162 L290 162', 'ink', 6) + L(P, 'M490 162 L580 162', 'ink', 9)
        out += _neb(P, 245, 162, True, 'Mesh here') + _neb(P, 675, 126, False, 'Mask over it')
        lines = ['Keep the high-flow running and the humidifier on.', 'Mesh nebuliser at the humidifier inlet: no extra gas.', 'A spacer close to the cannula, plume to the child.']
        out += ''.join(T(P, 30, 270 + j * 36, ln, 24, 'ink' if j == 0 else 'sec', 'start', 'fb') for j, ln in enumerate(lines))
        out += T(P, 30, 440, 'NIV · single limb', 36, 'acc', 'start', 'fd')
        out += _box(P, 30, 540, 160, 64, 'Bilevel', 'Turbine') + _box(P, 610, 540, 160, 64, 'Mask', 'Non-vented')
        out += L(P, 'M190 572 L610 572', 'ink', 9)
        out += f'<rect x="420" y="557" width="60" height="30" rx="6" fill="{P["paper"]}" stroke="{P["sec"]}" stroke-width="2.5"/>' + T(P, 450, 628, 'Leak port', 17, 'sec', 'middle', 'fm')
        out += _neb(P, 545, 572, True, 'Here') + _neb(P, 290, 572, False, 'Not here')
        lines = ['Do not take the mask off to nebulise.', 'Mesh nebuliser between the leak port and the mask;', 'a spacer there too, fired at the start of a breath.', 'A jet nebuliser adds gas: VT, FiO₂ and trigger change.']
        out += ''.join(T(P, 30, 690 + j * 36, ln, 24, 'ink' if j == 0 else 'sec', 'start', 'fb') for j, ln in enumerate(lines))
        return out
    out = T(P, 40, 50, 'High-flow', 34, 'acc', 'start', 'fd')
    y = 120
    out += _box(P, 40, y, 190, 70, 'Blender', 'Flow · FiO₂') + _box(P, 400, y, 210, 70, 'Humidifier', '37 °C') + _box(P, 1240, y, 230, 70, 'Cannula', 'Nose')
    out += L(P, f'M230 {y + 35} L400 {y + 35}', 'ink', 6) + L(P, f'M610 {y + 35} C800 {y + 35} 1000 {y + 35} 1240 {y + 35}', 'ink', 9)
    out += _neb(P, 315, y + 35, True, 'Mesh, at the humidifier inlet') + _neb(P, 1360, y - 2, False, 'Mask over the cannula')
    out += T(P, 640, y + 120, 'Keep the high-flow running and the humidifier on. Mesh rather than jet: no extra gas.', 24, 'ink', 'start', 'fb')
    out += T(P, 640, y + 156, 'A spacer goes close to the cannula, plume towards the child.', 22, 'sec', 'start', 'fb')
    y = 420
    out += T(P, 40, y - 60, 'NIV · single limb', 34, 'acc', 'start', 'fd')
    out += _box(P, 40, y, 200, 70, 'Bilevel', 'Turbine') + _box(P, 1300, y, 170, 70, 'Mask', 'Non-vented')
    out += L(P, f'M240 {y + 35} C600 {y + 35} 900 {y + 35} 1300 {y + 35}', 'ink', 9)
    out += f'<rect x="1010" y="{y + 20}" width="70" height="30" rx="6" fill="{P["paper"]}" stroke="{P["sec"]}" stroke-width="2.5"/>' + T(P, 1045, y + 92, 'Leak port', 17, 'sec', 'middle', 'fm')
    out += ''.join(f'<circle cx="{1032 + d * 12}" cy="{y + 14 - d * 6}" r="3" fill="{P["acc"]}"/>' for d in range(3))
    out += _neb(P, 1190, y + 35, True, 'Between port and mask') + _neb(P, 520, y + 35, False, 'Back at the machine')
    out += T(P, 40, y + 150, 'Do not take the mask off to nebulise. Mesh nebuliser between the leak port and the mask;', 24, 'ink', 'start', 'fb')
    out += T(P, 40, y + 186, 'a spacer in the same place, fired at the start of a breath. A jet nebuliser adds gas: it changes VT, FiO₂ and triggering.', 22, 'sec', 'start', 'fb')
    return out


def svgfile(inner, W, H):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<rect width="{W}" height="{H}" fill="{FILE["paper"]}"/>{inner}</svg>')


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'niv')
    os.makedirs(out, exist_ok=True)
    files = {'interfaces.svg': (gallery(FILE, cols=2, W=760, H=1520), 760, 1520),
             'fitting.svg': (fitting(FILE, portrait=True), 800, 1480),
             'nostrils.svg': (nostrils(FILE, W=800, portrait=True), 800, 1030),
             'machines.svg': (machines(FILE, portrait=True), 800, 1680),
             'nebulisers.svg': (nebs(FILE, portrait=True), 800, 840)}
    for n, (inner, w, h) in files.items():
        open(os.path.join(out, n), 'w').write(svgfile(inner, w, h))
        print(n)
