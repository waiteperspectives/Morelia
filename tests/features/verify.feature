Feature: verifing scripts
    Scenario: script from string
        Given sample feature in string exists
        When morelia verifies feature from given string
        Then no error is raised
    Scenario: script from file
        Given sample feature in file exists
        When morelia verifies feature from given file
        Then no error is raised
    Scenario: script from file passed as string
        Given sample feature in file exists
        When morelia verifies feature from given file passed as string
        Then no error is raised
    Scenario: script from http passed as string
        Given sample feature at url exists
        When morelia verifies feature from given url passed as string
        Then no error is raised
