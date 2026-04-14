# TrustGuardBDD — Behave BDD Framework: Complete Guide

---

## 1. What is Behave?

Behave is a Python-based Behaviour-Driven Development (BDD) framework that lets you write test specifications in plain English using the Gherkin language. Tests are expressed as human-readable **Feature files** containing **Scenarios**, which are then mapped to Python code in **Step Definition** files. This separation means non-technical stakeholders can read and validate the test specifications while developers and QA engineers implement the automation logic separately.

---

## 2. Project Folder Structure

```
TrustGuardBDD/
│
├── behave.ini                          ← Behave configuration file
├── requirements.txt                    ← Python dependencies
├── .env.example                        ← Environment variable template
├── README.md                           ← Project documentation
│
├── utils/                              ← Shared utility modules
│   ├── __init__.py                     ← Makes utils a Python package
│   └── helpers.py                      ← Reusable API functions and constants
│
├── features/                           ← Root directory for all Behave content
│   ├── __init__.py                     ← Makes features a Python package
│   ├── environment.py                  ← Behave hooks (lifecycle callbacks)
│   │
│   ├── signup.feature                  ← Feature file: User Signup API
│   ├── otp_verify.feature              ← Feature file: OTP Verification API
│   ├── otp_resend.feature              ← Feature file: OTP Resend API
│   ├── login.feature                   ← Feature file: Login API
│   ├── forgot_password.feature         ← Feature file: Forgot Password API
│   ├── reset_password.feature          ← Feature file: Password Reset API
│   ├── security.feature                ← Feature file: Security Tests
│   ├── e2e_journeys.feature            ← Feature file: End-to-End Journeys
│   │
│   └── steps/                          ← Step definition files (Python code)
│       ├── __init__.py                 ← Makes steps a Python package
│       ├── common_steps.py             ← Shared assertions (status, time, body)
│       ├── signup_steps.py             ← Step implementations for signup.feature
│       ├── otp_verify_steps.py         ← Step implementations for otp_verify.feature
│       ├── otp_resend_steps.py         ← Step implementations for otp_resend.feature
│       ├── login_steps.py              ← Step implementations for login.feature
│       ├── forgot_password_steps.py    ← Step implementations for forgot_password.feature
│       ├── reset_password_steps.py     ← Step implementations for reset_password.feature
│       ├── security_steps.py           ← Step implementations for security.feature
│       └── e2e_steps.py                ← Step implementations for e2e_journeys.feature
│
├── playwright_tests/                   ← Playwright test suite (extension)
│   ├── pages/                          ← Page Object Model classes
│   ├── tests/                          ← Playwright test spec files
│   └── utils/                          ← Shared helpers and fixtures
│
└── playwright.config.ts                ← Playwright configuration
```

### What each directory and file does

**`behave.ini`** — The central configuration file for Behave. It sets the path where feature files are located, the output format (pretty, JSON, HTML), whether stdout/stderr are captured, and default tags that control which tests run. It also stores user-defined data like the `base_url`.

**`features/`** — Behave requires all `.feature` files to live under this directory (or whatever path is configured in `behave.ini`). This is the root of the test suite.

**`features/environment.py`** — Contains lifecycle hook functions that Behave calls at specific points during execution. These hooks set up shared state (like `base_url`), reset per-scenario variables, and log outcomes.

**`features/steps/`** — All step definition files must live inside a `steps/` subdirectory within the `features/` folder. Behave scans every `.py` file in this directory and registers the step functions.

**`utils/helpers.py`** — A pure Python module with reusable functions for making API calls (`signup_user`, `verify_otp`, `login_user`, etc.), generating test data, and defining constants. Step definitions import from here to keep the step files focused on "what" rather than "how."

---

## 3. Behave Keywords — Detailed Reference

### 3.1 Feature

```gherkin
Feature: User Signup API
  As a new user
  I want to register with the authentication API
  So that I can create an account and access the system
```

**Role in the framework:** A `Feature` is the top-level grouping unit. Each `.feature` file contains exactly one `Feature` block. It represents a single capability or area of the application under test.

**How it works:** The three-line "As a / I want / So that" description beneath the `Feature` keyword follows the user story format. Behave does not execute this text — it serves purely as documentation for anyone reading the test. The `Feature` keyword groups all the `Scenario` blocks that follow it.

**In TrustGuardBDD:** Each API endpoint or concern has its own feature file. For example, `signup.feature` covers the `/api/v1/auth/signup` endpoint, while `security.feature` covers cross-cutting security concerns across all endpoints.

---

### 3.2 Background

```gherkin
Background:
  Given the auth API is available
```

**Role in the framework:** A `Background` block defines steps that run **before every Scenario** within the same Feature file. It eliminates duplication when every scenario shares the same precondition.

**How it works:** Behave executes the `Background` steps before each `Scenario` in the feature, not once for the entire file. If a Background step fails, the scenario is marked as failed and its remaining steps are skipped.

**In TrustGuardBDD:** Every feature file uses `Background: Given the auth API is available` to verify that the `BASE_URL` is configured before running any test. The step definition simply asserts that `context.base_url` is truthy.

---

### 3.3 Scenario

```gherkin
Scenario: TC-S01 Valid signup with all 5 mandatory fields
  When I send a signup request with valid data
  Then the response status code should be 201
  And the response body should contain a success indicator
```

**Role in the framework:** A `Scenario` is a single test case. It describes one specific behaviour of the system using a sequence of Given/When/Then steps.

**How it works:** Each Scenario runs in isolation. Behave creates a fresh `context` object and runs the Background (if any) followed by the Scenario's own steps. If any step fails, subsequent steps in that Scenario are skipped and the Scenario is marked failed.

**In TrustGuardBDD:** Scenarios are numbered with a test case ID (e.g., `TC-S01`, `TC-L14`, `TC-SEC08`) for traceability back to a test plan.

---

### 3.4 Scenario Outline (with Examples)

```gherkin
Scenario Outline: TC-S04-S08 Signup fails when <field> is missing
  When I send a signup request missing the "<field>" field
  Then the response status code should be 400

  Examples:
    | field      |
    | first_name |
    | last_name  |
    | email      |
    | phone      |
    | password   |
```

**Role in the framework:** A `Scenario Outline` is a parameterised test template. It runs the same sequence of steps multiple times, once for each row in the `Examples` table. Angle-bracket placeholders like `<field>` are substituted with the table values.

**How it works:** Behave expands the outline into N concrete scenarios (one per Examples row). Each expansion is an independent test — if `first_name` fails, `last_name` still runs. The `Examples` keyword introduces a pipe-delimited data table where the header row names the parameters and each subsequent row provides one set of values.

**In TrustGuardBDD:** This pattern is used extensively to test missing fields (TC-S04–S08), empty strings (TC-S09–S13), null values (TC-S14–S18), whitespace-only values (TC-S19–S23), and to run the same security test across all six endpoints (TC-SEC01–SEC03, SEC10–SEC11).

---

### 3.5 Given

```gherkin
Given a verified user exists with known credentials
```

**Role in the framework:** `Given` steps establish the **preconditions** for the test. They put the system into a known state before the action under test occurs.

**How it works:** In the step definition file, a `Given` step is decorated with `@given(pattern)`. Behave matches the Gherkin text to the pattern and calls the corresponding Python function, passing the `context` object.

**In TrustGuardBDD:** Given steps perform setup actions like creating a user (`signup_user`), verifying that user, or triggering a forgot-password flow. Examples:

- `Given a new user has signed up` — Calls `signup_user()` and stores the email/password on `context`.
- `Given a verified user exists with known credentials` — Signs up a user AND verifies their OTP.
- `Given the user has triggered forgot password` — Calls `forgot_password()` after the user is set up.

---

### 3.6 When

```gherkin
When I login with the correct username and password
```

**Role in the framework:** `When` steps describe the **action** being tested. This is the "do something" part of the test.

**How it works:** Decorated with `@when(pattern)`. The function performs the action (usually an API call) and stores the response on `context.response` so that `Then` steps can inspect it.

**In TrustGuardBDD:** When steps make HTTP requests using the helper functions from `utils/helpers.py`. Examples:

- `When I send a signup request with valid data` — Posts to `/api/v1/auth/signup`.
- `When I verify the OTP "123456" for the signed-up user` — Posts to `/api/v1/auth/verify/confirm`.
- `When I resend OTP 10 times rapidly for the signed-up user` — Loops 10 POST requests and collects results.

---

### 3.7 Then

```gherkin
Then the response status code should be 200
And the response body should contain a token
```

**Role in the framework:** `Then` steps define the **expected outcome**. They make assertions about what should have happened as a result of the When step.

**How it works:** Decorated with `@then(pattern)`. The function reads `context.response` and uses Python `assert` statements to verify expectations. If an assertion fails, the step fails and the scenario is marked failed.

**In TrustGuardBDD:** Then steps check HTTP status codes, response body contents, response time, and security properties. Examples:

- `Then the response status code should be 201` — Asserts `context.response.status_code == 201`.
- `Then the response body should not reveal user existence` — Checks that the response text doesn't contain phrases like "user not found" or "email not registered."
- `Then the response time should be less than 2 seconds` — Asserts `response.elapsed.total_seconds() < 2.0`.

---

### 3.8 And / But

```gherkin
Then the response status code should be 200
And the response body should contain a token
And the token value should be non-empty
And the response time should be less than 2 seconds
```

**Role in the framework:** `And` and `But` are syntactic sugar. They continue the previous step type (Given, When, or Then). `And` after a `Then` is treated as another `Then`. `But` works the same way but reads better for negative conditions ("But the status should not be 500").

**How it works:** Behave treats `And` and `But` identically to whatever keyword preceded them. They don't require separate decorators — you use `@given`, `@when`, or `@then` depending on what the step logically represents.

**In TrustGuardBDD:** `And` is used extensively to chain multiple assertions after a `Then`, and to chain multiple actions after a `When`. For example, in the E2E journey TC-E02, several `When` and `Then` steps are connected with `And` to form a multi-step flow within a single Scenario.

---

### 3.9 Tags

```gherkin
@signup
Feature: User Signup API

  @smoke
  Scenario: TC-S01 Valid signup with all 5 mandatory fields

  @security
  Scenario: TC-S30 SQL injection in email field does not cause 500

  @timing
  Scenario: TC-V04 Expired OTP after 65 seconds is rejected
```

**Role in the framework:** Tags are metadata labels prefixed with `@` that you attach to Features or Scenarios. They let you selectively run subsets of tests from the command line.

**How it works:** Tags can be placed on a line before `Feature`, `Scenario`, or `Scenario Outline`. A Feature-level tag is inherited by all its Scenarios. You run tagged tests with `behave --tags=@smoke` or exclude them with `behave --tags=~@timing`. Boolean combinations work too: `behave --tags="@smoke and not @security"`.

**In TrustGuardBDD:** The framework uses these tags:

| Tag | Purpose |
|-----|---------|
| `@smoke` | Core happy-path tests for quick validation |
| `@security` | Tests for SQL injection, XSS, enumeration, brute force |
| `@timing` | Tests that use `sleep()` to wait for OTP expiry (slow) |
| `@signup`, `@login`, etc. | Feature-level tags for running one module at a time |
| `@e2e` | End-to-end journey tests spanning multiple endpoints |
| `@wip` | Work-in-progress; excluded by default via `behave.ini` |

---

### 3.10 The Context Object

While not a Gherkin keyword, `context` is the most important runtime concept in Behave.

**Role in the framework:** `context` is a shared data container passed to every step function. It holds state that flows between Given → When → Then within a single Scenario.

**How it works:** Behave creates a new `context` object per Scenario. Steps store values on it (e.g., `context.response = resp`, `context.email = payload["email"]`), and later steps read those values. The `context` also provides built-in attributes: `context.feature`, `context.scenario`, and anything set in environment hooks.

**In TrustGuardBDD:** The framework uses these context attributes:

- `context.base_url` — Set in `before_all`, read by every API call.
- `context.response` — The HTTP response from the most recent API call.
- `context.email` — The email of the user created in the current scenario.
- `context.payload` — The full signup payload, for reference.
- `context.token` — The auth token after a successful login.
- `context.saved` — A general-purpose dictionary for multi-step scenarios (e.g., storing `old_token`, `brute_force_results`, `rapid_resend_results`).

---

## 4. Environment Hooks (environment.py)

Environment hooks are special functions in `environment.py` that Behave calls at specific lifecycle points.

### before_all(context)

Called once before any feature runs. In TrustGuardBDD, this loads the `.env` file, reads the `BASE_URL`, and stores it on `context.base_url`.

### before_scenario(context, scenario)

Called before every scenario. Resets per-scenario state: `context.response`, `context.email`, `context.token`, and `context.saved` are all cleared to prevent data leaking between tests.

### after_scenario(context, scenario)

Called after every scenario completes (whether it passed or failed). In TrustGuardBDD, this logs the scenario name and its pass/fail status for observability.

### Other available hooks (not used in this project but available)

- `before_feature(context, feature)` / `after_feature(context, feature)` — Run before/after each Feature file.
- `before_step(context, step)` / `after_step(context, step)` — Run before/after every individual step.
- `before_tag(context, tag)` / `after_tag(context, tag)` — Run before/after scenarios with a specific tag.
- `after_all(context)` — Run once after all features complete.

---

## 5. Step Definitions — How Matching Works

```python
@when('I send a signup request with email "{email}"')
def step_signup_custom_email(context, email):
    payload = generate_signup_payload(email=email)
    context.response = requests.post(
        f"{context.base_url}/api/v1/auth/signup", json=payload
    )
```

### Pattern matching

Behave matches the Gherkin text to the decorator string using these rules:

- **Quoted parameters** — `"{email}"` captures the Gherkin value `"invalidemail.com"` and passes it as a Python string argument named `email`.
- **Typed parameters** — `{status_code:d}` captures an integer. The `:d` suffix tells Behave to parse it as a decimal integer.
- **Multiple parameters** — A pattern can have multiple placeholders: `'I verify the OTP "{otp}" for username "{username}"'`.
- **Global registry** — Step definitions from ALL files in `features/steps/` are registered globally. A step in `common_steps.py` can be used by any feature file.

### The `context` parameter

Every step function receives `context` as its first argument. Additional arguments come from the pattern placeholders.

---

## 6. Observation Logging Pattern

A distinctive design choice in TrustGuardBDD is the "observation logging" pattern for tests where the expected behaviour depends on server policy:

```gherkin
Then I log the response status and body for duplicate phone
Then I log whether the server enforces a 60 second cooldown
Then I log the rate limiting behaviour
Then I log the brute force rate limiting behaviour
```

These steps do not assert a specific status code. Instead, they log what the server actually returns, making the tests informative rather than brittle. This is useful when server policies like rate limiting or duplicate-phone handling are not yet specified.

---

## 7. Configuration (behave.ini)

```ini
[behave]
paths = features                    # Where to find .feature files
format = pretty                     # Console output format
stdout_capture = false              # Don't suppress print statements
stderr_capture = false              # Don't suppress error output
log_capture = false                 # Don't suppress logging output
show_timings = true                 # Show execution time per step
default_tags = ~@wip                # Exclude @wip tests by default

[behave.formatters]
html = behave_html_formatter:HTMLFormatter   # Enable HTML report formatter

[behave.userdata]
base_url = http://13.232.201.222:8000       # Default API base URL
```

---

## 8. Running the Framework — Quick Reference

```bash
# Run everything
behave

# Run one feature file
behave features/signup.feature

# Run only smoke tests
behave --tags=@smoke

# Run security tests excluding slow timing tests
behave --tags="@security and not @timing"

# Run a specific scenario by name
behave --name="TC-S01"

# Generate an HTML report
behave -f html -o report.html

# Dry run (validate syntax without executing)
behave --dry-run

# Verbose output
behave --verbose
```

---

## 9. Summary: How Everything Connects

```
                    ┌──────────────────┐
                    │   behave.ini     │  Configuration: paths, tags, format
                    └───────┬──────────┘
                            │
                    ┌───────▼──────────┐
                    │  environment.py  │  Hooks: before_all, before_scenario, etc.
                    └───────┬──────────┘
                            │ sets context.base_url
                            │
          ┌─────────────────▼─────────────────┐
          │         .feature files             │
          │  (Gherkin: Feature, Scenario,      │
          │   Given, When, Then, Tags)         │
          └─────────────────┬─────────────────┘
                            │ pattern matching
                            │
          ┌─────────────────▼─────────────────┐
          │      features/steps/*.py           │
          │  (Step definitions: @given,        │
          │   @when, @then decorators)         │
          └─────────────────┬─────────────────┘
                            │ imports
                            │
          ┌─────────────────▼─────────────────┐
          │       utils/helpers.py             │
          │  (API calls, payload generators,   │
          │   token extraction, constants)     │
          └───────────────────────────────────┘
```

1. **behave.ini** tells Behave where to find tests and how to run them.
2. **environment.py** hooks set up global state and reset per-scenario state.
3. **.feature files** define the test specifications in plain English using Gherkin keywords.
4. **Step definition files** contain the Python functions that execute each Gherkin step.
5. **utils/helpers.py** provides reusable API functions so step definitions stay clean and focused.

This architecture keeps test intent (what to test) separate from test implementation (how to test it), making the suite maintainable and extensible.
