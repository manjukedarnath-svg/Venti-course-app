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
const rooms = {};
const sweepRooms = () => { const t = Date.now(); for (const k in rooms) if (t - rooms[k].at > 864e5) delete rooms[k]; };
const who = (b) => okUser(b) ? 'u:' + b.u : 'g:' + String(b.d || '').slice(0, 40);
function live(route, b) {
  sweepRooms();
  const r = rooms[String(b.room || '')] || rooms[String(b.room || '').toUpperCase()];
  switch (route) {
    case 'create': {
      // A deck may ask for a fixed code (e.g. CP1) so a printed QR code always lands in its room; asking again resets it.
      const want = String(b.code || '').toUpperCase();
      let code; if (/^[A-Z][A-Z0-9]{2,5}$/.test(want)) code = want; else do { code = String(1000 + Math.floor(Math.random() * 9000)); } while (rooms[code]);
      const key = Math.random().toString(36).slice(2) + Math.random().toString(36).slice(2);
      rooms[code] = { key, cur: null, at: Date.now(), opened: {}, ans: {} };
      return [200, { room: code, key }];
    }
    case 'set': {
      if (!r || r.key !== b.key) return [403, { error: 'no' }];
      r.cur = typeof b.q === 'string' && b.q.length < 40 ? b.q : null; r.at = Date.now();
      if (r.cur) r.opened[r.cur] = true;
      return [200, { ok: true }];
    }
    case 'state': { const rr = rooms[String(b.room || '').toUpperCase()] || r; return rr ? [200, { cur: rr.cur }] : [404, { error: 'no room' }]; }
    case 'answer': {
      if (!r) return [404, { error: 'no room' }];
      const q = String(b.q || ''), id = who(b);
      if (!(r.opened[q] || r.opened[q.split('~')[0]]) || id.length < 3) return [400, { error: 'closed' }];
      const a = String(b.a || '').replace(/\s+/g, ' ').trim().slice(0, 80);
      if (!a) return [400, { error: 'empty' }];
      (r.ans[q] = r.ans[q] || {})[id] = a;
      return [200, { ok: true }];
    }
    case 'results': {
      if (!r) return [404, { error: 'no room' }];
      const all = Object.values(r.ans[String(b.q || '')] || {}), counts = {}, texts = {};
      for (const a of all) { if (/^[A-F]$/.test(a)) counts[a] = (counts[a] || 0) + 1; const k = a.toLowerCase(); texts[k] = texts[k] || { t: a, n: 0 }; texts[k].n++; }
      return [200, { n: all.length, counts, texts: Object.values(texts).sort((x, y) => y.n - x.n).slice(0, 60) }];
    }
  }
  return [404, { error: 'not found' }];
}
function api(route, b) {
  if (route.startsWith('live/')) return live(route.slice(5), b);
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
    fs.readFile(file, (e, data) => {
      if (e) { res.writeHead(404); return res.end('Not found'); }
      res.writeHead(200, {
        'Content-Type': TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream',
        'Content-Security-Policy': CSP,
        'Cache-Control': 'no-cache'
      });
      res.end(data);
    });
  });
}).listen(PORT, '0.0.0.0', () => console.log('VentCourse running on ' + PORT));
