"""Step definitions for end-to-end journey scenarios."""

import logging
import requests
from behave import given, when, then
from utils.helpers import (
    signup_user, verify_otp, login_user, forgot_password,
    reset_password, extract_token, OTP_PLACEHOLDER,
)

logger = logging.getLogger("auth_api_tests")


# ---------------------------------------------------------------------------
# When steps — E2E signup
# ---------------------------------------------------------------------------

@when("I sign up a new user with valid data")
def step_e2e_signup(context):
    resp, payload = signup_user(context.base_url)
    context.response = resp
    context.payload = payload
    context.email = payload["email"]
    context.saved["email"] = payload["email"]
    context.saved["password"] = payload["password"]
    logger.info(f"E2E signup: {context.email}")


@when("I sign up a new user with valid data at T=0")
def step_e2e_signup_t0(context):
    import time
    resp, payload = signup_user(context.base_url)
    context.response = resp
    context.payload = payload
    context.email = payload["email"]
    context.saved["email"] = payload["email"]
    context.saved["password"] = payload["password"]
    context.saved["t0"] = time.time()
    logger.info(f"E2E signup at T=0: {context.email}")


# ---------------------------------------------------------------------------
# When steps — E2E verify
# ---------------------------------------------------------------------------

@when('I verify the signup OTP "{otp}" for the new user')
def step_e2e_verify(context, otp):
    email = context.email or context.saved.get("email")
    assert email, "No user email available for verification"
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    context.response = verify_otp(context.base_url, email, otp)


@when('I verify the OTP "{otp}" for the new user')
def step_e2e_verify_otp(context, otp):
    email = context.email or context.saved.get("email")
    assert email, "No user email available for verification"
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    context.response = verify_otp(context.base_url, email, otp)
