"""Utility helpers for the auth API BDD test framework."""

import uuid
import time
import requests
import logging

logger = logging.getLogger("auth_api_tests")


def generate_unique_email():
    """Generate a unique email using uuid to avoid collisions across tests."""
    return f"test_{uuid.uuid4().hex[:8]}@mailinator.com"


def generate_signup_payload(email=None, first_name="Test", last_name="User",
                            phone="9876543210", password="SecurePass123!"):
    """Build a complete signup payload with all 5 mandatory fields."""
    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email or generate_unique_email(),
        "phone": phone,
        "password": password,
    }


def signup_user(base_url, email=None, password="SecurePass123!"):
    """Signup a new user and return (response, payload)."""
    payload = generate_signup_payload(email=email, password=password)
    resp = requests.post(f"{base_url}/api/v1/auth/signup", json=payload)
    return resp, payload


def verify_otp(base_url, username, otp):
    """Verify an OTP for a given username."""
    return requests.post(
        f"{base_url}/api/v1/auth/verify/confirm",
        json={"username": username, "otp": otp},
    )


def resend_otp(base_url, username):
    """Resend OTP for a given username."""
    return requests.post(
        f"{base_url}/api/v1/auth/verify/resend",
        json={"username": username},
    )


def login_user(base_url, username, password):
    """Login and return the response."""
    return requests.post(
        f"{base_url}/api/v1/auth/login",
        json={"username": username, "password": password},
    )


def forgot_password(base_url, username):
    """Trigger forgot-password flow for a username."""
    return requests.post(
        f"{base_url}/api/v1/auth/password/forgot",
        json={"username": username},
    )


def reset_password(base_url, username, otp, new_password):
    """Reset the password using an OTP."""
    return requests.post(
        f"{base_url}/api/v1/auth/password/reset",
        json={"username": username, "otp": otp, "new_password": new_password},
    )


def extract_token(response):
    """Extract the auth token from a login response body."""
    body = response.json()
    # Try common key names
    for key in ("token", "access_token", "auth_token", "data"):
        if key in body:
            val = body[key]
            if isinstance(val, dict) and "token" in val:
                return val["token"]
            if isinstance(val, str) and val:
                return val
    return None


OTP_PLACEHOLDER = "000000"  # TODO: replace with real OTP from Mailtrap or Mailinator


# All endpoints for cross-cutting security tests
ALL_ENDPOINTS = [
    "/api/v1/auth/signup",
    "/api/v1/auth/verify/confirm",
    "/api/v1/auth/verify/resend",
    "/api/v1/auth/login",
    "/api/v1/auth/password/forgot",
    "/api/v1/auth/password/reset",
]

SENSITIVE_PHRASES = [
    "user not found",
    "no user",
    "email not registered",
    "email already registered",
    "account not found",
    "does not exist",
    "not exist",
    "unknown user",
    "invalid user",
]
