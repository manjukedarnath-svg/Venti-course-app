/* VentCourse patient physiology (window.VCPhysio). A teaching model for the live cases:
   two-compartment lung (an always-open "baby lung" and a recruitable compartment, both able to overdistend),
   gas exchange through shunt and dead space, and a heart–lung circulation (venous return, right-ventricle afterload, baroreflex).
   Every case stage calibrates the model to its scripted numbers (the anchor): the script's own settings reproduce the script's
   gas and monitor exactly, and a candidate's settings move the numbers from there by the physiology below.
   Checked against textbook behaviour by tools/physio_test.js. Not a validated simulator. */
(function (g) {
  if (g.VCPhysio) return;
  const PIO2 = 713;                                   // (760 − 47) mmHg: inspired PO2 at FiO2 1.0, sea level
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  const sig = x => 1 / (1 + Math.exp(-x));
  const so2 = po2 => { const p = Math.max(1, po2); return 100 / (1 + 23400 / (p * p * p + 150 * p)); };   // Severinghaus
  const cont = (po2, hb) => 1.34 * hb * so2(po2) / 100 + 0.003 * po2;                                    // O2 content, mL/dL
  const po2Of = (ca, hb) => { let lo = 5, hi = 700; for (let i = 0; i < 50; i++) { const m = (lo + hi) / 2; if (cont(m, hb) < ca) lo = m; else hi = m; } return (lo + hi) / 2; };

  // lung and circulation per disease. The ARDS values were fitted (tools/physio_test.js) to the case's PEEP titration sheet (SpO₂ and BP at PEEP 6–14)
  // and to the case's own decision points (PEEP 12 helps, a 10 mL/kg breath does not, PEEP 18 costs blood pressure).
  // kov: how much overstretch stiffens the lung; ovq: blood flow left in overstretched units; kvd: their dead space; kpvr: plateau → RV afterload;
  // kmap: how much the time-averaged pressure (not only PEEP) recruits; kmapq: aeration gain per cmH₂O of mean airway pressure; xe: expiratory/inspiratory time-constant ratio (asthma, calibrated to the scripted auto-PEEP). fB: always-open fraction; fD: recruitable fraction (the rest is consolidated, never opens);
  // Pcrit/w: the PEEP at which half the recruitable lung is open, and how gradually; Pover/wo: end-inspiratory pressure where units overdistend;
  // hpv: how much hypoxic vasoconstriction cuts flow to closed units; trans: fraction of airway pressure reaching the pleura (stiff lungs transmit less);
  // Hb g/dL; pms: mean systemic filling pressure, mmHg (venous return driving pressure with Pra 6).
  const KIND = {
    ards:   { fB: 0.40, fD: 0.15, Pcrit: 13, w: 2.0, Pover: 28, wo: 3, kov: 0.25, ovq: 0.85, kvd: 0.15, kpvr: 0.005, kmapq: 0.02, kmap: 0.5, hpv: 0.45, trans: 0.15, Hb: 9, pms: 18 },
    asthma: { fB: 0.93, fD: 0.05, Pcrit: 4, w: 2.0, Pover: 35, wo: 5.0, kov: 0.3, hpv: 0.5, trans: 0.4, Hb: 12, pms: 18 },
    normal: { fB: 0.97, fD: 0.03, Pcrit: 3, w: 1.5, Pover: 30, wo: 3.5, kov: 0.4, hpv: 0.5, trans: 0.5, Hb: 12, pms: 18 }
  };

  // the lung at a given total PEEP and end-inspiratory pressure
  function lung(K, pTot, pEnd) {
    const open = K.fB + K.fD * sig((pTot - K.Pcrit) / K.w);
    const ov = sig((pEnd - K.Pover) / K.wo);                              // share of open units overstretched at end inspiration
    return { open, ov, closed: 1 - open, cRel: open * (1 - (K.kov || 0.4) * ov) };  // compliance relative to a fully open, unstretched lung
  }
  // shunt: closed units keep (1 − hpv) of their flow; overstretched units are squeezed (0.3 of their flow) and become dead space
  const shuntOf = (L, K) => { const wc = L.closed * (1 - K.hpv), wo = L.open * (1 - L.ov) + L.open * L.ov * (K.ovq ?? 0.4); return wc / (wc + wo); };

  // one steady state for a support s: { iface, ctl, fio2, peep, auto, mapAw, pEnd, rr, vt (delivered), ps, flow }
  function state(P, K, cal, s) {
    const kg = P.kg, L = lung(K, s.peep + (s.auto || 0), s.pEnd);
    const vdAnat = (s.iface === 'VENT' ? 2.5 : 2.2) * kg * (s.iface === 'HFNC' ? 1 - 0.3 * clamp(s.flow / (2 * kg), 0, 1) : 1);
    let co = cal.co0, pa = cal.pao2a, out;
    for (let it = 0; it < 6; it++) {
      const vdAlv = s.vt * ((K.kvd ?? 0.35) * L.ov + 0.12 * Math.max(0, 1 - co / cal.co0));
      const va = s.rr * Math.max(0.2 * s.vt, s.vt - vdAnat - vdAlv) * Math.max(0.35, 1 - 0.04 * Math.max(0, (s.autoI ?? s.auto ?? 0) - 4));   // trapped gas, not PEEP set against it, costs ventilation
      const paco2 = clamp(cal.kCO2 / va, 18, 160);
      const pAO2 = Math.max(20, s.fio2 * PIO2 - paco2 / 0.8);
      const qs = clamp((shuntOf(L, K) + cal.qx) * Math.exp(-(K.kmapq ?? 0.03) * (s.mapAw - cal.mapAwA)), 0.01, 0.92);   // a higher mean airway pressure keeps open units better aerated
      const vo2 = 6 * kg;                                                  // mL/min
      const ca = cont(pAO2, K.Hb) - qs / (1 - qs) * vo2 / (co * 10);
      pa = po2Of(Math.max(2, ca), K.Hb);
      const ph = 6.1 + Math.log10(cal.hco3 / (0.03 * paco2));
      // circulation: venous return falls as pleural pressure (and so right atrial pressure) rises; the RV dislikes overstretch, hypoxia and acidosis
      const pra = 6 + K.trans * (s.mapAw - cal.mapAwA) + 0.35 * ((s.auto || 0) - cal.autoA);
      const vr = clamp((K.pms - pra) / (K.pms - 6), 0.3, 1.6);
      const pvr = 1 + (K.kpvr ?? 0.025) * Math.max(0, s.pEnd - 26) + 0.004 * Math.max(0, 80 - pa) + 0.6 * Math.max(0, 7.25 - ph);
      co = cal.co0 * vr * (1 + 0.5 * (cal.pvrA - 1)) / (1 + 0.5 * (pvr - 1));
      out = { L, qs, va, vdAlv, vdAnat, paco2, pa, ph, pra, co, pvr, pAO2, mapAw: s.mapAw };
    }
    return out;
  }

  // the breath for a set of settings ({iface, mode, v} as the phones send them): delivered VT, end-inspiratory (plateau) pressure,
  // mean airway pressure and auto-PEEP, with the compliance that the PEEP and the stretch leave open
  function breath(P, K, cUnit, set) {
    const v = set.v || {}, kg = P.kg, R = P.R || 20, own = P.own || 30;
    const s = { iface: set.iface, mode: set.mode, fio2: 0.21, peep: 0, auto: 0, rr: own, vt: 6 * kg, ps: 0, flow: 0, ctl: false };
    let L = lung(K, 0, 15), C = cUnit * L.cRel;
    const spont = (pe, ps) => { for (let i = 0; i < 20; i++) { s.vt = 6 * kg * Math.sqrt(L.cRel / Math.max(0.05, cal0(K))) + 0.6 * ps * C; s.pEnd = pe + s.vt / C; L = lung(K, pe, s.pEnd); C = 0.6 * C + 0.4 * cUnit * L.cRel; } };
    if (set.iface === 'MASK') { s.fio2 = Math.min(0.8, 0.21 + 0.04 * (v.l || 0)); spont(0, 0); s.mapAw = 0; }
    else if (set.iface === 'HFNC') { s.fio2 = (v.o || 21) / 100; s.flow = v.f || 0; s.peep = Math.min(6, s.flow / kg * 1.5);
      if (s.flow < 2 * kg) s.fio2 = s.fio2 - (s.fio2 - 0.21) * (1 - s.flow / (2 * kg)) * 0.5;             // below the child's demand, room air is entrained
      spont(s.peep, 0); s.mapAw = s.peep; }
    else if (set.iface === 'NIV' || set.mode === 'PS') {
      const pe = set.mode === 'CPAP' ? (v.cp || 5) : (v.ep ?? v.pe ?? 5), ps = set.mode === 'CPAP' ? 0 : set.mode === 'PS' ? (v.ps || 8) : Math.max(0, (v.ip || pe) - pe);
      s.fio2 = (v.o || 21) / 100; s.peep = pe; s.ps = ps; s.rr = Math.max(own * (1 - 0.25 * Math.min(1, ps / 10)), set.mode === 'ST' ? (v.br || 0) : 0);
      spont(pe, ps); s.mapAw = pe + ps * 0.35; }
    else {
      const rr = Math.max(v.rr || 20, P.trig || 0), ti = Math.min(v.ti || 0.7, 60 / rr - 0.15), pe = v.pe || 0, te = 60 / rr - ti;   // a triggering child breathes above the set rate
      s.fio2 = (v.o || 21) / 100; s.peep = pe; s.rr = rr; s.ctl = true;
      for (let i = 0; i < 30; i++) {
        // time constants from the open lung (overstretch stiffens the lung but does not speed emptying: trapped volume grows with VT, as Tuxen described)
        const tauI = R * cUnit * L.open / 1000, tauE = tauI * (K.xe ?? (P.kind === 'asthma' ? 2.5 : 1));
        s.vt = set.mode === 'PC' ? (v.pi || 12) * C * (1 - Math.exp(-ti / tauI)) : (v.vt || 6 * kg);
        const left = Math.exp(-Math.max(0.05, te) / tauE);
        s.auto = s.vt * left / (1 - left) / (cUnit * L.open);   // the trapped volume, over the compliance of the open lung
        if (P.kind === 'asthma') {   // flow limitation (the waterfall): external PEEP up to ~80% of the intrinsic PEEP does not raise the total
          const tot = pe <= 0.8 * s.auto ? s.auto : s.auto + (pe - 0.8 * s.auto) * 0.9; s.autoI = s.auto; s.auto = Math.max(0, tot - pe); }
        else s.autoI = s.auto;
        // the high-pressure limit (40 cmH₂O): the ventilator ends the breath early, so less volume goes in
        s.auto = Math.min(s.auto, Math.max(0, 38 - pe));   // trapped pressure cannot pass the limit: the chest stays full and barely ventilates
        if (pe + s.auto + s.vt / C > 40) { s.vt = Math.max(0.1 * (v.vt || 6 * kg), (40 - pe - s.auto) * C); s.limited = true; } else s.limited = false;
        s.pEnd = pe + s.auto + s.vt / C;
        s.mapAw = pe + (s.pEnd - pe) * (ti * rr / 60) * (set.mode === 'VC' ? 0.6 : 0.9);
        L = lung(K, pe + s.auto + (K.kmap ?? 0.5) * (s.mapAw - pe - s.auto), s.pEnd); C = 0.6 * C + 0.4 * cUnit * L.cRel; }   // recruitment follows the time-averaged pressure; damped: overstretch and plateau feed each other
      }
    s.C = C; s.L = L;
    return s;
  }
  const cal0 = K => K.fB + K.fD * 0.5;   // a reference open fraction for the spontaneous VT

  // calibration: the anchor support must give the anchor gas and blood pressure
  function calibrate(P, A) {
    const K = { ...(KIND[P.kind] || KIND.normal), ...(P.k || {}) }, g0 = A.gas || {};
    let cUnit = P.C / 0.6; for (let i = 0; i < 40; i++) { const b = breath(P, K, cUnit, A.set); cUnit *= Math.pow(P.C / b.C, 0.5); }
    if (P.autoA) { let lo = 0.5, hi = 20; for (let i = 0; i < 40; i++) { K.xe = Math.sqrt(lo * hi); const b = breath(P, K, cUnit, A.set); if (b.peep + b.auto < P.autoA) lo = K.xe; else hi = K.xe; } }
    A = { ...A, sup: breath(P, K, cUnit, A.set) };
    const bp = (A.bp && A.bp.match(/(\d+)\s*\/\s*(\d+)/)) || [0, 90, 55];
    const cal = { co0: 0.15 * P.kg, kCO2: 1, qx: 0, hco3: 24, mapAwA: A.sup.mapAw, autoA: A.sup.auto || 0, pvrA: 1, pao2a: g0['PaO₂'] || 0 };
    const paco2A = g0['PaCO₂'] || 40, phA = g0.pH || 7.4;
    cal.hco3 = 0.03 * paco2A * Math.pow(10, phA - 6.1);
    let st = state(P, K, cal, A.sup); cal.kCO2 = paco2A * st.va;           // CO2 production matched to the anchor PaCO2
    if (!g0['PaO₂'] && A.spo2) { let lo = 5, hi = 600; for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2; if (so2(m) < A.spo2) lo = m; else hi = m; } cal.pao2a = (lo + hi) / 2; }
    if (!cal.pao2a) cal.pao2a = 80;
    for (let round = 0; round < 4; round++) {                              // extra shunt / V/Q mismatch that gives the anchor PaO2, with the circulation settled
      let lo = -0.6, hi = 0.85;
      for (let i = 0; i < 40; i++) { cal.qx = (lo + hi) / 2; st = state(P, K, cal, A.sup); if (st.pa > cal.pao2a) lo = cal.qx; else hi = cal.qx; }
      st = state(P, K, cal, A.sup); cal.pvrA = st.pvr; st = state(P, K, cal, A.sup); cal.kCO2 *= paco2A / st.paco2; }
    st = state(P, K, cal, A.sup);
    cal.ref = st; cal.K = K; cal.cUnit = cUnit; cal.anc = A.sup; cal.sysA = +bp[1]; cal.diaA = +bp[2];
    return cal;
  }

  // the candidate's patient, relative to the anchor
  function run(P, cal, set) {
    const s = breath(P, cal.K, cal.cUnit, set), st = state(P, cal.K, cal, s), r = cal.ref;
    const mapA = cal.diaA + (cal.sysA - cal.diaA) / 3, ppA = cal.sysA - cal.diaA;
    const svrA = (mapA - 6) / r.co, svr = svrA * (1 + 0.5 * (1 - st.co / r.co));          // the baroreflex makes up half the fall
    const map = clamp(st.co * svr + st.pra, 20, 140), pp = ppA * clamp(st.co / r.co, 0.3, 1.5);
    return { ...st, sys: Math.round(map + 2 * pp / 3), dia: Math.round(map - pp / 3), mapBp: map, mapBpA: mapA,
      dSat: so2(st.pa) - so2(r.pa), coRel: st.co / r.co, sup: s, C: s.C, plat: s.pEnd, oi: s.mapAw * s.fio2 * 100 / st.pa, pf: st.pa / s.fio2 };
  }
  g.VCPhysio = { KIND, lung, breath, calibrate, run, so2, cont, po2Of, version: 1 };
})(typeof window !== 'undefined' ? window : globalThis);
