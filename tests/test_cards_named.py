import pytest
import httpx

from scryfall_ai_search_bot.scryfall_api_request_builder import (
    ScryfallAPIRequestBuilder,
)


@pytest.fixture
def httpx_client():
    return httpx.Client()


def test_cards_named(httpx_client: httpx.Client):
    black_lotus = (
        ScryfallAPIRequestBuilder()
        .cards()
        .named(fuzzy="black lotus")
        .execute(httpx_client)
    )
    print(black_lotus)
