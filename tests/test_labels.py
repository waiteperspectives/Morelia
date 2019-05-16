# -*- coding: utf-8 -*-
from pathlib import Path
from unittest import TestCase

from morelia import verify
from morelia.decorators import tags

features_dir = Path(__file__).parent / "features"


@tags(["acceptance"])
class LabelTest(TestCase):
    def setUpScenario(self):
        self.__labels = []

    def test_labels(self):
        filename = features_dir / "labels.feature"
        verify(filename, self)

    def step_step_which_accepts__labels_variable_is_executed(self, _labels=None):
        self.__labels = _labels

    def step_it_will_get_labels(self, labels):
        r'it will get labels "([^"]+)"'

        expected = labels.split(",")
        assert set(expected) == set(self.__labels)

    def step_step_which_does_not_accepts__labels_variable_is_executed(self):
        pass

    def step_it_will_not_get_any_labels(self):
        assert 0 == len(self.__labels)
