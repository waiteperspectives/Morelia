# -*- coding: utf-8 -*-
import re
from pathlib import Path
from unittest import TestCase

from morelia import File
from morelia.decorators import tags
from morelia.exceptions import MissingStepError
from morelia.grammar import And, Feature, Given, Then, When
from morelia.matchers import MethodNameStepMatcher, RegexpStepMatcher
from morelia.parser import Parser, execute_script

features_dir = Path(__file__).parent / "features"


@tags(["acceptance"])
class MoreliaSuite(TestCase):
    def step_I_have_entered_a_number_into_the_calculator(self, number):
        r"I have entered (\d+) into the calculator"
        if not hasattr(self, "stack"):
            self.stack = []
        self.stack.append(int(number))

    def step_I_press_add(self):
        self.result = sum(self.stack)

    def step_the_result_should_be_on_the_screen(self, number):
        r"the result should be (\d+) on the screen"
        self.assertEqual(int(number), self.result)

    def step_my_milkshake(self, youth="boys", article="the"):
        r"my milkshake brings all the (boys|girls) to (.*) yard"
        self.youth = youth

    def step_exceptional(self):
        x = 1 / 0  # noqa guilty pleasure for programmers!

    def test_handle_exceptions(self):
        source = "Given exceptional"
        s = Given(source=source, line_number=42)
        try:
            execute_script(s, self)
            assert False  # should raise!  # pragma: nocover
        except ZeroDivisionError as e:
            assert "Given exceptional" in str(e.__cause__)
            assert "division by zero" in str(e)

    def test_find_step_by_name(self):
        step = Given("Given my milkshake")
        matcher = self._get_default_machers()
        method, args, kwargs = step.find_method(matcher)
        expect = self.step_my_milkshake
        assert expect == method

    def test_find_step_by_doc_string(self):
        step = And("And my milkshake brings all the boys to the yard")
        matcher = self._get_default_machers()
        method, args, kwargs = step.find_method(matcher)
        expect = self.step_my_milkshake
        assert expect == method

    def test_find_step_with_match(self):
        step = When("When my milkshake brings all the girls to the yard")
        matcher = self._get_default_machers()
        method, args, kwargs = step.find_method(matcher)
        assert ("girls", "the") == args

    def test_step_not_found(self):
        step = Then("Then not there")
        matcher = self._get_default_machers()
        with self.assertRaises(MissingStepError):
            step.find_method(matcher)

    def step_fail_without_enough_function_name(self):
        step = And("And my milk")
        matcher = self._get_default_machers()
        with self.assertRaises(MissingStepError):
            step.find_method(matcher)

    def step_fail_step_without_enough_doc_string(self):
        step = Given("Given brings all the boys to the yard it's better than yours")
        matcher = self._get_default_machers()
        with self.assertRaises(MissingStepError):
            step.find_method(matcher)

    def step_evaluate_step_by_doc_string(self):
        step = Given("Given my milkshake brings all the girls to a yard")
        self.youth = "boys"
        execute_script(step, self)
        self.assertEqual("girls", self.youth)  # Uh...

    def step_multiline_predicate(self):
        feature = "Given umma\ngumma"
        steps = Parser().parse_feature(feature)
        self.assertEqual("umma\ngumma", steps[0].predicate)

    def test_step_multiline_predicate(self):
        feature = "When multiline predicate"
        steps = Parser().parse_feature(feature)
        execute_script(steps[0], self)

    def test_record_filename(self):
        filename = features_dir / "morelia.feature"
        feature = Parser().parse_features(File(filename))
        assert feature.__class__ == Feature
        assert str(filename) == feature.filename
        step = feature.steps[3].steps[1]
        assert str(filename) == step.get_filename()

    def test_format_faults_like_python_errors(self):
        filename = features_dir / "morelia.feature"
        feature = Parser().parse_features(File(filename))
        step = feature.steps[3].steps[1]
        assert str(filename) == step.get_filename()
        omen = "The Alpine glaciers move"
        diagnostic = step.format_fault(omen)
        parent_reconstruction = step.parent.source.strip("\n")
        reconstruction = step.source

        expect = '\n  File "%s", line %s, in %s\n %s\n%s' % (
            step.get_filename(),
            step.line_number,
            parent_reconstruction,
            reconstruction,
            omen,
        )

        assert expect == diagnostic

    def test_evaluate_file(self):
        feature = Parser().parse_features(File(features_dir / "morelia.feature"))
        execute_script(feature, self)

    def setUpScenario(self):
        self.culture = []

    def step_adventure_of_love_love_and_culture_(self, culture):
        r"adventure of love - love and (.+)"
        self.culture.append(culture)

    def step_Morelia_evaluates_this(self):
        pass

    def step_culture_contains(self, arguments):
        r'"culture" contains (.*)'
        self.assertEqual(1, arguments.count(self.culture[0]))
        self.assertEqual(1, len(self.culture))

    def step_a_feature_file_with_contents(self, file_contents):
        r'a feature file with "([^"]+)"'
        self.file_contents = file_contents

    def step_Morelia_evaluates_the_file(self):
        self.diagnostic = None

        try:
            p = Parser()
            self.file_contents.replace(
                "\\#", "#"
            )  # note - this is how to unescape characters - DIY
            prefix = "Feature: Sample\nScenario: Sample\n"
            feature = p.parse_features(prefix + self.file_contents)
            execute_script(feature, self)
        except (MissingStepError, AssertionError) as e:
            self.diagnostic = str(e)

    def step_it_prints_a_diagnostic(self, sample):
        r'it prints a diagnostic containing "([^"]+)"'
        self.assert_regex_contains(re.escape(sample), self.diagnostic)

    def step_the_second_line_contains(self, docstring):
        r'the second line contains "([^"]+)"'
        self.assert_regex_contains(re.escape(docstring), self.diagnostic)

    def step_a_source_file_with_a_Given_(self, predicate):
        r"a source file with a (.+)"
        self.predicate = predicate.replace("\\n", "\n")

    def step_we_evaluate_the_file(self):
        r"we evaluate the file"
        matcher = self._get_default_machers()
        self.suggestion, self.extra_arguments = matcher._suggest_doc_string(
            self.predicate
        )

    def step_we_convert_it_into_a_(self, suggestion):
        r"we convert it into a (.+)"
        self.assertEqual(suggestion, self.suggestion)

    def step_add_extra_arguments(self, extra=""):
        r"add (.+) arguments"
        self.assertEqual(extra, self.extra_arguments)

    def step_a_file_contains_statements_produce_diagnostics_(
        self, statements, diagnostics
    ):
        r"a file contains (.+), it produces (.+)"
        try:
            statements = statements.replace("\\n", "\n")
            statements = statements.replace("\\", "")
            feature = Parser().parse_features(statements)
            execute_script(feature, self)
            raise Exception("we expect syntax errors here")  # pragma: nocover
        except (SyntaxError, AssertionError) as e:
            e = e.args[0]
            self.assert_regex_contains(re.escape(diagnostics), e)

    def step_errors(self):
        raise SyntaxError("Some syntax error")

    def assert_regex_contains(self, pattern, string, flags=None):
        flags = flags or 0
        diagnostic = '"{}" not found in "{}"'.format(pattern, string)
        self.assertTrue(re.search(pattern, string, flags) is not None, diagnostic)

    def _get_default_machers(self):
        docstring_matcher = RegexpStepMatcher(self)
        method_name_matcher = MethodNameStepMatcher(self)
        docstring_matcher.add_matcher(method_name_matcher)
        return docstring_matcher
