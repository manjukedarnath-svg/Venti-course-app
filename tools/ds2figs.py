"""Native SVG figures for the disease-specific Part 2 talk (tools/build_ds2.py): dynamic hyperinflation, why the blood
pressure falls in asthma, and Tasker's inflation–deflation curves for bronchiolitis (Rimensberger, Pediatric and Neonatal
Mechanical Ventilation 2015, ch. 50, figs 50.3–50.5: model 5 kg infant, pressure control, passive expiration)."""
import math
from talkkit import ln, pth, poly, rc, tx, axes, circ

A, P, S = 'var(--text-accent)', 'var(--text-primary)', 'var(--text-secondary)'


# ------------------------------------------------------------------ dynamic hyperinflation ------------------------------
def fig_dhi():
    out = ''
    # left: one expiration
    X0, X1, Y0, Y1 = 150, 760, 560, 140
    xm = lambda t: X0 + (X1 - X0) * t / 4.0          # t in time constants
    ym = lambda v: Y0 - (Y0 - Y1) * v                # v = fraction of the breath still in the lung
    out += axes(X0, Y0, X1, Y1, '', 'Breath still in the lung', yticks=[], xticks=[], xmap=xm)
    for t in range(5):
        out += tx(xm(t), Y0 + 40, '0' if t == 0 else f'{t} τ', 24, S, anchor='middle', font='body')
    out += tx((X0 + X1) / 2, Y0 + 84, 'Expiratory time, in time constants (τ = R × C)', 24, S, anchor='middle', font='body')
    out += tx(X0 - 16, ym(1) + 8, '100%', 20, anchor='end') + tx(X0 - 16, ym(0) + 8, '0', 20, anchor='end')
    pts = [(xm(t / 50), ym(math.exp(-t / 50))) for t in range(0, 201)]
    out += poly(pts, c=P, w=5)
    for t, lab in [(1, '37% left'), (3, '5% left')]:
        out += ln(xm(t), ym(math.exp(-t)), xm(t), Y0, c=S, w=1.5, dash='6 6') + circ(xm(t), ym(math.exp(-t)), 8, P, P) + tx(xm(t) + 16, ym(math.exp(-t)) - 14, lab, 22, P)
    te = 1.5
    out += rc(xm(te) - 2, ym(math.exp(-te)), 4, Y0 - ym(math.exp(-te)), fill=A, c=A, sw=0)
    out += ln(xm(te), Y1 - 10, xm(te), ym(math.exp(-te)), c=A, w=3, dash='10 8')
    out += tx(xm(te), Y1 - 24, 'Next breath arrives at 1.5 τ', 26, A, anchor='middle', font='body')
    out += tx(xm(te) + 120, ym(0.42), '22% of the breath', 28, A, font='body') + tx(xm(te) + 120, ym(0.42) + 36, 'is still inside', 28, A, font='body') + ln(xm(te) + 110, ym(0.40), xm(te) + 10, ym(0.14), c=A, w=2, arrow='arra')
    out += tx(X0, 70, 'One breath out', 26, P)
    # right: the staircase to a new end-expiratory volume
    X0, X1, Y0, Y1 = 960, 1640, 560, 140
    out += ln(X0, Y0, X1, Y0) + ln(X0, Y1, X0, Y0)
    out += tx(X0, 70, 'Breath after breath', 26, P)
    vt, tau, ti, te = 1.0, 1.0, 0.6, 1.0                # Te = 1 τ: 37% of each breath left behind
    e_ = math.exp(-te / tau); vtrap = vt * e_ / (1 - e_)
    top = vtrap + vt
    ym = lambda v: Y0 - (Y0 - Y1) * v / (top * 1.08)
    n, T = 7, ti + te
    xm = lambda t: X0 + (X1 - X0 - 40) * t / (n * T)
    pts, v = [], 0.0
    for k in range(n):
        t0 = k * T
        pts.append((xm(t0), ym(v))); v += vt; pts.append((xm(t0 + ti), ym(v)))
        for j in range(1, 21):
            t = te * j / 20; pts.append((xm(t0 + ti + t), ym(v * math.exp(-t / tau))))
        v = v * math.exp(-te / tau)
    out += poly(pts, c=P, w=4)
    out += ln(X0, ym(0), X1, ym(0), c=S, w=2, dash='8 8') + tx(X0 - 14, ym(0) + 8, 'FRC', 22, anchor='end')
    out += ln(X0, ym(vtrap), X1, ym(vtrap), c=A, w=2.5, dash='10 8') + tx(X0 + 250, ym(vtrap) + 38, 'New end-expiratory volume', 22, A)
    bx = X1 - 20
    out += ln(bx, ym(0) - 4, bx, ym(vtrap) + 4, c=A, w=3, arrow='arra') + ln(bx, ym(vtrap) + 4, bx, ym(0) - 4, c=A, w=3, arrow='arra')
    out += tx(bx - 14, (ym(0) + ym(vtrap)) / 2 + 10, 'V trapped', 24, A, anchor='end')
    out += tx(X0 - 20, Y0 + 44, 'Climbs until each breath out equals each breath in', 24, S, font='body')
    out += tx(X0 - 20, Y0 + 86, 'V trapped = VT · e^(−Te/τ) ÷ (1 − e^(−Te/τ))', 28, P, font='body')
    out += tx(X0 - 20, Y0 + 124, 'auto-PEEP = V trapped ÷ C', 28, A, font='body', weight=500)
    return out


# ------------------------------------------------------------------ BP in asthma -----------------------------------------
def _box(x, y, w, h, lines, hot=False):
    out = rc(x, y, w, h, fill='color-mix(in oklab, var(--text-accent) 10%, var(--surface-page))' if hot else 'none', c=A if hot else P, sw=2, r=6)
    n = len(lines); y0 = y + h / 2 - (n - 1) * 17 + 9
    for i, l in enumerate(lines):
        out += tx(x + w / 2, y0 + i * 34, l, 27, P, anchor='middle', font='body')
    return out


def fig_bp_asthma():
    out = ''
    W, H, G = 340, 104, 64
    xs = [60 + i * (W + G) for i in range(4)]
    rows = [
        ('Trapped gas', [['Auto-PEEP', 'chest stays full'], ['Pleural and right', 'atrial pressure up'], ['Venous return', 'falls'], ['Preload and BP', 'fall']]),
        ('Big lung volume', [['Lung near TLC'], ['Alveolar vessels', 'squeezed: PVR up'], ['RV dilates, septum', 'pushes into the LV'], ['LV fills less,', 'output falls']]),
        ('Before the tube', [['Huge negative', 'pleural swings'], ['LV afterload up,', 'RV fills more'], ['Pulsus paradoxus', '> 10–20 mmHg'], None]),
    ]
    for r, (lab, boxes) in enumerate(rows):
        y = 44 + r * (H + 72)
        out += tx(60, y - 12, lab, 22, A)
        for i, b in enumerate(boxes):
            if not b:
                continue
            out += _box(xs[i], y, W, H, b, hot=(i == 3 or (r == 2 and i == 2)))
            if i < 3 and boxes[i + 1]:
                out += ln(xs[i] + W + 6, y + H / 2, xs[i + 1] - 8, y + H / 2, c=P, w=3, arrow='arr')
    y = 44 + 3 * (H + 72) - 30
    out += rc(60, y, 4 * W + 3 * G, 150, fill='none', c=A, sw=3, r=6)
    out += tx(90, y + 48, 'After the tube', 22, A)
    out += tx(90, y + 92, 'Sedation removes the sympathetic drive, positive pressure adds to the trapping, the child is dry: the BP falls in minutes.', 26, P, font='body')
    out += tx(90, y + 130, 'Disconnect and let the chest fall · fluid bolus · slower rate, smaller VT · then a vasopressor', 26, A, font='body', weight=500)
    return out


# ------------------------------------------------------------------ Tasker's bronchiolitis curves ------------------------
def _pc(C, R, pinf, f, ti, secs=4.0, dt=0.002):
    """Volume above FRC (mL) for square-wave pressure control with passive expiration, run to steady state."""
    tau = R * C; T = 60 / f; v = 0.0; tr = []
    for cyc in range(40):
        t = 0.0
        while t < T - 1e-9:
            v += ((C * pinf - v) / tau if t < ti else -v / tau) * dt
            if cyc >= 40 - math.ceil(secs / T):
                tr.append(v)
            t += dt
    return tr[-int(secs / dt):]


TASKER = [  # label, Crs mL/cmH2O, Rrs cmH2O/mL/s, Pinf, f, ti, PaCO2 (Tasker's estimate), source
    ('Control', 5.0, 0.06, 16, 30, 0.21, '35', 'Hammer 1997 · 26 controls'),
    ('Bronchiolitis', 2.8, 0.08, 16, 30, 0.50, '46', 'Derish 1998 · 25 cases'),
    ('Obstructive', 2.85, 0.37, 20, 30, 0.50, '109', 'Hammer 1997 · 27 cases'),
    ('Restrictive', 1.9, 0.10, 20, 30, 0.50, None, 'Hammer 1997 · ARDS pattern'),
]


def tasker_vt(C, R, pinf, f, ti):
    tr = _pc(C, R, pinf, f, ti)
    return max(tr) - min(tr), min(tr)


def fig_tasker():
    out = ''
    PW, PH = 700, 250
    pos = [(170, 40), (960, 40), (170, 400), (960, 400)]
    for k, (lab, C, R, pinf, f, ti, co2, src) in enumerate(TASKER):
        x0, y0 = pos[k]
        X0, X1, Yb, Yt = x0, x0 + PW, y0 + PH, y0 + 20
        ym = lambda v: Yb - (Yb - Yt) * v / 70
        xm = lambda t: X0 + (X1 - X0) * t / 4
        out += ln(X0, Yb, X1, Yb) + ln(X0, Yt, X0, Yb)
        for v in (0, 35, 70):
            out += tx(X0 - 12, ym(v) + 7, str(v), 18, anchor='end')
        tr = _pc(C, R, pinf, f, ti)
        out += poly([(xm(i * 0.002), ym(v)) for i, v in enumerate(tr) if i % 10 == 0], c=P if k < 2 else A, w=3.5)
        vt, eev = max(tr) - min(tr), min(tr)
        if k == 2:   # Tasker's graph B: rate 20, ti 1.0
            tr2 = _pc(C, R, pinf, 20, 1.0)
            out += poly([(xm(i * 0.002), ym(v)) for i, v in enumerate(tr2) if i % 10 == 0], c=S, w=3, dash='10 8')
        tau = R * C
        out += tx(X0, y0 + 2, f'{lab}', 26, A if k >= 2 else P)
        out += tx(X1, y0 + 2, f'C {C} · R {R} · τ {tau:.2f} s', 22, S, anchor='end', font='body')
        note = f'P {pinf} · rate {f} · Ti {ti} s → VT {vt / 5:.0f} mL/kg' + (f' · PaCO₂ ≈ {co2}' if co2 else '')
        out += tx(X0 + 10, Yb + 34, note, 20, P)
        if k == 2:
            out += tx(X0 + 10, Yb + 64, f'End-expiration {eev:.0f} mL above FRC · dashed: rate 20, Ti 1.0 s → PaCO₂ ≈ 93', 20, A)
    out += f'<text transform="translate(80,380) rotate(-90)" font-size="20" fill="var(--text-secondary)" text-anchor="middle">Lung volume above FRC, mL · 5 kg infant</text>'
    return out


if __name__ == '__main__':
    for lab, C, R, pinf, f, ti, co2, src in TASKER:
        vt, eev = tasker_vt(C, R, pinf, f, ti)
        print(f'{lab:14s} tau {R * C:.2f}  VT {vt:5.1f} mL ({vt / 5:.1f} mL/kg)  end-exp above FRC {eev:4.1f} mL')
    vt, eev = tasker_vt(2.85, 0.37, 20, 20, 1.0); print('Obstructive B', f'VT {vt:.1f} eev {eev:.1f}')
    vt, eev = tasker_vt(2.8, 0.08, 20, 36, 0.5); print('Bronch B', f'VT {vt:.1f} ({vt/5:.1f}/kg) eev {eev:.1f}')
