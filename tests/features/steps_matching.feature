Feature: Steps matching
    Scenario: matching with format-like pattern
        When test case class has docstring with format-like pattern
        Then morelia will match steps based on format-like pattern

    Scenario: matching with regex
        When test case class has docstring with regex pattern
        Then morelia will match steps based on regex pattern

    Scenario: matching with method name
        When test case class has no docstring
        Then morelia will match steps based on method name

    Scenario: matching based on augmented predicate
        When scenario with tables is verified
        Then morelia will match steps based on augmented predicate
