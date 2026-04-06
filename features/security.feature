@security
Feature: Security Tests
  As a security engineer
  I want to verify the API handles malicious input safely
  So that the system is protected against common attacks

  Background:
    Given the auth API is available

  # TC-SEC01
  Scenario Outline: TC-SEC01 All endpoints return 405 for GET
    When I send a GET request to "<endpoint>"
    Then the response status code should be 405
    And the response time should be less than 2 seconds

    Examples:
      | endpoint                       |
      | /api/v1/auth/signup            |
      | /api/v1/auth/verify/confirm    |
      | /api/v1/auth/verify/resend     |
      | /api/v1/auth/login             |
      | /api/v1/auth/password/forgot   |
      | /api/v1/auth/password/reset    |

  # TC-SEC02
  Scenario Outline: TC-SEC02 SQL injection in username must not return 500
    When I send a POST to "<endpoint>" with SQL injection in username
    Then the response status code should not be 500
    And the response time should be less than 2 seconds

    Examples:
      | endpoint                       |
      | /api/v1/auth/verify/confirm    |
      | /api/v1/auth/verify/resend     |
      | /api/v1/auth/login             |
      | /api/v1/auth/password/forgot   |
      | /api/v1/auth/password/reset    |

  # TC-SEC03
  Scenario Outline: TC-SEC03 XSS payload in string fields must not reflect
    When I send a POST to "<endpoint>" with XSS payload in string fields
    Then the response status code should not be 500
    And the response body should not contain "<script>"
    And the response time should be less than 2 seconds

    Examples:
      | endpoint                       |
      | /api/v1/auth/signup            |
      | /api/v1/auth/verify/confirm    |
      | /api/v1/auth/login             |
      | /api/v1/auth/password/forgot   |
      | /api/v1/auth/password/reset    |

  # TC-SEC04
  Scenario: TC-SEC04 Login error messages never reveal if user exists
    When I login with username "nonexistent@mailinator.com" and password "AnyPass123!"
    Then the response body should not reveal user existence
    And the response time should be less than 2 seconds

  # TC-SEC05
  Scenario: TC-SEC05 Forgot password error messages never reveal if user exists
    When I trigger forgot password for username "nonexistent@mailinator.com"
    Then the response body should not reveal user existence
    And the response time should be less than 2 seconds

  # TC-SEC06
  Scenario: TC-SEC06 Resend error messages never reveal if user exists
    When I resend OTP for username "nonexistent@mailinator.com"
    Then the response body should not reveal user existence
    And the response time should be less than 2 seconds

  # TC-SEC07
  Scenario: TC-SEC07 OTP brute force on verify — 10 wrong guesses
    Given a new user has signed up
    When I send 10 wrong OTP verification attempts for the signed-up user
    Then I log the OTP brute force rate limiting behaviour

  # TC-SEC08
  Scenario: TC-SEC08 Concurrent signup with same email — only one 201
    When I send 5 concurrent signup requests with the same email
    Then only one response should have status 201

  # TC-SEC09
  Scenario: TC-SEC09 Token format is valid JWT with 3 dot-separated parts
    Given a verified user exists with known credentials
    When I login with the correct username and password
    Then the token should be a valid JWT format with 3 parts

  # TC-SEC10
  Scenario Outline: TC-SEC10 Missing Content-Type header must not return 500
    When I send a POST to "<endpoint>" without Content-Type header
    Then the response status code should not be 500
    And the response time should be less than 2 seconds

    Examples:
      | endpoint                       |
      | /api/v1/auth/signup            |
      | /api/v1/auth/verify/confirm    |
      | /api/v1/auth/verify/resend     |
      | /api/v1/auth/login             |
      | /api/v1/auth/password/forgot   |
      | /api/v1/auth/password/reset    |

  # TC-SEC11
  Scenario Outline: TC-SEC11 Oversized 50KB request body must not return 500
    When I send a POST to "<endpoint>" with 50KB oversized body
    Then the response status code should not be 500
    And the response time should be less than 2 seconds

    Examples:
      | endpoint                       |
      | /api/v1/auth/signup            |
      | /api/v1/auth/verify/confirm    |
      | /api/v1/auth/login             |
      | /api/v1/auth/password/forgot   |
      | /api/v1/auth/password/reset    |

  # TC-SEC12
  Scenario: TC-SEC12 Special characters in password do not crash the server
    When I send a signup request with password "P@$$w0rd!#%^&*() spaces"
    Then the response status code should not be 500
    And the response time should be less than 2 seconds
