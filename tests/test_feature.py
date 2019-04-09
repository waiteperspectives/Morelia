# -*- coding: utf-8 -*-
from unittest import TestCase

from morelia.decorators import tags
from morelia.grammar import Feature, Scenario
from morelia.parser import Parser


@tags(["acceptance"])
class FeatureTest(TestCase):
    def test_feature(self):
        source = "Feature: prevent wild animals from eating us"
        steps = Parser().parse_feature(source)
        step = steps[0]
        assert isinstance(step, Feature)
        assert step.predicate == "prevent wild animals from eating us"

    def test_feature_with_scenario(self):
        source = """Feature: Civi-lie-zation
                   Scenario: starz upon tharz bucks"""
        steps = Parser().parse_feature(source)
        step = steps[0]
        assert isinstance(step, Feature)
        assert step.predicate == "Civi-lie-zation"
        step = steps[1]
        assert isinstance(step, Scenario)
        assert step.predicate == "starz upon tharz bucks"

    def test_script_without_feature_defined(self):
        # TODO: allow for files which have at least one step defined
        source = "i be a newbie feature"
        with self.assertRaisesRegex(
            SyntaxError, "feature files must start with a Feature"
        ):
            Parser().parse_feature(source)

    def test_feature_with_long_comment(
        self
    ):  # ERGO how to detect shadowed test cases??
        source = """Feature: The Sacred Giant Mosquito of the Andes
                   #  at http://www.onagocag.com/nazbird.jpg
                        so pay no attention to the skeptics!"""
        with self.assertRaisesRegex(SyntaxError, "linefeed in comment"):
            Parser().parse_feature(source)
