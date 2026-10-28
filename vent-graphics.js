/* VentCourse waveform engine: <vent-trace scenario="..." lanes="pfv|p|f|v|pf|pv|fv" theme="night|paper"> */
(function () {
  if (window.VentGraphics) return;
  const BASE = { mode: 'VC', flow: 'square', C: 50, R: 10, rr: 15, ti: 1, peep: 5, vt: 500, pinsp: 15, ps: 10, pause: 0, cycle: 25, rise: 0.08, ev: 0.25, si: 0, leak: 0, sec: 0, window: 8 };
  const reg = (rr, W, t0 = 0.3) => { const T = 60 / rr, a = []; for (let t = t0; t < W - 0.05; t += T) a.push(+t.toFixed(3)); return a; };
  const eff = (ts, amp, dur, lead = 0.08) => ts.map(t => ({ t: t - lead, amp, dur }));
  const S = {
    'normal-vc': { pause: 0.25, ti: 1.0, rr: 15, marks: [{ lane: 'p', at: 'pip', text: 'PIP' }, { lane: 'p', at: 'plat', text: 'Plateau' }] },
    'normal-vc-nopause': { ti: 1.0, rr: 15 },
    'normal-pc': { mode: 'PC', pinsp: 12, ti: 1.0, rr: 15 },
    'vc-anatomy': { pause: 0.4, ti: 1.2, rr: 12, window: 5, marks: [{ lane: 'p', at: 'step', text: 'R × V̇' }, { lane: 'p', at: 'pip', text: 'PIP' }, { lane: 'p', at: 'plat', text: 'Plateau' }, { lane: 'p', at: 'peep', text: 'PEEP' }] },
    'pc-anatomy': { mode: 'PC', pinsp: 14, ti: 1.0, rr: 12, window: 5 },
    'time-trigger': { rr: 15 },
    'patient-trigger': { rr: 15, efforts: eff(reg(15, 8), 4, 0.7), marks: [{ lane: 'p', at: 'dip', text: 'Trigger dip' }] },
    'flow-square': { flow: 'square', rr: 15, window: 4 },
    'flow-ramp': { flow: 'decel', rr: 15, window: 4 },
    'flow-sine': { flow: 'sine', rr: 15, window: 4 },
    'flow-exp': { mode: 'PC', pinsp: 12, rr: 15, window: 4 },
    'ps-spont': { mode: 'PS', ps: 10, rr: 15, efforts: eff(reg(15, 8), 6, 1.1) },
    'pc-ti-long': { mode: 'PC', C: 30, R: 8, pinsp: 14, ti: 1.6, rr: 15, marks: [{ lane: 'f', at: 'zero', text: 'Flow hits zero' }] },
    'pc-ti-short': { mode: 'PC', C: 60, R: 22, pinsp: 12, ti: 0.7, rr: 15, marks: [{ lane: 'f', at: 'endinsp', text: 'Still flowing' }] },
    'pc-ti-right': { mode: 'PC', C: 50, R: 10, pinsp: 12, ti: 1.0, rr: 15 },
    'vc-highR': { R: 30, C: 50, pause: 0.25, rr: 15, scale: { p: 50 }, marks: [{ lane: 'p', at: 'pip', text: 'PIP' }, { lane: 'p', at: 'plat', text: 'Plateau' }] },
    'vc-lowC': { R: 10, C: 22, pause: 0.25, rr: 15, scale: { p: 50 }, marks: [{ lane: 'p', at: 'pip', text: 'PIP' }, { lane: 'p', at: 'plat', text: 'Plateau' }] },
    'vc-ref': { R: 10, C: 50, pause: 0.25, rr: 15, scale: { p: 50 }, marks: [{ lane: 'p', at: 'pip', text: 'PIP' }, { lane: 'p', at: 'plat', text: 'Plateau' }] },
    'pc-highR': { mode: 'PC', R: 30, C: 50, pinsp: 15, rr: 15, scale: { f: 90, v: 700 } },
    'pc-lowC': { mode: 'PC', R: 10, C: 20, pinsp: 15, rr: 15, scale: { f: 90, v: 700 } },
    'pc-ref': { mode: 'PC', R: 10, C: 50, pinsp: 15, rr: 15, scale: { f: 90, v: 700 } },
    'si-linear': { si: 0, ti: 1.0, rr: 15, C: 40, window: 4, scale: { p: 30 } },
    'si-over': { si: 1.3, ti: 1.0, rr: 15, C: 40, window: 4, scale: { p: 30 } },
    'si-recruit': { si: -0.65, ti: 1.0, rr: 15, C: 40, window: 4, scale: { p: 30 } },
    'exp-normal': { R: 10, C: 50, rr: 15, scale: { f: 90 } },
    'exp-obstruct': { R: 32, C: 60, rr: 12, scale: { f: 90 }, marks: [{ lane: 'f', at: 'pef', text: 'Low peak' }] },
    'exp-stiff': { R: 8, C: 18, vt: 400, rr: 15, scale: { f: 90 } },
    'exp-bd': { R: 16, C: 60, rr: 12, scale: { f: 90 } },
    'autopeep': { R: 30, C: 50, rr: 24, ti: 0.9, marks: [{ lane: 'f', at: 'endexp', text: 'Not back to zero' }] },
    'autopeep-fixed': { R: 30, C: 50, rr: 12, ti: 0.8 },
    'efl': { R: 10, C: 70, rr: 14, efl: { k: 0.55, m: 6 }, marks: [{ lane: 'f', at: 'pef', text: 'Spike, then slow tail' }] },
    'pv-normal': { R: 10, C: 50, rr: 15, ti: 1.0, flow: 'square' },
    'pv-over': { R: 10, C: 45, si: 1.5, vt: 550, rr: 15, ti: 1.0, scale: { p: 45, v: 650 } },
    'pv-lowC': { R: 10, C: 22, rr: 15, ti: 1.0, scale: { p: 45, v: 650 } },
    'pv-ref': { R: 10, C: 50, rr: 15, ti: 1.0, scale: { p: 45, v: 650 } },
    'pv-highR': { R: 28, C: 50, rr: 15, ti: 1.0, scale: { p: 45, v: 650 } },
    'fv-normal': { R: 10, C: 50, rr: 15 },
    'fv-obstruct': { R: 30, C: 60, rr: 16, efl: { k: 0.75, m: 3 } },
    'fv-leak': { rr: 15, leak: 0.35 },
    'fv-secretions': { R: 12, C: 50, rr: 15, sec: 1 },
    'leak': { rr: 15, leak: 0.35, marks: [{ lane: 'v', at: 'endexp', text: 'Never returns' }] },
    'leak-infant': { mode: 'PC', C: 3, R: 60, pinsp: 16, peep: 5, ti: 0.5, rr: 35, window: 4, leak: 0.05, marks: [{ lane: 'v', at: 'endexp', text: 'Lost to the leak' }] },
    'secretions': { R: 12, C: 50, rr: 15, sec: 1, marks: [{ lane: 'f', at: 'pef', text: 'Sawtooth' }] },
    'ineffective': { mode: 'PS', ps: 14, R: 22, C: 70, rr: 15, window: 9, breaths: [0.3, 3.3, 6.3], efforts: [{ t: 0.22, amp: 6, dur: 1 }, { t: 3.22, amp: 6, dur: 1 }, { t: 6.22, amp: 6, dur: 1 }, { t: 2.0, amp: 4, dur: 0.6 }, { t: 5.0, amp: 4, dur: 0.6 }, { t: 8.0, amp: 4, dur: 0.6 }], marks: [{ lane: 'f', at: 2.3, text: 'Effort, no breath' }] },
    'autotrigger': { mode: 'PC', pinsp: 12, ti: 0.8, rr: 15, window: 8, breaths: [0.3, 2.1, 3.3, 4.2, 5.9, 6.8], marks: [{ lane: 'f', at: 3.25, text: 'No effort' }] },
    'double': { ti: 0.8, vt: 420, window: 8, breaths: [0.3, 1.12, 4.3, 5.12], efforts: [{ t: 0.22, amp: 9, dur: 1.5 }, { t: 4.22, amp: 9, dur: 1.5 }], marks: [{ lane: 'p', at: 1.2, text: 'Second breath, no exhalation' }] },
    'starvation': { ti: 1.2, vt: 450, rr: 15, efforts: eff(reg(15, 8), 11, 1.0), marks: [{ lane: 'p', at: 0.85, text: 'Scooped' }] },
    'ps-low': { mode: 'PS', ps: 4, R: 10, C: 40, rr: 34, window: 6, efforts: eff(reg(34, 6), 11, 0.65), marks: [{ lane: 'v', at: 'endinsp', text: 'Small VT, fast RR' }] },
    'ps-high': { mode: 'PS', ps: 20, R: 10, C: 50, rr: 15, window: 9, breaths: [0.3, 4.8], efforts: [{ t: 0.22, amp: 3, dur: 0.8 }, { t: 4.72, amp: 3, dur: 0.8 }, { t: 2.5, amp: 3, dur: 0.6 }, { t: 3.7, amp: 3, dur: 0.6 }, { t: 7.0, amp: 3, dur: 0.6 }, { t: 8.2, amp: 3, dur: 0.6 }], marks: [{ lane: 'f', at: 2.8, text: 'Efforts missed' }] },
    'starvation-fixed': { mode: 'PC', pinsp: 14, ti: 1.0, rr: 15, efforts: eff(reg(15, 8), 11, 1.0) },
    'premature': { mode: 'PS', ps: 8, cycle: 55, R: 8, C: 40, rr: 15, efforts: eff(reg(15, 8), 8, 1.5), marks: [{ lane: 'f', at: 'afterc', text: 'Still pulling' }] },
    'delayed': { mode: 'PS', ps: 12, cycle: 5, R: 20, C: 70, rr: 15, efforts: reg(15, 8).flatMap(t => [{ t: t - 0.08, amp: 6, dur: 0.8 }, { t: t + 0.85, amp: -9, dur: 0.6 }]), marks: [{ lane: 'p', at: 'spike', text: 'Pressure spike' }] },
    'infant-normal': { mode: 'PC', C: 3.3, R: 40, pinsp: 15, peep: 6, ti: 0.5, rr: 30, window: 4 },
    'bronchiolitis-obs': { mode: 'PC', C: 2.85, R: 370, pinsp: 20, peep: 5, ti: 0.5, rr: 30, window: 6, marks: [{ lane: 'f', at: 'endexp', text: 'Never empties' }] },
    'bronchiolitis-fixed': { mode: 'PC', C: 2.85, R: 370, pinsp: 20, peep: 5, ti: 0.8, rr: 16, window: 8 },
    // Disease-specific talk: ARDS (62 kg, C 20 → 28 once recruited) and asthma (70 kg, R 30)
    'ards-admit': { C: 20, R: 12, vt: 550, rr: 14, ti: 1.0, pause: 0.3, peep: 5, window: 8, scale: { p: 48, v: 650 }, marks: [{ lane: 'p', at: 'plat', text: 'Plateau 32' }, { lane: 'v', at: 'endinsp', text: '550 mL · 9 mL/kg' }] },
    'ards-protective': { C: 28, R: 12, vt: 370, rr: 24, ti: 0.8, pause: 0.3, peep: 12, window: 6, scale: { p: 48, v: 650 }, marks: [{ lane: 'p', at: 'plat', text: 'Plateau 25' }, { lane: 'p', at: 'peep', text: 'PEEP 12' }] },
    'ards-pc': { mode: 'PC', C: 28, R: 12, pinsp: 13, peep: 12, ti: 0.9, rr: 24, window: 6, scale: { p: 48 }, marks: [{ lane: 'f', at: 'zero', text: 'Flow reaches zero' }] },
    'ards-stiff-vs-normal': { C: 20, R: 12, vt: 400, rr: 15, ti: 1.0, pause: 0.3, peep: 5, window: 8, scale: { p: 48 }, marks: [{ lane: 'p', at: 'plat', text: 'High plateau' }, { lane: 'p', at: 'pip', text: 'Small gap' }] },
    'asthma-admit': { C: 50, R: 30, vt: 500, rr: 22, ti: 1.0, pause: 0.3, peep: 5, window: 8, scale: { p: 50, f: 90 }, marks: [{ lane: 'p', at: 'pip', text: 'PIP 44' }, { lane: 'p', at: 'plat', text: 'Plateau 22' }, { lane: 'f', at: 'endexp', text: 'Not back to zero' }] },
    'asthma-fixed': { C: 50, R: 30, vt: 500, rr: 10, ti: 1.0, pause: 0.3, peep: 0, window: 12, scale: { p: 50, f: 90 }, marks: [{ lane: 'f', at: 'endexp', text: 'Empty before the next breath' }] },
    'ri-drop': { C: 30, R: 12, vt: 400, rr: 15, ti: 1.0, pause: 0.25, peep: 15, window: 12, breaths: [0.3, 4.3, 8.3], peepDrop: { t: 5.3, to: 5, add: 0.55 }, scale: { p: 40, f: 90, v: 1000 }, marks: [{ lane: 'p', at: 2.0, text: 'PEEP 15' }, { lane: 'p', at: 7.0, text: 'PEEP 5 · one breath' }, { lane: 'v', at: 7.6, text: 'Exhaled 950 mL' }] },
    'nmd-weak': { mode: 'PS', ps: 6, C: 60, R: 8, rr: 30, window: 6, efforts: eff(reg(30, 6), 2.5, 0.6), marks: [{ lane: 'v', at: 'endinsp', text: 'Small breath, weak pull' }, { lane: 'p', at: 'dip', text: 'Trigger dip' }] },
    'nmd-supported': { mode: 'PS', ps: 14, C: 60, R: 8, rr: 16, window: 6, efforts: eff(reg(16, 6), 2.5, 0.8), marks: [{ lane: 'v', at: 'endinsp', text: 'Full breath from a weak pull' }] },
    'nmd-vc': { C: 60, R: 8, vt: 480, rr: 14, ti: 1.0, pause: 0.25, peep: 5, window: 8, scale: { p: 30 }, marks: [{ lane: 'p', at: 'plat', text: 'Plateau 13' }] },
    // CPV-START (CP interactions ventilator screens, generated)
    'cpv-m1': { mode: "PS", ps: 5, peep: 5, C: 8, R: 25, rr: 40, window: 6, efforts: eff(reg(40, 6), 5, 0.6) },
    'cpv-m2': { mode: "PC", pinsp: 15, peep: 5, C: 9.5, R: 25, rr: 25, ti: 0.8, window: 6 },
    'cpv-m3': { mode: "PC", pinsp: 13, peep: 5, C: 7.7, R: 25, rr: 20, ti: 0.8, window: 6 },
    'cpv-m4': { mode: "PC", pinsp: 13, peep: 6, C: 8, R: 25, rr: 30, ti: 0.7, window: 6 },
    'cpv-l0': { mode: "VC", vt: 110, peep: 14, C: 6.9, R: 30, rr: 24, ti: 0.8, pause: 0.15, window: 6 },
    'cpv-l1': { mode: "VC", vt: 110, peep: 18, C: 6.1, R: 30, rr: 24, ti: 0.8, si: 1.5, window: 6 },
    'cpv-l2': { mode: "VC", vt: 110, peep: 12, C: 6.9, R: 30, rr: 24, ti: 0.8, si: 0.2, window: 6 },
    'cpv-l3': { mode: "VC", vt: 110, peep: 12, C: 6.9, R: 55, rr: 24, ti: 0.8, window: 6 },
    'cpv-l4': { mode: "VC", vt: 110, peep: 12, C: 7.9, R: 55, rr: 28, ti: 0.8, window: 6 },
    'cpv-c1': { mode: "PC", pinsp: 15, peep: 7, C: 3, R: 45, rr: 30, ti: 0.6, window: 5 },
    'cpv-c2': { mode: "PC", pinsp: 14, peep: 4, C: 4.5, R: 40, rr: 25, ti: 0.6, window: 5 },
    'cpv-c3': { mode: "VC", vt: 25, peep: 10, C: 2.5, R: 50, rr: 30, ti: 0.6, window: 5 },
    'cpv-c4': { mode: "VC", vt: 45, peep: 8, C: 4, R: 40, rr: 25, ti: 0.8, window: 5 },
    'cpv-c5': { mode: "VC", vt: 110, peep: 8, C: 12, R: 25, rr: 22, ti: 0.9, window: 6 },
    'cpv-b0': { mode: "PS", ps: 6, peep: 8, C: 10, R: 25, rr: 50, window: 5, efforts: eff(reg(50, 5), 6, 0.5) },
    'cpv-b1': { mode: "PS", ps: 6, peep: 8, C: 6, R: 25, rr: 60, window: 5, efforts: eff(reg(60, 5), 10, 0.45) },
    'cpv-b2': { mode: "PC", pinsp: 12, peep: 8, C: 10, R: 25, rr: 25, ti: 0.7, window: 6 },
    'cpv-b3': { mode: "PS", ps: 0.5, peep: 0.5, C: 8, R: 25, rr: 50, window: 5, efforts: eff(reg(50, 5), 9, 0.5) },
    'cpv-su1': { mode: "VC", vt: 170, peep: 5, C: 13, R: 20, rr: 24, ti: 0.8, pause: 0.15, window: 6 },
    'cpv-su2': { mode: "VC", vt: 170, peep: 5, C: 13, R: 20, rr: 16, ti: 0.8, pause: 0.15, window: 8 },
    'cpv-su3': { mode: "VC", vt: 170, peep: 8, C: 13, R: 20, rr: 26, ti: 0.8, pause: 0.15, window: 6 },
    // CPV-END
    'asthma-pc': { mode: 'PC', C: 50, R: 30, pinsp: 20, peep: 5, ti: 1.0, rr: 22, window: 8, scale: { p: 50, f: 90 }, marks: [{ lane: 'v', at: 'endinsp', text: 'VT shrinks as gas traps' }, { lane: 'f', at: 'endexp', text: 'Not back to zero' }] }
  };

  function simulate(input) {
    const sc = typeof input === 'string' ? S[input] || S['normal-vc'] : input;
    const p = { ...BASE, ...sc }; if (!p.breaths) { const T0 = 60 / p.rr; p.window = Math.max(1, Math.round(p.window / T0)) * T0; } const W = p.window, dt = p.C < 10 ? 0.001 : 0.002, N = Math.round(W / dt);
    const C = p.C / 1000, R = p.R, br = p.breaths || reg(p.rr, W), efs = p.efforts || [];
    const Vref = p.vt / 1000 || 0.5;
    const pel = V => (V / C) * (1 + p.si * (V / Vref - 0.5));
    const pmAt = t => { let s = 0; for (const e of efs) if (t >= e.t && t < e.t + e.dur) s += e.amp * Math.sin(Math.PI * (t - e.t) / e.dur); return s; };
    const P = new Float32Array(N), F = new Float32Array(N), Vv = new Float32Array(N);
    let V = 0, vm = 0, tc = -9, insp = false, tb = 0, pk = 0, vStart = 0, bi = 0, ev = { cyc: [], start: [] };
    for (let pass = 0; pass < 4; pass++) {
      bi = 0; const last = pass === 3; if (last) ev = { cyc: [], start: [] };
      for (let i = 0; i < N; i++) {
        const t = i * dt, pm = pmAt(t);
        const peepNow = (p.peepDrop && t >= p.peepDrop.t) ? p.peepDrop.to : p.peep;
        if (p.peepDrop && i === Math.round(p.peepDrop.t / dt)) V += p.peepDrop.add || 0;
        if (bi < br.length && t >= br[bi]) { if (insp || t - tc > 0.15) vm = 0; insp = true; tb = t; pk = 0; bi++; if (last) ev.start.push(t); }
        let f = 0, paw = peepNow;
        if (insp) {
          const x = t - tb;
          if (p.mode === 'VC') {
            const tf = p.ti - p.pause, vt = p.vt / 1000 / (1 - 0.03 / tf);
            if (x < tf) {
              const u = x / tf;
              const on = Math.min(1, x / 0.06);
              f = on * (p.flow === 'decel' ? vt / (0.75 * tf) * (1 - 0.5 * u) : p.flow === 'sine' ? vt * Math.PI / (2 * tf) * Math.sin(Math.PI * u) : vt / tf);
              paw = peepNow + R * f + pel(V) - pm;
            } else if (x < p.ti) { f = 0; paw = peepNow + pel(V) - pm * 0.6; }
            else { insp = false; vStart = V; tc = t; if (last) ev.cyc.push(t); }
          } else {
            const lvl = p.mode === 'PS' ? p.ps : p.pinsp, set = peepNow + lvl * Math.min(1, x / p.rise);
            f = (set - peepNow - pel(V) + pm) / R; pk = Math.max(pk, f);
            paw = set + (pm < 0 ? -pm * 0.8 : 0);
            const cyc = p.mode === 'PS' ? (x > 0.12 && f < p.cycle / 100 * pk) || x > 2.5 : x >= p.ti;
            if (cyc) { insp = false; vStart = V; tc = t; if (last) ev.cyc.push(t); }
          }
        }
        if (!insp) {
          let Rt = R * (1 + p.ev);
          if (p.efl && V < p.efl.k * vStart) Rt *= p.efl.m;
          f = (pm - pel(V)) / Rt; if (V <= 0 && f < 0) f = 0;
          paw = peepNow + p.ev * R * Math.max(0, -f) - Math.max(0, pm) * 0.3;
        }
        V = Math.max(0, V + f * dt);
        let fm = f * 60 + (insp ? p.leak * Math.max(0, paw) : 0);
        if (p.sec && !insp) { const tri = Math.abs(((t * 14) % 1) - 0.5) * 4 - 1; fm += p.sec * tri * (Math.abs(f * 60) * 0.18 + 1.5); paw += p.sec * tri * 0.3; }
        vm += fm / 60 * dt * 1000;
        if (last) { P[i] = paw; F[i] = fm; Vv[i] = vm; }
      }
    }
    const mx = a => a.reduce((m, x) => x > m ? x : m, -1e9), mn = a => a.reduce((m, x) => x < m ? x : m, 1e9);
    const st = ev.start[0] ?? 0, cy = ev.cyc.find(c => c > st) ?? st + p.ti, nxt = ev.start[1] ?? W;
    const ix = t => Math.max(0, Math.min(N - 1, Math.round(t / dt)));
    let pipI = ix(st); for (let i = ix(st); i < ix(cy); i++) if (P[i] > P[pipI]) pipI = i;
    let dipI = ix(st - 0.1); for (let i = ix(st - 0.15); i < ix(st + 0.05); i++) if (P[i] < P[dipI]) dipI = i;
    let pefI = ix(cy); for (let i = ix(cy); i < ix(nxt); i++) if (F[i] < F[pefI]) pefI = i;
    let zI = ix(cy - 0.02); for (let i = ix(st + 0.15); i < ix(cy); i++) if (F[i] < 1) { zI = i; break; }
    let spI = pipI;
    const at = { pip: pipI, plat: ix(cy - 0.03), step: ix(st + 0.03), peep: ix(nxt - 0.15), dip: dipI, pef: pefI, endexp: ix(nxt - 0.02), endinsp: ix(cy - 0.02), zero: zI, afterc: ix(cy + 0.25), spike: spI };
    const marks = (p.marks || []).map(m => ({ ...m, i: typeof m.at === 'number' ? ix(m.at) : at[m.at] ?? 0 }));
    const sc2 = p.scale || {};
    const pmax = sc2.p || Math.max(10, mx(P) * 1.15), fabs = sc2.f || Math.max(1, Math.max(mx(F), -mn(F)) * 1.15);
    const vmax = sc2.v || Math.max(1, mx(Vv) * 1.15), vmin = Math.min(0, mn(Vv) * 1.15);
    return { p: P, f: F, v: Vv, N, dt, W, marks, scale: { p: [Math.min(0, mn(P) - 1), pmax], f: [-fabs, fabs], v: [vmin, vmax] },
      stats: { pip: P[pipI], plat: P[ix(cy - 0.03)], peep: p.peep, vt: mx(Vv), pef: -F[pefI], infant: p.C < 10 }, params: p };
  }

  const PAL = {
    night: { p: '#EBC77A', f: '#E08F71', v: '#93AEB5', grid: 'rgba(243,237,227,.14)', text: 'rgba(243,237,227,.72)', mark: '#F3EDE3' },
    paper: { p: '#9C7020', f: '#B04428', v: '#3F6670', grid: 'rgba(27,26,23,.14)', text: '#5E554B', mark: '#1B1A17' }
  };
  const LBL = { p: 'PAW  cmH₂O', f: 'FLOW  L/min', v: 'VOLUME  mL' };

  class VentTrace extends HTMLElement {
    static get observedAttributes() { return ['scenario', 'lanes', 'theme', 'speed', 'static', 'labels', 'font', 'lw', 'marks']; }
    connectedCallback() {
      if (!this.cv) {
        this.style.display = this.style.display || 'block'; this.style.position = this.style.position || 'relative';
        this.style.width = this.style.width || '100%'; this.style.height = this.style.height || '100%'; this.style.minHeight = this.style.minHeight || '40px';
        this.cv = document.createElement('canvas'); this.cv.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;display:block;';
        this.appendChild(this.cv);
      }
      this.build();
      this.ro = new ResizeObserver(() => this.size()); this.ro.observe(this); this.size();
      const loop = () => { this.draw(); this.raf = requestAnimationFrame(loop); }; this.raf = requestAnimationFrame(loop);
    }
    disconnectedCallback() { cancelAnimationFrame(this.raf); this.ro && this.ro.disconnect(); }
    attributeChangedCallback(n) { if (n === 'scenario' && this.cv) this.build(); }
    build() { this.sim = simulate(this.getAttribute('scenario') || 'normal-vc'); this.t0 = performance.now(); }
    size() { const d = Math.min(2, window.devicePixelRatio || 1); this.drawn = false; this.cv.width = Math.max(1, Math.round(this.clientWidth * d)); this.cv.height = Math.max(1, Math.round(this.clientHeight * d)); this.k = d; }
    draw() {
      if (!this.sim || !this.cv.width) return;
      if (this.sec === undefined) this.sec = this.closest('section[data-deck-slide], section[data-label]');
      const idle = this.sec && !this.sec.hasAttribute('data-deck-active');
      if (idle && this.drawn) return;
      if (!idle) { if (this.getClientRects().length === 0) return; const r = this.getBoundingClientRect(); if (r.width < 2 || r.bottom < 0 || r.top > innerHeight) return; }
      this.drawn = true; this.idle = idle;
      const ctx = this.cv.getContext('2d'), w = this.cv.width, H = this.cv.height, k = this.k, s = this.sim;
      const pal = PAL[this.getAttribute('theme') || 'night'], fs = +(this.getAttribute('font') || 12) * k, lw = +(this.getAttribute('lw') || 2) * k;
      const lanes = this.getAttribute('lanes') || 'pfv', isStatic = this.hasAttribute('static') || this.idle, showMarks = this.getAttribute('marks') !== 'off';
      const pos = isStatic ? s.W : ((performance.now() - this.t0) / 1000 * +(this.getAttribute('speed') || 1)) % s.W;
      ctx.clearRect(0, 0, w, H); ctx.lineJoin = 'round'; ctx.lineCap = 'round';
      ctx.font = `500 ${fs}px "IBM Plex Mono", monospace`;
      if (lanes === 'pv' || lanes === 'fv') return this.loop(ctx, w, H, k, s, pal, fs, lw, lanes, pos);
      const ks = lanes.split(''), lh = H / ks.length, top = this.getAttribute('labels') === 'off' ? 4 * k : fs * 1.6;
      ks.forEach((key, li) => {
        const y0 = li * lh + top, h = lh - top - 6 * k, [lo, hi] = s.scale[key], arr = s[key];
        const yOf = v => y0 + h - (Math.max(lo, Math.min(hi, v)) - lo) / (hi - lo) * h;
        ctx.strokeStyle = pal.grid; ctx.lineWidth = 1 * k; ctx.beginPath(); ctx.moveTo(0, yOf(0)); ctx.lineTo(w, yOf(0)); ctx.stroke();
        if (this.getAttribute('labels') !== 'off') { ctx.fillStyle = pal.text; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic'; ctx.fillText(LBL[key], 0, li * lh + fs * 1.1); }
        ctx.strokeStyle = pal[key]; ctx.lineWidth = lw; ctx.beginPath(); let pen = false;
        const step = Math.max(1, Math.round(k));
        for (let x = 0; x <= w; x += step) {
          const tt = x / w * s.W; let gap = tt - pos; if (gap < 0) gap += s.W;
          if (!isStatic && gap < 0.3) { pen = false; continue; }
          const y = yOf(arr[Math.min(s.N - 1, Math.floor(tt / s.dt))]);
          if (!pen) { ctx.moveTo(x, y); pen = true; } else ctx.lineTo(x, y);
        }
        ctx.stroke();
        if (showMarks) s.marks.filter(m => m.lane === key).forEach(m => {
          const x = m.i * s.dt / s.W * w, y = yOf(arr[m.i]);
          ctx.fillStyle = pal.mark; ctx.beginPath(); ctx.arc(x, y, 4 * k, 0, 7); ctx.fill();
          const txt = m.text.toUpperCase(), tw = ctx.measureText(txt).width, right = x > w * 0.6;
          let lx0 = right ? x - tw : x; lx0 = Math.max(0, Math.min(w - tw, lx0));
          const laneTop = li * lh, laneBot = (li + 1) * lh, lblW = ctx.measureText(LBL[key]).width + 16 * k;
          let mn = Infinity, mx = -Infinity;
          for (let xx = Math.max(0, lx0 - 8 * k); xx <= Math.min(w, lx0 + tw + 8 * k); xx += step) { const yy = yOf(arr[Math.min(s.N - 1, Math.floor(xx / w * s.W / s.dt))]); mn = Math.min(mn, yy); mx = Math.max(mx, yy); }
          const minTop = laneTop + (lx0 < lblW ? fs * 1.5 : 2 * k);
          const aboveB = Math.min(mn, y) - 12 * k, belowB = Math.max(mx, y) + fs + 12 * k;
          const okA = aboveB - fs >= minTop, okB = belowB <= laneBot - 2 * k;
          let tb = (okA && (!okB || y - aboveB <= belowB - y)) ? aboveB : okB ? belowB : Math.max(minTop + fs, aboveB);
          const edge = tb < y ? tb + 2 * k : tb - fs - 2 * k;
          ctx.strokeStyle = pal.mark; ctx.globalAlpha = .55; ctx.lineWidth = 1.5 * k; ctx.beginPath(); ctx.moveTo(x, y + (edge < y ? -6 : 6) * k); ctx.lineTo(x, edge); ctx.stroke(); ctx.globalAlpha = 1;
          ctx.textAlign = 'left'; ctx.textBaseline = 'bottom';
          ctx.fillText(txt, right ? Math.min(lx0, x - tw - 6 * k) : Math.max(lx0, x + 6 * k), tb);
        });
      });
    }
    loop(ctx, w, H, k, s, pal, fs, lw, lanes, pos) {
      const pad = fs * 2.2, X = lanes === 'pv' ? s.p : s.v, Y = lanes === 'pv' ? s.v : s.f;
      const [x0, x1] = lanes === 'pv' ? [0, s.scale.p[1]] : [Math.min(0, s.scale.v[0]), s.scale.v[1]];
      const [y0, y1] = lanes === 'pv' ? [Math.min(0, s.scale.v[0]), s.scale.v[1]] : s.scale.f;
      const px = v => pad + (v - x0) / (x1 - x0) * (w - pad * 1.4), py = v => H - pad - (v - y0) / (y1 - y0) * (H - pad * 1.6);
      ctx.strokeStyle = pal.grid; ctx.lineWidth = 1 * k; ctx.beginPath();
      ctx.moveTo(px(x0), py(0)); ctx.lineTo(w, py(0)); ctx.moveTo(px(Math.max(0, x0)), py(y0)); ctx.lineTo(px(Math.max(0, x0)), 0); ctx.stroke();
      ctx.fillStyle = pal.text; ctx.textAlign = 'right'; ctx.textBaseline = 'alphabetic';
      ctx.fillText(lanes === 'pv' ? 'PAW  cmH₂O' : 'VOLUME  mL', w, H - fs * 0.4);
      ctx.textAlign = 'left'; ctx.fillText(lanes === 'pv' ? 'VOLUME  mL' : 'FLOW  L/min', 0, fs * 1.1);
      const T = (s.params.breaths ? s.params.breaths[1] - s.params.breaths[0] : 60 / s.params.rr), b0 = (s.params.breaths ? s.params.breaths[0] : 0.3);
      const i0 = Math.round(b0 / s.dt), i1 = Math.min(s.N - 1, Math.round((b0 + T) / s.dt) - 1), step = Math.max(1, Math.round((i1 - i0) / 900));
      ctx.strokeStyle = lanes === 'pv' ? pal.v : pal.f; ctx.lineWidth = lw; ctx.beginPath();
      for (let i = i0; i <= i1; i += step) { const x = px(X[i]), y = py(Y[i]); i === i0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); }
      ctx.stroke();
      if (!this.hasAttribute('static')) {
        const ph = (pos % T) / T, i = Math.min(i1, i0 + Math.floor(ph * (i1 - i0)));
        ctx.fillStyle = pal.mark; ctx.beginPath(); ctx.arc(px(X[i]), py(Y[i]), 6 * k, 0, 7); ctx.fill();
      }
    }
  }
  if (!customElements.get('vent-trace')) customElements.define('vent-trace', VentTrace);
  window.VentGraphics = { simulate, SCENARIOS: S };
})();
