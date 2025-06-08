from typing import Generic, TypeVar
from uuid import UUID
import pydantic


T = TypeVar("T", bound=pydantic.BaseModel)


class ScryfallList(pydantic.BaseModel, Generic[T]):
    has_more: bool
    data: list[T]


class ScryfallCardLegalities(pydantic.BaseModel):
    commander: bool

    @pydantic.model_validator(mode="before")
    @classmethod
    def legalities_to_bools(cls, data: dict[str, str]) -> dict[str, bool]:
        return {key: legality == "legal" for key, legality in data.items()}


class ScryfallCardImageUris(pydantic.BaseModel):
    png: str | None = None
    border_crop: str | None = None
    art_crop: str | None = None
    large: str | None = None
    normal: str | None = None
    small: str | None = None

    def smallest(self):
        return self.small or self.normal or self.large or self.png

    def mediumest(self):
        return self.normal or self.small or self.large or self.png


class ScryfallCard(pydantic.BaseModel):
    name: str
    mana_cost: str | None = None
    type_line: str | None = None
    legalities: ScryfallCardLegalities
    oracle_text: str | None = None
    keywords: list[str]
    image_uris: ScryfallCardImageUris | None = None


class ScryfallSet(pydantic.BaseModel):
    id: UUID
    code: str
    name: str
    set_type: str


class ScryfallCardList(ScryfallList[ScryfallCard]):
    total_cards: int
    next_page: str | None = None


class ScryfallSetList(ScryfallList[ScryfallSet]):
    pass
