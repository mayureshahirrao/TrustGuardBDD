@otp_resend
Feature: OTP Resend API
  As a user who did not receive or lost their OTP
  I want to request a new OTP
  So that I can complete verification

  Background:
    Given the auth API is available

  # TC-R01
  @smoke
  Scenario: TC-R01 Resend OTP for unverified user succeeds
    Given a new user has signed up
    When I resend OTP for the signed-up user
    Then the response status code should be 200
    And the response time should be less than 2 seconds

  # TC-R02
  Scenario: TC-R02 Resend immediately — server cooldown check
    Given a new user has signed up
    When I resend OTP for the signed-up user
    And I immediately resend OTP for the signed-up user again
    Then I log whether the server enforces a 60 second cooldown

  # TC-R03
  Scenario: TC-R03 Old OTP fails after resend even if not time-expired
    Given a new user has signed up
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    And the original OTP is "OTP_PLACEHOLDER"
    When I resend OTP for the signed-up user
    And I verify the original OTP for the signed-up user
    Then the response status code should be 400
    And the response time should be less than 2 seconds

  # TC-R04
  Scenario: TC-R04 New OTP works after resend
    Given a new user has signed up
    When I resend OTP for the signed-up user
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    And I verify the OTP "OTP_PLACEHOLDER" for the signed-up user
    Then the response status code should be 200
    And the response time should be less than 2 seconds

  # TC-R05
  @timing
  Scenario: TC-R05 Resend resets the 60 second expiry timer
    Given a new user has signed up at T=0
    When I wait 30 seconds
    And I resend OTP for the signed-up user
    And I wait 35 seconds
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    And I verify the OTP "OTP_PLACEHOLDER" for the signed-up user
    Then the response status code should be 200
    And the response time should be less than 2 seconds

  # TC-R06
  Scenario: TC-R06 Resend for already-verified user is logged
    Given a new user has signed up and verified
    When I resend OTP for the signed-up user
    Then I log the response status and body for resend to verified user

  # TC-R07
  @security
  Scenario: TC-R07 Resend for non-existent user does not reveal existence
    When I resend OTP for username "nonexistent_user@mailinator.com"
    Then the response body should not reveal user existence
    And the response time should be less than 2 seconds

  # TC-R08
  Scenario: TC-R08 Rapid resend 10 times — rate limit check
    Given a new user has signed up
    When I resend OTP 10 times rapidly for the signed-up user
    Then I log the rate limiting behaviour

  # TC-R09
  Scenario: TC-R09 GET request to resend returns 405
    When I send a GET request to "/api/v1/auth/verify/resend"
    Then the response status code should be 405
    And the response time should be less than 2 seconds

  # TC-R10
  Scenario: TC-R10 Resend endpoint responds within 2 seconds
    Given a new user has signed up
    When I resend OTP for the signed-up user
    Then the response time should be less than 2 seconds
