/* VentCourse patient illustration: <patient-figure age="infant|toddler|child|teen" support="ett|bag|mask|niv|prone"> */
(() => {
  const BANDS = {
    infant: { r: 31, len: 150, th: 58 },
    toddler: { r: 28, len: 196, th: 58 },
    child: { r: 25, len: 248, th: 56 },
    teen: { r: 23, len: 296, th: 56 }
  };
  const SKIN = '#B9825A', SKIN_D = '#8E5C3B', HAIR = '#2B2420';
  const f = n => Math.round(n * 10) / 10;
  const pt = (cx, cy, r, deg) => [f(cx + r * Math.cos(deg * Math.PI / 180)), f(cy - r * Math.sin(deg * Math.PI / 180))];
  const arc = (cx, cy, r, a0, a1) => { const [x0, y0] = pt(cx, cy, r, a0), [x1, y1] = pt(cx, cy, r, a1); return `M${x0} ${y0} A${r} ${r} 0 ${Math.abs(a1 - a0) > 180 ? 1 : 0} 0 ${x1} ${y1}`; };

  function svg(age, support) {
    const B = BANDS[age] || BANDS.child, prone = support === 'prone';
    const ink = 'var(--text-primary)', soft = 'var(--text-tertiary)', acc = 'var(--accent)';
    const top = 196, r = B.r, hx = 64 + r, hy = top - 10 - r;
    const x0 = hx + r * 0.62, x1 = Math.min(452, x0 + B.len), L = x1 - x0, th = B.th;
    const y = h => f(top - h);
    const out = [];
    // monitor on a stand (screen dark, values on demand)
    out.push(`<g><line x1="408" y1="96" x2="408" y2="${top + 30}" stroke="${soft}" stroke-width="3"/>`,
      `<rect x="356" y="18" width="104" height="78" rx="5" fill="#1B1A17" stroke="${ink}" stroke-width="2"/>`,
      `<rect x="363" y="25" width="90" height="64" rx="2" fill="#0F1113"/>`,
      `<path d="M367 42 h12 l3 -8 l4 16 l3 -8 h14 l3 -8 l4 16 l3 -8 h14 l3 -8 l4 16 l3 -8 h6" fill="none" stroke="#6FBF73" stroke-width="1.6" stroke-linejoin="round"/>`,
      `<path d="M367 64 q6 -10 12 0 t12 0 t12 0 t12 0 t12 0 t12 0 t10 0" fill="none" stroke="#3CC3CC" stroke-width="1.6"/>`,
      `<path d="M367 80 h80" stroke="#E9B54A" stroke-width="1.2" stroke-dasharray="3 4"/></g>`);
    // bed
    out.push(`<g><rect x="22" y="${top}" width="436" height="16" rx="6" fill="var(--surface-raised)" stroke="${ink}" stroke-width="2"/>`,
      `<line x1="30" y1="${top + 16}" x2="30" y2="${top + 40}" stroke="${ink}" stroke-width="2.5"/><line x1="450" y1="${top + 16}" x2="450" y2="${top + 40}" stroke="${ink}" stroke-width="2.5"/>`,
      `<line x1="22" y1="${top + 34}" x2="458" y2="${top + 34}" stroke="${ink}" stroke-width="2"/>`,
      `<circle cx="38" cy="${top + 46}" r="6" fill="var(--surface-page)" stroke="${ink}" stroke-width="2"/><circle cx="442" cy="${top + 46}" r="6" fill="var(--surface-page)" stroke="${ink}" stroke-width="2"/></g>`);
    // pillow
    out.push(`<path d="M${hx - r - 26} ${top} q-4 -16 14 -18 h${2 * r + 30} q18 2 14 18 z" fill="var(--surface-card, var(--surface-page))" stroke="${ink}" stroke-width="2"/>`);
    // neck
    out.push(`<rect x="${f(hx + r * 0.35)}" y="${f(hy + r * 0.25)}" width="${f(r * 0.9)}" height="${f(top - 10 - hy - r * 0.25 + 4)}" fill="${SKIN}" stroke="${ink}" stroke-width="2"/>`);
    // blanket body
    const bl = `M${f(x0)} ${top} L${f(x0)} ${y(th * 0.82)} C${f(x0 + L * 0.06)} ${y(th * 1.02)} ${f(x0 + L * 0.3)} ${y(th * 1.06)} ${f(x0 + L * 0.42)} ${y(th * 0.92)} ` +
      `C${f(x0 + L * 0.52)} ${y(th * 0.82)} ${f(x0 + L * 0.6)} ${y(th * 0.86)} ${f(x0 + L * 0.68)} ${y(th * 0.7)} ` +
      `C${f(x0 + L * 0.78)} ${y(th * 0.52)} ${f(x0 + L * 0.86)} ${y(th * 0.56)} ${f(x0 + L * 0.9)} ${y(th * 0.62)} ` +
      `C${f(x0 + L * 0.95)} ${y(th * 0.86)} ${f(x1)} ${y(th * 0.8)} ${f(x1)} ${y(th * 0.4)} L${f(x1)} ${top} Z`;
    out.push(`<path d="${bl}" fill="var(--surface-sunken)" stroke="${ink}" stroke-width="2" stroke-linejoin="round"/>`);
    // folded hem
    const hemX = x0 + Math.max(16, L * 0.1);
    out.push(`<path d="M${f(hemX)} ${y(th * 0.99)} Q${f(hemX + 4)} ${y(th * 0.5)} ${f(hemX - 2)} ${top}" fill="none" stroke="${ink}" stroke-width="1.6"/>`);
    // arm lying on the blanket, hand with saturation probe
    const sh = [x0 + 8, top - th * 0.8], hand = [x0 + L * 0.34, top - th * 0.9];
    const armD = `M${f(sh[0])} ${f(sh[1])} Q${f(x0 + L * 0.18)} ${f(top - th * 0.98)} ${f(hand[0])} ${f(hand[1])}`;
    const aw = Math.max(9, r * 0.4);
    out.push(`<path d="${armD}" fill="none" stroke="${ink}" stroke-width="${f(aw + 4)}" stroke-linecap="round"/>`,
      `<path d="${armD}" fill="none" stroke="${prone ? 'var(--surface-sunken)' : SKIN}" stroke-width="${f(aw)}" stroke-linecap="round"/>`);
    out.push(`<rect x="${f(hand[0] - 3)}" y="${f(hand[1] - aw * 0.7)}" width="${f(aw * 1.1)}" height="${f(aw * 1.4)}" rx="3" fill="${acc}" stroke="${ink}" stroke-width="1.5"/>`);
    // cables to the monitor
    out.push(`<path d="M${f(hand[0] + aw)} ${f(hand[1])} C${f(hand[0] + 70)} ${f(hand[1] - 10)} 330 120 372 96" fill="none" stroke="${soft}" stroke-width="1.6"/>`,
      `<path d="M${f(x0 + L * 0.26)} ${y(th * 1.04)} C${f(x0 + L * 0.3)} 70 330 110 386 96" fill="none" stroke="${soft}" stroke-width="1.6"/>`);
    // head
    out.push(`<circle cx="${hx}" cy="${hy}" r="${r}" fill="${SKIN}" stroke="${ink}" stroke-width="2"/>`);
    if (!prone) {
      out.push(`<path d="${arc(hx, hy, r, 118, 268)} Q${pt(hx, hy, r * 0.2, 200).join(' ')} ${pt(hx, hy, r, 118).join(' ')} Z" fill="${HAIR}"/>`,
        `<path d="${arc(hx, hy, r, 128, 262)}" fill="none" stroke="${ink}" stroke-width="2"/>`);
      const [nx, ny] = pt(hx, hy, r, 82);
      out.push(`<path d="M${f(nx - 6)} ${f(ny + 1)} q4 -9 9 -2" fill="${SKIN}" stroke="${ink}" stroke-width="2" stroke-linejoin="round"/>`);
      const [ex, ey] = pt(hx, hy, r * 0.62, 104);
      out.push(`<path d="M${f(ex - 5)} ${f(ey)} q5 4 10 0" fill="none" stroke="${ink}" stroke-width="1.8" stroke-linecap="round"/>`);
      const [ax, ay] = pt(hx, hy, r * 0.12, 250);
      out.push(`<path d="M${f(ax - 4)} ${f(ay - 6)} a6 7 0 1 0 2 12" fill="${SKIN_D}" stroke="${ink}" stroke-width="1.5"/>`);
    } else {
      out.push(`<path d="${arc(hx, hy, r, 30, 230)} Q${pt(hx, hy, r * 0.1, 310).join(' ')} ${pt(hx, hy, r, 30).join(' ')} Z" fill="${HAIR}"/>`,
        `<path d="${arc(hx, hy, r, 30, 230)}" fill="none" stroke="${ink}" stroke-width="2"/>`);
      const [ax, ay] = pt(hx, hy, r * 0.2, 290);
      out.push(`<path d="M${f(ax - 4)} ${f(ay - 6)} a6 7 0 1 0 2 12" fill="${SKIN_D}" stroke="${ink}" stroke-width="1.5"/>`);
      out.push(`<rect x="${f(x0 + L * 0.12)}" y="${top - 7}" width="${f(L * 0.28)}" height="9" rx="4.5" fill="var(--surface-raised)" stroke="${ink}" stroke-width="1.5"/>`);
    }
    // airway
    const mA = prone ? 330 : 50, [mx, my] = pt(hx, hy, r, mA);
    const circuit = (sx, sy) => {
      const d = `M${f(sx)} ${f(sy)} C${f(sx + 30)} ${f(sy - 60)} 250 10 330 24`;
      return `<path d="${d}" fill="none" stroke="${ink}" stroke-width="11" stroke-linecap="round"/>` +
        `<path d="${d}" fill="none" stroke="var(--surface-page)" stroke-width="8" stroke-linecap="round"/>` +
        `<path d="${d}" fill="none" stroke="${soft}" stroke-width="8" stroke-dasharray="1.6 3.2"/>`;
    };
    if (support === 'trach') {
      const tx = hx + r * 0.8, ty = hy + r * 0.25;
      out.push(`<rect x="${f(tx - 9)}" y="${f(ty - 3)}" width="18" height="5" rx="2" fill="var(--surface-page)" stroke="${ink}" stroke-width="1.5"/>`,
        `<path d="M${f(tx)} ${f(ty - 2)} L${f(tx + 2)} ${f(ty - 22)}" stroke="${acc}" stroke-width="5" stroke-linecap="round"/>`,
        `<rect x="${f(tx - 3)}" y="${f(ty - 34)}" width="10" height="12" rx="2" fill="${ink}"/>`, circuit(tx + 2, ty - 34));
    } else if (support === 'nc') {
      const [nx, ny] = pt(hx, hy, r, 80), [ex, ey] = pt(hx, hy, r * 0.15, 240);
      out.push(`<path d="M${f(nx + 3)} ${f(ny + 3)} Q${f(hx + r * 0.3)} ${f(hy + 2)} ${f(ex)} ${f(ey)}" fill="none" stroke="${acc}" stroke-width="2.4"/>`,
        `<path d="M${f(nx + 3)} ${f(ny + 3)} C${f(nx + 30)} ${f(ny - 30)} 250 20 330 28" fill="none" stroke="${acc}" stroke-width="2.4"/>`,
        `<rect x="${f(nx - 2)}" y="${f(ny)}" width="9" height="5" rx="2" fill="${acc}" stroke="${ink}" stroke-width="1"/>`);
    } else if (support === 'mask' || support === 'niv') {
      const th0 = 66, [px, py] = pt(hx, hy, r * 0.9, th0), mw = r * 0.78, mh = r * 0.62, rot = 90 - th0;
      // strap round the head
      out.push(`<path d="${arc(hx, hy, r + 1.5, 30, 225)}" fill="none" stroke="${support === 'niv' ? ink : acc}" stroke-width="${support === 'niv' ? 3 : 1.6}" opacity=".75"/>`);
      out.push(`<g transform="translate(${px} ${py}) rotate(${rot})">` +
        `<path d="M${f(-mw)} 4 C${f(-mw)} ${f(-mh * 0.4)} ${f(-mw * 0.45)} ${f(-mh)} 0 ${f(-mh)} C${f(mw * 0.45)} ${f(-mh)} ${f(mw)} ${f(-mh * 0.4)} ${f(mw)} 4 Z" fill="rgba(214,226,229,.6)" stroke="${ink}" stroke-width="2" stroke-linejoin="round"/>` +
        `<rect x="-6" y="${f(-mh - 8)}" width="12" height="9" rx="2" fill="${ink}"/></g>`);
      const [ox, oy] = [f(px + (mh + 6) * Math.cos(th0 * Math.PI / 180)), f(py - (mh + 6) * Math.sin(th0 * Math.PI / 180))];
      if (support === 'mask') {
        // reservoir bag hangs onto the chest, oxygen tubing to the wall
        out.push(`<path d="M${ox} ${oy} C${f(ox + 18)} ${f(oy - 4)} ${f(ox + 26)} ${f(oy + 6)} ${f(ox + 30)} ${f(oy + 14)} C${f(ox + 38)} ${f(oy + 34)} ${f(ox + 10)} ${f(oy + 40)} ${f(ox + 6)} ${f(oy + 22)} C${f(ox + 4)} ${f(oy + 12)} ${f(ox + 2)} ${f(oy + 6)} ${ox} ${oy} Z" fill="color-mix(in oklab, ${acc} 32%, var(--surface-page))" stroke="${ink}" stroke-width="1.8"/>`,
          `<path d="M${ox} ${oy} C${f(ox + 10)} ${f(oy - 50)} 250 18 330 28" fill="none" stroke="${soft}" stroke-width="2.2"/>`);
      } else out.push(circuit(ox, oy));
    } else {
      const ex = mx + (prone ? 26 : 5), ey = my - (prone ? 4 : 30);
      out.push(`<path d="M${mx} ${my} Q${f(mx + (prone ? 10 : 2))} ${f(my - (prone ? 2 : 16))} ${f(ex)} ${f(ey)}" fill="none" stroke="${acc}" stroke-width="4.5" stroke-linecap="round"/>`,
        `<rect x="${f(mx - 7)}" y="${f(my - 3)}" width="14" height="6" rx="1.5" fill="var(--surface-page)" stroke="${ink}" stroke-width="1.4" transform="rotate(${prone ? 20 : -40} ${mx} ${my})"/>`,
        `<rect x="${f(ex - 5)}" y="${f(ey - 12)}" width="10" height="12" rx="2" fill="${ink}"/>`);
      if (support === 'bag') {
        const bx = ex, by = ey - 12;
        out.push(`<g transform="rotate(-28 ${bx} ${by})"><rect x="${f(bx - 4)}" y="${f(by - 14)}" width="8" height="14" fill="${ink}"/>` +
          `<ellipse cx="${bx}" cy="${f(by - 46)}" rx="20" ry="32" fill="color-mix(in oklab, ${acc} 22%, var(--surface-page))" stroke="${ink}" stroke-width="2"/>` +
          `<path d="M${f(bx - 12)} ${f(by - 50)} q12 6 24 0 M${f(bx - 12)} ${f(by - 40)} q12 6 24 0" fill="none" stroke="${ink}" stroke-width="1.2" opacity=".5"/>` +
          `<rect x="${f(bx - 6)}" y="${f(by - 86)}" width="12" height="9" fill="${ink}"/>` +
          `<path d="M${f(bx)} ${f(by - 86)} C${f(bx - 2)} ${f(by - 104)} ${f(bx + 22)} ${f(by - 116)} ${f(bx + 30)} ${f(by - 100)} C${f(bx + 36)} ${f(by - 88)} ${f(bx + 14)} ${f(by - 84)} ${f(bx)} ${f(by - 86)}" fill="color-mix(in oklab, ${acc} 30%, transparent)" stroke="${ink}" stroke-width="1.6"/></g>`);
      } else out.push(circuit(ex, ey - 12));
    }
    return `<svg viewBox="0 -40 480 302" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Illustration of the patient in bed" xmlns="http://www.w3.org/2000/svg">${out.join('')}</svg>`;
  }

  class PatientFigure extends HTMLElement {
    static get observedAttributes() { return ['age', 'support', 'img']; }
    connectedCallback() { this.style.display = this.style.display || 'block'; this.render(); }
    attributeChangedCallback() { if (this.isConnected) this.render(); }
    render() { const img = this.getAttribute('img') || '', k = (this.getAttribute('age') || 'child') + '|' + (this.getAttribute('support') || 'ett') + '|' + img; if (k === this._k) return; this._k = k;
      // A scene illustration (assets/illus/*.jpg) replaces the drawn figure when the stage has one.
      this.innerHTML = img ? `<img src="${img.replace(/"/g, '&quot;')}" alt="The patient at the bedside" style="display:block; width:100%; height:100%; object-fit:contain; border-radius:4px; background:#F4EFE6;">` : svg(this.getAttribute('age') || 'child', this.getAttribute('support') || 'ett'); }
  }
  if (!customElements.get('patient-figure')) customElements.define('patient-figure', PatientFigure);
  window.PatientFigure = { svg };
})();
