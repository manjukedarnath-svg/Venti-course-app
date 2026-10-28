    // ── branching cases (deck side): grade settings like the phones do, word cloud, percentages, severity of the room ──
    const VC_SEV = [['Improving', '#3E7D4F'], ['No change', '#8A857C'], ['Worse', '#C27A12'], ['Life-threatening', '#B42318']];
    const VC_MD = { Mask: 'O₂ mask', HFNC: 'High-flow', CPAP: 'CPAP', ST: 'Bilevel ST', PC: 'PC', VC: 'VC', PRVC: 'PRVC', PS: 'PS + PEEP' };
    const VC_IF = { MASK: 'Face mask', HFNC: 'High-flow', NIV: 'NIV', VENT: 'Ventilator' };
    const VC_K = [['vt', 'VT'], ['pi', 'Pinsp'], ['pe', 'PEEP'], ['cp', 'CPAP'], ['ip', 'IPAP'], ['ep', 'EPAP'], ['rr', 'RR'], ['ti', 'Ti'], ['o', 'FiO₂'], ['f', 'Flow'], ['l', 'O₂']];
    function vcGrade(rule, enc) {
      if (!rule || !enc) return null;
      const [iface, mode, kv] = String(enc).split(':'), v = {};
      (kv || '').split(',').forEach(p => { const [k, x] = p.split('='); if (k) v[k] = +x; });
      let sev = rule.iface && rule.iface[iface] !== undefined ? rule.iface[iface] : 2;
      if (iface === 'VENT' || iface === 'NIV') { const K = rule.knobs || {};
        if (v.rr && v.ti && K.te) v.te = +(60 / v.rr - v.ti).toFixed(1);
        for (const k in K) { if (v[k] === undefined) continue; const [lo, hi, blo, bhi] = K[k], x = v[k];
          sev = Math.max(sev, x < blo || x > bhi ? 3 : x < lo || x > hi ? 2 : 0); } }
      return sev;
    }
    const vcRead = enc => { const [iface, mode, kv] = String(enc).split(':'); if (!kv) return enc; const v = {}; kv.split(',').forEach(p => { const [k, x] = p.split('='); v[k] = x; });
      return (VC_MD[mode] || mode) + ' · ' + VC_K.filter(([k]) => v[k] !== undefined && k !== 'ti').map(([k, l]) => l + ' ' + (k === 'o' ? (v[k] / 100).toFixed(2) : v[k])).join(' · '); };
    const vcBar = (el, counts, n) => { if (!el) return; const tot = Math.max(1, n);
      el.innerHTML = '<div style="display:flex; height:22px; border-radius:3px; overflow:hidden; background:var(--border-subtle);">' +
        counts.map((c, i) => c ? `<div style="width:${c / tot * 100}%; background:${VC_SEV[i][1]}; transition:width .6s;"></div>` : '').join('') + '</div>' +
        '<div style="display:flex; flex-wrap:wrap; gap:6px 18px; margin-top:8px; font-size:20px;">' + counts.map((c, i) => `<span style="color:${VC_SEV[i][1]};">${VC_SEV[i][0]} ${n ? Math.round(c / tot * 100) : 0}%</span>`).join('') + '</div>'; };
    const vcJSON = (s, a) => { try { return JSON.parse(s.getAttribute(a) || 'null'); } catch (x) { return null; } };
    function vcRoomSet(s, all) {
      const rule = vcJSON(s, 'data-rule');
      const cloud = s.querySelector('[data-set-cloud]');
      if (cloud) { const by = {}; all.forEach(t => { const r = vcRead(t); by[r] = (by[r] || 0) + 1; });
        const top = Object.entries(by).sort((a, b) => b[1] - a[1]).slice(0, 18), mx = top.length ? top[0][1] : 1;
        cloud.innerHTML = top.length ? top.map(([t, n]) => { const g = rule ? vcGrade(rule, all.find(x => vcRead(x) === t)) : null;
          return `<span style="display:inline-flex; align-items:baseline; gap:10px; border:2px solid ${g === null ? 'var(--border-default)' : VC_SEV[g][1]}; border-radius:999px; padding:8px 18px; font-size:${Math.round(20 + 22 * n / mx)}px; line-height:1.15; background:var(--surface-page);">${t}<span style="font-family:var(--font-mono); font-size:18px; color:var(--text-accent);">${n > 1 ? '×' + n : ''}</span></span>`; }).join('')
          : '<span style="font-size:24px; color:var(--text-secondary);">Settings appear here as the phones send them</span>'; }
      const pct = s.querySelector('[data-set-pct]');
      if (pct) { const by = {}; all.forEach(t => { const [i, m] = t.split(':'); const k = (VC_IF[i] || i) + (i === 'VENT' || i === 'NIV' ? ' · ' + (VC_MD[m] || m) : ''); by[k] = (by[k] || 0) + 1; });
        const n = Math.max(1, all.length);
        pct.innerHTML = Object.entries(by).sort((a, b) => b[1] - a[1]).map(([k, c]) => `<div style="display:flex; align-items:center; gap:14px;"><span style="flex:none; width:300px; font-size:22px;">${k}</span><div style="flex:1; height:18px; background:var(--border-subtle); border-radius:3px;"><div style="width:${c / n * 100}%; height:100%; background:var(--text-accent); border-radius:3px;"></div></div><span style="flex:none; width:90px; text-align:right; font-family:var(--font-mono); font-size:20px;">${Math.round(c / n * 100)}%</span></div>`).join('') || ''; }
      const sv = s.querySelector('[data-sev-set]');
      if (sv && rule) { const c = [0, 0, 0, 0]; all.forEach(t => { const g = vcGrade(rule, t); if (g !== null) c[g]++; }); vcBar(sv, c, all.length); }
    }
    function vcRoomOrd(s, j) {
      const el = s.querySelector('[data-sev-ord]'), sev = vcJSON(s, 'data-sev'); if (!el || !sev) return;
      const c = [0, 0, 0, 0]; Object.entries(j.counts || {}).forEach(([L, n]) => { if (sev[L] !== undefined) c[sev[L]] += n; }); vcBar(el, c, j.n || 0);
    }
    async function vcCourse(s, post, room) {
      for (const row of s.querySelectorAll('[data-cq]')) { const q = row.getAttribute('data-cq'), sev = vcJSON(row, 'data-sev'), rule = vcJSON(row, 'data-rule');
        try { const a = await post('results', { room, q }), c = [0, 0, 0, 0]; let n = 0;
          if (a.ok && sev) { Object.entries(a.j.counts || {}).forEach(([L, k]) => { if (sev[L] !== undefined) { c[sev[L]] += k; n += k; } }); }
          if (rule) { const b = await post('results', { room, q: q + '~s' }); if (b.ok) b.j.texts.forEach(t => { const g = vcGrade(rule, t.t); if (g !== null) { c[g] += t.n; n += t.n; } }); }
          vcBar(row.querySelector('[data-bar-sev]'), c, n); } catch (x) {} }
    }
