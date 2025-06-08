from .base import ScryfallAPIBaseRequestBuilder
from .cards import ScryfallAPICardsRequestBuilder


class ScryfallAPIRequestBuilder(ScryfallAPIBaseRequestBuilder):
    def __init__(self, base_url: str = "https://api.scryfall.com"):
        super().__init__(base_url)

    def cards(self):
        return ScryfallAPICardsRequestBuilder(f"{self.base_url}/cards")
