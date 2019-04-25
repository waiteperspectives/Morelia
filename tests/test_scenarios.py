from pathlib import Path
from unittest import TestCase

from morelia import run
from morelia.decorators import tags
from morelia.exceptions import InvalidScenarioMatchingPattern
from morelia.grammar import Scenario
from morelia.parser import Parser

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
        assert [given_step, and_step, when_step, then_step] == scenario.steps

    def __sample_scenario(self):
        return """Scenario: See all vendors
                      Given I am logged in as a user in the administrator role
                        And There are 3 vendors
                       When I go to the manage vendors page
                       Then I should see the first 3 vendor names"""


@tags(["acceptance"])
class RegexSpecifiedScenariosTest(TestCase):
    def setUp(self):
        self.executed = []
        self.filename = features_dir / "scenario_matching.feature"

    def test_should_only_run_matching_scenarios(self):
        self._matching_pattern = r"Scenario Matches [12]"
        run(self.filename, self, scenario=self._matching_pattern)
        assert ["first", "fourth"] == self.executed

    def test_fail_informatively_on_bad_scenario_regex(self):
        self._matching_pattern = "\\"

        with self.assertRaises(InvalidScenarioMatchingPattern):
            run(self.filename, self, scenario=self._matching_pattern)

    def step_nth_scenario_is_executed(self, nth):
        r'"{nth}" scenario is executed'
        self.executed.append(nth)

    def step_nth_scenario_is_not_executed(self, nth):
        r'"{nth}" scenario is not executed'
        self.executed.append(nth)
