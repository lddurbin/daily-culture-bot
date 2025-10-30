#!/usr/bin/env python3
"""
CostGuard: simple per-day OpenAI spend control with local persistence.
"""

import json
import os
from datetime import date
from pathlib import Path
from typing import Optional

try:
    from . import logging_config
except ImportError:  # when imported as top-level module in tests
    import logging_config  # type: ignore


class OpenAICostLimitExceeded(Exception):
    pass


class CostGuard:
    def __init__(self, daily_limit_usd: Optional[float] = None):
        self.logger = logging_config.get_logger(__name__)
        self.daily_limit = float(os.getenv("OPENAI_DAILY_LIMIT_USD", daily_limit_usd or 2.0))
        self.spend_file = Path.home() / ".daily_culture_bot" / "daily_spend.json"
        self._soft_warned = False
        self.daily_spend = self._load_daily_spend()

    def _load_daily_spend(self) -> float:
        if not self.spend_file.exists():
            return 0.0
        try:
            with open(self.spend_file) as f:
                data = json.load(f)
            if data.get("date") != str(date.today()):
                return 0.0
            return float(data.get("spend", 0.0))
        except Exception:
            return 0.0

    def _persist_spend(self) -> None:
        self.spend_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.spend_file, "w") as f:
            json.dump({"date": str(date.today()), "spend": self.daily_spend}, f)

    def check_budget(self, estimated_cost_usd: float) -> None:
        if self.daily_spend + estimated_cost_usd > self.daily_limit:
            raise OpenAICostLimitExceeded(
                f"Budget exceeded: ${self.daily_spend:.4f} + ${estimated_cost_usd:.4f} > ${self.daily_limit:.2f}"
            )
        if not self._soft_warned and (self.daily_spend + estimated_cost_usd) > 0.8 * self.daily_limit:
            self.logger.warning(
                "openai_cost_soft_limit",
                projected=self.daily_spend + estimated_cost_usd,
                daily_limit=self.daily_limit,
            )
            self._soft_warned = True

    def track_cost(self, tokens_used: int, model: str) -> float:
        cost = self._estimate_cost(tokens_used, model)
        self.daily_spend += cost
        self._persist_spend()
        self.logger.info(
            "openai_cost_tracked",
            tokens=tokens_used,
            model=model,
            cost_usd=cost,
            daily_total=self.daily_spend,
        )
        return cost

    @staticmethod
    def _estimate_cost(tokens: int, model: str) -> float:
        pricing = {
            "gpt-4o": {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000},
            "gpt-4o-mini": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
        }
        rate = pricing.get(model, pricing["gpt-4o-mini"])  # default conservative
        # Approximate 50/50 split
        return tokens * (rate["input"] + rate["output"]) / 2


