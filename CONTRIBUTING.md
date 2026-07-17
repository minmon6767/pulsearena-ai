# Contributing

This started as a hackathon build, but if you want to poke at it after judging's done:

1. Fork it, clone it, `pip install -r requirements.txt`
2. Make a branch off `main`
3. Run `pytest tests/ -v` before you open a PR — it should pass with zero setup (no API key needed, the whole suite runs against the offline fallback path on purpose)
4. Keep new agents consistent with the pattern in `agents/base_agent.py` — read from the shared `StadiumContextGraph`, build a grounded prompt, always give it a fallback

If you're adding a new agent, the fastest way is to copy `agents/green_route.py` since it's the smallest complete example and rename from there.

Not accepting big architectural changes right now since this is still hackathon-stage, but bug reports and small fixes are welcome via issues/PRs.
