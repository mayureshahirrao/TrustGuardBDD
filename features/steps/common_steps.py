"""Common step definitions shared across all feature files."""

import logging
import requests
from behave import given, when, then

logger = logging.getLogger("auth_api_tests")


# ---------------------------------------------------------------------------
# Background / Given
# ---------------------------------------------------------------------------

@given("the auth API is available")
def step_api_available(context):
    """Verify the base URL is configured."""
    assert context.base_url, "BASE_URL is not configured"


# ---------------------------------------------------------------------------
# GET request steps
# ---------------------------------------------------------------------------

@when('I send a GET request to "{endpoint}"')
def step_send_get(context, endpoint):
    url = f"{context.base_url}{endpoint}"
    context.response = requests.get(url)


# ---------------------------------------------------------------------------
# Status code assertions
# ---------------------------------------------------------------------------

@then("the response status code should be {status_code:d}")
def step_assert_status(context, status_code):
    assert context.response is not None, "No response captured"
    actual = context.response.status_code
    assert actual == status_code, (
        f"Expected {status_code}, got {actual}. Body: {context.response.text[:500]}"
    )


@then("the response status code should not be {status_code:d}")
def step_assert_not_status(context, status_code):
    assert context.response is not None, "No response captured"
    actual = context.response.status_code
    assert actual != status_code, (
        f"Expected NOT {status_code}, but got {actual}. Body: {context.response.text[:500]}"
    )


@then("the response status code should be one of {code1:d} or {code2:d}")
def step_assert_status_one_of(context, code1, code2):
    assert context.response is not None, "No response captured"
    actual = context.response.status_code
    assert actual in (code1, code2), (
        f"Expected {code1} or {code2}, got {actual}. Body: {context.response.text[:500]}"
    )


# ---------------------------------------------------------------------------
# Response time assertion
# ---------------------------------------------------------------------------

@then("the response time should be less than {seconds:d} seconds")
def step_assert_response_time(context, seconds):
    assert context.response is not None, "No response captured"
    elapsed = context.response.elapsed.total_seconds()
    assert elapsed < seconds, (
        f"Response took {elapsed:.2f}s, exceeding {seconds}s limit"
    )


# ---------------------------------------------------------------------------
# Body content assertions
# ---------------------------------------------------------------------------

@then("the response body should contain a success indicator")
def step_assert_success_indicator(context):
    body = context.response.json()
    # Check for common success indicators in the response
    text = str(body).lower()
    has_success = any(k in text for k in ("success", "created", "message", "id", "user"))
    assert has_success, f"No success indicator found in response: {body}"


@then('the response body should not contain "{text}"')
def step_assert_body_not_contain(context, text):
    body_text = context.response.text
    assert text not in body_text, (
        f"Response body should not contain '{text}' but it does: {body_text[:500]}"
    )


@then("the response body should not reveal user existence")
def step_assert_no_user_existence_leak(context):
    from utils.helpers import SENSITIVE_PHRASES

    body_text = context.response.text.lower()
    for phrase in SENSITIVE_PHRASES:
        assert phrase not in body_text, (
            f"Security issue: response reveals user existence with '{phrase}'. "
            f"Body: {context.response.text[:500]}"
        )


# ---------------------------------------------------------------------------
# Token assertions
# ---------------------------------------------------------------------------

@then("the response body should contain a token")
def step_assert_token_present(context):
    from utils.helpers import extract_token

    token = extract_token(context.response)
    assert token is not None, (
        f"No token found in response body: {context.response.text[:500]}"
    )
    context.token = token


@then("the token value should be non-empty")
def step_assert_token_nonempty(context):
    from utils.helpers import extract_token

    token = context.token or extract_token(context.response)
    assert token and len(token) > 0, "Token is empty or missing"
    context.token = token


@then("the token should be a valid JWT format with 3 parts")
def step_assert_jwt_format(context):
    from utils.helpers import extract_token

    token = context.token or extract_token(context.response)
    assert token, "No token to validate"
    parts = token.split(".")
    assert len(parts) == 3, (
        f"Token does not look like JWT (expected 3 dot-separated parts, got {len(parts)})"
    )


# ---------------------------------------------------------------------------
# Wait / timing steps
# ---------------------------------------------------------------------------

@when("I wait {seconds:d} seconds")
def step_wait(context, seconds):
    import time
    logger.info(f"Sleeping {seconds} seconds...")
    time.sleep(seconds)


@when("I wait {seconds:d} seconds for OTP to expire")
def step_wait_otp_expire(context, seconds):
    import time
    logger.info(f"Sleeping {seconds}s to let OTP expire...")
    time.sleep(seconds)


# ---------------------------------------------------------------------------
# Logging steps (for tests where outcome is observed, not asserted)
# ---------------------------------------------------------------------------

@then("I log the response status and body for duplicate phone")
def step_log_duplicate_phone(context):
    logger.info(
        f"[OBSERVATION] Duplicate phone signup — "
        f"Status: {context.response.status_code}, Body: {context.response.text[:300]}"
    )


@then("I log the response status and body for short password")
def step_log_short_password(context):
    logger.info(
        f"[OBSERVATION] Short password signup — "
        f"Status: {context.response.status_code}, Body: {context.response.text[:300]}"
    )


@then("I log the response status and body for phone with letters")
def step_log_phone_letters(context):
    logger.info(
        f"[OBSERVATION] Phone with letters signup — "
        f"Status: {context.response.status_code}, Body: {context.response.text[:300]}"
    )


@then("I log the response status and body for already verified user")
def step_log_already_verified(context):
    logger.info(
        f"[OBSERVATION] Already-verified user verify again — "
        f"Status: {context.response.status_code}, Body: {context.response.text[:300]}"
    )


@then("I log the response status and body for resend to verified user")
def step_log_resend_verified(context):
    logger.info(
        f"[OBSERVATION] Resend OTP for verified user — "
        f"Status: {context.response.status_code}, Body: {context.response.text[:300]}"
    )


@then("I log whether the server enforces a 60 second cooldown")
def step_log_cooldown(context):
    logger.info(
        f"[OBSERVATION] Immediate resend cooldown — "
        f"Status: {context.response.status_code}, Body: {context.response.text[:300]}"
    )
    if context.response.status_code == 200:
        logger.info("[OBSERVATION] Server does NOT enforce 60s cooldown (UI-only)")
    else:
        logger.info("[OBSERVATION] Server enforces 60s cooldown")


@then("I log the rate limiting behaviour")
def step_log_rate_limit(context):
    results = context.saved.get("rapid_resend_results", [])
    blocked = [r for r in results if r != 200]
    logger.info(
        f"[OBSERVATION] Rapid resend 10x — "
        f"Success count: {len(results) - len(blocked)}, Blocked count: {len(blocked)}"
    )
    if blocked:
        logger.info(f"[OBSERVATION] Server rate-limits resend. Blocked codes: {blocked}")
    else:
        logger.info("[OBSERVATION] Server does NOT rate-limit resend")


@then("I log the brute force rate limiting behaviour")
def step_log_brute_force(context):
    results = context.saved.get("brute_force_results", [])
    non_401 = [r for r in results if r != 401]
    logger.info(
        f"[OBSERVATION] 10 failed login attempts — "
        f"Codes: {results}"
    )
    if any(r == 429 for r in results):
        logger.info("[OBSERVATION] Server rate-limits brute force with 429")
    elif non_401:
        logger.info(f"[OBSERVATION] Non-401 codes seen: {non_401} — possible lock/block")
    else:
        logger.info("[OBSERVATION] Server does NOT rate-limit or lock brute force")


@then("I log the OTP brute force rate limiting behaviour")
def step_log_otp_brute_force(context):
    results = context.saved.get("otp_brute_results", [])
    logger.info(
        f"[OBSERVATION] 10 wrong OTP attempts — Codes: {results}"
    )
    if any(r == 429 for r in results):
        logger.info("[OBSERVATION] Server rate-limits OTP brute force")
    else:
        logger.info("[OBSERVATION] Server does NOT rate-limit OTP brute force")


@then("I log the response status and body for case sensitivity")
def step_log_case_sensitivity(context):
    logger.info(
        f"[OBSERVATION] Email case sensitivity — "
        f"Status: {context.response.status_code}, Body: {context.response.text[:300]}"
    )


@then("I log the response status and body for unverified forgot password")
def step_log_unverified_forgot(context):
    logger.info(
        f"[OBSERVATION] Unverified user forgot password — "
        f"Status: {context.response.status_code}, Body: {context.response.text[:300]}"
    )


@then("I log whether second OTP invalidates the first")
def step_log_second_otp_invalidation(context):
    logger.info(
        f"[OBSERVATION] Double forgot password trigger — "
        f"Status: {context.response.status_code}, Body: {context.response.text[:300]}"
    )


@then("I log the response for same-as-old password policy")
def step_log_same_password(context):
    logger.info(
        f"[OBSERVATION] Same-as-old password reset — "
        f"Status: {context.response.status_code}, Body: {context.response.text[:300]}"
    )


@then("I log the response for weak password policy")
def step_log_weak_password(context):
    logger.info(
        f"[OBSERVATION] Weak new password reset — "
        f"Status: {context.response.status_code}, Body: {context.response.text[:300]}"
    )
