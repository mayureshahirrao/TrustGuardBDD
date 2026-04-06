@login
Feature: Login API
  As a registered and verified user
  I want to log in with my credentials
  So that I receive an authentication token

  Background:
    Given the auth API is available

  # TC-L01
  @smoke
  Scenario: TC-L01 Valid login returns 200 and a token
    Given a verified user exists with known credentials
    When I login with the correct username and password
    Then the response status code should be 200
    And the response body should contain a token
    And the response time should be less than 2 seconds

  # TC-L02
  Scenario: TC-L02 Token is present and non-empty in response
    Given a verified user exists with known credentials
    When I login with the correct username and password
    Then the response body should contain a token
    And the token value should be non-empty

  # TC-L03
  Scenario: TC-L03 Token is usable for an authenticated request
    Given a verified user exists with known credentials
    When I login with the correct username and password
    And I use the returned token for an authenticated request
    Then the authenticated request should succeed

  # TC-L04
  @security
  Scenario: TC-L04 Wrong password returns 401 without revealing user exists
    Given a verified user exists with known credentials
    When I login with the correct username and wrong password "WrongPass999!"
    Then the response status code should be 401
    And the response body should not reveal user existence
    And the response time should be less than 2 seconds

  # TC-L05
  @security
  Scenario: TC-L05 Non-existent username returns 401 without revealing info
    When I login with username "nonexistent@mailinator.com" and password "AnyPass123!"
    Then the response status code should be 401
    And the response body should not reveal user existence
    And the response time should be less than 2 seconds

  # TC-L06
  Scenario: TC-L06 Unverified user cannot login
    Given a new user has signed up but not verified
    When I login with the unverified user credentials
    Then the response status code should be one of 401 or 403
    And the response time should be less than 2 seconds

  # TC-L07
  Scenario: TC-L07 Wrong case in email — behaviour logged
    Given a verified user exists with known credentials
    When I login with the email in uppercase
    Then I log the response status and body for case sensitivity

  # TC-L08
  Scenario: TC-L08 Empty password is rejected
    Given a verified user exists with known credentials
    When I login with empty password
    Then the response status code should be 400
    And the response time should be less than 2 seconds

  # TC-L09
  Scenario: TC-L09 Null password is rejected
    Given a verified user exists with known credentials
    When I login with null password
    Then the response status code should be 400
    And the response time should be less than 2 seconds

  # TC-L10
  Scenario: TC-L10 Missing username field is rejected
    When I send login request without username field
    Then the response status code should be 400
    And the response time should be less than 2 seconds

  # TC-L11
  Scenario: TC-L11 Brute force 10 failed logins — rate limit check
    Given a verified user exists with known credentials
    When I send 10 login requests with wrong password
    Then I log the brute force rate limiting behaviour

  # TC-L12
  Scenario: TC-L12 GET request to login returns 405
    When I send a GET request to "/api/v1/auth/login"
    Then the response status code should be 405
    And the response time should be less than 2 seconds

  # TC-L13
  Scenario: TC-L13 Login endpoint responds within 2 seconds
    Given a verified user exists with known credentials
    When I login with the correct username and password
    Then the response time should be less than 2 seconds

  # TC-L14
  Scenario: TC-L14 Old token is rejected after password reset
    Given a verified user exists with known credentials
    And the user has a valid login token
    When the user resets their password
    And I use the old token for an authenticated request
    Then the authenticated request should return 401
    And the response time should be less than 2 seconds
