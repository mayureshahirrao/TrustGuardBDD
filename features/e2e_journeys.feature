@e2e @smoke
Feature: End-to-End User Journeys
  As a QA engineer
  I want to validate complete user workflows across multiple endpoints
  So that I can confirm the system works as a cohesive whole

  Background:
    Given the auth API is available

  # TC-E01
  Scenario: TC-E01 New user full journey — signup, verify, login
    When I sign up a new user with valid data
    Then the response status code should be 201
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    When I verify the signup OTP "OTP_PLACEHOLDER" for the new user
    Then the response status code should be 200
    When I login as the new user
    Then the response status code should be 200
    And the response body should contain a token
    And the token value should be non-empty
    And the response time should be less than 2 seconds

  # TC-E02
  Scenario: TC-E02 Existing user forgot password full journey
    Given a verified user exists with known credentials
    When I login with the correct username and password
    Then the response status code should be 200
    And I save the login token as "old_token"
    When I trigger forgot password for the verified user
    Then the response status code should be 200
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    When I reset the password with OTP "OTP_PLACEHOLDER" and new password "BrandNew789!"
    Then the response status code should be 200
    When I login with the old password
    Then the response status code should be 401
    When I login with the new password "BrandNew789!"
    Then the response status code should be 200
    And the response body should contain a token
    When I use the saved "old_token" for an authenticated request
    Then the authenticated request should return 401

  # TC-E03
  Scenario: TC-E03 Unverified user cannot login until verified
    When I sign up a new user with valid data
    Then the response status code should be 201
    When I login as the new user
    Then the response status code should be one of 401 or 403
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    When I verify the signup OTP "OTP_PLACEHOLDER" for the new user
    Then the response status code should be 200
    When I login as the new user
    Then the response status code should be 200
    And the response body should contain a token
    And the response time should be less than 2 seconds

  # TC-E04
  @timing
  Scenario: TC-E04 OTP resend timer journey — expiry and renewal
    When I sign up a new user with valid data at T=0
    Then the response status code should be 201
    # OTP-A is issued at T=0
    When I wait 30 seconds
    And I resend OTP for the new user
    Then the response status code should be 200
    # OTP-B is issued at T=30
    # TODO: replace OTP_A_PLACEHOLDER with original OTP from Mailtrap or Mailinator
    When I verify the OTP "OTP_A_PLACEHOLDER" for the new user
    Then the response status code should not be 200
    # OTP-A must fail because resend invalidated it
    When I wait 65 seconds
    # Now at T=95 — OTP-B (issued at T=30) expired at T=90
    # TODO: replace OTP_B_PLACEHOLDER with resent OTP from Mailtrap or Mailinator
    When I verify the OTP "OTP_B_PLACEHOLDER" for the new user
    Then the response status code should not be 200
    # OTP-B expired
    When I resend OTP for the new user
    Then the response status code should be 200
    # OTP-C issued now
    # TODO: replace OTP_C_PLACEHOLDER with latest OTP from Mailtrap or Mailinator
    When I verify the OTP "OTP_C_PLACEHOLDER" for the new user
    Then the response status code should be 200
    And the response time should be less than 2 seconds

  # TC-E05
  Scenario: TC-E05 OTP scope isolation — signup OTP vs reset OTP
    When I sign up a new user with valid data
    Then the response status code should be 201
    # TODO: replace OTP_PLACEHOLDER with real signup OTP from Mailtrap or Mailinator
    # Signup OTP is OTP-SIGNUP
    When I verify the signup OTP "OTP_PLACEHOLDER" for the new user
    Then the response status code should be 200
    When I trigger forgot password for the new user
    Then the response status code should be 200
    # Reset OTP is OTP-RESET
    # TODO: replace RESET_OTP_PLACEHOLDER with real reset OTP from Mailtrap or Mailinator
    # Try reset OTP on verify endpoint — must fail
    When I verify the OTP "RESET_OTP_PLACEHOLDER" for the new user
    Then the response status code should not be 200
    # Try signup OTP on reset endpoint — must fail
    When I reset the password with OTP "OTP_PLACEHOLDER" and new password "ScopeTest123!"
    Then the response status code should not be 200
    # Use correct OTP on correct endpoint
    When I reset the password with OTP "RESET_OTP_PLACEHOLDER" and new password "ScopeTest123!"
    Then the response status code should be 200
    And the response time should be less than 2 seconds
