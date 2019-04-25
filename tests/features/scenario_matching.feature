Feature: Scenario Matching
    In order to isolate scenarios in my tests with more precision
    As a test idiot
    I want to be able to specify regex patterns for scenarios and only run those tests

    Scenario: Scenario Matches 1
        Then "first" scenario is executed

    Scenario: Scenario DOESN'T MATCH!
        Then "second" scenario is not executed

    Scenario: Scenario also DOESN'T MATCH
        Then "third" scenario is not executed

    Scenario: Scenario Matches 2
        Then "fourth" scenario is executed
