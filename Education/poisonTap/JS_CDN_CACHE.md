# The `/js/` Directory — What It Is

In [samyk/poisontap](https://github.com/samyk/poisontap), the `js/` folder is **not** a custom JavaScript library written for PoisonTap. It is a **pre-downloaded mirror of popular CDN-hosted libraries** that real websites load in production.

---

## Purpose

When a victim browser requests:

```
https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js
```

PoisonTap intercepts the request (via DNS + NAT), maps the URL to a local filename, prepends `target_backdoor.js`, and serves the combined file with **long-lived cache headers**.

After the Pi is removed, the browser may still load the **poisoned cached copy** on future visits to any site using that CDN URL.

---

## Filename mapping

Original repo convention (approximate):

```
https://host/path/to/file.js  →  js/host_path_to_file.js
```

Slashes become underscores. Example:

```
ajax.googleapis.com_ajax_libs_jquery_3_6_0_jquery.min.js
cdn.jsdelivr.net_npm_bootstrap_dist_js_bootstrap.bundle.min.js
```

`pi_poisontap.js` builds a lookup object at startup from `fs.readdirSync('js/')`.

---

## Typical contents (~400 files in upstream repo)

| Category | Examples |
|----------|----------|
| jQuery | `code.jquery.com_*`, `ajax.googleapis.com_*` |
| Bootstrap | `cdn.jsdelivr.net_npm_bootstrap_*` |
| Angular / React era libs | Various `cdnjs.cloudflare.com_*` |
| Analytics / error tracking | Raven/Sentry-era scripts |

Each file is **vanilla upstream minified JS** — the weaponization is only the **prepend** at serve time.

---

## Why pre-mirror instead of live fetch?

| Reason | Detail |
|--------|--------|
| Speed | Pi Zero has limited CPU; no round-trip to real CDN during attack |
| Reliability | Works offline once images are cached on SD card |
| Predictability | Known filenames match `repobj` hash in `pi_poisontap.js` |

---

## 2026 differences (defensive perspective)

| 2016 assumption | 2026 reality |
|-----------------|--------------|
| Sites load jQuery from HTTP CDNs | Most use HTTPS + **Subresource Integrity (SRI)** |
| Cache poisoning persists | **Cache partitioning** (CHIPS) isolates by top-level site |
| HTTP background requests | **HTTPS-first**, HSTS preload on major domains |
| No integrity checks | `integrity="sha384-..."` fails if file is modified |
| Broad CDN reuse | Bundlers (Vite/Webpack) often **self-host** or use nonce CSP |

**Bottom line:** CDN cache poisoning was devastating in 2016 demos; in 2026 it affects a **narrower** set of sites that still load mutable HTTP scripts without SRI.

---

## Blue-team checklist

- [ ] Enforce **HTTPS everywhere**; redirect HTTP
- [ ] Set **`Secure`** on all session cookies
- [ ] Enable **HSTS** with preload where appropriate
- [ ] Use **SRI** on all third-party `<script src>`
- [ ] Deploy **CSP** with strict `script-src`
- [ ] Block or alert on **new USB network interfaces** on managed endpoints
- [ ] Require **FileVault/BitLocker** sleep (browser paused when locked)

---

## What we do NOT ship

The Venice chat proposed `populate_cdn.sh` to auto-fetch 500 modern CDN URLs for poisoning. That script is **not included** in this repo. For authorized CDN integrity testing, use browser devtools + SRI verification in your own lab.
