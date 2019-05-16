Feature: verifing scripts
    Scenario: script from string
        Given sample feature in string exists
        When verify is called with feature script
        Then morelia will execute it

    Scenario: script from file
        Given sample feature in file exists
        When verify is called with single line string ending in ".feature"
        Then morelia will interpret it as file path and execute it

    Scenario: script from url
        Given sample feature at url exists
        When verify is called with single line string staring with "http://" or "https://"
        Then morelia will interpret it as url and execute it

    Scenario: script from Text source object
        Given sample feature in file exists
        When verify is called with Text source object
        Then morelia will interpret it as feature script and execute it

    Scenario: script from File source object
        Given sample feature in file exists
        When verify is called with File source object
        Then morelia will interpret it as file path and execute it

    Scenario: script from Url source object
        Given sample feature in file exists
        When verify is called with Url source object
        Then morelia will interpret it as url and execute it
