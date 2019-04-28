.. _usage-guide:

Quick usage guide
=================

Write a feature description:

.. code-block:: cucumber

    # calculator.feature

    Feature: Addition
        In order to avoid silly mistakes
        As a math idiot
        I want to be told the sum of two numbers

    Scenario: Add two numbers
        Given I have powered calculator on
        When I enter "50" into the calculator
        And I enter "70" into the calculator
        And I press add
        Then the result should be "120" on the screen


Create standard python's :py:mod:`unittest` and hook Morelia into it:

.. code-block:: python

    # test_acceptance.py

    import unittest

    from morelia import verify


    class CalculatorTestCase(unittest.TestCase):
    
        def test_addition(self):
            """ Addition feature """
            verify('calculator.feature', self)

Run test with your favourite runner: unittest, pytest, nose, trial. You name it!

.. code-block:: console

   $ python -m unittest -v test_acceptance  # or
   $ pytest test_acceptance.py  # or
   $ nosetests -v test_acceptance.py  # or
   $ trial test_acceptance.py  # or
   $ # django/pyramid/flask/(place for your favourite test runner)

And you'll see which steps are missing:

.. code-block:: python

    F
    ======================================================================
    FAIL: test_addition (test_acceptance.CalculatorTestCase)
    Addition feature.
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "(..)test_acceptance.py", line 31, in test_addition
        verify(filename, self)
      File "(..)/morelia/__init__.py", line 120, in verify
        execute_script(feature, suite, scenario=scenario, config=conf)
      File "(..)/morelia/parser.py", line 59, in execute_script
        assert all_found, "Cannot match steps:\n\n{}".format(suggest)
    AssertionError: Cannot match steps:

        def step_I_have_powered_calculator_on(self):
            r'I have powered calculator on'

            raise NotImplementedError('I have powered calculator on')

        def step_I_enter_number_into_the_calculator(self, number):
            r'I enter "([^"]+)" into the calculator'

            raise NotImplementedError('I enter "50" into the calculator')

        def step_I_enter_number_into_the_calculator(self, number):
            r'I enter "([^"]+)" into the calculator'

            raise NotImplementedError('I enter "70" into the calculator')

        def step_I_press_add(self):
            r'I press add'

            raise NotImplementedError('I press add')

        def step_the_result_should_be_number_on_the_screen(self, number):
            r'the result should be "([^"]+)" on the screen'

            raise NotImplementedError('the result should be "120" on the screen')

    ----------------------------------------------------------------------
    Ran 1 test in 0.013s

    FAILED (failures=1)

Now implement steps with standard :py:class:`TestCases <unittest.TestCase>` that you are familiar:

.. code-block:: python

    # test_acceptance.py

    import unittest

    from morelia import run
    

    class CalculatorTestCase(unittest.TestCase):
    
        def test_addition(self):
            """ Addition feature """
            verify('calculator.feature', self)
    
        def step_I_have_powered_calculator_on(self):
            r'I have powered calculator on'
            self.stack = []

        def step_I_enter_a_number_into_the_calculator(self, number):
            r'I enter "(\d+)" into the calculator'  # match by regexp
            self.stack.append(int(number))
    
        def step_I_press_add(self):  # matched by method name
            self.result = sum(self.stack)
    
        def step_the_result_should_be_on_the_screen(self, number):
            r'the result should be "{number}" on the screen'  # match by format-like string
            self.assertEqual(int(number), self.result)


And run it again:

.. code-block:: console

    $ python -m unittest test_acceptance

    Feature: Addition
        In order to avoid silly mistakes
        As a math idiot
        I want to be told the sum of two numbers
    Scenario: Add two numbers
        Given I have powered calculator on                       # pass  0.000s
        When I enter "50" into the calculator                    # pass  0.000s
        And I enter "70" into the calculator                     # pass  0.000s
        And I press add                                          # pass  0.001s
        Then the result should be "120" on the screen            # pass  0.001s
    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.028s

    OK

Note that Morelia does not waste anyone's time inventing a new testing back-end
just to add a layer of literacy over our testage. Steps are miniature :py:class:`TestCases <unittest.TestCase>`.
Your onsite customer need never know, and your unit tests and customer tests
can share their support methods. The same one test button can run all TDD and BDD tests.
