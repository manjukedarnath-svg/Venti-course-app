const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const PORT = process.env.PORT || 3000;
const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon', '.json': 'application/json', '.mp3': 'audio/mpeg', '.wav': 'audio/wav',
  '.woff2': 'font/woff2', '.webmanifest': 'application/manifest+json', '.mp4': 'video/mp4', '.webm': 'video/webm', '.md': 'text/plain; charset=utf-8'
};
const CSP = "default-src * data: blob: 'unsafe-inline' 'unsafe-eval'; script-src * data: blob: 'unsafe-inline' 'unsafe-eval'; worker-src * blob: data:; img-src * data: blob:; media-src * data: blob:; font-src * data:; style-src * 'unsafe-inline'; connect-src * data: blob:";

const DATA = fs.existsSync('/data') ? '/data' : ROOT;
const DB = path.join(DATA, 'users.json');
const hash = s => { let x = 5381; for (const c of s) x = ((x << 5) + x + c.charCodeAt(0)) | 0; return (x >>> 0).toString(36); };
let users = {};
try { users = JSON.parse(fs.readFileSync(DB, 'utf8')); } catch (e) { users = {}; }
users.admin = { joined: Date.now(), ...(users.admin || {}), e: 'ventcourse2026@gmail.com', ph: hash(process.env.ADMIN_PASSWORD || 'VentAdmin@2026'), role: 'admin' };
const save = () => { fs.writeFileSync(DB + '.tmp', JSON.stringify(users)); fs.renameSync(DB + '.tmp', DB); };
save();
const lessonsOf = (p) => { if (!p) return 0; const q = p.q && typeof p.q === 'object' ? Object.keys(p.q).filter(k => !k.startsWith('02:')).length : 0; return q + (p.mq ? 6 : p.mv ? 1 : 0); };
const pub = (u) => ({ e: users[u].e, role: users[u].role, joined: users[u].joined, last: users[u].last, lessons: lessonsOf(users[u].prog) });
const mergeProg = (a, b) => { a = a && typeof a === 'object' ? a : {}; b = b && typeof b === 'object' ? b : {}; const o = { ...a };
  for (const k of ['q', 'solved', 'finished']) if (b[k] && typeof b[k] === 'object') o[k] = { ...(a[k] || {}), ...b[k] };
  if (b.mq) o.mq = String(b.mq).slice(0, 4); if (b.mv) o.mv = true; return o; };
const okUser = (b) => b && typeof b.u === 'string' && users[b.u] && users[b.u].ph === b.ph;
const isAdmin = (b) => okUser(b) && users[b.u].role === 'admin';
const admins = () => Object.values(users).filter(v => v.role === 'admin').length;
// Live sessions: a talk deck creates a room, sets the current question; candidates answer from the app.
// Rooms are saved to disk so a restart does not drop a session. A fixed-code room (CP1, LTV …) is never reset by
// opening the deck again: every copy of the deck (laptop, second tab, Present bundle) gets the same presenter key.
const ROOMS = path.join(DATA, 'rooms.json');
let rooms = {};
try { rooms = JSON.parse(fs.readFileSync(ROOMS, 'utf8')) || {}; } catch (e) { rooms = {}; }
let roomsDirty = null;
const saveRooms = () => { if (roomsDirty) return; roomsDirty = setTimeout(() => { roomsDirty = null;
  try { fs.writeFileSync(ROOMS + '.tmp', JSON.stringify(rooms)); fs.renameSync(ROOMS + '.tmp', ROOMS); } catch (e) {} }, 800); };
const sweepRooms = () => { const t = Date.now(); for (const k in rooms) if (t - rooms[k].at > 864e5) { delete rooms[k]; saveRooms(); } };
const who = (b) => okUser(b) ? 'u:' + b.u : 'g:' + String(b.d || '').slice(0, 40);
const phonesIn = (r) => { const t = Date.now(); return Object.values(r.seen || {}).filter(x => t - x < 3e4).length; };
function live(route, b) {
  sweepRooms();
  const code0 = String(b.room || '').toUpperCase();
  const r = rooms[code0];
  switch (route) {
    case 'create': {
      const want = String(b.code || '').toUpperCase();
      if (/^[A-Z][A-Z0-9]{2,5}$/.test(want) && rooms[want] && !b.reset && Date.now() - rooms[want].at < 4 * 36e5) {  // reopened deck within 4 h: same room, same key, answers kept
        rooms[want].at = Date.now(); saveRooms();
        return [200, { room: want, key: rooms[want].key, cur: rooms[want].cur }];
      }
      let code; if (/^[A-Z][A-Z0-9]{2,5}$/.test(want)) code = want; else do { code = String(1000 + Math.floor(Math.random() * 9000)); } while (rooms[code]);
      const key = Math.random().toString(36).slice(2) + Math.random().toString(36).slice(2);
      rooms[code] = { key, cur: null, at: Date.now(), opened: {}, ans: {}, seen: {} };
      saveRooms();
      return [200, { room: code, key }];
    }
    case 'set': {
      if (!r) return [404, { error: 'no room' }];
      if (r.key !== b.key) return [403, { error: 'no' }];
      const cur = typeof b.q === 'string' && b.q.length < 40 ? b.q : null;
      r.at = Date.now();
      if (cur !== r.cur || (cur && !r.opened[cur])) { r.cur = cur; if (cur) r.opened[cur] = true; saveRooms(); }
      return [200, { ok: true, phones: phonesIn(r) }];
    }
    case 'state': {
      if (!r) return [404, { error: 'no room' }];
      if (b.d) { (r.seen = r.seen || {})[String(b.d).slice(0, 40)] = Date.now(); }
      return [200, { cur: r.cur, phones: phonesIn(r) }];
    }
    case 'answer': {
      if (!r) return [404, { error: 'no room' }];
      const q = String(b.q || ''), id = who(b);
      if (!(r.opened[q] || r.opened[q.split('~')[0]]) || id.length < 3) return [400, { error: 'closed' }];
      const a = String(b.a || '').replace(/\s+/g, ' ').trim().slice(0, 80);
      if (!a) return [400, { error: 'empty' }];
      (r.ans[q] = r.ans[q] || {})[id] = a;
      if (b.d) (r.seen = r.seen || {})[String(b.d).slice(0, 40)] = Date.now();
      saveRooms();
      return [200, { ok: true }];
    }
    case 'results': {
      if (!r) return [404, { error: 'no room' }];
      const all = Object.values(r.ans[String(b.q || '')] || {}), counts = {}, texts = {};
      for (const a of all) { if (/^[A-F]$/.test(a)) counts[a] = (counts[a] || 0) + 1; const k = a.toLowerCase(); texts[k] = texts[k] || { t: a, n: 0 }; texts[k].n++; }
      return [200, { n: all.length, counts, texts: Object.values(texts).sort((x, y) => y.n - x.n).slice(0, 60), phones: phonesIn(r) }];
    }
  }
  return [404, { error: 'not found' }];
}
// Live simulation rooms (sim.html): one facilitator panel, a ventilator screen and a patient monitor share a state.
// Every change is appended to `hist` with the server's clock, so each screen computes the same patient from the same history.
const SIMS = path.join(DATA, 'sims.json');
let sims = {};
try { sims = JSON.parse(fs.readFileSync(SIMS, 'utf8')) || {}; } catch (e) { sims = {}; }
let simsDirty = null;
const saveSims = () => { if (simsDirty) return; simsDirty = setTimeout(() => { simsDirty = null;
  try { fs.writeFileSync(SIMS + '.tmp', JSON.stringify(sims)); fs.renameSync(SIMS + '.tmp', SIMS); } catch (e) {} }, 800); };
function sim(route, b) {
  const t = Date.now(); for (const k in sims) if (t - sims[k].at > 2 * 864e5) delete sims[k];
  const code = String(b.room || '').toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 8), r = sims[code];
  switch (route) {
    case 'create': {
      if (code.length < 3) return [400, { error: 'code' }];
      if (r && !b.reset) { r.at = t; return [200, { room: code, key: r.key }]; }
      const key = Math.random().toString(36).slice(2) + Math.random().toString(36).slice(2);
      sims[code] = { key, at: t, v: 1, s: { case: null, stage: 0, set: null, mods: {}, reveals: [], hist: [] } }; saveSims();
      return [200, { room: code, key }];
    }
    case 'get': {
      if (!r) return [404, { error: 'no room' }];
      if (b.v && +b.v === r.v) return [200, { same: true, v: r.v, now: t }];
      return [200, { s: r.s, v: r.v, now: t }];
    }
    case 'act': {
      if (!r) return [404, { error: 'no room' }];
      const a = b.act || {}, ctl = b.key && b.key === r.key, S = r.s;
      if (a.kind === 'set' || a.kind === 'hold') {           // the ventilator screen: settings and holds, no key needed
        if (a.kind === 'set') { S.set = a.set; S.hist.push({ at: t, kind: 'set', set: a.set }); }
        else S.hold = { type: a.type === 'exp' ? 'exp' : 'insp', at: t };
      } else if (ctl) {                                        // the facilitator: case, stage, orders, events, results, story
        const ent = { at: t, kind: String(a.kind || 'note').slice(0, 20) };
        for (const k of ['case', 'stage', 'set', 'mods', 'reveals', 'story', 'note', 'label', 'debt', 'clock']) if (a[k] !== undefined) { ent[k] = a[k]; if (k !== 'note' && k !== 'label') S[k] = a[k]; }
        if (a.kind === 'reset') { r.s = { case: a.case || null, stage: 0, set: a.set || null, mods: {}, reveals: [], hist: [{ at: t, kind: 'reset', case: a.case, set: a.set }] }; }
        else S.hist.push(ent);
      } else return [403, { error: 'no' }];
      if (r.s.hist.length > 3000) r.s.hist = r.s.hist.slice(-3000);
      r.v++; r.at = t; saveSims();
      return [200, { ok: true, v: r.v, now: t }];
    }
  }
  return [404, { error: 'not found' }];
}
function api(route, b) {
  if (route.startsWith('live/')) return live(route.slice(5), b);
  if (route.startsWith('sim/')) return sim(route.slice(4), b);
  switch (route) {
    case 'exists': return [200, { exists: !!users[String(b.u || '').trim().replace(/\s+/g, ' ').toLowerCase()] }];
    case 'register': {
      const u = String(b.u || '').trim().replace(/\s+/g, ' ').toLowerCase();
      if (u.length < 2 || u.length > 40 || typeof b.ph !== 'string' || !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(String(b.e || ''))) return [400, { error: 'bad' }];
      if (users[u]) return [409, { error: 'taken' }];
      users[u] = { e: String(b.e).toLowerCase(), ph: b.ph, role: 'student', joined: Date.now() }; save();
      return [200, { user: pub(u) }];
    }
    case 'login': return okUser(b) ? [200, { user: pub(b.u) }] : [401, { error: 'no' }];
    case 'progress': {
      if (!okUser(b)) return [401, { error: 'no' }];
      if (b.prog && typeof b.prog === 'object' && JSON.stringify(b.prog).length < 2e4) { users[b.u].prog = mergeProg(users[b.u].prog, b.prog); save(); }
      return [200, { prog: users[b.u].prog || {} }];
    }
    case 'touch': if (!okUser(b)) return [401, { error: 'no' }]; users[b.u].last = Date.now(); save(); return [200, { user: pub(b.u) }];
    case 'admin/list': { if (!isAdmin(b)) return [403, { error: 'no' }]; const o = {}; for (const k in users) o[k] = pub(k); return [200, { users: o }]; }
    case 'admin/role': {
      if (!isAdmin(b) || !users[b.target]) return [403, { error: 'no' }];
      if (b.role !== 'admin' && users[b.target].role === 'admin' && admins() <= 1) return [400, { error: 'last admin' }];
      users[b.target].role = b.role === 'admin' ? 'admin' : 'student'; save(); return [200, { ok: true }];
    }
    case 'admin/delete': {
      if (!isAdmin(b) || !users[b.target] || b.target === b.u) return [403, { error: 'no' }];
      delete users[b.target]; save(); return [200, { ok: true }];
    }
  }
  return [404, { error: 'not found' }];
}

http.createServer((req, res) => {
  if (req.url.startsWith('/api/')) {
    const cors = req.url.startsWith('/api/') ? { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'POST, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type' } : {};
    if (req.method === 'OPTIONS') { res.writeHead(204, cors); return res.end(); }
    let body = '';
    req.on('data', c => { body += c; if (body.length > 1e5) req.destroy(); });
    req.on('end', () => {
      let b = {}; try { b = JSON.parse(body || '{}'); } catch (e) {}
      const [st, out] = req.method === 'POST' ? api(req.url.slice(5).split('?')[0], b) : [405, { error: 'POST only' }];
      res.writeHead(st, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store', ...cors });
      res.end(JSON.stringify(out));
    });
    return;
  }
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (p.endsWith('/')) p += 'index.html';
  let file = path.normalize(path.join(ROOT, p));
  if (!file.startsWith(ROOT)) { res.writeHead(403); return res.end(); }
  fs.stat(file, (err, st) => {
    if (err || !st.isFile()) file = path.join(ROOT, 'index.html');
    // videos and audio: answer byte ranges (iPhone Safari will not play an mp4 without them)
    const ext = path.extname(file).toLowerCase();
    if (st && st.isFile() && /^\.(mp4|webm|mp3|m4a|mov)$/.test(ext)) {
      const size = st.size, m = /bytes=(\d*)-(\d*)/.exec(req.headers.range || '');
      const head = { 'Content-Type': TYPES[ext] || 'application/octet-stream', 'Accept-Ranges': 'bytes', 'Cache-Control': 'public, max-age=3600' };
      if (m) {
        let a = m[1] === '' ? Math.max(0, size - +m[2]) : +m[1], b = m[1] !== '' && m[2] !== '' ? Math.min(+m[2], size - 1) : size - 1;
        if (a >= size || a > b) { res.writeHead(416, { 'Content-Range': 'bytes */' + size }); return res.end(); }
        res.writeHead(206, { ...head, 'Content-Range': `bytes ${a}-${b}/${size}`, 'Content-Length': b - a + 1 });
        return fs.createReadStream(file, { start: a, end: b }).pipe(res);
      }
      res.writeHead(200, { ...head, 'Content-Length': size });
      return fs.createReadStream(file).pipe(res);
    }
    fs.readFile(file, (e, data) => {
      if (e) { res.writeHead(404); return res.end('Not found'); }
      // phones: drop the hidden (skipped) theory slides from a talk so Safari does not run out of memory
      if (/[\\/]talks[\\/][^\\/]+\.html$/.test(file) && /iPhone|iPad|iPod|Android|Mobile/i.test(req.headers['user-agent'] || '')) {
        data = Buffer.from(data.toString('utf8').replace(/<section data-deck-skip[\s\S]*?<\/section>\n?/g, '').replace(/<section ([^>]*?)data-deck-skip([^>]*)>[\s\S]*?<\/section>\n?/g, ''));
      }
      res.writeHead(200, {
        'Content-Type': TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream',
        'Content-Security-Policy': CSP,
        'Cache-Control': 'no-cache'
      });
      res.end(data);
    });
  });
}).listen(PORT, '0.0.0.0', () => console.log('VentCourse running on ' + PORT));
