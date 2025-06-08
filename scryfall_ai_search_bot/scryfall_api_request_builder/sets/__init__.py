from ..base import ScryfallAPIBaseRequestBuilder
from ..request import ScryfallAPIRequest
from ..model import ScryfallSetList


class ScryfallAPISetsRequestBuilder(ScryfallAPIBaseRequestBuilder):
    def all(self):
        return ScryfallAPIRequest(
            response_model=ScryfallSetList,
            url=f"{self.base_url}",
        )
