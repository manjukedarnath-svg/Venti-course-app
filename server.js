const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const PORT = process.env.PORT || 3000;
const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon', '.json': 'application/json', '.mp3': 'audio/mpeg', '.wav': 'audio/wav',
  '.woff2': 'font/woff2', '.webmanifest': 'application/manifest+json'
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
const pub = (u) => ({ e: users[u].e, role: users[u].role, joined: users[u].joined, last: users[u].last });
const okUser = (b) => b && typeof b.u === 'string' && users[b.u] && users[b.u].ph === b.ph;
const isAdmin = (b) => okUser(b) && users[b.u].role === 'admin';
const admins = () => Object.values(users).filter(v => v.role === 'admin').length;
function api(route, b) {
  switch (route) {
    case 'exists': return [200, { exists: !!users[String(b.u || '').toLowerCase()] }];
    case 'register': {
      const u = String(b.u || '').toLowerCase();
      if (!/^[a-z0-9._]{3,24}$/.test(u) || typeof b.ph !== 'string' || !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(String(b.e || ''))) return [400, { error: 'bad' }];
      if (users[u]) return [409, { error: 'taken' }];
      users[u] = { e: String(b.e).toLowerCase(), ph: b.ph, role: 'student', joined: Date.now() }; save();
      return [200, { user: pub(u) }];
    }
    case 'login': return okUser(b) ? [200, { user: pub(b.u) }] : [401, { error: 'no' }];
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
    let body = '';
    req.on('data', c => { body += c; if (body.length > 1e5) req.destroy(); });
    req.on('end', () => {
      let b = {}; try { b = JSON.parse(body || '{}'); } catch (e) {}
      const [st, out] = req.method === 'POST' ? api(req.url.slice(5).split('?')[0], b) : [405, { error: 'POST only' }];
      res.writeHead(st, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
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
