# -*- coding: utf-8 -*-
#            __  __                _ _
#           |  \/  | ___  _ __ ___| (_) __ _
#           | |\/| |/ _ \| '__/ _ \ | |/ _` |
#           | |  | | (_) | | |  __/ | | (_| |
#           |_|  |_|\___/|_|  \___|_|_|\__,_|
#                             o        o     |  o
#                                 ,_       __|      ,
#                        |  |_|  /  |  |  /  |  |  / \_
#                         \/  |_/   |_/|_/\_/|_/|_/ \/
from pathlib import Path
import re
import textwrap

from morelia.breadcrumbs import Breadcrumbs
from morelia.exceptions import MissingStepError
from morelia.formatters import NullFormatter
from morelia.grammar import (
    And,
    Background,
    But,
    Comment,
    Examples,
    Feature,
    Given,
    Row,
    Scenario,
    Step,
    Then,
    When,
)
from morelia.i18n import TRANSLATIONS
from morelia.matchers import MethodNameStepMatcher, ParseStepMatcher, RegexpStepMatcher
from morelia.visitors import TestVisitor


def execute_script(
    script_root, suite, formatter=None, matchers=None, show_all_missing=True
):
    if formatter is None:
        formatter = NullFormatter()
    if matchers is None:
        matchers = [RegexpStepMatcher, ParseStepMatcher, MethodNameStepMatcher]
    matcher = _create_matchers_chain(suite, matchers)
    if show_all_missing:
        _find_and_report_missing(script_root, matcher)
    test_visitor = TestVisitor(suite, matcher, formatter)
    breadcrumbs = Breadcrumbs()
    test_visitor.register(breadcrumbs)
    try:
        script_root.accept(test_visitor)
    except Exception as exc:
        exc.__traceback__.tb_frame.f_locals
        tb = exc.__traceback__.tb_next
        while tb and not tb.tb_frame.f_locals.get("__tracebackhide__", False):
            tb = tb.tb_next
        if not tb:
            del tb
            raise
        exc.__traceback__ = tb.tb_next
        del tb
        raise exc from AssertionError(breadcrumbs)


def _create_matchers_chain(suite, matcher_classes):
    root_matcher = None
    for matcher_class in matcher_classes:
        matcher = matcher_class(suite)
        try:
            root_matcher.add_matcher(matcher)
        except AttributeError:
            root_matcher = matcher
    return root_matcher


def _find_and_report_missing(feature, matcher):
    not_matched = set()
    for step in feature.get_all_steps():
        try:
            step.find_method(matcher)
        except MissingStepError as e:
            not_matched.add(e.suggest)
    suggest = "".join(not_matched)
    if suggest:
        diagnostic = "Cannot match steps:\n\n{}".format(suggest)
        assert False, diagnostic


class Parser:
    def __init__(self, language=None):
        self.__node_classes = [
            Feature,
            Background,
            Scenario,
            Given,
            When,
            Then,
            And,
            But,
            Row,
            Comment,
            Examples,
            Step,
        ]
        self.nodes = []
        if language is None:
            language = "en"
        self.__language = language
        self.__continuation_marker_re = re.compile(r"\\\s*$")

    def parse_as_str(self, filename, prose, scenario=None):
        feature = self.parse_features(prose, scenario=scenario)
        feature.filename = filename
        return feature

    def parse_file(self, filename, scenario=r".*"):
        with Path(filename).open("rb") as input_file:
            return self.parse_as_str(
                filename=filename,
                prose=input_file.read().decode("utf-8"),
                scenario=scenario,
            )

    def parse_features(self, prose, scenario=r".*"):
        self.parse_feature(prose)

        # Filter steps to only include requested scenarios
        try:
            scenario_re = re.compile(scenario)
        except Exception as e:
            raise SyntaxError(
                'Invalid scenario matching regex "{}": {}'.format(scenario, e)
            )

        matched_feature_steps = []
        matched_steps = []
        matching = True
        for s in self.nodes:
            if isinstance(s, Background):
                matched_feature_steps.append(s)
                matching = True
            elif isinstance(s, Scenario):
                matching = scenario_re.match(s.predicate) is not None
                if matching is True:
                    matched_feature_steps.append(s)
            if matching is True:
                matched_steps.append(s)
        self.nodes = matched_steps
        self.nodes[0].steps = matched_feature_steps

        feature = self.nodes[0]
        assert isinstance(feature, Feature), "Exactly one Feature per file"
        feature.enforce(
            any(isinstance(step, Scenario) for step in feature.steps),
            "Feature without Scenario(s)",
        )
        return self.nodes[0]

    def parse_feature(self, lines):
        self.__line_producer = LineSource(lines)
        self.__docstring_parser = DocStringParser(self.__line_producer)
        self.__language_parser = LanguageParser(default_language=self.__language)
        self.__labels_parser = LabelParser()
        try:
            while True:
                line = self.__line_producer.get_line()
                if line:
                    self.__parse_line(line)
        except StopIteration:
            pass
        return self.nodes

    def __parse_line(self, line):
        if self.__language_parser.parse(line):
            self.__language = self.__language_parser.language
            return

        if self.__labels_parser.parse(line):
            return

        if self.__docstring_parser.parse(line):
            previous = self.nodes[-1]
            previous.payload = self.__docstring_parser.payload
            return

        if self.__parse_node(line):
            return

        if 0 < len(self.nodes):
            self.__append_to_previous_node(line)
        else:
            line_number = self.__line_producer.line_number
            s = Step(line, line_number=line_number)
            feature_name = TRANSLATIONS[self.__language_parser.language].get(
                "feature", "Feature"
            )
            feature_name = feature_name.replace("|", " or ")
            s.enforce(False, "feature files must start with a %s" % feature_name)

    def __parse_node(self, line):
        line_number = self.__line_producer.line_number
        folded_lines = self.__read_folded_lines(line)
        line = line.rstrip()
        source = line + folded_lines
        for node_class in self.__node_classes:
            if node_class.match(line, self.__language):
                labels = self.__labels_parser.pop_labels()
                node = node_class(
                    source=source,
                    line_number=line_number,
                    labels=labels,
                    predecessors=self.nodes,
                    language=self.__language,
                )
                self.nodes.append(node)
                return node

    def __read_folded_lines(self, line):
        folded_lines = [""]
        while self.__continuation_marker_re.search(line):
            line = self.__line_producer.get_line()
            folded_lines.append(line)
        return "\n".join(folded_lines)

    def __append_to_previous_node(self, line):
        previous = self.nodes[-1]
        previous.append_line(line)


class LabelParser:
    def __init__(self, labels_pattern=r"@\w+"):
        self._labels = []
        self._labels_re = re.compile(labels_pattern)
        self._labels_prefix_re = re.compile(r"^\s*@")

    def parse(self, line):
        """Parse labels.

        :param str line: line to parse
        :returns: True if line contains labels
        :side effects: sets self._labels to parsed labels
        """
        if self._labels_prefix_re.match(line):
            matches = self._labels_re.findall(line)
            if matches:
                self._labels.extend(matches)
                return True
        return False

    def pop_labels(self):
        """Return labels.

        :returns: labels
        :side effects: clears current labels
        """
        labels = [label.strip("@") for label in self._labels]
        self._labels = []
        return labels


class LanguageParser:
    def __init__(self, lang_pattern=r"^# language: (\w+)", default_language=None):
        if default_language is None:
            default_language = "en"
        self.__language = default_language
        self.__lang_re = re.compile(lang_pattern)

    def parse(self, line):
        """Parse language directive.

        :param str line: line to parse
        :returns: True if line contains language directive
        :side effects: sets self.language to parsed language
        """
        match = self.__lang_re.match(line)
        if match:
            self.__language = match.groups()[0]
            return True
        return False

    @property
    def language(self):
        return self.__language


class DocStringParser:
    def __init__(self, source, pattern=r'\s*"""\s*'):
        self.__source = source
        self.__docstring_re = re.compile(pattern)
        self.__payload = []

    def parse(self, line):
        """Parse docstring payload.

        :param str line: first line to parse
        :returns: True if docstring parsed
        :side effects: sets self.payload to parsed docstring
        """
        match = self.__docstring_re.match(line)
        if match:
            start_line = line
            self.__payload = []
            line = self.__source.get_line()
            while line != start_line:
                self.__payload.append(line)
                line = self.__source.get_line()
            return True
        return False

    @property
    def payload(self):
        return textwrap.dedent("\n".join(self.__payload))


class LineSource:
    def __init__(self, text):
        self.__lines = iter(line for line in text.split("\n") if line)
        self.__line_number = 0

    def get_line(self):
        """Return next line.

        :returns: next line of text
        """
        self.__line_number += 1
        return next(self.__lines)

    @property
    def line_number(self):
        return self.__line_number
