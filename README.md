# 🏟️ PulseArena AI
### A GenAI Operational Intelligence Mesh for FIFA World Cup 2026 Stadiums

> Built for: *Build a GenAI-enabled solution that enhances stadium operations and the overall tournament experience for fans, organisers, volunteers, and venue staff.*

**Live stack:** static HTML/CSS/JS site + a Netlify Function for the Claude API call. No build step, no database, deploys straight from this repo.

---

## 1. The Problem

A FIFA World Cup 2026 match day is really **four different crises happening at once**, seen through four different lenses:

| Persona | What breaks on a bad day |
|---|---|
| 🧍 **Fans** | Get lost, can't find their gate/seat, don't speak the local language, miss kickoff in queues |
| 🎽 **Volunteers** | React to crowd surges *after* they've already formed, no shared situational picture |
| 🧑‍🦽 **Accessibility-needs fans** | Instructions aren't adapted to their needs; last-minute seating issues go unresolved |
| 🚌 **Transport/Sustainability teams** | Shuttle bunching, emissions spikes, no live feedback loop between fan flow and transit dispatch |
| 🎛️ **Ops/Venue staff** | Drowning in five different dashboards with no single narrative of "what's actually happening right now" |

Almost every hackathon submission for this theme solves **one** of these with a chatbot. Judges have seen a dozen "AI stadium assistant" bots. That's the gap PulseArena AI is built to close.

## 2. The Idea

PulseArena AI is not a single chatbot — it's a **mesh of five specialised GenAI agents** that all read and write to one shared, live **Stadium Context Graph** (gate queue lengths, weather, transit status, incident reports, accessibility requests). Because every agent shares the same live picture of the stadium, their outputs stay consistent with each other — the volunteer's redirect instruction, the fan's navigation answer, and the control room briefing are all telling the *same* story, just translated for a different audience.

```
                     ┌─────────────────────────────┐
                     │   Stadium Context Graph      │
                     │  (live simulated telemetry)  │
                     └───────────────┬───────────────┘
                                     │
        ┌──────────────┬────────────┼────────────┬──────────────┐
        ▼              ▼            ▼            ▼              ▼
   Wayfinder      Crowd Marshal  AccessAI     GreenRoute    Ops Commander
   (fans)         (volunteers)   Companion    (transport &   (fuses all 4 into
   navigation,    surge          (accessible  sustainability) one control-room
   multilingual   prediction &   instructions, dynamic      situation report)
   Q&A            redirects      seating help  shuttle plans)
```

| Agent | Audience | What it does with GenAI |
|---|---|---|
| **Wayfinder** | Fans | Multilingual natural-language navigation ("Where's the nearest accessible restroom near Gate C?"), grounded in live gate/queue data |
| **Crowd Marshal** | Volunteers & organisers | Turns raw queue-length telemetry into plain-language redirect directives *before* a surge becomes a bottleneck |
| **AccessAI Companion** | Accessibility-needs fans & staff | Converts any instruction into simplified, calm phrasing and proposes concrete accommodations |
| **GreenRoute** | Transport & sustainability teams | Recommends the lowest-emission shuttle/transit combination for current demand and generates a plain-English eco-impact summary |
| **Ops Commander** | Venue control room | Fuses the outputs of the other four agents into one live "Situation Report" |

## 3. Tech Stack

- **Plain HTML / CSS / JavaScript (ES modules)** for the frontend — no framework, no build step, no bundler
- **Netlify Functions** (Node 18+, using native `fetch`) — the only place the Claude API key ever touches, keeping it out of the browser entirely
- **Anthropic Claude API** (`claude-sonnet-4-6`) — the GenAI layer, with an automatic per-agent fallback if no key is configured

## 4. Project Structure

```
pulsearena-ai/
├── index.html                # the whole dashboard, one page, five tabs
├── style.css
├── app.js                    # wires up tabs, buttons, and the agents
├── core/
│   ├── contextGraph.js       # simulated live stadium telemetry (seeded)
│   ├── genaiClient.js        # calls the Netlify function, falls back client-side
│   └── i18n.js
├── agents/
│   ├── wayfinder.js
│   ├── crowdMarshal.js
│   ├── accessCompanion.js
│   ├── greenRoute.js
│   └── opsCommander.js
├── data/
│   ├── gates.json
│   ├── transit_routes.json
│   └── venues.json
├── netlify/
│   └── functions/
│       └── generate.js       # the only file that ever sees ANTHROPIC_API_KEY
├── netlify.toml               # publish dir, functions dir, /api/* redirect
├── tests/
│   └── contextGraph.test.js  # node --test, runs fully offline
├── docs/
│   ├── ARCHITECTURE.md
│   └── PITCH.md
├── package.json
├── .env.example
├── CONTRIBUTING.md
└── LICENSE
```

## 5. Deploying to Netlify (the part that actually matters)

**Option A — one click, no local setup:**

1. Push this repo to your own GitHub account (or fork it).
2. Go to [app.netlify.com](https://app.netlify.com) → **Add new site** → **Import an existing project** → connect your GitHub repo.
3. Netlify will read `netlify.toml` automatically:
   - Publish directory: `.` (the repo root — it's a static site, no build needed)
   - Functions directory: `netlify/functions`
4. Click **Deploy site**. That's it — no build command to configure, `netlify.toml` already has it (`echo` no-op).
5. *(Optional, but recommended)* To turn on real GenAI responses: **Site configuration → Environment variables → Add a variable**
   - Key: `ANTHROPIC_API_KEY`
   - Value: your Anthropic API key
   - Redeploy the site (Netlify → Deploys → Trigger deploy) for the env var to take effect.

Without step 5, the site is still fully functional — every agent uses its offline fallback response instead of a live Claude-generated one, and the sidebar tells you which mode you're in.

**Option B — Netlify CLI, if you want to test locally first:**

```bash
npm install -g netlify-cli
netlify dev
```

This runs the static site *and* the function locally at `http://localhost:8888`, so you can test the full flow (including a real API key, if you export `ANTHROPIC_API_KEY` in your shell first) before pushing.

**Why the earlier version didn't deploy:** Netlify only serves static files and short-lived serverless functions — it can't run a persistent Python process like Streamlit needs. This version is a genuine static site with a Netlify Function doing the one thing that needs a server (calling Claude with a secret key), so it fits the platform properly.

## 6. Running the Tests

```bash
npm test
```

Runs entirely offline with Node's built-in test runner (`node --test`) — no API key, no network, no Netlify CLI required. This is also what runs automatically in CI on every push (`.github/workflows/tests.yml`).

## 7. Local Preview Without Netlify CLI

Since it's a static site, any local web server works — you just can't open `index.html` by double-clicking it (the browser will block the JSON `fetch` calls under the `file://` protocol). For example:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

The dashboard will load and the simulation will run — the GenAI calls will use the offline fallback since there's no Netlify Function running behind a plain static server. Use `netlify dev` (Option B above) if you want the full live-API flow locally.

## 8. What's Real vs. What's Simulated (being upfront about it)

- **Simulated:** all live telemetry — gate queues, transit load, weather, incidents. There's no real stadium sensor feed for a hackathon, so `core/contextGraph.js` runs a seeded random walk instead. It's designed so a real feed could be swapped in later without touching any agent code.
- **Real:** the GenAI layer. Every agent genuinely calls the Claude API through the Netlify Function when a key is configured, with prompts grounded in the (simulated) live data.
- **Real:** the offline fallback logic. This isn't a placebo — it's a fully separate, hand-written response path per agent, tested in CI with no API key at all.

## 9. Roadmap Beyond the Hackathon

- Replace simulated `contextGraph.js` with real gate-turnstile / CCTV-derived crowd density feeds
- Add a real-time voice interface (Whisper + Claude) for the Wayfinder and AccessAI agents
- Integrate live transit-provider APIs for GreenRoute
- Push Ops Commander digests to a real control-room Slack/Teams channel via webhook

## 10. License

MIT — see [LICENSE](LICENSE).

## 11. Team

Built solo by Pranjal for the FIFA World Cup 2026 GenAI Stadium Operations Hackathon.
