# agents/green_route.py
#
# Picks the best transit option balancing two things that don't always
# agree: lowest emissions and lowest current load (no point recommending
# the "green" option if it's already packed). Also spits out a rough CO2
# estimate so the number isn't just vibes.

from __future__ import annotations

from .base_agent import BaseAgent


class GreenRouteAgent(BaseAgent):
    name = "GreenRoute"
    audience = "Transport & Sustainability Teams"

    def recommend(self, party_size: int = 1, distance_km: float = 8.0) -> dict:
        snapshot = self.graph.snapshot()
        low_emission = self.graph.lowest_emission_transit()
        low_load = self.graph.least_loaded_transit()

        # Rough estimated emissions for the trip under each candidate option.
        options = sorted(snapshot["transit"], key=lambda t: (t["co2_g_per_km_per_person"], t["load_pct"]))
        best = options[0]
        est_co2_kg = round((best["co2_g_per_km_per_person"] * distance_km * party_size) / 1000, 2)
        worst_co2_kg = round((max(o["co2_g_per_km_per_person"] for o in options) * distance_km * party_size) / 1000, 2)
        co2_saved_kg = round(worst_co2_kg - est_co2_kg, 2)

        system_prompt = (
            "You are GreenRoute, a sustainability-focused transport assistant for a FIFA "
            "World Cup 2026 host stadium. Recommend the best transit option for a fan party "
            "from the live options provided, balancing low emissions and low current load "
            "(to avoid overcrowding a single route). Explain the environmental benefit in "
            "plain, encouraging language (not preachy). Maximum 4 sentences."
        )

        user_prompt = (
            f"Party size: {party_size}. Trip distance: {distance_km} km.\n"
            f"Live transit options:\n{snapshot['transit']}\n\n"
            f"Lowest-emission option: {low_emission.name} ({low_emission.co2_g_per_km_per_person} g CO2/km/person).\n"
            f"Least-loaded option right now: {low_load.name} ({low_load.current_load_pct}% load).\n"
            f"Estimated CO2 for the recommended trip: {est_co2_kg} kg "
            f"(vs {worst_co2_kg} kg for the highest-emission option — a saving of {co2_saved_kg} kg).\n\n"
            "Write the recommendation."
        )

        def fallback() -> str:
            return (
                f"For your group of {party_size}, we recommend {best['name']} "
                f"({best['mode'].replace('_', ' ')}) — currently at {best['load_pct']}% load. "
                f"Estimated trip footprint: {est_co2_kg} kg CO2, saving about {co2_saved_kg} kg "
                f"compared to the highest-emission option for the same trip. Small choice, real impact."
            )

        result = self._run(system_prompt, user_prompt, fallback, max_tokens=250)
        result["estimated_co2_kg"] = est_co2_kg
        result["co2_saved_kg"] = co2_saved_kg
        result["recommended_option"] = best["name"]
        return result
