@signup
Feature: User Signup API
  As a new user
  I want to register with the authentication API
  So that I can create an account and access the system

  Background:
    Given the auth API is available

  # TC-S01
  @smoke
  Scenario: TC-S01 Valid signup with all 5 mandatory fields
    When I send a signup request with valid data
    Then the response status code should be 201
    And the response time should be less than 2 seconds
    And the response body should contain a success indicator

  # TC-S02
  Scenario: TC-S02 Duplicate email signup is rejected
    Given a user already signed up with a known email
    When I send a signup request with the same email
    Then the response status code should not be 201
    And the response time should be less than 2 seconds

  # TC-S03
  Scenario: TC-S03 Duplicate phone signup behaviour is logged
    Given a user already signed up with phone "9876500001"
    When I send a signup request with the same phone "9876500001" but different email
    Then I log the response status and body for duplicate phone

  # TC-S04 – TC-S08: Missing each field one at a time
  Scenario Outline: TC-S04-S08 Signup fails when <field> is missing
    When I send a signup request missing the "<field>" field
    Then the response status code should be 400
    And the response time should be less than 2 seconds

    Examples:
      | field      |
      | first_name |
      | last_name  |
      | email      |
      | phone      |
      | password   |

  # TC-S09 – TC-S13: Empty string for each field
  Scenario Outline: TC-S09-S13 Signup fails when <field> is empty string
    When I send a signup request with "<field>" set to empty string
    Then the response status code should be 400
    And the response time should be less than 2 seconds

    Examples:
      | field      |
      | first_name |
      | last_name  |
      | email      |
      | phone      |
      | password   |

  # TC-S14 – TC-S18: Null for each field
  Scenario Outline: TC-S14-S18 Signup fails when <field> is null
    When I send a signup request with "<field>" set to null
    Then the response status code should be 400
    And the response time should be less than 2 seconds

    Examples:
      | field      |
      | first_name |
      | last_name  |
      | email      |
      | phone      |
      | password   |

  # TC-S19 – TC-S23: Whitespace-only for each field
  Scenario Outline: TC-S19-S23 Signup fails when <field> is whitespace only
    When I send a signup request with "<field>" set to whitespace only
    Then the response status code should be 400
    And the response time should be less than 2 seconds

    Examples:
      | field      |
      | first_name |
      | last_name  |
      | email      |
      | phone      |
      | password   |

  # TC-S24
  Scenario: TC-S24 Invalid email format without @ symbol
    When I send a signup request with email "invalidemail.com"
    Then the response status code should be 400
    And the response time should be less than 2 seconds

  # TC-S25
  Scenario: TC-S25 Email with spaces is rejected
    When I send a signup request with email "test user@mailinator.com"
    Then the response status code should be 400
    And the response time should be less than 2 seconds

  # TC-S26
  Scenario: TC-S26 Password too short is logged
    When I send a signup request with password "ab"
    Then I log the response status and body for short password

  # TC-S27
  Scenario: TC-S27 Password with only spaces is rejected
    When I send a signup request with password "      "
    Then the response status code should be 400
    And the response time should be less than 2 seconds

  # TC-S28
  Scenario: TC-S28 Phone with letters is logged
    When I send a signup request with phone "abcde12345"
    Then I log the response status and body for phone with letters

  # TC-S29
  Scenario Outline: TC-S29 Very long value in <field> is rejected
    When I send a signup request with "<field>" set to 500 character string
    Then the response status code should be one of 400 or 413
    And the response time should be less than 2 seconds

    Examples:
      | field      |
      | first_name |
      | last_name  |
      | email      |
      | phone      |
      | password   |

  # TC-S30
  @security
  Scenario: TC-S30 SQL injection in email field does not cause 500
    When I send a signup request with email "' OR 1=1 --@test.com"
    Then the response status code should not be 500
    And the response time should be less than 2 seconds

  # TC-S31
  @security
  Scenario: TC-S31 XSS payload in first_name is not reflected
    When I send a signup request with first_name "<script>alert('xss')</script>"
    Then the response status code should not be 500
    And the response body should not contain "<script>"
    And the response time should be less than 2 seconds

  # TC-S32
  Scenario: TC-S32 Extra unknown fields are ignored
    When I send a signup request with extra unknown fields
    Then the response status code should not be 500
    And the response time should be less than 2 seconds

  # TC-S33
  Scenario: TC-S33 Wrong Content-Type text/plain is rejected
    When I send a signup request with Content-Type "text/plain"
    Then the response status code should be one of 400 or 415
    And the response time should be less than 2 seconds

  # TC-S34
  Scenario: TC-S34 GET request to signup returns 405
    When I send a GET request to "/api/v1/auth/signup"
    Then the response status code should be 405
    And the response time should be less than 2 seconds

  # TC-S35
  Scenario: TC-S35 All signup tests respond within 2 seconds
    When I send a signup request with valid data
    Then the response time should be less than 2 seconds
