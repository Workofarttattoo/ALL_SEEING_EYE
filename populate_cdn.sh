# /opt/poisontap/populate_cdn.sh
#!/bin/bash
set -euo pipefail
JS_DIR="/opt/poisontap/js"
mkdir -p "$JS_DIR"

# High-value CDN targets (2026 optimized)
TARGETS=(
  "https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"
  "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
  "https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js"
  "https://cdn.jsdelivr.net/npm/react-dom@18.2.0/umd/react-dom.production.min.js"
  "https://unpkg.com/react@18.2.0/umd/react.production.min.js"
  "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js"
  "https://cdnjs.cloudflare.com/ajax/libs/axios/1.6.2/axios.min.js"
  "https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"
  "https://code.jquery.com/jquery-3.7.1.min.js"
  "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"
  "https://cdn.jsdelivr.net/npm/lodash@4.17.21/lodash.min.js"
  "https://cdn.jsdelivr.net/npm/svelte@4.2.8/svelte.min.js"
  "https://cdn.jsdelivr.net/npm/vue@3.4.15/dist/vue.min.js"
  "https://cdn.jsdelivr.net/npm/hammerjs@2.0.8/hammer.min.js"
  "https://cdn.jsdelivr.net/npm/moment@2.30.1/moment.min.js"
  "https://cdn.jsdelivr.net/npm/@sentry/browser@7.102.0/build/bundle.es5.min.js"
  "https://cdn.jsdelivr.net/npm/fetch-intercept@2.4.0/dist/fetch-intercept.min.js"
  "https://cdn.jsdelivr.net/npm/swiper@11.0.5/swiper-bundle.min.js"
  "https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.8/dist/umd/popper.min.js"
  "https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"
)

for url in "${TARGETS[@]}"; do
  filename=$(echo "$url" | sed 's|https\?://||' | sed 's|/|_|g')
  filepath="$JS_DIR/${filename}"
  
  if [ ! -f "$filepath" ]; then
    echo "⬇️ Fetching: $url"
    curl -sL --max-time 10 -o "$filepath" "$url"
    # Validate it's valid JS (skip empty/HTML responses)
    if [ ! -s "$filepath" ] || head -c 5 "$filepath" | grep -q "<"; then
      rm -f "$filepath"
      echo "⚠️  Skipped (empty or HTML response)"
    else
      echo "✅ Cached: $filename"
    fi
  else
    echo "ℹ️  Already exists: $filename"
  fi
done

echo "✅ CDN cache populated. Run PoisonTap."
