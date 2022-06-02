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
    Then the client sends the word "how"
    Then the client will receive the word "how"
    Then the client sends the word "now"
    Then the client will receive the word "now"
    Then the client sends the word "brown"
    Then the client will receive the word "brown"
    Then the client sends the word "cow"
    Then the client will receive the word "cow"

