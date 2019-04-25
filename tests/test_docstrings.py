# -*- coding: utf-8 -*-
from pathlib import Path
from unittest import TestCase

from morelia import verify
from morelia.decorators import tags

features_dir = Path(__file__).parent / "features"


@tags(["acceptance"])
class DocStringTest(TestCase):
    def test_docstrings(self):
        filename = features_dir / "docstrings.feature"
        verify(filename, self)

    def step_I_put_docstring_after_step_definition(self, _text=None):
        assert _text is not None
        self._text = _text

    def step_I_will_get_docstring_passed_in__text_variable(self):
        r"I will get docstring passed in _text variable"
        assert self._text == "Docstring line1\nline2"
