@otp_verify
Feature: OTP Verification API
  As a newly signed-up user
  I want to verify my account using the OTP sent to my email
  So that I can activate my account and log in

  Background:
    Given the auth API is available

  # TC-V01
  @smoke
  Scenario: TC-V01 Valid OTP within 60 seconds succeeds
    Given a new user has signed up
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    When I verify the OTP "OTP_PLACEHOLDER" for the signed-up user
    Then the response status code should be 200
    And the response time should be less than 2 seconds

  # TC-V02
  Scenario: TC-V02 Wrong OTP is rejected
    Given a new user has signed up
    When I verify the OTP "999999" for the signed-up user
    Then the response status code should be one of 400 or 401
    And the response time should be less than 2 seconds

  # TC-V03
  Scenario: TC-V03 OTP used twice is rejected on second attempt
    Given a new user has signed up
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    When I verify the OTP "OTP_PLACEHOLDER" for the signed-up user
    And the response status code should be 200
    And I verify the OTP "OTP_PLACEHOLDER" for the signed-up user again
    Then the response status code should not be 200
    And the response time should be less than 2 seconds

  # TC-V04
  @timing
  Scenario: TC-V04 Expired OTP after 65 seconds is rejected
    Given a new user has signed up
    When I wait 65 seconds for OTP to expire
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    And I verify the OTP "OTP_PLACEHOLDER" for the signed-up user
    Then the response status code should be one of 400 or 401
    And the response time should be less than 2 seconds

  # TC-V05
  Scenario: TC-V05 OTP with 5 digits is rejected
    Given a new user has signed up
    When I verify the OTP "12345" for the signed-up user
    Then the response status code should be 400
    And the response time should be less than 2 seconds

  # TC-V06
  Scenario: TC-V06 OTP with 7 digits is rejected
    Given a new user has signed up
    When I verify the OTP "1234567" for the signed-up user
    Then the response status code should be 400
    And the response time should be less than 2 seconds

  # TC-V07
  Scenario: TC-V07 Empty string OTP is rejected
    Given a new user has signed up
    When I verify the OTP "" for the signed-up user
    Then the response status code should be 400
    And the response time should be less than 2 seconds

  # TC-V08
  Scenario: TC-V08 Null OTP is rejected
    Given a new user has signed up
    When I verify with null OTP for the signed-up user
    Then the response status code should be 400
    And the response time should be less than 2 seconds

  # TC-V09
  Scenario: TC-V09 OTP as letters is rejected
    Given a new user has signed up
    When I verify the OTP "abcdef" for the signed-up user
    Then the response status code should be 400
    And the response time should be less than 2 seconds

  # TC-V10
  Scenario: TC-V10 Missing username field is rejected
    When I send verify request without username field
    Then the response status code should be 400
    And the response time should be less than 2 seconds

  # TC-V11
  @security
  Scenario: TC-V11 Unregistered username does not reveal user existence
    When I verify the OTP "123456" for username "nonexistent@mailinator.com"
    Then the response status code should be 400
    And the response body should not reveal user existence
    And the response time should be less than 2 seconds

  # TC-V12
  Scenario: TC-V12 Already verified user verifying again is logged
    Given a new user has signed up and verified
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    When I verify the OTP "OTP_PLACEHOLDER" for the signed-up user
    Then I log the response status and body for already verified user

  # TC-V13
  Scenario: TC-V13 Phone number used as username must fail
    Given a new user has signed up with phone "9876543210"
    When I verify the OTP "123456" for username "9876543210"
    Then the response status code should not be 200
    And the response time should be less than 2 seconds

  # TC-V14
  Scenario: TC-V14 GET request to verify returns 405
    When I send a GET request to "/api/v1/auth/verify/confirm"
    Then the response status code should be 405
    And the response time should be less than 2 seconds

  # TC-V15
  Scenario: TC-V15 Verify endpoint responds within 2 seconds
    Given a new user has signed up
    When I verify the OTP "123456" for the signed-up user
    Then the response time should be less than 2 seconds
