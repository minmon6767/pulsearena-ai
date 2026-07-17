# 🏟️ PulseArena AI
### A GenAI Operational Intelligence Mesh for FIFA World Cup 2026 Stadiums

> Built for: *Build a GenAI-enabled solution that enhances stadium operations and the overall tournament experience for fans, organisers, volunteers, and venue staff.*

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
| **Wayfinder** | Fans | Multilingual natural-language navigation ("Where's the nearest accessible restroom near Gate C?"), answers in the fan's own language, grounded in live gate/queue data |
| **Crowd Marshal** | Volunteers & organisers | Turns raw queue-length telemetry into plain-language redirect directives *before* a surge becomes a bottleneck |
| **AccessAI Companion** | Accessibility-needs fans & staff | Converts any instruction into simplified language / audio-friendly phrasing / sign-language gloss text and proposes real-time seat reassignment when needed |
| **GreenRoute** | Transport & sustainability teams | Recommends the lowest-emission shuttle/transit combination for current demand and generates a plain-English eco-impact summary |
| **Ops Commander** | Venue control room | Fuses the outputs of the other four agents into one live "Situation Report" — the single narrative a duty manager actually needs |

## 3. Why This Is Different (and award-worthy)

- **Shared context, not five silos.** Every agent's answer is generated from the *same* live graph, so the demo tells one coherent story end-to-end — this is what a judge remembers.
- **Covers almost the entire theme brief in one coherent system**: navigation ✅, crowd management ✅, accessibility ✅, transportation ✅, sustainability ✅, multilingual ✅, operational intelligence ✅, real-time decision support ✅ — without feeling bolted together, because of the shared graph.
- **Works with zero setup friction.** If no `ANTHROPIC_API_KEY` is present, every agent gracefully falls back to a rule-based template engine — so the app **never crashes during a live demo**, judges can run it instantly, and it upgrades automatically to full GenAI quality the moment a key is added.
- **Simulated but realistic telemetry.** `core/context_graph.py` ships with a believable, seeded random walk of gate queues, weather, transit load and incidents so the dashboard feels alive without needing real stadium sensor access.

## 4. Tech Stack

- **Python 3.10+**
- **Streamlit** — single-command demo UI, no frontend build step
- **Anthropic Claude API** (`claude-sonnet-4-6`) — the GenAI layer, with automatic offline fallback
- Pure standard-library simulation for the context graph (no external data dependency)

## 5. Project Structure

```
pulsearena-ai/
├── app.py                    # Streamlit dashboard (entry point)
├── core/
│   ├── context_graph.py      # Simulated live stadium telemetry
│   ├── claude_client.py      # GenAI wrapper + offline fallback
│   └── i18n.py               # Supported languages
├── agents/
│   ├── base_agent.py
│   ├── wayfinder.py
│   ├── crowd_marshal.py
│   ├── access_companion.py
│   ├── green_route.py
│   └── ops_commander.py
├── data/
│   ├── gates.json
│   ├── transit_routes.json
│   └── venues.json
├── tests/
│   └── test_agents.py
├── docs/
│   ├── ARCHITECTURE.md
│   └── PITCH.md
├── .github/workflows/tests.yml   # CI — runs the offline test suite on every push
├── requirements.txt
├── .env.example
├── CONTRIBUTING.md
└── LICENSE
```

There's a green "tests passing" badge you can add once this is pushed — GitHub Actions kicks off automatically off `.github/workflows/tests.yml`, no setup needed on your end.

## 6. Quickstart

```bash
git clone https://github.com/<your-username>/pulsearena-ai.git
cd pulsearena-ai
pip install -r requirements.txt

# Optional but recommended — enables real GenAI responses.
# Without this, the app still runs fully on smart rule-based fallbacks.
cp .env.example .env
# then edit .env and add: ANTHROPIC_API_KEY=sk-ant-...

streamlit run app.py
```

Open the local URL Streamlit prints (typically `http://localhost:8501`). No database, no build step, no external API is *required* to run the demo.

## 7. Running Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## 8. Roadmap Beyond the Hackathon

- Replace simulated `context_graph.py` with real gate-turnstile / CCTV-derived crowd density feeds
- Add a real-time voice interface (Whisper + Claude) for the Wayfinder and AccessAI agents
- Integrate live transit-provider APIs for GreenRoute
- Push Ops Commander digests to a real control-room Slack/Teams channel via webhook

## 9. What's Real vs. What's Simulated (being upfront about it)

Being honest about this rather than hiding it:

- **Simulated:** all live telemetry — gate queues, transit load, weather, incidents. There's no real stadium sensor feed for a hackathon, so `core/context_graph.py` runs a seeded random walk instead. It's designed so a real feed could be swapped in later without touching any agent code, but right now it's a simulation and we say so in the app itself.
- **Real:** the GenAI layer. Every agent genuinely calls the Claude API when a key is present, with prompts grounded in the (simulated) live data — nothing about the generation itself is faked.
- **Real:** the offline fallback logic. This isn't a placebo — it's a fully separate, hand-written response path per agent that we deliberately test against in CI with no API key at all.

## 10. License

MIT — see [LICENSE](LICENSE).

## 11. Team

Built solo by Pranjal for the FIFA World Cup 2026 GenAI Stadium Operations Hackathon.
