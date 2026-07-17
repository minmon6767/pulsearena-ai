# agents/wayfinder.py
#
# The fan-facing one. Answers "where's the nearest X" type questions in
# whatever language the fan picks, grounded in whatever the context graph
# currently says about gates/queues/amenities — so it won't tell someone to
# go to a gate that doesn't exist or quote a wait time we made up.

from __future__ import annotations

from core.i18n import language_instruction
from .base_agent import BaseAgent


class WayfinderAgent(BaseAgent):
    name = "Wayfinder"
    audience = "Fans"

    def answer(self, question: str, language: str = "English") -> dict:
        snapshot = self.graph.snapshot()

        system_prompt = (
            "You are Wayfinder, the friendly navigation assistant for a FIFA World Cup 2026 "
            "host stadium. You help fans find gates, seats, amenities, restrooms, first aid, "
            "and accessibility facilities. Always ground your answer in the live stadium data "
            "provided to you — never invent gate names or wait times that aren't in the data. "
            "Keep answers short (2-4 sentences), warm, and immediately actionable. "
            + language_instruction(language)
        )

        user_prompt = (
            f"Live stadium data:\n{snapshot}\n\n"
            f"Fan question: {question}\n\n"
            "Give a short, specific, friendly answer using the live data above."
        )

        def fallback() -> str:
            calmest = self.graph.calmest_gate()
            amenity = None
            q_lower = question.lower()
            for kind in ["accessible_restroom", "first_aid", "prayer_room", "sensory_room", "water_refill"]:
                if kind.split("_")[0] in q_lower or kind in q_lower:
                    amenity = self.graph.find_amenity(kind)
                    break

            if amenity:
                return (
                    f"Here's what I found: {amenity['label']}. "
                    f"If it's busy, {calmest.name} nearby currently has the shortest wait "
                    f"(~{calmest.wait_min} min)."
                )
            return (
                f"Right now {calmest.name} has the shortest wait at about {calmest.wait_min} "
                f"minutes ({calmest.queue_len} people in queue) — I'd recommend heading there. "
                f"Nearest transit link: {calmest.nearest_transit}."
            )

        return self._run(system_prompt, user_prompt, fallback, max_tokens=300)
