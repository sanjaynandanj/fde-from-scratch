# Frontend in the Field: One HTML File, No Build Step

**Phase 2 · Lesson 03 · ~1.5h**

## PROBLEM

Week two at a mid-sized insurer. The FDE has a working API — CSV in, JSON out, running as a stdlib `http.server` on his laptop. The customer wants to see it. He fires up a Next.js scaffold because that's what he uses at home. Two hours later npm has downloaded 1,300 packages, the customer's proxy is blocking half of them, the corporate laptop's antivirus is quarantining the rest, and the demo is in an hour. He ends up screen-sharing his terminal, reading JSON out loud. The champion is polite. The champion does not come back the next week.

The colleague sitting next to him on the flight home opens her laptop, writes 180 lines in `dashboard.html` — one file, no build, opens in any browser, hits the API — and mails it to the champion by the time they land. The next Monday the champion has forwarded it to three other people in the company.

## INTUITION

Frontend at customer sites is a different sport. You are not optimizing for developer ergonomics, code splitting, or hot reload. You are optimizing for: *survives the customer's network, opens without a toolchain, is legible to the next engineer, and can be modified in the meeting.*

The design space:

- **One HTML file with inline CSS and JS.** Ships as an attachment. Opens with double-click. Zero dependencies. The default choice.
- **HTML + one CDN import (Chart.js, HTMX, Alpine).** Fine on the open internet. Blocked on 40% of enterprise networks. Only use when you've confirmed egress works.
- **Static site generator output (Hugo, Astro).** Great for docs, overkill for pilot dashboards.
- **SPA framework (React, Vue, Svelte).** Wrong tool. The build step is your enemy. Reserve for post-pilot when a real frontend team owns it.

Constraints you learn to design around: the customer's browser is probably last-gen Chrome or Edge, sometimes locked to a corporate version. The customer's proxy strips things. The customer's IT team must be able to open the file with no elevated permissions. The customer's champion will copy-paste your file to a colleague — it must survive that.

The one-HTML-file dashboard is a specific idiom: semantic HTML, a `<style>` block with maybe 40 lines of CSS (custom properties for theme, grid for layout), and a `<script>` block that fetches your API, renders tables and simple SVG charts, and re-renders on button click. No framework. No build.

## BUILD IT

The template. Save as `dashboard.html`, open with double-click, works.

```html
<!doctype html>
<meta charset="utf-8">
<title>Pilot Dashboard</title>
<style>
  :root { --fg:#111; --muted:#666; --bg:#fff; --accent:#0a5; --line:#eee; }
  body { font: 15px/1.5 system-ui, sans-serif; color:var(--fg); background:var(--bg);
         margin:0; padding:24px; max-width:1100px; }
  h1 { margin:0 0 4px; }
  .sub { color:var(--muted); margin-bottom:24px; }
  .cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
           gap:12px; margin-bottom:24px; }
  .card { border:1px solid var(--line); border-radius:8px; padding:16px; }
  .card .n { font-size:28px; font-weight:600; }
  .card .l { color:var(--muted); font-size:12px; text-transform:uppercase; }
  table { width:100%; border-collapse:collapse; }
  th, td { text-align:left; padding:8px 6px; border-bottom:1px solid var(--line); }
  th { color:var(--muted); font-weight:500; font-size:12px; text-transform:uppercase; }
  button { background:var(--accent); color:white; border:0; padding:8px 14px;
           border-radius:6px; cursor:pointer; }
</style>
<h1>Recovered Revenue — Pilot</h1>
<div class="sub" id="stamp">Loading&hellip;</div>
<div class="cards" id="cards"></div>
<button onclick="load()">Refresh</button>
<h2>Flagged Invoices</h2>
<table><thead><tr><th>ID</th><th>Vendor</th><th>Amount</th><th>Reason</th></tr>
  </thead><tbody id="rows"></tbody></table>
<script>
async function load() {
  const r = await fetch('/api/summary');
  const d = await r.json();
  document.getElementById('stamp').textContent = 'As of ' + d.asof;
  document.getElementById('cards').innerHTML = d.cards
    .map(c => `<div class="card"><div class="n">${c.n}</div>
               <div class="l">${c.l}</div></div>`).join('');
  document.getElementById('rows').innerHTML = d.rows
    .map(r => `<tr><td>${r.id}</td><td>${r.vendor}</td>
               <td>$${r.amount.toLocaleString()}</td><td>${r.reason}</td></tr>`).join('');
}
load();
</script>
```

That's the whole file. About 50 lines, no dependencies, opens in every browser made this decade. Grow it by adding sections, not tooling.

For charts: hand-rolled `<svg>` with `<rect>` and `<line>` beats any library at pilot scale. Ten lines of code, no CDN, no debate about which chart lib to standardize on.

## FIELD NOTES

- Test your file by double-clicking it from a fresh directory before you send it. `file://` behaves differently than `http://`; some `fetch()` calls will need CORS or relative paths.
- If the customer opens it and sees a blank page, it's almost always their proxy blocking your API or a CSP header from their intranet if they hosted it. Print something visible on load ("Loading...") so blank means *your* JS didn't fire.
- Everyone forgets: version the file. `dashboard-v3.html` in the email is worth more than clever cache-busting.
- The champion will screenshot your dashboard and paste it into a deck. Design for that. Big numbers, clear labels, no dark-mode-only palette.

## INTERVIEW ANGLE

Interviewers watch for candidates who can name the trade-off between developer comfort and field reality.

Sample questions:

1. "You need a dashboard for a customer whose IT team blocks npm and disallows external CDNs. Walk me through your approach." (Testing: default to one HTML file, inline everything, no CDNs.)
2. "Why not just use React for a pilot dashboard?" (Testing: build step, toolchain fragility, the customer can't modify or forward it, overkill for the surface area.)
3. "How do you handle charts without a chart library?" (Testing: SVG primitives are enough at pilot scale; the trade is code volume for zero dependencies.)

## DRILL

Take the template above. Extend it with: (1) a search box that filters the table client-side, (2) a bar chart of amount-by-vendor rendered as inline SVG (no library), (3) a "Copy as CSV" button that copies the visible rows to the clipboard. Keep it to one file. Then open it via `file://` and via a local server — reconcile any difference. Save the result as your starter template for the next pilot.
