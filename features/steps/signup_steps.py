"""Step definitions for the signup feature."""

import json
import logging
import requests
from behave import given, when, then
from utils.helpers import generate_unique_email, generate_signup_payload, signup_user

logger = logging.getLogger("auth_api_tests")


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------

@given("a user already signed up with a known email")
def step_existing_user(context):
    resp, payload = signup_user(context.base_url)
    assert resp.status_code == 201, f"Pre-signup failed: {resp.status_code} {resp.text}"
    context.email = payload["email"]
    context.payload = payload


@given('a user already signed up with phone "{phone}"')
def step_existing_user_phone(context, phone):
    resp, payload = signup_user(context.base_url)
    payload["phone"] = phone
    # Re-signup with specified phone
    resp = requests.post(
        f"{context.base_url}/api/v1/auth/signup", json=payload
    )
    # Might fail if phone reuse — use a fresh email for the first one
    first_payload = generate_signup_payload(phone=phone)
    first_resp = requests.post(
        f"{context.base_url}/api/v1/auth/signup", json=first_payload
    )
    context.saved["first_phone_signup"] = first_resp
    context.saved["phone"] = phone
    context.email = first_payload["email"]


# ---------------------------------------------------------------------------
# When steps — valid signup
# ---------------------------------------------------------------------------

@when("I send a signup request with valid data")
def step_valid_signup(context):
    resp, payload = signup_user(context.base_url)
    context.response = resp
    context.payload = payload
    context.email = payload["email"]


@when("I send a signup request with the same email")
def step_duplicate_email(context):
    payload = generate_signup_payload(email=context.email)
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/signup", json=payload
    )


@when('I send a signup request with the same phone "{phone}" but different email')
def step_duplicate_phone(context, phone):
    payload = generate_signup_payload(phone=phone)
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/signup", json=payload
    )


# ---------------------------------------------------------------------------
# When steps — missing / empty / null / whitespace fields
# ---------------------------------------------------------------------------

@when('I send a signup request missing the "{field}" field')
def step_missing_field(context, field):
    payload = generate_signup_payload()
    payload.pop(field, None)
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/signup", json=payload
    )


@when('I send a signup request with "{field}" set to empty string')
def step_empty_field(context, field):
    payload = generate_signup_payload()
    payload[field] = ""
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/signup", json=payload
    )


@when('I send a signup request with "{field}" set to null')
def step_null_field(context, field):
    payload = generate_signup_payload()
    payload[field] = None
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/signup", json=payload
    )


@when('I send a signup request with "{field}" set to whitespace only')
def step_whitespace_field(context, field):
    payload = generate_signup_payload()
    payload[field] = "   "
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/signup", json=payload
    )


# ---------------------------------------------------------------------------
# When steps — specific invalid values
# ---------------------------------------------------------------------------

@when('I send a signup request with email "{email}"')
def step_signup_custom_email(context, email):
    payload = generate_signup_payload(email=email)
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/signup", json=payload
    )


@when('I send a signup request with password "{password}"')
def step_signup_custom_password(context, password):
    payload = generate_signup_payload(password=password)
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/signup", json=payload
    )


@when('I send a signup request with phone "{phone}"')
def step_signup_custom_phone(context, phone):
    payload = generate_signup_payload(phone=phone)
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/signup", json=payload
    )


@when('I send a signup request with first_name "{first_name}"')
def step_signup_custom_firstname(context, first_name):
    payload = generate_signup_payload(first_name=first_name)
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/signup", json=payload
    )


# ---------------------------------------------------------------------------
# When steps — long values
# ---------------------------------------------------------------------------

@when('I send a signup request with "{field}" set to 500 character string')
def step_long_field(context, field):
    payload = generate_signup_payload()
    long_val = "A" * 500
    if field == "email":
        long_val = "A" * 490 + "@test.com"
    payload[field] = long_val
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/signup", json=payload
    )


# ---------------------------------------------------------------------------
# When steps — extra fields, wrong content type
# ---------------------------------------------------------------------------

@when("I send a signup request with extra unknown fields")
def step_extra_fields(context):
    payload = generate_signup_payload()
    payload["unknown_field"] = "some_value"
    payload["another_extra"] = 12345
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/signup", json=payload
    )


@when('I send a signup request with Content-Type "{content_type}"')
def step_wrong_content_type(context, content_type):
    payload = generate_signup_payload()
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/signup",
        data=json.dumps(payload),
        headers={"Content-Type": content_type},
    )
