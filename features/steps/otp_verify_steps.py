"""Step definitions for the OTP verify feature."""

import logging
import requests
from behave import given, when, then
from utils.helpers import (
    signup_user, verify_otp, generate_unique_email,
    OTP_PLACEHOLDER,
)

logger = logging.getLogger("auth_api_tests")


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------

@given("a new user has signed up")
def step_new_signup(context):
    resp, payload = signup_user(context.base_url)
    assert resp.status_code == 201, f"Signup failed: {resp.status_code} {resp.text}"
    context.email = payload["email"]
    context.payload = payload
    context.saved["password"] = payload["password"]
    logger.info(f"Signed up user: {context.email}")


@given("a new user has signed up and verified")
def step_signed_up_and_verified(context):
    resp, payload = signup_user(context.base_url)
    assert resp.status_code == 201, f"Signup failed: {resp.status_code} {resp.text}"
    context.email = payload["email"]
    context.payload = payload
    context.saved["password"] = payload["password"]
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    verify_resp = verify_otp(context.base_url, context.email, OTP_PLACEHOLDER)
    logger.info(
        f"Verification attempt for {context.email}: "
        f"status={verify_resp.status_code}"
    )


@given('a new user has signed up with phone "{phone}"')
def step_signup_with_phone(context, phone):
    from utils.helpers import generate_signup_payload
    payload = generate_signup_payload(phone=phone)
    resp = requests.post(f"{context.base_url}/api/v1/auth/signup", json=payload)
    assert resp.status_code == 201, f"Signup failed: {resp.status_code} {resp.text}"
    context.email = payload["email"]
    context.payload = payload


# ---------------------------------------------------------------------------
# When steps — verify OTP
# ---------------------------------------------------------------------------

@when('I verify the OTP "{otp}" for the signed-up user')
def step_verify_otp(context, otp):
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    context.response = verify_otp(context.base_url, context.email, otp)


@when('I verify the OTP "{otp}" for the signed-up user again')
def step_verify_otp_again(context, otp):
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    context.response = verify_otp(context.base_url, context.email, otp)


@when('I verify the OTP "{otp}" for username "{username}"')
def step_verify_otp_custom_user(context, otp, username):
    context.response = verify_otp(context.base_url, username, otp)


@when("I verify with null OTP for the signed-up user")
def step_verify_null_otp(context):
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/verify/confirm",
        json={"username": context.email, "otp": None},
    )


@when("I send verify request without username field")
def step_verify_missing_username(context):
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/verify/confirm",
        json={"otp": "123456"},
    )
