import re
from pathlib import Path
from unittest import TestCase

from morelia import run
from morelia.decorators import tags
from morelia.grammar import Scenario
from morelia.parser import Parser, execute_script

features_dir = Path(__file__).parent / "features"


@tags(["acceptance"])
class ScenarioTest(TestCase):
    def test_is_parsed(self):
        source = "Scenario: range free Vegans"
        steps = Parser().parse_feature(source)
        step = steps[0]
        assert isinstance(step, Scenario)
        assert step.predicate == "range free Vegans"

    def test_prefixed_with_spaces_is_parsed(self):
        source = "  Scenario: with spaces"
        steps = Parser().parse_feature(source)
        step = steps[0]
        assert isinstance(step, Scenario)
        assert step.predicate == "with spaces"

    def test_scenario_with_steps_is_parsed(self):
        scenario = self.__sample_scenario()
        steps = Parser().parse_feature(scenario)
        scenario, given_step, and_step, when_step, then_step = steps
        assert scenario.predicate == "See all vendors"
        assert (
            given_step.predicate == "I am logged in as a user in the administrator role"
        )
        assert and_step.predicate == "There are 3 vendors"
        assert when_step.predicate == "I go to the manage vendors page"
        assert then_step.predicate == "I should see the first 3 vendor names"

    def test_links_to_their_steps(self):
        steps = Parser().parse_feature(self.__sample_scenario())
        scenario, given_step, and_step, when_step, then_step = steps
        self.assertEqual([given_step, and_step, when_step, then_step], scenario.steps)

    def __sample_scenario(self):
        return """Scenario: See all vendors
                      Given I am logged in as a user in the administrator role
                        And There are 3 vendors
                       When I go to the manage vendors page
                       Then I should see the first 3 vendor names"""


class SampleTestCaseMixIn:
    def runTest(self):
        pass  # pragma: no cover

    def step_I_have_powered_calculator_on(self):
        r"I have powered calculator on"

        self.stack = []

    def step_I_enter_number_into_the_calculator(self, number):
        r'I enter "([^"]+)" into the calculator'

        self.stack.append(int(number))

    def step_I_press_add(self):
        r"I press add"

        num1 = self.stack.pop()
        num2 = self.stack.pop()
        self.stack.append(num1 + num2)

    def step_the_result_should_be_number_on_the_screen(self, number):
        r'the result should be "([^"]+)" on the screen'

        self.assertEqual(self.stack[-1], int(number))

    def step_I_press_subtract(self):
        r"I press subtract"

        num1 = self.stack.pop()
        num2 = self.stack.pop()
        self.stack.append(num2 - num1)

    def step_I_press_multiply(self):
        r"I press multiply"

        num1 = self.stack.pop()
        num2 = self.stack.pop()
        self.stack.append(num2 * num1)

    def step_I_press_divide(self):
        r"I press divide"

        num1 = self.stack.pop()
        num2 = self.stack.pop()
        self.stack.append(num2 / num1)


@tags(["acceptance"])
class RegexSpecifiedScenariosTest(SampleTestCaseMixIn, TestCase):
    def test_should_only_run_matching_scenarios(self):
        filename = features_dir / "scenario_matching.feature"
        self._matching_pattern = r"Scenario Matches [12]"
        self.feature = Parser().parse_file(filename, scenario=self._matching_pattern)
        scenario_matcher_re = re.compile(self._matching_pattern)
        for included_scenario in self.feature.steps:
            self.assertIsNotNone(scenario_matcher_re.match(included_scenario.predicate))

    def test_fail_informatively_on_bad_scenario_regex(self):
        filename = features_dir / "scenario_matching.feature"
        self._matching_pattern = "\\"

        with self.assertRaises(SyntaxError):
            self.feature = Parser().parse_file(
                filename, scenario=self._matching_pattern
            )


@tags(["acceptance"])
class InfoOnAllFailingScenariosTest(TestCase):
    def test_should_report_on_all_failing_scenarios(self):
        self._add_failure_pattern = re.compile(
            'Scenario: Add two numbers\n\\s*Then the result should be "120" on the screen\n\\s*.*AssertionError:\\s*70 != 120',
            re.DOTALL,
        )
        self._substract_failure_pattern = re.compile(
            'Scenario: Subtract two numbers\n\\s*Then the result should be "80" on the screen\n\\s*.*AssertionError:\\s*70 != 80',
            re.DOTALL,
        )
        self._multiply_failure_pattern = re.compile(
            'Scenario: Multiply two numbers\n\\s*Then the result should be "12" on the screen\n\\s*.*AssertionError:\\s*3 != 12',
            re.DOTALL,
        )
        self._division_failure_pattern = re.compile(
            'Scenario: Divide two numbers\n\\s*Then the result should be "4" on the screen\n\\s*.*AssertionError:\\s*2 != 4',
            re.DOTALL,
        )
        filename = features_dir / "info_on_all_failing_scenarios.feature"
        run(filename, self)

    def step_feature_with_number_scenarios_has_been_described_in_file(
        self, feature_file
    ):
        r'that feature with 4 scenarios has been described in file "([^"]+)"'
        filename = features_dir / feature_file
        self.feature = Parser().parse_file(filename)

    def step_that_test_case_passing_number_and_number_scenario_and_failing_number_and_number_has_been_written(
        self
    ):
        r"that test case passing 1 and 3 scenario and failing 2 and 4 has been written"

        class _EvaluatedTestCase(SampleTestCaseMixIn, TestCase):
            def step_I_press_subtract(self):
                pass

            def step_I_press_divide(self):
                pass

        self._evaluated_test_case = _EvaluatedTestCase
        self._failing_patterns = [
            self._substract_failure_pattern,
            self._division_failure_pattern,
        ]

    def step_that_test_case_failing_all_scenarios_been_written(self):
        r"that test case failing all scenarios been written"

        class _EvaluatedTestCase(SampleTestCaseMixIn, TestCase):
            def step_I_press_add(self):
                pass

            def step_I_press_subtract(self):
                pass

            def step_I_press_multiply(self):
                pass

            def step_I_press_divide(self):
                pass

        self._evaluated_test_case = _EvaluatedTestCase
        self._failing_patterns = [
            self._add_failure_pattern,
            self._substract_failure_pattern,
            self._multiply_failure_pattern,
            self._division_failure_pattern,
        ]

    def step_that_test_case_passing_number_number_and_number_scenario_and_failing_number_has_been_written(
        self
    ):
        r"that test case passing 2, 3 and 4 scenario and failing 1 has been written"

        class _EvaluatedTestCase(SampleTestCaseMixIn, TestCase):
            def step_I_press_add(self):
                pass

        self._evaluated_test_case = _EvaluatedTestCase
        self._failing_patterns = [self._add_failure_pattern]

    def step_that_test_case_passing_all_scenarios_been_written(self):
        r"that test case passing all scenarios been written"

        class _EvaluatedTestCase(SampleTestCaseMixIn, TestCase):
            pass

        self._evaluated_test_case = _EvaluatedTestCase

    def step_that_test_case_failing_number_number_and_number_scenario_and_passing_number_has_been_written(
        self
    ):
        r"that test case failing 1, 2 and 3 scenario and passing 4 has been written"

        class _EvaluatedTestCase(SampleTestCaseMixIn, TestCase):
            def step_I_press_add(self):
                pass

            def step_I_press_subtract(self):
                pass

            def step_I_press_multiply(self):
                pass

        self._evaluated_test_case = _EvaluatedTestCase
        self._failing_patterns = [
            self._add_failure_pattern,
            self._substract_failure_pattern,
            self._multiply_failure_pattern,
        ]

    def step_I_run_test_case(self):
        r"I run test case"

        self._catch_exception = None
        try:
            tc = self._evaluated_test_case()
            execute_script(self.feature, tc)
        except Exception as e:
            self._catch_exception = e  # warning: possible leak, use with caution

    def step_I_will_get_assertion_error_with_information_number_scenarios_passed_number_scenarios_failed(
        self, message
    ):
        r'I will get assertion error with information "([^"]+)"'

        message = self._catch_exception.args[0]
        self.assertTrue(message.startswith(message))

    def step_I_will_get_traceback_of_each_failing_scenario(self):
        r"I will get traceback of each failing scenario"

        patterns = self._failing_patterns
        message = self._catch_exception.args[0]
        for pattern in patterns:
            self.assertRegex(message, pattern)

    def step_I_won_t_get_assertion_error(self):
        r"I won\'t get assertion error"

        self.assertIsNone(self._catch_exception)
