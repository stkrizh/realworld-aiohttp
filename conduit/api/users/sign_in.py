__all__ = [
    "sign_in_endpoint",
]

import typing as t
from http import HTTPStatus

from aiohttp import web
from aiohttp_apispec import (
    docs,
    request_schema,
    response_schema,
)
from marshmallow import Schema, fields, post_load, validate

from conduit.api.base import Endpoint, ErrorSchema, UserSchema
from conduit.api.users.response import convert_to_user_response
from conduit.core.use_cases import UseCase
from conduit.core.use_cases.users.sign_in import SignInInput, SignInResult


class SignInUserSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=320))
    password = fields.String(required=True, validate=validate.Length(max=2048))

    @post_load
    def to_input(self, data: dict[str, t.Any], **_: t.Any) -> SignInInput:
        return SignInInput(
            email=data["email"],
            password=data["password"],
        )


class SignInRequestSchema(Schema):
    user = fields.Nested(SignInUserSchema(), required=True)

    @post_load
    def to_input(self, data: dict[str, t.Any], **_: t.Any) -> SignInInput:
        return data["user"]


class SignInResponseSchema(Schema):
    user = fields.Nested(UserSchema(), required=True)


def sign_in_endpoint(use_case: UseCase[SignInInput, SignInResult]) -> Endpoint:
    @docs(tags=["users"], summary="Sign in with email and password.")
    @request_schema(SignInRequestSchema, put_into="input")
    @response_schema(SignInResponseSchema, code=HTTPStatus.OK, description="User successfully signed in.")
    @response_schema(ErrorSchema, code=HTTPStatus.UNAUTHORIZED, description="Invalid credentials.")
    async def handler(request: web.Request) -> web.Response:
        input = request["input"]
        assert isinstance(input, SignInInput)
        result = await use_case.execute(input)
        return convert_to_user_response(result.user, result.token)

    return handler
