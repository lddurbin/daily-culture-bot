from unittest.mock import Mock

from src.wikidata_resolver import WikidataResolver


def test_resolver_maps_labels_with_cache():
    session = Mock()
    session.get.return_value.json.return_value = {
        "search": [{"id": "Q999"}, {"id": "Q888"}]
    }
    session.get.return_value.raise_for_status.return_value = None

    resolver = WikidataResolver(session=session)
    first = resolver.resolve_labels(["Miracle of the loaves"], limit=2)
    assert first["Miracle of the loaves"] == ["Q999", "Q888"]

    # Second call should hit cache and not invoke another HTTP request
    session.get.reset_mock()
    second = resolver.resolve_labels(["miracle of the loaves"], limit=2)
    assert second["miracle of the loaves"] == ["Q999", "Q888"]
    session.get.assert_not_called()


