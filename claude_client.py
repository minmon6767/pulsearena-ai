# core/claude_client.py
#
# Small wrapper around the Anthropic API that every agent goes through.
#
# The one rule that matters here: this must never blow up mid-demo, key or
# no key. If ANTHROPIC_API_KEY is missing, wrong, or the network hiccups,
# we quietly fall back to the rule-based response the calling agent hands
# us instead of letting the exception surface. Judges shouldn't see a stack
# trace just because someone forgot to set an env var.

from __future__ import annotations

import os
from typing import Callable

try:
    import anthropic
except ImportError:  # pragma: no cover - anthropic should always be installed
    anthropic = None

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = os.getenv("PULSEARENA_MODEL", "claude-sonnet-4-6")


class ClaudeClient:
    """Wraps the Anthropic Messages API. Falls back to templated answers if anything goes wrong."""

    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        self._client = None
        self.live = False

        if api_key and anthropic is not None:
            try:
                self._client = anthropic.Anthropic(api_key=api_key)
                self.live = True
            except Exception:
                self._client = None
                self.live = False

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        fallback: Callable[[], str],
        max_tokens: int = 500,
    ) -> tuple[str, bool]:
        """
        Returns (text, used_live_genai).

        `fallback` is just a zero-arg function that returns a decent
        rule-based answer — every agent passes one of these in so it still
        works with no API key set at all.
        """
        if not self.live or self._client is None:
            return fallback(), False

        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            text_blocks = [b.text for b in response.content if getattr(b, "type", "") == "text"]
            text = "\n".join(text_blocks).strip()
            return (text if text else fallback()), bool(text)
        except Exception:
            # bad key, rate limit, timeout, whatever — just degrade quietly
            # instead of taking the whole app down with it
            return fallback(), False
