# agents/crowd_marshal.py
#
# Turns raw gate queue numbers into something a volunteer can actually act
# on — "send people to Gate C instead" rather than a chart they have to
# interpret themselves. The goal is catching a surge before it's a
# bottleneck, not reporting on one after the fact.

from __future__ import annotations

from .base_agent import BaseAgent

SURGE_THRESHOLD_MIN = 8.0


class CrowdMarshalAgent(BaseAgent):
    name = "Crowd Marshal"
    audience = "Volunteers & Organisers"

    def briefing(self) -> dict:
        snapshot = self.graph.snapshot()
        busiest = self.graph.busiest_gate()
        calmest = self.graph.calmest_gate()

        system_prompt = (
            "You are Crowd Marshal, a real-time crowd management assistant used by stadium "
            "volunteers and organisers during a FIFA World Cup 2026 match. Given live gate "
            "queue data, produce a short, clear, actionable directive volunteers can act on "
            "immediately (e.g. redirecting fans, opening a gate, requesting extra staff). "
            "Be concrete: name gates, cite wait times, and estimate the impact of your "
            "recommendation. Maximum 4 sentences. Do not use markdown headers."
        )

        user_prompt = (
            f"Live gate data:\n{snapshot['gates']}\n\n"
            f"Busiest gate: {busiest.name}, wait {busiest.wait_min} min, trend {busiest.trend}.\n"
            f"Calmest gate: {calmest.name}, wait {calmest.wait_min} min.\n\n"
            "Write the volunteer directive for this moment."
        )

        def fallback() -> str:
            if busiest.wait_min >= SURGE_THRESHOLD_MIN:
                est_saved = round(busiest.wait_min - calmest.wait_min, 1)
                return (
                    f"⚠️ Surge alert: {busiest.name} is at {busiest.wait_min} min wait and "
                    f"{busiest.trend}. Redirect incoming fans to {calmest.name} "
                    f"({calmest.wait_min} min wait) — estimated wait reduction ~{est_saved} min "
                    f"per redirected fan. Consider opening an additional lane at "
                    f"{busiest.name} if redirect volume exceeds capacity."
                )
            return (
                f"All gates currently within normal range. {busiest.name} is the busiest at "
                f"{busiest.wait_min} min wait — no action needed, continue monitoring."
            )

        result = self._run(system_prompt, user_prompt, fallback, max_tokens=250)
        result["surge_detected"] = busiest.wait_min >= SURGE_THRESHOLD_MIN
        result["busiest_gate"] = busiest.name
        result["calmest_gate"] = calmest.name
        return result
