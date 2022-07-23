Feature:

  Scenario:
    Given an async-step waits 0.3 seconds

  Scenario:
    Given I dispatch an async-call with param "Alice"
    And   I dispatch an async-call with param "Bob"
    Then the collected result of the async-calls is "ALICE, BOB"

  Scenario:
    Given the client sends the words "how, now, brown, cow"
    Then the client will receive the words "how, now, brown, cow"

  Scenario:
    Given the client is started
    Then the client sends the word "hello"
    Then the client will receive the word "hello"
    Then the client sends the word "world"
    Then the client will receive the word "world"

  Scenario:
    Given the fixture transport context is available
    When the client using the fixture transport sends "hello"
    Then the client using the fixture transport receives "hello"

  Scenario:
    Given the fixture transport context is available
    When the client using the fixture transport sends "world"
    Then the client using the fixture transport receives "world"
