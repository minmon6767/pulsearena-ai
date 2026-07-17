# agents/access_companion.py
#
# Rewrites instructions into plain, calm, short-sentence language and
# points people to a real accessible option that actually exists in the
# data — accessible gate, quiet room, whatever fits the request. Not just a
# "simplify this text" wrapper, it's grounded the same way every other
# agent here is.

from __future__ import annotations

from .base_agent import BaseAgent


class AccessCompanionAgent(BaseAgent):
    name = "AccessAI Companion"
    audience = "Accessibility-needs Fans & Staff"

    def assist(self, request: str, need_type: str = "General accessibility") -> dict:
        snapshot = self.graph.snapshot()
        accessible_gates = [g for g in snapshot["gates"] if g["accessible"]]
        best = min(accessible_gates, key=lambda g: g["wait_min"]) if accessible_gates else None
        sensory_room = self.graph.find_amenity("sensory_room")

        system_prompt = (
            "You are AccessAI Companion, an assistant that helps stadium staff and fans "
            "with accessibility needs at a FIFA World Cup 2026 venue. The need category is: "
            f"'{need_type}'. Use simple, calm, unambiguous sentences (short sentences, no "
            "jargon, no idioms) suitable for text-to-speech playback or for a fan who "
            "processes information best with plain language. Always point to a concrete, "
            "real accessible option from the data provided. Maximum 4 sentences."
        )

        user_prompt = (
            f"Accessible gates available:\n{accessible_gates}\n\n"
            f"Sensory-friendly room on-site: {sensory_room}\n\n"
            f"Request: {request}\n\n"
            "Give calm, simple, concrete guidance."
        )

        def fallback() -> str:
            parts = []
            if best:
                parts.append(
                    f"The best accessible entry right now is {best['name']}, with a short "
                    f"wait of about {best['wait_min']} minutes."
                )
            if "sensory" in request.lower() or "quiet" in request.lower() or need_type.lower().startswith("sensory"):
                if sensory_room:
                    parts.append(f"A low-sensory quiet room is available: {sensory_room['label']}.")
            if not parts:
                parts.append(
                    "Please proceed to the nearest accessible gate marked with the wheelchair "
                    "symbol. A staff member will assist you there."
                )
            return " ".join(parts)

        return self._run(system_prompt, user_prompt, fallback, max_tokens=250)
