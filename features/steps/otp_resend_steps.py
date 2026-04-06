"""Step definitions for the OTP resend feature."""

import logging
import requests
from behave import given, when, then
from utils.helpers import resend_otp, verify_otp, signup_user, OTP_PLACEHOLDER

logger = logging.getLogger("auth_api_tests")


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------

@given("a new user has signed up at T=0")
def step_signup_at_t0(context):
    import time
    resp, payload = signup_user(context.base_url)
    assert resp.status_code == 201, f"Signup failed: {resp.status_code} {resp.text}"
    context.email = payload["email"]
    context.payload = payload
    context.saved["password"] = payload["password"]
    context.saved["t0"] = time.time()
    logger.info(f"Signed up user at T=0: {context.email}")


@given('the original OTP is "{otp}"')
def step_save_original_otp(context, otp):
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    context.saved["original_otp"] = otp
    logger.info(f"Original OTP saved: {otp}")


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------

@when("I resend OTP for the signed-up user")
def step_resend_otp(context):
    context.response = resend_otp(context.base_url, context.email)


@when("I immediately resend OTP for the signed-up user again")
def step_resend_otp_immediately(context):
    context.response = resend_otp(context.base_url, context.email)


@when('I resend OTP for username "{username}"')
def step_resend_otp_custom(context, username):
    context.response = resend_otp(context.base_url, username)


@when("I verify the original OTP for the signed-up user")
def step_verify_original_otp(context):
    otp = context.saved.get("original_otp", OTP_PLACEHOLDER)
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    context.response = verify_otp(context.base_url, context.email, otp)


@when("I resend OTP 10 times rapidly for the signed-up user")
def step_resend_10_times(context):
    results = []
    for i in range(10):
        resp = resend_otp(context.base_url, context.email)
        results.append(resp.status_code)
        logger.info(f"Rapid resend #{i+1}: status={resp.status_code}")
    context.saved["rapid_resend_results"] = results
    context.response = resp  # keep last response for response time check


# ---------------------------------------------------------------------------
# When steps — E2E journey support
# ---------------------------------------------------------------------------

@when("I resend OTP for the new user")
def step_resend_otp_new_user(context):
    email = context.email or context.saved.get("email")
    assert email, "No user email available for resend"
    context.response = resend_otp(context.base_url, email)
