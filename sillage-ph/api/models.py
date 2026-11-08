"""Validation shared by write requests and the seed loader."""
from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, UrlConstraints, AnyUrl

Text = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=200)]
Note = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=1000)]
Https = Annotated[AnyUrl, UrlConstraints(allowed_schemes=['https'], host_required=True, max_length=2048)]
Gender = Literal['Men', 'Women', 'Unisex']
Family = Literal['Amber', 'Floral', 'Fruity', 'Fresh', 'Woody', 'Gourmand', 'Leather']
Sort = Literal['price_asc', 'price_desc']


class Model(BaseModel):
    model_config = ConfigDict(extra='forbid')


class Seller(Model):
    store: Text
    url: Https
    note: Note


class OtherStore(Model):
    store: Text
    dupe: Text
    url: Https


class PerfumeInput(Model):
    name: Text
    brand: Text
    scent_family: Family
    key_notes: Annotated[list[Text], Field(min_length=1, max_length=30)]
    dupes: Annotated[list[Text], Field(min_length=1, max_length=30)]
    gender: Gender
    year_launched: Annotated[int, Field(strict=True, ge=1900, le=date.today().year)]
    concentration: Text
    best_season: Text
    best_occasion: Text
    dupe_size: Text
    vibe: Note
    dupe_price_php: Text
    price_php_min: Annotated[int, Field(strict=True, ge=0, le=1000000)]
    where_to_buy: Seller
    other_stores: Annotated[list[OtherStore], Field(max_length=30)] = Field(default_factory=list)
