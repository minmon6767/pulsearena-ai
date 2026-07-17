# app.py — PulseArena AI
#
# Run with:  streamlit run app.py
#
# One dashboard, five tabs, one persona each — fan, volunteer, accessibility,
# transport, control room. All five agents pull from the same simulated
# context graph in session_state, so hitting "advance simulation" in the
# sidebar updates the story everywhere at once.

from __future__ import annotations

import pandas as pd
import streamlit as st

from agents.access_companion import AccessCompanionAgent
from agents.crowd_marshal import CrowdMarshalAgent
from agents.green_route import GreenRouteAgent
from agents.ops_commander import OpsCommanderAgent
from agents.wayfinder import WayfinderAgent
from core.claude_client import ClaudeClient
from core.context_graph import StadiumContextGraph
from core.i18n import SUPPORTED_LANGUAGES

st.set_page_config(
    page_title="PulseArena AI — FIFA World Cup 2026 Stadium Ops",
    page_icon="🏟️",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Session state / bootstrap
# ---------------------------------------------------------------------------
if "graph" not in st.session_state:
    st.session_state.graph = StadiumContextGraph.bootstrap(seed=42)

if "client" not in st.session_state:
    st.session_state.client = ClaudeClient()

graph = st.session_state.graph
client = st.session_state.client


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🏟️ PulseArena AI")
    st.caption("A GenAI Operational Intelligence Mesh for FIFA World Cup 2026 Stadiums")

    if client.live:
        st.success("GenAI: LIVE (Claude API connected)", icon="✅")
    else:
        st.warning("GenAI: Offline fallback mode — add ANTHROPIC_API_KEY to .env for live GenAI responses.", icon="⚠️")

    st.markdown("---")
    st.markdown(f"**Venue:** {graph.venue.get('venue_name', 'N/A')}")
    st.markdown(f"**Match:** {graph.venue.get('match', 'N/A')}")
    st.markdown(f"**Weather:** {graph.weather['condition']}, {graph.weather['temp_c']}°C")
    st.markdown(f"**Sim tick:** {graph.tick}")

    if st.button("⏱️ Advance Simulation (+1 min)", use_container_width=True):
        graph.advance()
        st.rerun()

    st.markdown("---")
    language = st.selectbox("🌐 Fan-facing language", list(SUPPORTED_LANGUAGES.keys()))
    st.caption("Applies to the Wayfinder and AccessAI tabs.")


st.title("🏟️ PulseArena AI")
st.caption(
    "Five specialised GenAI agents sharing one live Stadium Context Graph — "
    "one coherent operational picture, five audiences."
)

tab_fan, tab_crowd, tab_access, tab_transport, tab_ops = st.tabs(
    ["🧍 Fan — Wayfinder", "🎽 Volunteer — Crowd Marshal", "🧑‍🦽 Accessibility — AccessAI",
     "🚌 Transport — GreenRoute", "🎛️ Control Room — Ops Commander"]
)


# ---------------------------------------------------------------------------
# Tab 1 — Wayfinder (Fans)
# ---------------------------------------------------------------------------
with tab_fan:
    st.subheader("Ask Wayfinder anything about getting around the stadium")
    st.caption("Multilingual, grounded in live gate & amenity data.")

    example_qs = [
        "Where's the nearest accessible restroom?",
        "Which gate has the shortest line right now?",
        "Is there somewhere quiet I can pray before the match?",
        "Where can I refill my water bottle?",
    ]
    cols = st.columns(len(example_qs))
    picked = None
    for c, q in zip(cols, example_qs):
        if c.button(q, use_container_width=True):
            picked = q

    question = st.text_input("Or type your own question", value=picked or "")
    if st.button("Ask Wayfinder", type="primary") and question.strip():
        agent = WayfinderAgent(graph, client)
        with st.spinner("Wayfinder is checking live stadium data..."):
            result = agent.answer(question, language=language)
        st.info(result["text"])
        st.caption(f"GenAI live: {result['genai_live']}")


# ---------------------------------------------------------------------------
# Tab 2 — Crowd Marshal (Volunteers)
# ---------------------------------------------------------------------------
with tab_crowd:
    st.subheader("Live gate status & volunteer directive")

    df = pd.DataFrame(
        [
            {
                "Gate": g.name,
                "Queue Length": g.queue_len,
                "Wait (min)": g.wait_min,
                "Trend": g.trend,
                "Accessible": "✅" if g.accessible else "—",
            }
            for g in graph.gates.values()
        ]
    ).sort_values("Wait (min)", ascending=False)

    st.dataframe(df, use_container_width=True, hide_index=True)
    st.bar_chart(df.set_index("Gate")["Wait (min)"])

    if st.button("Generate Crowd Marshal Directive", type="primary"):
        agent = CrowdMarshalAgent(graph, client)
        with st.spinner("Crowd Marshal is analysing queues..."):
            result = agent.briefing()
        if result["surge_detected"]:
            st.error(result["text"], icon="🚨")
        else:
            st.success(result["text"], icon="✅")
        st.caption(f"GenAI live: {result['genai_live']}")


# ---------------------------------------------------------------------------
# Tab 3 — AccessAI Companion (Accessibility)
# ---------------------------------------------------------------------------
with tab_access:
    st.subheader("Accessibility support")
    st.caption("Simplified, calm, concrete guidance for fans and staff.")

    need_type = st.selectbox(
        "Type of support needed",
        ["General accessibility", "Mobility / Wheelchair access", "Sensory-friendly / Low-stimulation",
         "Visual impairment", "Hearing impairment"],
    )
    request = st.text_area(
        "Describe what's needed",
        value="I use a wheelchair and need the closest accessible entry with a short wait.",
    )

    if st.button("Ask AccessAI Companion", type="primary") and request.strip():
        agent = AccessCompanionAgent(graph, client)
        with st.spinner("AccessAI Companion is finding the best option..."):
            result = agent.assist(request, need_type=need_type)
        st.info(result["text"])
        st.caption(f"GenAI live: {result['genai_live']}")


# ---------------------------------------------------------------------------
# Tab 4 — GreenRoute (Transport & Sustainability)
# ---------------------------------------------------------------------------
with tab_transport:
    st.subheader("Sustainable transport recommendation")

    tdf = pd.DataFrame(
        [
            {
                "Route": t.name,
                "Mode": t.mode.replace("_", " ").title(),
                "Current Load %": t.current_load_pct,
                "CO2 (g/km/person)": t.co2_g_per_km_per_person,
            }
            for t in graph.transit.values()
        ]
    )
    st.dataframe(tdf, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    party_size = col1.number_input("Party size", min_value=1, max_value=10000, value=4)
    distance_km = col2.number_input("Trip distance (km)", min_value=0.5, max_value=100.0, value=8.0)

    if st.button("Get GreenRoute Recommendation", type="primary"):
        agent = GreenRouteAgent(graph, client)
        with st.spinner("GreenRoute is comparing options..."):
            result = agent.recommend(party_size=int(party_size), distance_km=float(distance_km))
        st.success(result["text"])
        m1, m2 = st.columns(2)
        m1.metric("Estimated trip CO2", f"{result['estimated_co2_kg']} kg")
        m2.metric("CO2 saved vs worst option", f"{result['co2_saved_kg']} kg")
        st.caption(f"GenAI live: {result['genai_live']}")


# ---------------------------------------------------------------------------
# Tab 5 — Ops Commander (Control Room)
# ---------------------------------------------------------------------------
with tab_ops:
    st.subheader("Fused real-time situation report")
    st.caption("Ops Commander fuses Crowd Marshal + GreenRoute + the live incident log into one briefing.")

    if graph.incidents:
        st.markdown("**Recent incident log:**")
        for inc in reversed(graph.incidents):
            st.markdown(f"- `t={inc['tick']}` {inc['message']}")
    else:
        st.caption("No incidents logged yet — try advancing the simulation a few times from the sidebar.")

    if st.button("Generate Situation Report", type="primary"):
        agent = OpsCommanderAgent(graph, client)
        with st.spinner("Ops Commander is fusing all agent outputs..."):
            result = agent.situation_report()
        if result["surge_detected"]:
            st.error(result["text"], icon="🚨")
        else:
            st.success(result["text"], icon="✅")
        st.caption(f"GenAI live: {result['genai_live']}")

        with st.expander("See individual sub-agent outputs that were fused"):
            st.json(result["sub_agent_outputs"])

st.markdown("---")
st.caption(
    "PulseArena AI — Wayfinder · Crowd Marshal · AccessAI Companion · GreenRoute · Ops Commander, "
    "all reading from one shared Stadium Context Graph. Built for the FIFA World Cup 2026 "
    "GenAI Stadium Operations Hackathon."
)
