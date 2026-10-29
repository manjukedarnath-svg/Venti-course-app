    // ── free-text orders: read a typed answer as one of the stage's options (keywords, synonyms, numbers), or 'Other' ──
    const VC_SYN = [
      [/high[\s-]*flow|\bh+fnc\w*|\bhfno\b|optiflow|nasal high|\bhfo2\b/g, ' highflow '],
      [/\bbi[\s-]*pap\b|bi[\s-]*level|\bnippv\b|non[\s-]*invasive|\bniv\b|\bnppv\b/g, ' niv '],
      [/\bcpap\b/g, ' niv cpap '],
      [/\bhfov\b|oscillat\w*|\bhfo\b/g, ' hfov '],
      [/intubat\w*|endotracheal|\bett?\b|\bintubation\b|\bmech\w* vent\w*/g, ' intubate '],
      [/extubat\w*/g, ' extubate '],
      [/salbutamol|albuterol|nebuli[sz]\w*|\bnebs?\b|bronchodilat\w*|ipratropium/g, ' neb '],
      [/paraly[sz]\w*|neuromuscular|\bnmb\w*|blocker|vecuronium|atracurium|cisatracurium/g, ' blocker '],
      [/rocuronium|\broc\b/g, ' rocuronium blocker '],
      [/sux\w*|succinyl\w*/g, ' suxamethonium '],
      [/sedat\w*|fentanyl|morphine|dexmed\w*/g, ' sedation '],
      [/\bprone\w*|proning/g, ' prone '],
      [/nitric|\bino\b/g, ' nitric '],
      [/\becmo\b|\becls\b|extracorporeal/g, ' ecmo '],
      [/transfus\w*|\bprbc\b|packed (red )?cells|\bblood\b/g, ' transfuse '],
      [/bicarb\w*|nahco3|\bsoda bicarb\w*/g, ' bicarbonate '],
      [/permissive|accept\w*|tolerat\w*/g, ' accept '],
      [/disconnect\w*|off the vent\w*|let (it|him|the chest) (out|empty|exhale)/g, ' disconnect '],
      [/needle\w*|thoracocent\w*|thoracost\w*|decompress\w*/g, ' needle '],
      [/fluid bolus|\bbolus\w*|\bnormal saline\b|\bns\b|\brl\b/g, ' bolus '],
      [/increase\w*|rais\w*|higher|\bup\b|more|↑/g, ' up '],
      [/decreas\w*|reduc\w*|lower\w*|\bdown\b|less|wean\w*|↓/g, ' down '],
      [/fio2|fio₂|\boxygen\b|\bo2\b/g, ' fio2 '],
      [/respiratory rate|\brr\b|\brate\b|frequency|breaths? (per|a) min\w*/g, ' rate '],
      [/tidal volume|\bvt\b|\btv\b/g, ' vt '],
      [/inspiratory time|\bti\b|i\s*:\s*e|\bie ratio\b|longer insp\w*/g, ' ti '],
      [/expirat\w*|exhal\w*/g, ' expiration '],
      [/steroid\w*|methylpred\w*|dexameth\w*|hydrocort\w*/g, ' steroid '],
      [/\bivig\b|immunoglob\w*/g, ' ivig '],
      [/\bgas\b|\babg\b|\bvbg\b|blood gas/g, ' gas '],
      [/\bmask\b|\bnrm\b|non[\s-]*rebreath\w*/g, ' mask '],
      [/\bzero\b|\bnil\b/g, ' 0 '],
      [/fail\w*|ceiling|\bplan\b|time[\s-]*limit/g, ' plan ']
    ];
    const VC_STOP = new Set('a an the to and or of with for in on at by then now her his she he it is be give start set do i would we will go use try put just my our this that first after before as so from into than more less ml kg cmh2o cm h2o mmhg min minute minutes s sec seconds per hour hours h about'.split(' '));
    const VC_NEG = new Set(['no', 'not', 'avoid', 'dont', "don't", 'without', 'never', 'stop']);
    const VC_PAR = new Set(['peep', 'fio2', 'rate', 'vt', 'ti', 'ps', 'pc', 'pinsp', 'pip', 'cpap', 'epap', 'ipap', 'hb', 'spo2', 'ph']);
    const vcToks = t => { let x = ' ' + String(t || '').toLowerCase().replace(/₂/g, '2').replace(/–|—/g, '-') + ' ';
      VC_SYN.forEach(([re, w]) => { x = x.replace(re, w); });
      const raw = x.replace(/[^a-z0-9.%'\s-]/g, ' ').split(/[\s-]+/).filter(Boolean), out = [];
      for (let i = 0; i < raw.length; i++) { const w = raw[i].replace(/^\.+|\.+$/g, '');
        if (!w || VC_STOP.has(w)) continue;
        if (VC_NEG.has(w)) { i++; continue; }  // "no intubation": drop the next word
        if (w === 'if' || w === 'unless') { out.push('plan'); i += 2; continue; }  // "intubate if worse": a plan, not the order
        out.push(w.replace(/%$/, '')); }
      // a number belongs to the setting just before it: "PEEP 12" and "FiO2 100" are different from "VT 100"
      for (let i = 0; i < out.length; i++) if (/^\d/.test(out[i])) { const p = out[i - 1] && !/^\d/.test(out[i - 1]) && out[i - 1] !== 'up' && out[i - 1] !== 'down' ? out[i - 1] : out[i - 2];
        if (p && VC_PAR.has(p)) out[i] = p + '=' + out[i]; else if (out[i + 1] && VC_PAR.has(out[i + 1])) out[i] = out[i + 1] + '=' + out[i]; }
      return out; };
    function vcMatch(text, match) {
      if (!match || !text) return null;
      const opt = match.map(([L, short, long]) => { const a = new Set(vcToks(short)), b = new Set(vcToks(long)); return { L, a, b }; });
      const df = {}; opt.forEach(o => new Set([...o.a, ...o.b]).forEach(t => { df[t] = (df[t] || 0) + 1; }));
      const words = new Set(vcToks(text)); if (!words.size) return null;
      const sc = opt.map(o => { let s = 0; words.forEach(w => { const idf = 1 / (df[w] || 1), num = /\d/.test(w) ? 1.5 : 1;
        if (o.a.has(w)) s += idf * num; else if (o.b.has(w)) s += 0.5 * idf * num; }); return { L: o.L, s }; }).sort((x, y) => y.s - x.s);
      return sc[0].s >= 0.5 && sc[0].s - (sc[1] ? sc[1].s : 0) >= 0.2 ? sc[0].L : 'Other';
    }
    // a free-text stage: count the typed answers as options, so every percentage and severity bar works as for tapped answers
    function vcFixCounts(s, j) {
      const sec = s && (s.closest ? s.closest('[data-match]') || s : s); let m = null;
      try { m = JSON.parse((sec && sec.getAttribute && sec.getAttribute('data-match')) || 'null'); } catch (x) {}
      if (!m || !j || !j.texts) return j;
      const c = {}, by = {}; j.texts.forEach(t => { const L = vcMatch(t.t, m) || 'Other'; c[L] = (c[L] || 0) + t.n; (by[L] = by[L] || []).push(t); });
      j.counts = c; j.bundles = by; return j;
    }
