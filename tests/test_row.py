# -*- coding: utf-8 -*-
import re
from unittest import TestCase

from morelia import verify
from morelia.decorators import tags
from morelia.grammar import Row, _permute_indices
from morelia.matchers import MethodNameStepMatcher, RegexpStepMatcher
from morelia.parser import Parser
from morelia.visitors import TestVisitor


@tags(["acceptance"])
class RowTest(TestCase):
    def test_Row_parse(self):
        sauce = "buddha | brot |"
        row = Row("| " + sauce)
        assert row.predicate == sauce

    def test_parse_feature_Row(self):
        steps = Parser().parse_feature(""" | piggy | op |""")
        step = steps[0]
        assert isinstance(step, Row)
        assert step.predicate == "piggy | op |"

    def test_Scenes_count_Row_dimensions(self):
        self.assemble_scene_table()
        scenario = self.table_scene.steps[0]
        dims = scenario.count_Row_dimensions()
        assert [2, 3] == dims

    def test_Scenes_count_more_Row_dimensions(self):
        self.assemble_scene_table("Step whatever\n")
        scenario = self.table_scene.steps[0]
        dims = scenario.count_Row_dimensions()
        assert [2, 0, 3] == dims

    def test_permutate(self):
        expect = [
            (0, 0, 0),
            (0, 0, 1),
            (0, 0, 2),
            (0, 1, 0),
            (0, 1, 1),
            (0, 1, 2),
            (0, 2, 0),
            (0, 2, 1),
            (0, 2, 2),
            (0, 3, 0),
            (0, 3, 1),
            (0, 3, 2),
        ]
        assert expect == _permute_indices([0, 4, 3])
        expect = [(0, 0, 0)]
        assert expect == _permute_indices([1, 1, 1])
        expect = [(0, 0, 0), (0, 0, 1)]
        assert expect == _permute_indices([1, 1, 2])

    def test_permute_schedule(self):
        expect = _permute_indices([2, 0, 3])  # NOTE:  by rights, 0 should be -1
        self.assemble_scene_table("Step you betcha\n")
        scenario = self.table_scene.steps[0]
        schedule = scenario.permute_schedule()
        assert expect == schedule

    def test_evaluate_permuted_schedule(self):
        self.assemble_scene_table("Step flesh is weak\n")
        scenario = self.table_scene.steps[0]
        matcher = RegexpStepMatcher(self).add_matcher(MethodNameStepMatcher(self))
        visitor = TestVisitor(self, matcher, re.compile(".*"))
        self.crunks = []
        self.zones = []
        scenario.row_indices = [1, 0, 2]
        scenario.accept(visitor)
        assert "hotel" == self.got_party_zone
        assert "jail" == self.got_crunk

    def test_Rows_find_step_parents(self):
        self.assemble_scene_table()
        given, then, = self.table_scene.steps[0].steps
        assert isinstance(given.steps[0], Row)
        assert isinstance(then.steps[0], Row)
        assert "zone  |" == given.steps[0].predicate
        assert "crunk |" == then.steps[0].predicate

    def assemble_scene_table(self, more=""):
        scene = self.assemble_scene_table_source(more)
        self.table_scene = Parser().parse_features(scene)

    def test_harvest(self):
        assert ["crock", "of"] == Row(r"| crock | of").values
        assert ["crock", "of"] == Row(r"| crock | of |").values
        assert [r"crane \| wife", "three"] == Row(r"| crane \| wife | three").values

    def test_two_dimensional_table(self):
        self.elements = []
        self.factions = []
        scene = self.assemble_short_scene_table()
        verify(scene, self)
        assert [["Pangolin", "Glyptodon"], ["Pangea", "Laurasia"]] == [
            self.factions,
            self.elements,
        ]

    def assemble_short_scene_table(self):
        return """Feature: the smoker you drink
                    Scenario: the programmer you get
                      Given party <element> from <faction>

                                | faction   | element  |

                                | Pangolin  | Pangea   |
                                | Glyptodon | Laurasia |"""

    def test_another_two_dimensional_table(self):
        self.crunks = []
        self.zones = []
        scene = self.assemble_scene_table_source(
            "Step my milkshake brings all the boys to the yard\n"
        )
        verify(scene, self)
        assert ["work", "mall", "jail", "work", "mall", "jail"] == self.crunks
        assert ["beach", "beach", "beach", "hotel", "hotel", "hotel"] == self.zones

    def assemble_scene_table_source(self, more=""):
        return """Feature: permute tables
                       Scenario: turn one feature into many
                           Given party <zone>
                                | zone  |
                                | beach |
                                | hotel |
                           {more}Then hearty <crunk>
                                | crunk |
                                | work  |
                                | mall  |
                                | jail  |""".format(
            more=more
        )

    def step_party_zone(self, zone):
        r"party (\w+)"
        self.got_party_zone = zone
        self.zones.append(zone)

    def step_party_element_from_faction(self, element, faction):
        r"party (\w+) from (\w+)"
        self.factions.append(faction)
        self.elements.append(element)

    def step_flesh_is_weak(self):
        pass

    def step_hearty_crunk_(self, crunk):
        r"hearty (\w+)"
        self.crunks.append(crunk)
        self.got_crunk = crunk

    def step_my_milkshake(self, youth="boys", article="the"):
        r"my milkshake brings all the (boys|girls) to (.*) yard"
        self.youth = youth
