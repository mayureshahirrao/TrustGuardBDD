"""Step definitions for the login feature."""

import logging
import requests
from behave import given, when, then
from utils.helpers import (
    signup_user, verify_otp, login_user, forgot_password,
    reset_password, extract_token, OTP_PLACEHOLDER,
)

logger = logging.getLogger("auth_api_tests")


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------

@given("a verified user exists with known credentials")
def step_verified_user(context):
    resp, payload = signup_user(context.base_url)
    assert resp.status_code == 201, f"Signup failed: {resp.status_code} {resp.text}"
    context.email = payload["email"]
    context.payload = payload
    context.saved["password"] = payload["password"]
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    verify_resp = verify_otp(context.base_url, context.email, OTP_PLACEHOLDER)
    logger.info(
        f"Verified user setup: {context.email}, "
        f"verify status={verify_resp.status_code}"
    )


@given('a verified user exists with password "{password}"')
def step_verified_user_custom_pw(context, password):
    resp, payload = signup_user(context.base_url, password=password)
    assert resp.status_code == 201, f"Signup failed: {resp.status_code} {resp.text}"
    context.email = payload["email"]
    context.payload = payload
    context.saved["password"] = password
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    verify_otp(context.base_url, context.email, OTP_PLACEHOLDER)


@given("a new user has signed up but not verified")
def step_unverified_user(context):
    resp, payload = signup_user(context.base_url)
    assert resp.status_code == 201, f"Signup failed: {resp.status_code} {resp.text}"
    context.email = payload["email"]
    context.payload = payload
    context.saved["password"] = payload["password"]
    logger.info(f"Unverified user created: {context.email}")


@given("the user has a valid login token")
def step_user_has_token(context):
    resp = login_user(context.base_url, context.email, context.saved["password"])
    token = extract_token(resp)
    context.saved["old_token"] = token
    logger.info(f"Saved old token for {context.email}")


# ---------------------------------------------------------------------------
# When steps — login
# ---------------------------------------------------------------------------

@when("I login with the correct username and password")
def step_login_correct(context):
    context.response = login_user(
        context.base_url, context.email, context.saved["password"]
    )
    token = extract_token(context.response)
    if token:
        context.token = token


@when('I login with the correct username and wrong password "{password}"')
def step_login_wrong_pw(context, password):
    context.response = login_user(context.base_url, context.email, password)


@when('I login with username "{username}" and password "{password}"')
def step_login_custom(context, username, password):
    context.response = login_user(context.base_url, username, password)


@when("I login with the unverified user credentials")
def step_login_unverified(context):
    context.response = login_user(
        context.base_url, context.email, context.saved["password"]
    )


@when("I login with the email in uppercase")
def step_login_uppercase(context):
    context.response = login_user(
        context.base_url, context.email.upper(), context.saved["password"]
    )


@when("I login with empty password")
def step_login_empty_pw(context):
    context.response = login_user(context.base_url, context.email, "")


@when("I login with null password")
def step_login_null_pw(context):
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/login",
        json={"username": context.email, "password": None},
    )


@when("I send login request without username field")
def step_login_missing_username(context):
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/login",
        json={"password": "SomePass123!"},
    )


@when("I send 10 login requests with wrong password")
def step_brute_force(context):
    results = []
    for i in range(10):
        resp = login_user(context.base_url, context.email, f"WrongPass{i}!")
        results.append(resp.status_code)
        logger.info(f"Brute force attempt #{i+1}: status={resp.status_code}")
    context.saved["brute_force_results"] = results
    context.response = resp


# ---------------------------------------------------------------------------
# When steps — token usage
# ---------------------------------------------------------------------------

@when("I use the returned token for an authenticated request")
def step_use_token(context):
    token = context.token or extract_token(context.response)
    assert token, "No token available for authenticated request"
    # Try a generic authenticated endpoint — adjust if the API has a specific one
    context.saved["auth_response"] = requests.get(
        f"{context.base_url}/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )


@when("I use the old token for an authenticated request")
def step_use_old_token(context):
    token = context.saved.get("old_token")
    assert token, "No old token saved"
    context.saved["auth_response"] = requests.get(
        f"{context.base_url}/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )


@when('I use the saved "{token_key}" for an authenticated request')
def step_use_saved_token(context, token_key):
    token = context.saved.get(token_key)
    assert token, f"No token saved under key '{token_key}'"
    context.saved["auth_response"] = requests.get(
        f"{context.base_url}/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )


@then("the authenticated request should succeed")
def step_auth_success(context):
    resp = context.saved.get("auth_response")
    assert resp is not None, "No authenticated response captured"
    # Accept 200 or any 2xx as success
    assert 200 <= resp.status_code < 300, (
        f"Authenticated request failed: {resp.status_code} {resp.text[:300]}"
    )


@then("the authenticated request should return 401")
def step_auth_401(context):
    resp = context.saved.get("auth_response")
    assert resp is not None, "No authenticated response captured"
    assert resp.status_code == 401, (
        f"Expected 401 for old token, got {resp.status_code} {resp.text[:300]}"
    )


# ---------------------------------------------------------------------------
# When steps — password reset (used in login feature TC-L14)
# ---------------------------------------------------------------------------

@when("the user resets their password")
def step_user_resets_pw(context):
    forgot_resp = forgot_password(context.base_url, context.email)
    logger.info(f"Forgot password triggered: {forgot_resp.status_code}")
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    reset_resp = reset_password(
        context.base_url, context.email, OTP_PLACEHOLDER, "ResetNew999!"
    )
    context.saved["new_password"] = "ResetNew999!"
    logger.info(f"Password reset: {reset_resp.status_code}")


# ---------------------------------------------------------------------------
# When steps — E2E support
# ---------------------------------------------------------------------------

@when('I save the login token as "{key}"')
def step_save_token(context, key):
    token = context.token or extract_token(context.response)
    assert token, "No token to save"
    context.saved[key] = token
    logger.info(f"Saved token as '{key}'")


@when("I login with the old password")
def step_login_old_pw(context):
    context.response = login_user(
        context.base_url, context.email, context.saved["password"]
    )


@when('I login with the new password "{password}"')
def step_login_new_pw(context, password):
    context.response = login_user(context.base_url, context.email, password)


@when("I login as the new user")
def step_login_new_user(context):
    email = context.email or context.saved.get("email")
    password = context.saved.get("password", context.payload.get("password"))
    context.response = login_user(context.base_url, email, password)
