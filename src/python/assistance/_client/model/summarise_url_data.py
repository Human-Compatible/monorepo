"""
    FastAPI

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.1.0
    Generated by: https://openapi-generator.tech
"""

import decimal  # noqa: F401
import functools  # noqa: F401
import io  # noqa: F401
import re  # noqa: F401
import typing  # noqa: F401
import uuid  # noqa: F401
from datetime import date, datetime  # noqa: F401

import frozendict  # noqa: F401
import typing_extensions  # noqa: F401
from _client import schemas  # noqa: F401


class SummariseUrlData(schemas.DictSchema):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    class MetaOapg:
        required = {
            "record_grouping",
            "query",
            "url",
        }

        class properties:
            record_grouping = schemas.StrSchema
            query = schemas.StrSchema
            url = schemas.StrSchema
            __annotations__ = {
                "record_grouping": record_grouping,
                "query": query,
                "url": url,
            }

    record_grouping: MetaOapg.properties.record_grouping
    query: MetaOapg.properties.query
    url: MetaOapg.properties.url

    @typing.overload
    def __getitem__(
        self, name: typing_extensions.Literal["record_grouping"]
    ) -> MetaOapg.properties.record_grouping:
        ...

    @typing.overload
    def __getitem__(
        self, name: typing_extensions.Literal["query"]
    ) -> MetaOapg.properties.query:
        ...

    @typing.overload
    def __getitem__(
        self, name: typing_extensions.Literal["url"]
    ) -> MetaOapg.properties.url:
        ...

    @typing.overload
    def __getitem__(self, name: str) -> schemas.UnsetAnyTypeSchema:
        ...

    def __getitem__(
        self,
        name: typing.Union[
            typing_extensions.Literal[
                "record_grouping",
                "query",
                "url",
            ],
            str,
        ],
    ):
        # dict_instance[name] accessor
        return super().__getitem__(name)

    @typing.overload
    def get_item_oapg(
        self, name: typing_extensions.Literal["record_grouping"]
    ) -> MetaOapg.properties.record_grouping:
        ...

    @typing.overload
    def get_item_oapg(
        self, name: typing_extensions.Literal["query"]
    ) -> MetaOapg.properties.query:
        ...

    @typing.overload
    def get_item_oapg(
        self, name: typing_extensions.Literal["url"]
    ) -> MetaOapg.properties.url:
        ...

    @typing.overload
    def get_item_oapg(
        self, name: str
    ) -> typing.Union[schemas.UnsetAnyTypeSchema, schemas.Unset]:
        ...

    def get_item_oapg(
        self,
        name: typing.Union[
            typing_extensions.Literal[
                "record_grouping",
                "query",
                "url",
            ],
            str,
        ],
    ):
        return super().get_item_oapg(name)

    def __new__(
        cls,
        *args: typing.Union[
            dict,
            frozendict.frozendict,
        ],
        record_grouping: typing.Union[
            MetaOapg.properties.record_grouping,
            str,
        ],
        query: typing.Union[
            MetaOapg.properties.query,
            str,
        ],
        url: typing.Union[
            MetaOapg.properties.url,
            str,
        ],
        _configuration: typing.Optional[schemas.Configuration] = None,
        **kwargs: typing.Union[
            schemas.AnyTypeSchema,
            dict,
            frozendict.frozendict,
            str,
            date,
            datetime,
            uuid.UUID,
            int,
            float,
            decimal.Decimal,
            None,
            list,
            tuple,
            bytes,
        ],
    ) -> "SummariseUrlData":
        return super().__new__(
            cls,
            *args,
            record_grouping=record_grouping,
            query=query,
            url=url,
            _configuration=_configuration,
            **kwargs,
        )
