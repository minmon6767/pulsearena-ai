# core/context_graph.py
#
# This is the "single source of truth" every agent reads from — the Stadium
# Context Graph. Gate queues, transit load, weather, incidents, all of it
# lives here, and it's what keeps all five agents' answers consistent with
# each other instead of contradicting one another.
#
# We obviously don't have real turnstile counters or CCTV crowd density for
# a hackathon, so this simulates it with a seeded random walk instead.
# Seeded on purpose — if a judge hits "advance simulation" twice during a
# demo we want a coherent story, not noise that makes no sense.
#
# Swapping this out for a real sensor feed later should be a drop-in job —
# agents only ever call the public methods below (busiest_gate, snapshot,
# etc), they never touch the random-walk logic directly.

from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_json(filename: str) -> dict:
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


@dataclass
class GateState:
    id: str
    name: str
    capacity_per_min: int
    accessible: bool
    nearest_transit: str
    queue_len: int = 0
    wait_min: float = 0.0
    trend: str = "stable"  # rising | falling | stable


@dataclass
class TransitState:
    id: str
    name: str
    mode: str
    co2_g_per_km_per_person: int
    capacity: int
    typical_headway_min: int
    current_load_pct: int = 0


@dataclass
class StadiumContextGraph:
    """Holds the full live state of the stadium at a point in time."""

    venue: dict = field(default_factory=dict)
    gates: dict[str, GateState] = field(default_factory=dict)
    transit: dict[str, TransitState] = field(default_factory=dict)
    amenities: list[dict] = field(default_factory=list)
    weather: dict = field(default_factory=dict)
    incidents: list[dict] = field(default_factory=list)
    tick: int = 0
    seed: int = 42

    # ---- construction -----------------------------------------------
    @classmethod
    def bootstrap(cls, seed: int = 42) -> "StadiumContextGraph":
        gates_data = _load_json("gates.json")
        transit_data = _load_json("transit_routes.json")
        venue_data = _load_json("venues.json")

        rng = random.Random(seed)

        gates = {
            g["id"]: GateState(
                id=g["id"],
                name=g["name"],
                capacity_per_min=g["capacity_per_min"],
                accessible=g["accessible"],
                nearest_transit=g["nearest_transit"],
                queue_len=rng.randint(20, 120),
            )
            for g in gates_data["gates"]
        }

        transit = {
            t["id"]: TransitState(
                id=t["id"],
                name=t["name"],
                mode=t["mode"],
                co2_g_per_km_per_person=t["co2_g_per_km_per_person"],
                capacity=t["capacity"],
                typical_headway_min=t["typical_headway_min"],
                current_load_pct=rng.randint(20, 60),
            )
            for t in transit_data["routes"]
        }

        weather = {
            "condition": rng.choice(["Clear", "Partly Cloudy", "Light Rain", "Hot & Humid"]),
            "temp_c": rng.randint(18, 34),
        }

        graph = cls(
            venue=venue_data,
            gates=gates,
            transit=transit,
            amenities=gates_data["amenities"],
            weather=weather,
            incidents=[],
            tick=0,
            seed=seed,
        )
        return graph

    # ---- simulation ----------------------------------------------------
    def advance(self, rng: random.Random | None = None) -> None:
        """Move the simulated world forward by one tick (roughly a minute of match-day time)."""
        rng = rng or random.Random(self.seed + self.tick)
        self.tick += 1

        for gate in self.gates.values():
            # queues grow a bit faster than they drain, felt more realistic
            # than a pure random walk centered on zero
            delta = rng.randint(-25, 35)
            gate.queue_len = max(0, gate.queue_len + delta)
            gate.wait_min = round(gate.queue_len / max(gate.capacity_per_min, 1), 1)
            gate.trend = "rising" if delta > 5 else ("falling" if delta < -5 else "stable")

        for t in self.transit.values():
            delta = rng.randint(-8, 12)
            t.current_load_pct = min(100, max(5, t.current_load_pct + delta))

        # every so often something mildly interesting happens — kept it PG
        # and low-drama on purpose, this isn't meant to simulate an actual crisis
        if rng.random() < 0.12:
            incident_pool = [
                "Minor queue congestion reported",
                "Temporary signage obstruction cleared",
                "Medical assistance requested — non-urgent",
                "Lost child reunited with family",
                "Weather advisory issued for outdoor concourse",
                "Accessibility ramp temporarily congested",
            ]
            self.incidents.append(
                {"tick": self.tick, "message": rng.choice(incident_pool)}
            )
            self.incidents = self.incidents[-5:]  # keep last 5

    # ---- read helpers used by agents ------------------------------------
    def busiest_gate(self) -> GateState:
        return max(self.gates.values(), key=lambda g: g.wait_min)

    def calmest_gate(self, accessible_only: bool = False) -> GateState:
        pool = [g for g in self.gates.values() if (g.accessible or not accessible_only)]
        return min(pool, key=lambda g: g.wait_min)

    def least_loaded_transit(self) -> TransitState:
        return min(self.transit.values(), key=lambda t: t.current_load_pct)

    def lowest_emission_transit(self) -> TransitState:
        return min(self.transit.values(), key=lambda t: t.co2_g_per_km_per_person)

    def find_amenity(self, amenity_type: str) -> dict | None:
        matches = [a for a in self.amenities if a["type"] == amenity_type]
        return matches[0] if matches else None

    def snapshot(self) -> dict[str, Any]:
        """Plain-dict view of the current state — this is what gets dropped straight into prompts."""
        return {
            "tick": self.tick,
            "venue": self.venue,
            "weather": self.weather,
            "gates": [
                {
                    "id": g.id,
                    "name": g.name,
                    "queue_len": g.queue_len,
                    "wait_min": g.wait_min,
                    "trend": g.trend,
                    "accessible": g.accessible,
                    "nearest_transit": g.nearest_transit,
                }
                for g in self.gates.values()
            ],
            "transit": [
                {
                    "id": t.id,
                    "name": t.name,
                    "mode": t.mode,
                    "load_pct": t.current_load_pct,
                    "co2_g_per_km_per_person": t.co2_g_per_km_per_person,
                }
                for t in self.transit.values()
            ],
            "recent_incidents": self.incidents,
        }
