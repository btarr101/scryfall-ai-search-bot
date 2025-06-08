import pytest
import httpx
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.json import JSONSnapshotExtension

from scryfall_ai_search_bot.scryfall_api_request_builder import (
    ScryfallAPIRequestBuilder,
)


@pytest.fixture
def httpx_client():
    return httpx.Client()


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion):
    return snapshot.with_defaults(extension_class=JSONSnapshotExtension)


def test_cards_named(httpx_client: httpx.Client, snapshot: SnapshotAssertion):
    black_lotus = ScryfallAPIRequestBuilder().cards().named(fuzzy="black lotus").execute(httpx_client)

    snapshot.assert_match(black_lotus.model_dump())


def test_sets(httpx_client: httpx.Client, snapshot: SnapshotAssertion):
    sets = ScryfallAPIRequestBuilder().sets().all().execute(httpx_client)

    snapshot.assert_match(sets.model_dump())
