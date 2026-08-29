# Feature Flags for Demos: One Codebase, Per-Stakeholder Views

**Phase 2 · Lesson 07 · ~1h**

## PROBLEM

Week five of a pilot at a regional health system. The FDE has three stakeholder groups to demo to this week: the CFO (wants recovered revenue), the compliance officer (wants the audit trail), and the clinical operations lead (wants patient throughput). Same underlying app. Three very different demos.

The junior FDE forks the repo three times, tweaks each branch to hide-and-show different sections, and by Wednesday afternoon has three subtly-different codebases with three subtly-different bugs. The Thursday demo to compliance shows a chart with the CFO's language on it. Nobody notices in the room. Compliance notices on the recording. Trust dents.

The senior FDE on the engagement has one branch with a `?view=compliance` query parameter and a five-line flag block at the top of `index.html`. The clinical demo is the same URL with `?view=clinical`. Nothing forks. Every stakeholder sees exactly the surface designed for them.

## INTUITION

You will show one pilot to three or four audiences per week. Each cares about a different subset of the surface. Building separate versions is the wrong axis — the app is the same, the *view* differs. Feature flags for demos are the primitive that lets one codebase serve every meeting.

The design space:

- **URL query param (`?view=cfo`).** Simplest. Bookmarkable. Shareable in an email. The FDE default.
- **Environment variable at server startup.** Fine for a single-audience deploy; awkward when you'll switch mid-day.
- **Cookie or localStorage toggle.** Sticky, but invisible — you'll forget which mode you're in and demo the wrong thing.
- **Path-based (`/cfo/`, `/compliance/`).** Feels more "product." More code to wire. Fine at week 8, overkill at week 5.
- **Full auth-based personalization.** The eventual right answer, but not a pilot problem.

The primitive is a `flags` object, read once at page load or request start, that gates sections of the UI, columns in tables, and sometimes even API endpoints. Keep the flag *names* stable; toggle the *values* per audience.

Rules to keep the pattern from collapsing:

- **One place to read flags.** A single function `getFlags()` that everyone calls. No `if (searchParams.get(...))` scattered through the code.
- **Named audiences, not booleans.** `view === 'compliance'` beats twelve booleans that could combine in surprise ways.
- **Default to the most complete view.** No flag = show everything. Absence of a flag should never break the app.
- **A `?debug=1` mode that lists which flags are on.** Ten minutes of work; saves you when you accidentally demo the wrong view.

## BUILD IT

The five-line flag block, then how to use it.

```html
<script>
  const params = new URLSearchParams(location.search);
  const flags = {
    view: params.get('view') || 'full',          // full | cfo | compliance | clinical
    seed: params.get('seed') === '1',            // use seeded demo data
    debug: params.get('debug') === '1',
  };
  if (flags.debug) console.log('DEMO FLAGS', flags);
  document.body.dataset.view = flags.view;       // enables CSS targeting
</script>

<style>
  [data-view="cfo"] .compliance-only,
  [data-view="cfo"] .clinical-only { display: none; }
  [data-view="compliance"] .cfo-only,
  [data-view="compliance"] .clinical-only { display: none; }
  [data-view="clinical"] .cfo-only,
  [data-view="clinical"] .compliance-only { display: none; }
</style>

<section class="cfo-only"> <h2>Recovered Revenue</h2> ... </section>
<section class="compliance-only"> <h2>Access Audit Trail</h2> ... </section>
<section class="clinical-only"> <h2>Throughput by Unit</h2> ... </section>
<section> <h2>Shared: Data Refresh Status</h2> ... </section>
```

Server-side flags follow the same pattern in Python:

```python
def flags_from_request(handler):
    q = urllib.parse.parse_qs(urllib.parse.urlparse(handler.path).query)
    return {
        "view": (q.get("view", ["full"])[0]),
        "seed": q.get("seed", ["0"])[0] == "1",
        "debug": q.get("debug", ["0"])[0] == "1",
    }
```

Use the same `view` name in HTML and API. When the CFO's URL loads, both the UI and the endpoints filter to the CFO's slice.

Keep a `FLAGS.md` alongside `THROWAWAY.md` — every flag, what audience it's for, and when it should be removed (when the surface is real for everyone, or when the audience-specific view becomes the default).

## FIELD NOTES

- Pre-open the correct URL on your machine before the demo starts. Never fumble with query params on a shared screen. Bookmark `pilot.local/?view=cfo` and `pilot.local/?view=compliance` in the browser's bookmark bar.
- Tell the champion what URL you're demoing. "This is the CFO view — same app, same data, just filtered to what your CFO asked about." Transparent. Feature flags are not a trick; they are a courtesy.
- Watch for combinatorial explosion. If you find yourself writing `flags.view === 'cfo' && flags.seed && !flags.debug`, stop and refactor. Named audiences should not compose.
- The `debug=1` panel is a lifesaver in customer meetings. When something looks off, one URL edit and you can see which flags are engaged.
- Remove obsolete flags weekly. Dead flags rot into confusion. `FLAGS.md` gives you the audit.

## INTERVIEW ANGLE

Interviewers probe how you handle multi-stakeholder demos without forking chaos.

Sample questions:

1. "You have three stakeholders, three different views of the same pilot, and one week. How do you structure the code?" (Testing: single codebase, flag-based views, named audiences.)
2. "Why not just build three separate apps?" (Testing: divergence risk, code duplication, the recording that shows the wrong label; and — separate apps still share business logic that will drift.)
3. "How do you avoid accidentally demoing the wrong flag combination?" (Testing: bookmarked URLs, a debug indicator, keeping flags simple and named.)

## DRILL

Take the one-HTML-file dashboard from Lesson 03. Add a `?view=` flag with three audiences: `finance`, `ops`, `exec`. Hide/show sections per audience via `data-view`. Add `?debug=1` that shows the current flags in a corner banner. Bookmark all three URLs. Then hand the file to a colleague and ask them to demo the "exec view" without telling them which URL — see if they can find it. If they can't, your flags aren't discoverable enough; fix that before the next pilot.
