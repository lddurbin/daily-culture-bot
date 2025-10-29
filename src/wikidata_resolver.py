import requests
from typing import List, Dict, Optional


class WikidataResolver:
    """Resolve labels to Wikidata Q-codes via wbsearchentities with in-memory cache."""

    def __init__(self, language: str = "en", session: Optional[requests.Session] = None):
        self.language = language
        self.session = session or requests.Session()
        self._cache: Dict[str, List[str]] = {}

    def resolve_labels(self, labels: List[str], limit: int = 2) -> Dict[str, List[str]]:
        results: Dict[str, List[str]] = {}
        for label in labels:
            key = (label or "").strip().lower()
            if not key:
                results[label] = []
                continue
            if key in self._cache:
                results[label] = self._cache[key]
                continue
            try:
                qcodes = self._resolve_single(key, limit=limit)
            except Exception:
                qcodes = []
            self._cache[key] = qcodes
            results[label] = qcodes
        return results

    def _resolve_single(self, label: str, limit: int = 2) -> List[str]:
        params = {
            "action": "wbsearchentities",
            "search": label,
            "language": self.language,
            "format": "json",
            "limit": str(limit),
        }
        resp = self.session.get("https://www.wikidata.org/w/api.php", params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        qcodes: List[str] = []
        for item in data.get("search", []):
            id_ = item.get("id")
            if isinstance(id_, str) and id_.startswith("Q"):
                qcodes.append(id_)
        return qcodes


