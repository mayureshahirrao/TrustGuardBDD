@forgot_password
Feature: Forgot Password API
  As a user who has forgotten my password
  I want to request a password reset OTP
  So that I can reset my password

  Background:
    Given the auth API is available

  # TC-F01
  @smoke
  Scenario: TC-F01 Valid username triggers forgot password successfully
    Given a verified user exists with known credentials
    When I trigger forgot password for the verified user
    Then the response status code should be 200
    And the response time should be less than 2 seconds

  # TC-F02
  @security
  Scenario: TC-F02 Non-existent username does not reveal user existence
    When I trigger forgot password for username "nonexistent@mailinator.com"
    Then the response body should not reveal user existence
    And the response time should be less than 2 seconds

  # TC-F03
  Scenario: TC-F03 Unverified user triggers forgot password — logged
    Given a new user has signed up but not verified
    When I trigger forgot password for the unverified user
    Then I log the response status and body for unverified forgot password

  # TC-F04
  Scenario: TC-F04 Empty username is rejected
    When I trigger forgot password with empty username
    Then the response status code should be 400
    And the response time should be less than 2 seconds

  # TC-F05
  Scenario: TC-F05 Null username is rejected
    When I trigger forgot password with null username
    Then the response status code should be 400
    And the response time should be less than 2 seconds

  # TC-F06
  Scenario: TC-F06 Phone number as username must fail
    When I trigger forgot password for username "9876543210"
    Then the response status code should not be 200
    And the response time should be less than 2 seconds

  # TC-F07
  Scenario: TC-F07 Two forgot password requests — second invalidates first OTP
    Given a verified user exists with known credentials
    When I trigger forgot password for the verified user
    And I trigger forgot password for the verified user again
    Then I log whether second OTP invalidates the first

  # TC-F08
  Scenario: TC-F08 GET request to forgot password returns 405
    When I send a GET request to "/api/v1/auth/password/forgot"
    Then the response status code should be 405
    And the response time should be less than 2 seconds

  # TC-F09
  Scenario: TC-F09 Forgot password endpoint responds within 2 seconds
    Given a verified user exists with known credentials
    When I trigger forgot password for the verified user
    Then the response time should be less than 2 seconds
