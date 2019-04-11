# -*- coding: utf-8 -*-
from unittest import TestCase

from morelia.decorators import tags
from morelia.grammar import Given, Scenario, Step, Then, When
from morelia.parser import Parser


@tags(["acceptance"])
class StepTest(TestCase):
    def test_parses_given(self):
        source = "Given some precondition"
        steps = Parser().parse_feature(source)
        step = steps[0]
        assert isinstance(step, Given)
        assert step.predicate == "some precondition"

    def test_parses_when(self):
        source = "When some action"
        steps = Parser().parse_feature(source)
        step = steps[0]
        assert isinstance(step, When)
        assert step.predicate == "some action"

    def test_parses_then(self):
        source = "Then some postcondition"
        steps = Parser().parse_feature(source)
        step = steps[0]
        assert isinstance(step, Then)
        assert step.predicate == "some postcondition"

    def test_given_a_string_with_given_in_it(self):
        source = "Given a string with Given in it   \nAnd another string"
        steps = Parser().parse_feature(source)  # ^ note the spacies
        step = steps[0]
        assert isinstance(step, Given)
        assert (
            step.predicate == "a string with Given in it"
        )  # <-- note spacies are gone

    def test_given_a_broken_string_with_excess_spacies(self):
        source = "Given a string with spacies and   \n  another string  "
        steps = Parser().parse_feature(source)
        step = steps[0]
        assert isinstance(step, Given)
        assert step.predicate == "a string with spacies and\nanother string"

    def test_deal_with_pesky_carriage_returns(
        self
    ):  # because Morse Code will live forever!
        source = "Given a string with spacies and   \r\n  another string  "
        steps = Parser().parse_feature(source)
        step = steps[0]
        assert isinstance(step, Given)
        assert step.predicate == "a string with spacies and\nanother string"

    def test_given_a_string_with_a_line_breaker_followed_by_a_keyword(self):
        source = "Given a string \\\n And another string"
        steps = Parser().parse_feature(source)
        assert 1 == len(steps)
        step = steps[0]
        assert isinstance(step, Given)
        assert step.source == "Given a string \\\n And another string"
        assert step.predicate == "a string \\\n And another string"

    def test_given_a_string_with_a_line_breaker_followed_by_a_keyword_with_stray_spacies(
        self
    ):
        source = "Given a string \\  \n And another string, without stray spacies"
        steps = Parser().parse_feature(source)
        assert 1 == len(steps)
        step = steps[0]
        assert isinstance(step, Given)
        assert (
            step.predicate == "a string \\\n And another string, without stray spacies"
        )

    def test_strip_predicates(self):
        step = Parser().parse_feature("  Given   gangsta girl   \t     ")[0]
        assert step.predicate == "gangsta girl"

    def test_how_to_identify_trees_from_quite_a_long_distance_away(self):
        assert Given != Step
        assert issubclass(Given, Step)
        assert issubclass(Given, Given)
        assert not issubclass(Scenario, Given)
