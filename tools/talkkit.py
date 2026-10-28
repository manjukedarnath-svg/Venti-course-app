"""Theory-slide helpers for the Solstice talks (same markup as talks/long-term-ventilation.html).

Each function returns one <section>. Figures are native SVG on a 1680 x 760 canvas, drawn with CSS tokens so the
deck's theme carries through. Used by tools/build_niv.py.
"""
import html

e = lambda t: html.escape(str(t), quote=True)
MONO = "font-family:var(--font-mono); letter-spacing:.14em; text-transform:uppercase;"
LOGO = ('<div data-logo-plate="1" style="position:absolute; right:28px; bottom:16px; display:flex; align-items:center; gap:22px; background:#FFFFFF; border-radius:4px; padding:8px 16px; z-index:5; pointer-events:none;">'
        '<img src="../assets/logo-kims.png" alt="KIMS Hospitals Bengaluru" style="height:44px; width:auto; display:block;"><span style="width:1px; height:36px; background:#D2C5B1;"></span>'
        '<img src="../assets/logo-cuddles.png" alt="KIMS Cuddles Mother &amp; Child Centre" style="height:36px; width:auto; display:block;"></div>')
BODY = 'font-family:var(--font-body, Hanken Grotesk, sans-serif); letter-spacing:0; text-transform:none;'
DISP = 'font-family:var(--font-display); letter-spacing:-.01em; text-transform:none;'


def _sec(label, inner, notes, pad='80px 120px', chord=None, extra='', skip=False):
    a = f'data-label="{e(label)}"' + (' data-deck-skip' if skip else '') + (f' data-chord="{chord}"' if chord else '')
    return (f'<section {a} data-speaker-notes="{e(notes)}" style="background:var(--surface-page); color:var(--text-primary); padding:{pad}; box-sizing:border-box; display:flex; flex-direction:column; gap:36px;{extra}">\n'
            f'{inner}\n{LOGO}\n</section>\n')


def head(h, tag=''):
    return ('<div style="flex:none; display:flex; justify-content:space-between; align-items:baseline; gap:40px;">'
            f'<h2 style="margin:0; flex:1; min-width:0; font-family:var(--font-display); font-weight:400; font-size:84px; line-height:1; letter-spacing:-.01em; text-wrap:balance;">{h}</h2>'
            + (f'<span style="{MONO} font-size:24px; color:var(--text-secondary); text-align:right; flex:none;">{e(tag)}</span>' if tag else '') + '</div>')


def title(kicker, h, sub, notes):
    inner = (f'<span style="{MONO} font-size:26px; color:var(--text-secondary);">{e(kicker)}</span>'
             f'<div style="display:flex; flex-direction:column; gap:36px;"><h1 style="margin:0; font-family:var(--font-display); font-weight:400; font-size:150px; line-height:.94; letter-spacing:-.02em;">{h}</h1>'
             f'<p style="margin:0; font-weight:300; font-size:48px; line-height:1.3; color:var(--text-secondary);">{e(sub)}</p></div>'
             f'<div style="display:flex; flex-direction:column; gap:12px;"><span style="{MONO} font-size:24px; color:var(--text-primary);">Dr Manju Kedarnath</span>'
             f'<span style="{MONO} font-size:24px; color:var(--text-secondary);">Senior consultant and clinical lead · Pediatrics, Peds ER and PICU</span>'
             f'<span style="{MONO} font-size:24px; color:var(--text-secondary);">KIMS Hospitals, Electronic City, Bangalore</span></div>')
    return _sec('Title', inner, notes, pad='120px 140px', chord='dusk', extra=' justify-content:space-between;')


def divider(label, kicker, h, sub, notes):
    inner = (f'<span style="{MONO} font-size:30px; color:var(--text-secondary);">{e(kicker)}</span>'
             f'<h2 style="margin:0; font-family:var(--font-display); font-weight:400; font-size:140px; line-height:.95; letter-spacing:-.02em;">{h}</h2>'
             f'<p style="margin:0; font-size:44px; line-height:1.3; color:var(--text-secondary);">{e(sub)}</p>')
    return _sec(label, inner, notes, pad='120px 140px', chord='dusk', extra=' justify-content:flex-end; gap:32px;')


def bullets(label, h, tag, items, notes, size=50, skip=False):
    dots = ''.join('<div style="display:flex; gap:24px; align-items:baseline;"><span style="flex:none; width:14px; height:14px; border-radius:50%; background:var(--text-accent); transform:translateY(-6px);"></span>'
                   f'<span style="font-size:{size}px; line-height:1.25; text-wrap:balance;">{x}</span></div>' for x in items)
    return _sec(label, head(h, tag) + f'<div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:44px; max-width:1560px;">{dots}</div>', notes, skip=skip)


def numbers(label, h, tag, items, notes, foot='', skip=False):
    cols = ''.join('<div style="border-top:2px solid var(--text-primary); padding-top:28px; display:flex; flex-direction:column; gap:18px;">'
                   f'<span style="font-family:var(--font-display); font-size:{140 if len(n) < 7 else 104}px; line-height:.9; color:var(--text-accent);">{e(n)}</span>'
                   f'<span style="{MONO} font-size:26px; color:var(--text-secondary);">{e(k)}</span>'
                   f'<span style="font-size:36px; line-height:1.3; text-wrap:balance;">{e(t)}</span></div>' for n, k, t in items)
    body = head(h, tag) + f'<div style="flex:1; min-height:0; display:grid; grid-template-columns:repeat({len(items)},1fr); gap:64px; align-items:center;">{cols}</div>'
    if foot:
        body += f'<p style="margin:0; font-size:40px; line-height:1.3; text-wrap:balance;">{e(foot)}</p>'
    return _sec(label, body, notes, skip=skip)


def cards(label, h, tag, items, notes, big=None, size=38, skip=False):
    """items: (eyebrow, [lines]) ; big: optional list of large numerals/words per card."""
    out = ''
    for i, (k, lines) in enumerate(items):
        top = f'<span style="font-family:var(--font-display); font-size:96px; line-height:.95; color:var(--text-accent);">{e(big[i])}</span>' if big else ''
        out += ('<div style="border:1px solid var(--border-default); border-radius:4px; padding:34px 36px; display:flex; flex-direction:column; gap:18px; min-height:0; justify-content:center;">'
                f'{top}<span style="{MONO} font-size:24px; color:var(--text-secondary);">{e(k)}</span>'
                + ''.join(f'<span style="font-size:{size}px; line-height:1.3; text-wrap:balance;">{x}</span>' for x in lines) + '</div>')
    n = len(items)
    cols = n if n <= 4 else (3 if n in (5, 6) else 4)
    body = head(h, tag) + f'<div style="flex:1; min-height:0; display:grid; grid-template-columns:repeat({cols},1fr); grid-auto-rows:1fr; gap:24px; align-items:stretch;">{out}</div>'
    return _sec(label, body, notes, skip=skip)


def two(label, h, tag, left, right, notes, skip=False):
    """Two columns of (eyebrow, [lines]); left in ink, right in accent."""
    def col(k, lines, acc):
        return (f'<div style="border-top:{"3px solid var(--text-accent)" if acc else "2px solid var(--text-primary)"}; padding-top:28px; display:flex; flex-direction:column; gap:26px;">'
                f'<span style="{MONO} font-size:26px; color:{"var(--text-accent)" if acc else "var(--text-secondary)"};">{e(k)}</span>'
                + ''.join(f'<span style="font-size:42px; line-height:1.3; text-wrap:balance;">{x}</span>' for x in lines) + '</div>')
    body = head(h, tag) + f'<div style="flex:1; min-height:0; display:grid; grid-template-columns:1fr 1fr; gap:96px; align-items:center;">{col(*left, False)}{col(*right, True)}</div>'
    return _sec(label, body, notes, skip=skip)


def table(label, h, tag, cols, rows, notes, widths=None, size=30, skip=False):
    th = f'{MONO} font-size:20px; color:var(--text-secondary); text-align:left; padding:0 20px 14px 0; border-bottom:2px solid var(--text-primary);'
    cg = ''.join(f'<col style="width:{w}">' for w in widths) if widths else ''
    trs = ''
    for r in rows:
        trs += '<tr>' + ''.join(f'<td style="vertical-align:top; padding:18px 20px 18px 0; border-bottom:1px solid var(--border-subtle); font-size:{size}px; line-height:1.3;{" color:var(--text-accent);" if j == 0 else ""}">{c}</td>' for j, c in enumerate(r)) + '</tr>'
    body = head(h, tag) + (f'<div style="flex:1; min-height:0; display:flex; align-items:center;"><table style="width:100%; border-collapse:collapse; table-layout:fixed;"><colgroup>{cg}</colgroup>'
                           f'<thead><tr>{"".join(f"<th style={chr(34)}{th}{chr(34)}>{e(c)}</th>" for c in cols)}</tr></thead><tbody>{trs}</tbody></table></div>')
    return _sec(label, body, notes, skip=skip)


def figure(label, h, tag, svg_inner, notes, side=None, skip=False):
    """A native SVG figure (1680x760 canvas). side = optional (eyebrow, [lines]) column on the right; the figure then narrows."""
    svg = ('<svg viewBox="0 0 1680 760" preserveAspectRatio="xMidYMid meet" style="position:absolute; inset:0; width:100%; height:100%; font-family:var(--font-mono); letter-spacing:.08em; text-transform:uppercase;">'
           '<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--text-primary)"/></marker>'
           '<marker id="arra" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--text-accent)"/></marker></defs>'
           f'{svg_inner}</svg>')
    fig = f'<div style="flex:1; min-height:0; position:relative;">{svg}</div>'
    if side:
        k, lines = side
        col = (f'<div style="flex:none; width:470px; display:flex; flex-direction:column; justify-content:center; gap:26px; border-left:2px solid var(--text-primary); padding-left:40px;">'
               f'<span style="{MONO} font-size:24px; color:var(--text-accent);">{e(k)}</span>'
               + ''.join(f'<span style="font-size:36px; line-height:1.3; text-wrap:balance;">{x}</span>' for x in lines) + '</div>')
        fig = f'<div style="flex:1; min-height:0; display:flex; gap:48px;">{fig}{col}</div>'
    return _sec(label, head(h, tag) + fig, notes, skip=skip)


def quiz(n, h, stem, opts, ans, why, notes_q, notes_a, skip=False):
    def optbox(L, t, good):
        b = 'border:1px solid var(--success); background:var(--success-soft);' if good else 'border:1px solid var(--border-default); background:transparent;'
        return (f'<div style="display:flex; gap:24px; align-items:center; padding:24px 28px; border-radius:4px; {b}"><span style="font-family:var(--font-mono); font-size:26px; color:var(--text-secondary);">{L}</span>'
                f'<span style="font-size:32px; line-height:1.3;">{t}</span></div>')
    q = (head(h, 'Check your understanding') + '<div style="flex:1; min-height:0; display:grid; grid-template-columns:1fr 1fr; gap:72px; align-items:stretch;">'
         f'<div style="display:flex; flex-direction:column; gap:20px; min-width:0; min-height:0;"><p style="margin:0; font-size:36px; line-height:1.45; text-wrap:pretty;">{stem}</p></div>'
         '<div style="display:flex; flex-direction:column; gap:28px; min-width:0; align-self:start;">' + ''.join(optbox(L, t, False) for L, t in opts) + '</div></div>')
    a = (head(h, 'Answer') + '<div style="flex:1; min-height:0; display:grid; grid-template-columns:1fr 1fr; gap:72px; align-items:stretch;">'
         f'<div style="display:flex; flex-direction:column; gap:24px; min-width:0; justify-content:center;"><span style="{MONO} font-size:24px; color:var(--text-accent);">Why</span>'
         f'<p style="margin:0; font-size:34px; line-height:1.45; text-wrap:pretty;">{why}</p></div>'
         '<div style="display:flex; flex-direction:column; gap:28px; min-width:0; align-self:start;">' + ''.join(optbox(L, t, L == ans) for L, t in opts) + '</div></div>')
    return _sec(f'Quiz {n}', q, notes_q, skip=skip) + _sec(f'Quiz {n} · answer', a, notes_a, skip=skip)


def ending(label, kicker, h, sub, notes):
    inner = (f'<span style="{MONO} font-size:30px; color:var(--text-secondary);">{e(kicker)}</span>'
             f'<h2 style="margin:0; font-family:var(--font-display); font-weight:400; font-size:140px; line-height:.95; letter-spacing:-.02em;">{h}</h2>'
             f'<p style="margin:0; font-size:44px; line-height:1.3; color:var(--text-secondary);">{e(sub)}</p>')
    return _sec(label, inner, notes, pad='120px 140px', chord='dusk', extra=' justify-content:flex-end; gap:32px;')


# ---------------------------------------------------------------- SVG primitives ---------------------------------------
def ln(x1, y1, x2, y2, c='var(--text-primary)', w=2, dash=None, arrow=None, op=1):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    m = f' marker-end="url(#{arrow})"' if arrow else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"{d}{m} opacity="{op}"/>'


def pth(d, c='var(--text-primary)', w=4, fill='none', dash=None, arrow=None, op=1):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    m = f' marker-end="url(#{arrow})"' if arrow else ''
    return f'<path d="{d}" fill="{fill}" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{da}{m} opacity="{op}"/>'


def poly(pts, **k):
    return pth('M' + ' L'.join(f'{round(x, 1)},{round(y, 1)}' for x, y in pts), **k)


def rc(x, y, w, h, fill='none', c='var(--text-primary)', sw=2, r=0, op=1, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{c}" stroke-width="{sw}"{da} opacity="{op}"/>'


def circ(cx, cy, r, fill='none', c='var(--text-primary)', sw=2, op=1):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{c}" stroke-width="{sw}" opacity="{op}"/>'


def tx(x, y, t, size=26, c='var(--text-secondary)', anchor='start', font='mono', weight=None):
    st = {'mono': '', 'body': BODY, 'disp': DISP}[font]
    wt = f' font-weight="{weight}"' if weight else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{c}" text-anchor="{anchor}"{wt} style="{st}">{t}</text>'


def axes(x0, y0, x1, y1, xlab='', ylab='', yticks=(), xticks=(), ymap=None, xmap=None):
    out = ln(x0, y0, x1, y0) + ln(x0, y1, x0, y0)
    for v in yticks:
        y = ymap(v)
        out += ln(x0 - 10, y, x0, y) + tx(x0 - 20, y + 8, v, 20, anchor='end')
    for v, lab in xticks:
        x = xmap(v)
        out += tx(x, y0 + 40, lab, 24, anchor='middle')
    if ylab:
        out += f'<text transform="translate({x0 - 90},{(y0 + y1) / 2}) rotate(-90)" font-size="20" fill="var(--text-secondary)" text-anchor="middle">{ylab}</text>'
    if xlab:
        out += tx((x0 + x1) / 2, y0 + 80, xlab, 22, anchor='middle')
    return out
