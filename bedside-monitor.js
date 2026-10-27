/* VentCourse bedside monitor: <bedside-monitor vitals='[["HR","145"],["SpO₂","82% and falling"],...]'> */
(() => {
  const COL = { hr: '#6FBF73', spo2: '#3CC3CC', bp: '#EE7A63', rr: '#E9B54A', temp: '#D8D4CC', cvp: '#B59AE6', etco2: '#E9B54A', other: '#D8D4CC' };
  const kind = l => { const k = l.toLowerCase().replace(/[₂2]/g, '2'); return /^hr|heart/.test(k) ? 'hr' : /spo2|sat/.test(k) ? 'spo2' : /^bp|^nibp|^abp/.test(k) ? 'bp' : /^rr|resp/.test(k) ? 'rr' : /temp/.test(k) ? 'temp' : /cvp/.test(k) ? 'cvp' : /etco2/.test(k) ? 'etco2' : 'other'; };
  const LBL = { hr: 'HR', spo2: 'SpO₂', bp: 'NIBP', rr: 'RR', temp: 'Temp', cvp: 'CVP', etco2: 'EtCO₂' };
  const UNIT = { hr: 'bpm', spo2: '%', bp: 'mmHg', rr: '/min', temp: '°C', cvp: 'cmH₂O', etco2: 'mmHg' };
  const esc = t => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
  function split(v) {
    const m = /^\s*([+−-]?[<>~≈]?\d[\d.\/]*)\s*(%|°C|°|s|mL|mmHg|\/min)?\s*[,·]?\s*(.*)$/.exec(String(v));
    if (!m) return { big: '––', small: String(v) };
    return { big: m[1], small: m[3] || '' };
  }
  const W = 300, H = 40, SPEED = 100;
  function wave(type, rate) {
    const P = Math.max(8, SPEED * 60 / Math.max(20, Math.min(240, rate || 120)));
    const n = Math.ceil((W + P) / P) + 1; let d = '';
    for (let i = 0; i < n; i++) {
      const x = i * P, f = v => (x + v * P).toFixed(1);
      if (type === 'hr') d += `${i ? 'L' : 'M'}${f(0)} 26 L${f(.12)} 26 Q${f(.17)} 21 ${f(.22)} 26 L${f(.3)} 26 L${f(.33)} 29 L${f(.37)} 4 L${f(.41)} 34 L${f(.45)} 26 L${f(.58)} 26 Q${f(.68)} 17 ${f(.78)} 26 L${f(1)} 26 `;
      else if (type === 'spo2') d += `${i ? 'L' : 'M'}${f(0)} 32 C${f(.06)} 32 ${f(.12)} 6 ${f(.2)} 7 C${f(.28)} 8 ${f(.34)} 20 ${f(.4)} 21 C${f(.44)} 21 ${f(.47)} 17 ${f(.52)} 19 C${f(.66)} 25 ${f(.84)} 32 ${f(1)} 32 `;
      else d += `${i ? 'L' : 'M'}${f(0)} 30 C${f(.2)} 30 ${f(.3)} 8 ${f(.45)} 8 C${f(.6)} 8 ${f(.7)} 30 ${f(1)} 30 `;
    }
    return { d, P, dur: (P / SPEED).toFixed(3) };
  }
  function strip(type, rate, color) {
    const w = wave(type, rate);
    return `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" style="display:block; width:100%; height:100%;"><g><path d="${w.d}" fill="none" stroke="${color}" stroke-width="1.6" vector-effect="non-scaling-stroke" stroke-linejoin="round"/>` +
      `<animateTransform attributeName="transform" type="translate" from="0 0" to="${(-w.P).toFixed(1)} 0" dur="${w.dur}s" repeatCount="indefinite"/></g></svg>`;
  }
  function render(list) {
    const items = list.map(([l, v]) => ({ k: kind(l), l, v }));
    const get = k => items.find(x => x.k === k);
    const num = x => x ? parseFloat(split(x.v).big) : NaN;
    const hr = get('hr'), sp = get('spo2'), rr = get('rr');
    const label = x => esc(LBL[x.k] || x.l);
    const rowNum = (x, c) => { const s = split(x.v); return `<div style="flex:none; width:38%; display:flex; flex-direction:column; align-items:flex-end; justify-content:center; gap:1px; min-width:0;">` +
      `<div style="display:flex; align-items:baseline; gap:6px;"><span style="font:500 10px/1 var(--font-mono, monospace); letter-spacing:.1em; color:${c}; opacity:.85;">${label(x)}</span><span style="font:500 30px/1 var(--font-mono, monospace); color:${c}; letter-spacing:-.02em;">${esc(s.big)}</span></div>` +
      (s.small ? `<span style="font:400 10px/1.3 var(--font-sans, sans-serif); color:#9A968E; text-align:right; overflow-wrap:anywhere;">${esc(s.small)}</span>` : '') + `</div>`; };
    const row = (x, type, c, rate) => `<div style="display:flex; gap:10px; align-items:center; min-height:52px; border-bottom:1px solid #1E2124; padding:4px 0;"><div style="flex:1; height:40px; min-width:0; overflow:hidden;">${strip(type, rate, c)}</div>${rowNum(x, c)}</div>`;
    let h = '';
    if (hr) h += row(hr, 'hr', COL.hr, num(hr));
    if (sp) h += row(sp, 'spo2', COL.spo2, num(hr) || 120);
    if (rr) h += row(rr, 'rr', COL.rr, num(rr) || 20);
    const rest = items.filter(x => x !== hr && x !== sp && x !== rr);
    if (rest.length) h += `<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(96px, 1fr)); gap:10px 12px; padding-top:10px;">` + rest.map(x => {
      const c = COL[x.k] || COL.other, s = split(x.v), u = UNIT[x.k] || '';
      return `<div style="display:flex; flex-direction:column; gap:2px; min-width:0;"><span style="font:500 10px/1.2 var(--font-mono, monospace); letter-spacing:.1em; text-transform:uppercase; color:${c}; opacity:.85;">${label(x)}${u ? ' <span style="opacity:.6; text-transform:none;">' + u + '</span>' : ''}</span>` +
        `<span style="font:500 ${x.k === 'bp' ? 24 : 20}px/1.05 var(--font-mono, monospace); color:${c};">${esc(s.big)}</span>` + (s.small ? `<span style="font:400 10px/1.3 var(--font-sans, sans-serif); color:#9A968E; overflow-wrap:anywhere;">${esc(s.small)}</span>` : '') + `</div>`; }).join('') + `</div>`;
    return `<div style="background:#0E1012; border:1px solid #2A2D30; border-radius:4px; padding:8px 12px 12px; color:#D8D4CC; box-sizing:border-box;">` +
      `<div style="display:flex; justify-content:space-between; font:500 9px/1 var(--font-mono, monospace); letter-spacing:.14em; text-transform:uppercase; color:#6E6A63; padding:2px 0 6px; border-bottom:1px solid #1E2124;"><span>Bedside monitor</span><span style="color:#6FBF73;">● live</span></div>${h}</div>`;
  }
  class BedsideMonitor extends HTMLElement {
    static get observedAttributes() { return ['vitals']; }
    connectedCallback() { if (!this.style.display) this.style.display = 'block'; this.render(); }
    attributeChangedCallback() { if (this.isConnected) this.render(); }
    render() { const a = this.getAttribute('vitals') || '[]'; if (a === this._a) return; this._a = a; let v = []; try { v = JSON.parse(a); } catch (e) {} this.innerHTML = render(Array.isArray(v) ? v : []); }
  }
  if (!customElements.get('bedside-monitor')) customElements.define('bedside-monitor', BedsideMonitor);
})();
