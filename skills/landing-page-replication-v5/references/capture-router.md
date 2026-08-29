# When to load: Loop 0 — non-SSR targets, empty curl bodies, or 403/challenge pages
# Precondition: Target URL + writable `recon/` directory
# Output: Route chosen + capture artifacts listed in pipeline.yaml (incl. runtime.json)

# Capture Router (v5)

curl is a **fast path**, not the default for every stack. Route by fingerprint, then save more than HTML. **v5 requires runtime surface capture** for theater-class targets.

## Artifacts (always aim for these)

| Artifact | Purpose |
|----------|---------|
| `recon/headers.txt` | Framework + CDN + CSP CDNs |
| `recon/index.html` | Curl body **or** Playwright `page.content()` |
| `recon/dom.html` | Post-hydration `document.documentElement.outerHTML` when SPA/Framer |
| `recon/computed.json` | Computed styles for H1/H2/body/primary button |
| `recon/css/` | Fetched stylesheet chunks |
| `recon/screenshots/` | Density acceptance set (≥5) + `scroll-00…N` for long pages |
| `recon/assets.json` | canvases / imgs / videos — feeds Static Snapshot gate |
| `recon/offsets.json` | section tops + **maxScroll** — feeds scroll-length gate |
| `recon/runtime.json` | canvasCount, webgl, Lenis, scrollContainers — feeds Behavior |

## Fingerprint → route

| Fingerprint | Route |
|-------------|-------|
| `x-nextjs-prerender` / `/_next/` + real `<h1>` in curl | **curl fast path** + fetch CSS chunks; still run `capture-runtime.py` if interactive |
| `__next` / RSC shell but **no** real headings | Playwright wait for hydration → save `dom.html` |
| Vite / SPA (`#root` / `#app` empty of product copy) | Playwright + `networkidle` / wait for selector |
| Framer (`*.framer.*`, `data-framer`) | Playwright **required** — Framer often ships little author CSS; rely on `computed.json` |
| Webflow (`.w-` classes, `webflow.css`) | curl + fetch Webflow CSS chunks; vision for spacing |
| Astro / Nuxt with SSR content | curl fast path |
| `<canvas>` / Lenis / WebGL portfolio | Playwright **required** + `capture-runtime.py` + scroll progression shots |
| Cloudflare managed challenge (`cf-mitigated` header / `Just a moment...` title / `_cf_chl_opt`) | **Headed persistent-profile session first** (Playwright MCP with a real browser profile — cleared lovable.dev 2026-08-29 without manual solve), manual DevTools as last resort. Document as legitimate Loop 0 — not a failure. |
| Google Fonts / Typekit only (no woff2 filenames) | curl OK; `extract-tokens.py` parses families from link URLs |

## Bot management (2026 default failure mode)

Known SaaS targets often block **both** curl and default headless Chromium.
Lovable.dev evidence (2026-08-29): curl 403 from datacenter + residential IPs;
plain headless Chromium and real-Chrome-UA headless both looped on a CF managed
challenge for 75–90 s. Do not retry plain headless against such targets.

Route order when blocked:

1. **Headed persistent-profile session (preferred, semi-automated).** Playwright
   MCP (or equivalent) driving a headed Chromium with a persistent real profile.
   The CF managed challenge cleared in-session with no manual interaction, and
   the full artifact set (screenshots, dom.html, runtime, headers) was captured
   from that same session (lovable.dev, 2026-08-29). Capture the main-document
   response headers from the network log for `headers.txt`.
2. **Manual DevTools (last resort).**
   - Open the live site in a normal browser.
   - DevTools → Network: copy response headers → `headers.txt`.
   - Elements: save outerHTML of meaningful root (or copy computed styles for H1/body/button).
   - Screenshots still required — they remain the density bar.
   - Manually note runtime: canvas count, inner scroller, approx scroll height → stub `runtime.json`.
   - Note in SIGNAL.md: `Dump quality: bot-blocked; manual capture`.

Do not burn hours fighting fingerprints before escalating to route 1.

Fingerprint discipline: challenge detection must use **structural markers**
(`cf-mitigated:` header, `_cf_chl_opt`, `cdn-cgi/challenge-platform`,
`Just a moment...` title, Datadome endpoints) — never a bare word-match on
"challenge" in body copy. bolt.new and replit.com marketing copy contains the
word and produced false positives on real HTTP 200 pages (2026-08-29 wave);
a 200 with real headings should proceed to the Playwright pass.

## Computed styles (required when CSS is opaque)

In Playwright (or DevTools console):

```js
() => {
  const pick = (sel) => {
    const el = document.querySelector(sel);
    if (!el) return null;
    const s = getComputedStyle(el);
    return {
      fontFamily: s.fontFamily,
      fontSize: s.fontSize,
      fontWeight: s.fontWeight,
      letterSpacing: s.letterSpacing,
      lineHeight: s.lineHeight,
      color: s.color,
      backgroundColor: s.backgroundColor,
    };
  };
  return {
    h1: pick("h1"),
    h2: pick("h2"),
    body: pick("body"),
    button: pick("a[href*='signup'], a[href*='start'], button, .btn, [class*='button']"),
  };
}
```

Save as `recon/computed.json`. Feed TSS gate via `audit.py --typescale` (live) or compare manually in SIGNAL.md.

## Runtime probe (required for theater-class)

```bash
python3 scripts/capture-runtime.py --url https://target.com --out recon/runtime.json
```

Minimal contract:

```json
{
  "canvasCount": 2,
  "webgl": true,
  "hasLenis": true,
  "maxScroll": 12319,
  "scrollContainers": [{ "className": "lenis", "maxScroll": 12319 }],
  "flags": { "WEBGL_THEATER": true, "INNER_SCROLLER": true, "LENIS": true }
}
```

If `WEBGL_THEATER` → tag SIGNAL + fill Interaction Contract rows before Skeleton.

## Screenshots (always)

1. Full-page scroll
2. Hero (product collage / theater region)
3. Densest product-demo section
4. Dark feature band (if any)
5. Nav at top **and** mid-scroll
6. **Long pages:** `scroll-00` … `scroll-05` at 0/20/40/60/80/100% (tunnel evidence)

These images are Loop 3 acceptance criteria; scroll progression is Loop 5 evidence.

### Vision analysis of the shot set

Screenshots have three consumers: the ≥5 validation gate, agent vision during
signal extraction, and Loop 3/5 acceptance evidence. When a signal sheet needs
systematic visual census (palette histogram, radius/shadow measurement, density
counting, layout classification) that is expensive to do ad hoc, batch the shot
set through a VLM instead of eyeballing frame by frame. Working option in this
workspace: `bailian-cli` on `liz-tencent` (Singapore) calling Qwen-VL
(cost-effective); if remote throughput is too slow, run the same CLI locally.
Record the VLM-derived numbers in SIGNAL.md with a `VLM census:` evidence tag so
they remain auditable, and keep raw screenshots in `recon/` as the ground truth.

## CLI

```bash
python3 scripts/capture.py --url https://target.com --out recon/
# Force Playwright:
python3 scripts/capture.py --url https://target.com --out recon/ --engine playwright
# Skip screenshots (CI / headless missing):
python3 scripts/capture.py --url https://target.com --out recon/ --no-shots
# Runtime only:
python3 scripts/capture-runtime.py --url https://target.com --out recon/runtime.json
```
