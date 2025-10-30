import os
import json
from pathlib import Path

import pytest

from src.cost_guard import CostGuard, OpenAICostLimitExceeded


def test_cost_guard_tracks_and_persists(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("OPENAI_DAILY_LIMIT_USD", "1.0")

    cg = CostGuard()
    assert cg.daily_spend == 0.0

    # Track cost for 10000 tokens on gpt-4o-mini
    cost = cg.track_cost(10000, "gpt-4o-mini")
    assert cost > 0

    # Persisted file exists
    spend_file = home / ".daily_culture_bot" / "daily_spend.json"
    assert spend_file.exists()
    data = json.loads(spend_file.read_text())
    assert data["date"]
    assert data["spend"] == pytest.approx(cg.daily_spend)


def test_cost_guard_budget_exceeded(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("OPENAI_DAILY_LIMIT_USD", "0.0001")

    cg = CostGuard()
    with pytest.raises(OpenAICostLimitExceeded):
        cg.check_budget(0.001)


