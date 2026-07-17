# PulseArena AI — One-Page Pitch

## The Hook
Every FIFA World Cup 2026 match day is five different operational stories
happening at once — fan navigation, crowd surges, accessibility needs,
transport/sustainability, and control-room decision-making. Most GenAI
submissions solve one of these with a chatbot. **PulseArena AI solves all
five with a mesh of agents that share one live picture of the stadium**, so
their answers stay consistent with each other instead of contradicting one
another the way five separate tools would.

## The Problem, In One Line
Stadium ops teams don't lack data — they lack a way to turn five different
data streams into five audience-appropriate, *consistent* narratives in
real time.

## The Solution
Five specialised GenAI agents — **Wayfinder** (fans), **Crowd Marshal**
(volunteers), **AccessAI Companion** (accessibility), **GreenRoute**
(transport & sustainability), and **Ops Commander** (control room) — all
read from and reason over one shared **Stadium Context Graph**. Ops
Commander goes a step further: it doesn't re-analyse raw data, it *fuses*
the natural-language outputs of the other agents into one situation report,
the same way a real duty manager synthesises reports from field teams.

## Theme Coverage
| Brief requirement | Covered by |
|---|---|
| Navigation | Wayfinder |
| Crowd management | Crowd Marshal |
| Accessibility | AccessAI Companion |
| Transportation | GreenRoute |
| Sustainability | GreenRoute |
| Multilingual assistance | Wayfinder + AccessAI Companion |
| Operational intelligence | Ops Commander |
| Real-time decision support | Ops Commander + Crowd Marshal |

## Why It's Demo-Safe
The entire system runs with **zero required external dependencies** — no API
key, no database, no real sensor feed. A seeded simulation drives believable
live stadium telemetry, and every agent has a rule-based fallback that
activates automatically if no `ANTHROPIC_API_KEY` is set or a network call
fails. The demo cannot crash mid-pitch.

## What Makes It Different From a Typical Submission
1. **One shared state, not five silos** — consistency judges can actually
   verify by clicking through tabs.
2. **A genuine fusion agent** (Ops Commander), not just a router.
3. **Graceful degradation by design**, not an afterthought — the fallback
   path was engineered in from the start, not bolted on.
4. **Grounded generation** — every prompt embeds live structured data so the
   model can't hallucinate a gate or amenity that doesn't exist.

## Post-Hackathon Path
Swap the simulated context graph for real turnstile/CCTV/transit feeds — no
agent code changes required, because agents only depend on the graph's
public interface. Add voice I/O for Wayfinder/AccessAI. Pipe Ops Commander
digests into a real control-room channel via webhook.
