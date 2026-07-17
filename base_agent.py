# agents/base_agent.py
#
# Every agent in here follows the same three steps: pull what it needs off
# the shared context graph, build a prompt grounded in that data, then ask
# ClaudeClient for a response (with a fallback ready in case there's no key
# configured). This base class just wraps step 3 so it's not copy-pasted
# five times.

from __future__ import annotations

from core.claude_client import ClaudeClient
from core.context_graph import StadiumContextGraph


class BaseAgent:
    name: str = "BaseAgent"
    audience: str = "General"

    def __init__(self, graph: StadiumContextGraph, client: ClaudeClient | None = None):
        self.graph = graph
        self.client = client or ClaudeClient()

    def _run(self, system_prompt: str, user_prompt: str, fallback_fn, max_tokens: int = 500):
        text, live = self.client.generate(system_prompt, user_prompt, fallback_fn, max_tokens=max_tokens)
        return {
            "agent": self.name,
            "audience": self.audience,
            "text": text,
            "genai_live": live,
        }
