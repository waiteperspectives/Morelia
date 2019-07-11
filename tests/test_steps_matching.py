# -*- coding: utf-8 -*-

from pathlib import Path
from unittest import TestCase

from morelia import verify
from morelia.decorators import tags

features_dir = Path(__file__).parent / "features"


@tags(["acceptance"])
class StepMatchingTest(TestCase):
    def test_step_matching(self):
        path = features_dir / "steps_matching.feature"
        verify(path, self)

    def step_scenario_with_tables_is_verified(self):
        source = """
        Feature: Step matching
        Scenario: augmented predicate matching
          When I enter "<number>" into the calculator

          Examples:
            | number |
            | 1      |
        """
        self.__verify(source)

    def step_morelia_will_match_steps_based_on_augmented_predicate(self):
        assert self.has_match, "Not matched by augmented predicate"

    def step_test_case_class_has_docstring_with_format_like_pattern(self):
        source = """
        Feature: Step matching
        Scenario: by format-like
          When I match value "1" by format-like pattern
        """
        self.__verify(source)

    def step_morelia_will_match_steps_based_on_format_like_pattern(self):
        assert self.has_match, "Not matched by format-like pattern"

    def step_test_case_class_has_docstring_with_regex_pattern(self):
        source = """
        Feature: Step matching
        Scenario: by regex
          When I match value "1" by regex pattern
        """
        self.__verify(source)

    def step_morelia_will_match_steps_based_on_regex_pattern(self):
        assert self.has_match, "Not matched by regex pattern"

    def step_test_case_class_has_no_docstring(self):
        source = """
        Feature: Step matching
        Scenario: by method name
          When I match value "1" by method name
        """
        self.__verify(source)

    def step_morelia_will_match_steps_based_on_method_name(self):
        assert self.has_match, "Not matched by method name"

    def __verify(self, source):
        try:
            verify(source, CalculatorTest())
        except AssertionError:
            self.has_match = False
        else:
            self.has_match = True


class CalculatorTest:
    def step_I_enter_a_number_into_the_calculator(self, number):
        r'I enter "(\d+)" into the calculator'

    def step_I_match_by_format_like_pattern_is_matched(self, value):
        'I match value "{value}" by format-like pattern'

    def step_I_match_by_regex_pattern_is_matched(self, value):
        r'I match value "(\d+)" by regex pattern'

    def step_I_match_value_1_by_method_name(self):
        pass
