// Venice AI bridge — uncensored chat fallback for ALL_SEEING_EYE.
// Reads VENICE_API_KEY (or VENICE_INFERENCE_KEY) from env or a .env at repo root.
// OpenAI-compatible: swap base URL + model to point at any other backend
// (e.g. your own Hugging Face inference endpoint) without changing call sites.

const fs = require('fs');
const path = require('path');
const https = require('https');

const DEFAULT_BASE_URL = process.env.VENICE_BASE_URL || 'https://api.venice.ai/api/v1';
const DEFAULT_MODEL = process.env.VENICE_MODEL || 'venice-uncensored';
const DEFAULT_TIMEOUT_MS = 60000;

let dotenvLoaded = false;
function loadDotenvOnce() {
  if (dotenvLoaded) return;
  dotenvLoaded = true;
  const candidate = path.join(__dirname, '.env');
  if (!fs.existsSync(candidate)) return;
  for (const raw of fs.readFileSync(candidate, 'utf8').split('\n')) {
    const line = raw.trim();
    if (!line || line.startsWith('#') || !line.includes('=')) continue;
    const eq = line.indexOf('=');
    const key = line.slice(0, eq).trim();
    let value = line.slice(eq + 1).trim();
    if ((value.startsWith('"') && value.endsWith('"')) ||
        (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    if (process.env[key] === undefined) process.env[key] = value;
  }
}

function resolveKey() {
  loadDotenvOnce();
  return process.env.VENICE_API_KEY || process.env.VENICE_INFERENCE_KEY || null;
}

function ask({ prompt, system, model, temperature, maxTokens, history }) {
  return new Promise((resolve, reject) => {
    const key = resolveKey();
    if (!key) {
      return reject(new Error('VENICE_API_KEY not set (env or .env).'));
    }

    const messages = [];
    if (system) messages.push({ role: 'system', content: system });
    if (Array.isArray(history)) {
      for (const m of history) {
        if (m && m.role && typeof m.content === 'string') {
          messages.push({ role: m.role, content: m.content });
        }
      }
    }
    messages.push({ role: 'user', content: String(prompt || '') });

    const body = JSON.stringify({
      model: model || DEFAULT_MODEL,
      messages,
      ...(typeof temperature === 'number' ? { temperature } : {}),
      ...(typeof maxTokens === 'number' ? { max_tokens: maxTokens } : {}),
    });

    const base = new URL(DEFAULT_BASE_URL);
    const req = https.request({
      method: 'POST',
      hostname: base.hostname,
      port: base.port || 443,
      path: `${base.pathname.replace(/\/$/, '')}/chat/completions`,
      headers: {
        'Authorization': `Bearer ${key}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
      },
      timeout: DEFAULT_TIMEOUT_MS,
    }, (res) => {
      let chunks = '';
      res.on('data', (c) => { chunks += c; });
      res.on('end', () => {
        if (res.statusCode >= 400) {
          return reject(new Error(`Venice ${res.statusCode}: ${chunks.slice(0, 500)}`));
        }
        try {
          const json = JSON.parse(chunks);
          const text = json?.choices?.[0]?.message?.content;
          if (typeof text !== 'string') {
            return reject(new Error(`Unexpected Venice payload: ${chunks.slice(0, 300)}`));
          }
          resolve({ reply: text, raw: json });
        } catch (e) {
          reject(new Error(`Parse error: ${e.message}`));
        }
      });
    });

    req.on('timeout', () => req.destroy(new Error('Venice request timed out.')));
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

module.exports = { ask, resolveKey, DEFAULT_MODEL };
