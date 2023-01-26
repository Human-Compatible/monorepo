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


class Token(schemas.DictSchema):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    class MetaOapg:
        required = {
            "access_token",
            "token_type",
        }

        class properties:
            access_token = schemas.StrSchema
            token_type = schemas.StrSchema
            __annotations__ = {
                "access_token": access_token,
                "token_type": token_type,
            }

    access_token: MetaOapg.properties.access_token
    token_type: MetaOapg.properties.token_type

    @typing.overload
    def __getitem__(
        self, name: typing_extensions.Literal["access_token"]
    ) -> MetaOapg.properties.access_token:
        ...

    @typing.overload
    def __getitem__(
        self, name: typing_extensions.Literal["token_type"]
    ) -> MetaOapg.properties.token_type:
        ...

    @typing.overload
    def __getitem__(self, name: str) -> schemas.UnsetAnyTypeSchema:
        ...

    def __getitem__(
        self,
        name: typing.Union[
            typing_extensions.Literal[
                "access_token",
                "token_type",
            ],
            str,
        ],
    ):
        # dict_instance[name] accessor
        return super().__getitem__(name)

    @typing.overload
    def get_item_oapg(
        self, name: typing_extensions.Literal["access_token"]
    ) -> MetaOapg.properties.access_token:
        ...

    @typing.overload
    def get_item_oapg(
        self, name: typing_extensions.Literal["token_type"]
    ) -> MetaOapg.properties.token_type:
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
                "access_token",
                "token_type",
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
        access_token: typing.Union[
            MetaOapg.properties.access_token,
            str,
        ],
        token_type: typing.Union[
            MetaOapg.properties.token_type,
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
    ) -> "Token":
        return super().__new__(
            cls,
            *args,
            access_token=access_token,
            token_type=token_type,
            _configuration=_configuration,
            **kwargs,
        )
