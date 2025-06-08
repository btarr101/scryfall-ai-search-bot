from enum import Enum
from typing import TypeVar, Generic, Type

import httpx
from pydantic import BaseModel


class RequestMethod(str, Enum):
    GET = "GET"


T = TypeVar("T", bound=BaseModel)


class ScryfallAPIRequest(Generic[T]):
    def __init__(
        self,
        *,
        response_model: Type[T],
        method: RequestMethod = RequestMethod.GET,
        url: str,
        query_prams: dict[str, str] | None = None,
    ):
        self.response_model = response_model
        self.url = url
        self.method = method
        self.query_params = query_prams

    def execute(self, client: httpx.Client):
        response = client.request(
            method=self.method, url=self.url, params=self.query_params
        )

        response.raise_for_status()
        response_bytes = response.read()
        return self.response_model.model_validate_json(response_bytes)

    async def aexecute(self, client: httpx.AsyncClient):
        response = await client.request(
            method=self.method, url=self.url, params=self.query_params
        )

        response.raise_for_status()
        response_bytes = await response.aread()
        return self.response_model.model_validate_json(response_bytes)
