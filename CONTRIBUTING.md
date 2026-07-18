# Contributing

This started as a hackathon build, but if you want to poke at it after judging's done:

1. Fork it, clone it — no `npm install` needed for the site itself, it's dependency-free vanilla JS
2. Make a branch off `main`
3. Run `npm test` before you open a PR — it should pass with zero setup (no API key, no Netlify CLI needed; the whole suite runs against the offline fallback path on purpose)
4. If you're touching the frontend, `python3 -m http.server 8000` (or any static server) is enough to preview it locally — just don't open `index.html` directly via `file://`, the `fetch()` calls for `data/*.json` will get blocked by the browser

If you're adding a new agent, the fastest way is to copy `agents/greenRoute.js` since it's the smallest complete example and rename from there — keep the same shape: read from the shared `StadiumContextGraph`, build a grounded prompt, always pass a fallback function into `generate()`.

Not accepting big architectural changes right now since this is still hackathon-stage, but bug reports and small fixes are welcome via issues/PRs.
