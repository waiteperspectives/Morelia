# -*- coding: utf-8 -*-
from unittest import TestCase

from morelia import verify
from morelia.decorators import tags


@tags(["acceptance"])
class SetUpTearDownTest(TestCase):
    def setUp(self):
        self.executed = []

    def test_executes_setup_teardown_pairs(self):
        source = """
            Feature: setUp/tearDown pairs
                Scenario: passing scenario
                    When step passes
                    And next step passes
                Scenario: failing scenario
                    When step fails
        """
        try:
            verify(source, self)
        except AssertionError:
            pass
        expected_sequence = [
            "setUpFeature",
            "setUpScenario",
            "setUpStep",
            "step passes",
            "tearDownStep",
            "setUpStep",
            "next step passes",
            "tearDownStep",
            "tearDownScenario",
            "setUpScenario",
            "setUpStep",
            "step fails",
            "tearDownStep",
            "tearDownScenario",
            "tearDownFeature",
        ]
        assert expected_sequence == self.executed

    def setUpFeature(self):
        self.executed.append("setUpFeature")

    def tearDownFeature(self):
        self.executed.append("tearDownFeature")

    def setUpScenario(self):
        self.executed.append("setUpScenario")

    def tearDownScenario(self):
        self.executed.append("tearDownScenario")

    def setUpStep(self):
        self.executed.append("setUpStep")

    def tearDownStep(self):
        self.executed.append("tearDownStep")

    def step_step_passes(self):
        self.executed.append("step passes")
        assert True

    def step_next_step_passes(self):
        self.executed.append("next step passes")
        assert True

    def step_step_fails(self):
        self.executed.append("step fails")
        assert False
