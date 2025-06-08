from typing import TypedDict, Unpack, cast
from ..base import ScryfallAPIBaseRequestBuilder
from ..request import ScryfallAPIRequest
from ..model import ScryfallCardList, ScryfallCard


class ScryfallAPICardsRequestBuilder(ScryfallAPIBaseRequestBuilder):
    def search(self, query: str):
        return ScryfallAPIRequest(
            response_model=ScryfallCardList,
            url=f"{self.base_url}/search",
            query_prams={"q": query},
        )

    class CardsNamedParams(TypedDict, total=False):
        exact: str
        fuzzy: str

    def named(self, **kwargs: Unpack[CardsNamedParams]):
        return ScryfallAPIRequest(
            response_model=ScryfallCard,
            url=f"{self.base_url}/named",
            query_prams=cast(dict[str, str], kwargs),
        )
