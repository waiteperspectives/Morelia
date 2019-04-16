# -*- coding: utf-8 -*-
from pathlib import Path
from unittest import TestCase

from morelia import run
from morelia.decorators import tags

features_dir = Path(__file__).parent / "features"


@tags(["acceptance"])
class CommentsTest(TestCase):
    def test_comments(self):
        filename = features_dir / "comments.feature"
        run(filename, self)

    def step_scenario_will_pass(self):
        assert True

    def step_I_put_some_comment_after_step_on_separate_line(self):
        pass

    def step_I_put_comment_between_rows_of_table(self):
        pass

    def step_I_won_t_have_comment_in_interpolated_data_from_table(self, data):
        r"I won\'t have comment in interpolated (.+) from table"
        assert "#" not in data

    def step_I_put_some_comment_after_scenario_declaration(self):
        pass

    def step_I_put_comment_after_examples_declaration(self):
        pass
