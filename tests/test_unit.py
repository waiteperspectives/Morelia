#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase

from unittest.mock import sentinel, Mock

from morelia.decorators import tags
from morelia.grammar import Step
from morelia.exceptions import MissingStepError


@tags(["unit"])
class MissingStepErrorTestCase(TestCase):
    """ Test :py:meth:`MissingStepError`. """

    def test_should_create_exception(self):
        """ Scenario: exception with step and suggest """
        # Arrange
        # Act
        result = MissingStepError(
            "predicate line",
            "def step_predicate_line(self):\n    pass",
            "step_predicate_line",
            "",
        )
        # Assert
        assert result is not None
        assert result.predicate == "predicate line"


@tags(["unit"])
class StepFindStepTestCase(TestCase):

    def test_should_find_method(self):
        """ Scenario: method found """
        # Arrange
        obj = Step("???", "method")
        # Act
        matcher = Mock()
        matcher.find.return_value = (sentinel.method, [], {})
        result, args, kwargs = obj.find_method(matcher)
        # Assert
        assert result == sentinel.method

    def test_should_not_find_method(self):
        """ Scenario: not found """
        # Arrange
        obj = Step("???", "some_method")
        matcher = Mock()
        matcher.find.return_value = (None, [], {})
        matcher.suggest.return_value = ("suggest", "method_name", "docstring")
        with self.assertRaises(MissingStepError):
            obj.find_method(matcher)
