# Auth API — Behave BDD Test Framework

A comprehensive Behave BDD (Behaviour-Driven Development) automation framework for testing
an authentication REST API. Covers signup, OTP verification, OTP resend, login,
forgot password, password reset, security, and full end-to-end user journeys.

## Project Structure

```
auth-api-bdd/
├── behave.ini                  # Behave configuration and tags
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── README.md                   # This file
├── utils/
│   ├── __init__.py
│   └── helpers.py              # Shared helpers, payloads, constants
└── features/
    ├── environment.py          # Behave hooks (before_all, before_scenario, etc.)
    ├── signup.feature          # TC-S01 – TC-S35
    ├── otp_verify.feature      # TC-V01 – TC-V15
    ├── otp_resend.feature      # TC-R01 – TC-R10
    ├── login.feature           # TC-L01 – TC-L14
    ├── forgot_password.feature # TC-F01 – TC-F09
    ├── reset_password.feature  # TC-RP01 – TC-RP15
    ├── security.feature        # TC-SEC01 – TC-SEC12
    ├── e2e_journeys.feature    # TC-E01 – TC-E05
    └── steps/
        ├── __init__.py
        ├── common_steps.py         # Shared assertions (status, time, logging)
        ├── signup_steps.py         # Signup step implementations
        ├── otp_verify_steps.py     # OTP verify step implementations
        ├── otp_resend_steps.py     # OTP resend step implementations
        ├── login_steps.py          # Login step implementations
        ├── forgot_password_steps.py# Forgot password step implementations
        ├── reset_password_steps.py # Reset password step implementations
        ├── security_steps.py       # Security step implementations
        └── e2e_steps.py            # End-to-end journey step implementations
```

## Setup

```bash
# 1. Clone / copy the project
cd auth-api-bdd

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your BASE_URL and OTP provider keys
```

## Running Tests

```bash
# Run all tests with pretty output
behave

# Run with verbose output
behave --verbose

# Generate HTML report
behave -f html -o report.html

# Run a specific feature file
behave features/signup.feature
behave features/login.feature
behave features/security.feature
behave features/e2e_journeys.feature

# Run by tag — smoke tests only
behave --tags=@smoke

# Run by tag — security tests only
behave --tags=@security

# Run by tag — timing tests (OTP expiry)
behave --tags=@timing

# Run by tag — exclude slow timing tests
behave --tags=~@timing

# Run a specific scenario by name
behave --name="TC-S01"

# Dry run (validate feature files without executing)
behave --dry-run
```

## Tags

| Tag          | Description                                      |
|--------------|--------------------------------------------------|
| `@smoke`     | Core happy-path and E2E journey tests            |
| `@security`  | Security-focused tests (injection, enumeration)  |
| `@timing`    | Tests involving `sleep()` for OTP expiry          |
| `@signup`    | All signup feature tests                         |
| `@login`     | All login feature tests                          |
| `@otp_verify`| All OTP verification tests                       |
| `@otp_resend`| All OTP resend tests                             |
| `@forgot_password` | All forgot password tests                 |
| `@reset_password`  | All reset password tests                  |
| `@e2e`       | End-to-end journey tests                         |

## OTP Handling

This framework does **not** hardcode OTP values. Every test that requires a real
OTP is marked with:

```
# TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
```

To make OTP-dependent tests pass, integrate with your email provider:

1. **Mailtrap** — Use the Mailtrap API to fetch the latest email and extract the OTP.
2. **Mailinator** — Use the Mailinator API to read the inbox for `@mailinator.com` addresses.

Update `utils/helpers.py` with a function like:

```python
def fetch_otp_from_email(email: str) -> str:
    # Implement Mailtrap/Mailinator API call here
    # Parse the OTP from the email body
    # Return the 6-digit OTP as a string
    pass
```

## Key Design Decisions

- **Unique emails**: Every test generates a fresh UUID-based email to avoid cross-test pollution.
- **sleep(65)**: OTP expiry tests use 65 seconds (not 60) to absorb network latency, per spec.
- **Observation logging**: Tests where the outcome depends on server policy (e.g., rate limiting,
  duplicate phone) log the result instead of asserting a specific status.
- **Email-only OTP**: Per Rule 1, OTP is never tested via phone number.
- **Response time**: Every single test asserts `response.elapsed.total_seconds() < 2.0`.
