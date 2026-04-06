"""Step definitions for the forgot password feature."""

import logging
import requests
from behave import given, when, then
from utils.helpers import forgot_password

logger = logging.getLogger("auth_api_tests")


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------

@when("I trigger forgot password for the verified user")
def step_forgot_pw_verified(context):
    context.response = forgot_password(context.base_url, context.email)


@when('I trigger forgot password for username "{username}"')
def step_forgot_pw_custom(context, username):
    context.response = forgot_password(context.base_url, username)


@when("I trigger forgot password for the unverified user")
def step_forgot_pw_unverified(context):
    context.response = forgot_password(context.base_url, context.email)


@when("I trigger forgot password with empty username")
def step_forgot_pw_empty(context):
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/password/forgot",
        json={"username": ""},
    )


@when("I trigger forgot password with null username")
def step_forgot_pw_null(context):
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/password/forgot",
        json={"username": None},
    )


@when("I trigger forgot password for the verified user again")
def step_forgot_pw_again(context):
    context.response = forgot_password(context.base_url, context.email)


@when("I trigger forgot password for the new user")
def step_forgot_pw_new_user(context):
    email = context.email or context.saved.get("email")
    assert email, "No user email available for forgot password"
    context.response = forgot_password(context.base_url, email)
