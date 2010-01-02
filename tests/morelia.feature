Feature: Morelia Viridis puts the squeeze on your features.

         Morelia processes this prose and runs the results as 
         a test suite, with strings passed into each test case
         as data to evaluate

#  ----8<----  these Scenarios document good examples of Morelia abilities  ----

Scenario: Add two numbers
  Given I have entered 50 into the calculator
    And I have entered 70 into the calculator
  When I press add
   Then the result should be 120 on the screen

Scenario: When we challenge Morelia with a Step with no matching
          entry in your test suite, supply a helpful error message
    Given a feature file with "Given your nose is on fire"
    When Moralia evaluates the file
    Then it prints a diagnostic containing "    def step_your_nose_is_on_fire"
    And the second line contains "your nose is on fire"

Scenario: Fail to match prose if feature file has bad strings
    Step: fail_without_enough_function_name
    Step: fail_step_without_enough_doc_string


#      | pipe \| me      | r'pipe \\\| me'        |             |

Scenario: Raise useful errors with incomplete files
  When a file contains <statements>, it produces <diagnostics>
  
    |    statements       |   diagnostics

    |  Feature yo         | Feature without Scenario(s), line 1

    |  Feature comp-      \
       Feature placent    | Only one Feature per file, line 2

    | Feature    resist   \
        Scenario syntax   \
          Step   errors   | Scenario: syntax, line 3
