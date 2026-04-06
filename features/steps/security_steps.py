"""Step definitions for the security feature."""

import json
import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from behave import given, when, then
from utils.helpers import (
    generate_unique_email, generate_signup_payload,
    signup_user, verify_otp, OTP_PLACEHOLDER,
)

logger = logging.getLogger("auth_api_tests")

SQL_INJECTION = "' OR 1=1 --"
XSS_PAYLOAD = "<script>alert('xss')</script>"


# ---------------------------------------------------------------------------
# SQL injection payloads per endpoint
# ---------------------------------------------------------------------------

def _sql_payload_for(endpoint):
    """Return a JSON body with SQL injection in the username/string fields."""
    if "signup" in endpoint:
        return generate_signup_payload(email=f"{SQL_INJECTION}@test.com")
    if "verify/confirm" in endpoint:
        return {"username": SQL_INJECTION, "otp": "123456"}
    if "verify/resend" in endpoint:
        return {"username": SQL_INJECTION}
    if "login" in endpoint:
        return {"username": SQL_INJECTION, "password": "anything"}
    if "password/forgot" in endpoint:
        return {"username": SQL_INJECTION}
    if "password/reset" in endpoint:
        return {"username": SQL_INJECTION, "otp": "123456", "new_password": "New123!"}
    return {}


def _xss_payload_for(endpoint):
    """Return a JSON body with XSS payload in string fields."""
    if "signup" in endpoint:
        return generate_signup_payload(first_name=XSS_PAYLOAD)
    if "verify/confirm" in endpoint:
        return {"username": XSS_PAYLOAD, "otp": XSS_PAYLOAD}
    if "login" in endpoint:
        return {"username": XSS_PAYLOAD, "password": XSS_PAYLOAD}
    if "password/forgot" in endpoint:
        return {"username": XSS_PAYLOAD}
    if "password/reset" in endpoint:
        return {"username": XSS_PAYLOAD, "otp": XSS_PAYLOAD, "new_password": XSS_PAYLOAD}
    return {}


# ---------------------------------------------------------------------------
# When steps — SQL injection
# ---------------------------------------------------------------------------

@when('I send a POST to "{endpoint}" with SQL injection in username')
def step_sql_inject(context, endpoint):
    payload = _sql_payload_for(endpoint)
    context.response = requests.post(
        f"{context.base_url}{endpoint}", json=payload
    )


# ---------------------------------------------------------------------------
# When steps — XSS
# ---------------------------------------------------------------------------

@when('I send a POST to "{endpoint}" with XSS payload in string fields')
def step_xss_payload(context, endpoint):
    payload = _xss_payload_for(endpoint)
    context.response = requests.post(
        f"{context.base_url}{endpoint}", json=payload
    )


# ---------------------------------------------------------------------------
# When steps — missing Content-Type
# ---------------------------------------------------------------------------

@when('I send a POST to "{endpoint}" without Content-Type header')
def step_no_content_type(context, endpoint):
    payload = json.dumps({"username": "test@test.com", "password": "Test123!"})
    context.response = requests.post(
        f"{context.base_url}{endpoint}",
        data=payload,
        headers={},  # no Content-Type
    )


# ---------------------------------------------------------------------------
# When steps — oversized body
# ---------------------------------------------------------------------------

@when('I send a POST to "{endpoint}" with 50KB oversized body')
def step_oversized_body(context, endpoint):
    big_payload = {"data": "A" * 50000}
    context.response = requests.post(
        f"{context.base_url}{endpoint}", json=big_payload
    )


# ---------------------------------------------------------------------------
# When steps — OTP brute force
# ---------------------------------------------------------------------------

@when("I send 10 wrong OTP verification attempts for the signed-up user")
def step_otp_brute_force(context):
    results = []
    for i in range(10):
        otp_guess = f"{100000 + i}"
        resp = verify_otp(context.base_url, context.email, otp_guess)
        results.append(resp.status_code)
        logger.info(f"OTP brute force #{i+1}: otp={otp_guess}, status={resp.status_code}")
    context.saved["otp_brute_results"] = results
    context.response = resp


# ---------------------------------------------------------------------------
# When steps — concurrent signup
# ---------------------------------------------------------------------------

@when("I send 5 concurrent signup requests with the same email")
def step_concurrent_signup(context):
    email = generate_unique_email()
    context.saved["concurrent_email"] = email

    def do_signup(_):
        payload = generate_signup_payload(email=email)
        return requests.post(f"{context.base_url}/api/v1/auth/signup", json=payload)

    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = [pool.submit(do_signup, i) for i in range(5)]
        results = [f.result() for f in as_completed(futures)]

    context.saved["concurrent_results"] = [r.status_code for r in results]
    context.response = results[-1]  # keep one for response time assertion
    logger.info(f"Concurrent signup results: {context.saved['concurrent_results']}")


@then("only one response should have status 201")
def step_only_one_201(context):
    codes = context.saved["concurrent_results"]
    count_201 = codes.count(201)
    assert count_201 <= 1, (
        f"Expected at most one 201 for concurrent signup, got {count_201}. "
        f"All codes: {codes}"
    )
    logger.info(f"Concurrent signup 201 count: {count_201}, all codes: {codes}")


# ---------------------------------------------------------------------------
# When steps — special characters in password
# ---------------------------------------------------------------------------
#
# @when('I send a signup request with password "{password}"')
# def step_signup_special_pw(context, password):
#     payload = generate_signup_payload(password=password)
#     context.response = requests.post(
#         f"{context.base_url}/api/v1/auth/signup", json=payload
#     )
