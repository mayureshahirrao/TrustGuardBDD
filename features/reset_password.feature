@reset_password
Feature: Password Reset API
  As a user who has requested a password reset
  I want to reset my password using the OTP
  So that I can regain access to my account

  Background:
    Given the auth API is available

  # TC-RP01
  @smoke
  Scenario: TC-RP01 Valid reset OTP with strong new password succeeds
    Given a verified user exists with known credentials
    And the user has triggered forgot password
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    When I reset the password with OTP "OTP_PLACEHOLDER" and new password "NewSecure456!"
    Then the response status code should be 200
    And the response time should be less than 2 seconds

  # TC-RP02
  Scenario: TC-RP02 Login with new password after reset succeeds
    Given a verified user has reset their password to "NewSecure456!"
    When I login with the new password "NewSecure456!"
    Then the response status code should be 200
    And the response time should be less than 2 seconds

  # TC-RP03
  Scenario: TC-RP03 Login with old password after reset must fail
    Given a verified user has reset their password to "NewSecure456!"
    When I login with the old password
    Then the response status code should be 401
    And the response time should be less than 2 seconds

  # TC-RP04
  @timing
  Scenario: TC-RP04 Expired reset OTP after 65 seconds is rejected
    Given a verified user exists with known credentials
    And the user has triggered forgot password
    When I wait 65 seconds for OTP to expire
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    And I reset the password with OTP "OTP_PLACEHOLDER" and new password "NewSecure456!"
    Then the response status code should be one of 400 or 401
    And the response time should be less than 2 seconds

  # TC-RP05
  Scenario: TC-RP05 Wrong OTP for password reset is rejected
    Given a verified user exists with known credentials
    And the user has triggered forgot password
    When I reset the password with OTP "999999" and new password "NewSecure456!"
    Then the response status code should be one of 400 or 401
    And the response time should be less than 2 seconds

  # TC-RP06
  Scenario: TC-RP06 Reset OTP used twice is rejected on second attempt
    Given a verified user exists with known credentials
    And the user has triggered forgot password
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    When I reset the password with OTP "OTP_PLACEHOLDER" and new password "NewSecure456!"
    And the response status code should be 200
    And I reset the password with the same OTP again
    Then the response status code should not be 200
    And the response time should be less than 2 seconds

  # TC-RP07
  @security
  Scenario: TC-RP07 Signup OTP cannot be used for password reset
    Given a new user has signed up
    # TODO: replace OTP_PLACEHOLDER with real signup OTP from Mailtrap or Mailinator
    When I reset the password with OTP "OTP_PLACEHOLDER" and new password "NewSecure456!"
    Then the response status code should not be 200
    And the response time should be less than 2 seconds

  # TC-RP08
  Scenario: TC-RP08 New password same as old — behaviour logged
    Given a verified user exists with password "SecurePass123!"
    And the user has triggered forgot password
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    When I reset the password with OTP "OTP_PLACEHOLDER" and new password "SecurePass123!"
    Then I log the response for same-as-old password policy

  # TC-RP09
  Scenario: TC-RP09 Weak new password — behaviour logged
    Given a verified user exists with known credentials
    And the user has triggered forgot password
    # TODO: replace OTP_PLACEHOLDER with real OTP from Mailtrap or Mailinator
    When I reset the password with OTP "OTP_PLACEHOLDER" and new password "123"
    Then I log the response for weak password policy

  # TC-RP10
  Scenario: TC-RP10 Empty new_password is rejected
    Given a verified user exists with known credentials
    And the user has triggered forgot password
    When I reset the password with OTP "123456" and new password ""
    Then the response status code should be 400
    And the response time should be less than 2 seconds

  # TC-RP11
  Scenario: TC-RP11 Null new_password is rejected
    Given a verified user exists with known credentials
    And the user has triggered forgot password
    When I reset the password with OTP "123456" and null new_password
    Then the response status code should be 400
    And the response time should be less than 2 seconds

  # TC-RP12
  Scenario: TC-RP12 Missing username field is rejected
    When I send password reset request without username field
    Then the response status code should be 400
    And the response time should be less than 2 seconds

  # TC-RP13
  Scenario: TC-RP13 GET request to reset password returns 405
    When I send a GET request to "/api/v1/auth/password/reset"
    Then the response status code should be 405
    And the response time should be less than 2 seconds

  # TC-RP14
  Scenario: TC-RP14 Reset password endpoint responds within 2 seconds
    Given a verified user exists with known credentials
    And the user has triggered forgot password
    When I reset the password with OTP "123456" and new password "NewSecure456!"
    Then the response time should be less than 2 seconds

  # TC-RP15
  Scenario: TC-RP15 Old session token rejected after password reset
    Given a verified user exists with known credentials
    And the user has a valid login token
    When the user resets their password
    And I use the old token for an authenticated request
    Then the authenticated request should return 401
    And the response time should be less than 2 seconds
