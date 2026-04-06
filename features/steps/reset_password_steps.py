"""Step definitions for the reset password feature."""

import logging
import requests
from behave import given, when, then
from utils.helpers import (
    signup_user, verify_otp, forgot_password, reset_password,
    login_user, extract_token, OTP_PLACEHOLDER,
)

logger = logging.getLogger("auth_api_tests")


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------

@given("the user has triggered forgot password")
def step_trigger_forgot(context):
    resp = forgot_password(context.base_url, context.email)
    logger.info(f"Forgot password triggered: status={resp.status_code}")
    context.saved["forgot_response"] = resp


@given('a verified user has reset their password to "{new_password}"')
def step_verified_and_reset(context, new_password):
    # Signup
    resp, payload = signup_user(context.base_url)
    assert resp.status_code == 201, f"Signup failed: {resp.status_code} {resp.text}"
    context.email = payload["email"]
    context.payload = payload
    context.saved["password"] = payload["password"]

    # Verify
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    verify_otp(context.base_url, context.email, OTP_PLACEHOLDER)

    # Forgot + Reset
    forgot_password(context.base_url, context.email)
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    reset_password(context.base_url, context.email, OTP_PLACEHOLDER, new_password)
    context.saved["new_password"] = new_password
    logger.info(f"User {context.email} password reset to '{new_password}'")


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------

@when('I reset the password with OTP "{otp}" and new password "{new_password}"')
def step_reset_pw(context, otp, new_password):
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    context.response = reset_password(
        context.base_url, context.email, otp, new_password
    )


@when('I reset the password with OTP "{otp}" and null new_password')
def step_reset_pw_null(context, otp):
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/password/reset",
        json={"username": context.email, "otp": otp, "new_password": None},
    )


@when("I reset the password with the same OTP again")
def step_reset_pw_same_otp(context):
    # Re-use the OTP from the previous reset attempt
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    context.response = reset_password(
        context.base_url, context.email, OTP_PLACEHOLDER, "AnotherNew123!"
    )


@when("I send password reset request without username field")
def step_reset_missing_username(context):
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/password/reset",
        json={"otp": "123456", "new_password": "NewPass123!"},
    )


@when('I login with the new password "{password}" after reset')
def step_login_after_reset(context, password):
    context.response = login_user(context.base_url, context.email, password)
