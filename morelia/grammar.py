import copy
import itertools
import re

from morelia.exceptions import MissingStepError
from morelia.i18n import TRANSLATIONS

PLACEHOLDER_RE = re.compile(r"\<(\w+)\>")


class Node:
    allowed_parents = (None,)

    def __init__(self, source="", line_number=0, language="en", labels=None):
        super().__init__()
        self.__source = source
        self.__line_number = line_number
        self.__language = language
        self.__labels = labels if labels is not None else []
        self.parent = None
        self.steps = []
        self.__predicate = self.__extract_predicate()

    def __extract_predicate(self):
        node_re = self.__get_compiled_pattern(self.__language)
        return node_re.sub("", self.source).strip()

    @classmethod
    def match(cls, line, language):
        node_re = cls.__get_compiled_pattern(language)
        return node_re.match(line)

    @classmethod
    def __get_compiled_pattern(cls, language, __memo={}):
        try:
            return __memo[cls, language]
        except KeyError:
            pattern = cls._get_pattern(language)
            node_re = re.compile(pattern)
            __memo[cls, language] = node_re
            return node_re

    @classmethod
    def _get_pattern(cls, language):
        class_name = cls.__name__
        name = class_name.lower()
        name = TRANSLATIONS[language].get(name, class_name)
        return r"^\s*({name}):?(\s+|$)".format(name=name)

    @property
    def source(self):
        return self.__source

    @property
    def line_number(self):
        return self.__line_number

    @property
    def predicate(self):
        return self.__predicate

    def append_line(self, line):
        self.__source += "\n" + line
        self.__predicate = (self.__predicate + "\n" + line.strip()).strip()
        self._validate_predicate()

    def _validate_predicate(self):
        return  # looks good! (-:

    def get_labels(self):
        labels = self.__labels[:]
        if self.parent:
            labels.extend(self.parent.get_labels())
        return labels

    def find_step(self, matcher):
        pass

    def __iter__(self):
        for child in self.steps:
            yield child
            for descendant in child:
                yield descendant

    def connect_to_parent(self, candidate_paremnts):
        allowed_parents = self.allowed_parents
        try:
            for step in candidate_paremnts[::-1]:
                if isinstance(step, allowed_parents):
                    step.add_child(self)
                    self.parent = step
                    break
        except TypeError:
            self.enforce(False, "Only one Feature per file")

    def add_child(self, child):
        self.steps.append(child)

    def enforce(self, condition, diagnostic):
        if not condition:
            text = ""
            offset = 1
            if self.parent:
                text = self.parent.source
                offset = 5
            text += self.source
            text = text.replace("\n\n", "\n").replace("\n", "\n\t")
            raise SyntaxError(
                diagnostic, (self.get_filename(), self.line_number, offset, text)
            )

    def get_filename(self):
        if self.parent:
            return self.parent.get_filename()
        try:
            return self.filename
        except AttributeError:
            return None

    def interpolated_source(self):
        return self.source + "\n"

    def count_dimensions(self):
        """ Get number of rows. """
        return sum(step.count_dimension() for step in self.steps)

    def count_dimension(self):
        return 0

    def format_fault(self, diagnostic):
        parent_reconstruction = ""
        if self.parent:
            parent_reconstruction = self.parent.source.strip("\n")
        args = (
            self.get_filename(),
            self.line_number,
            parent_reconstruction,
            self.source,
            diagnostic,
        )
        return '\n  File "%s", line %s, in %s\n %s\n%s' % args


class Feature(Node):

    def accept(self, visitor):
        visitor.visit_feature(self, self.steps)

    def prepend_steps(self, scenario):
        background = self.steps[0]
        try:
            background.prepend_steps(scenario)
        except AttributeError:
            pass


class Scenario(Node):
    allowed_parents = (Feature,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.row_indices = [0]

    def accept(self, visitor):
        self.parent.prepend_steps(self)
        self.enforce(
            0 < len(self.steps),
            "Scenario without step(s) - Step, Given, When, Then, And, or #",
        )
        schedule = self.permute_schedule()

        old_row_indices = self.row_indices
        for indices in schedule:
            self.row_indices = indices
            visitor.visit_scenario(self, self.steps)
        self.row_indices = old_row_indices

    def permute_schedule(self):
        dims = self.count_Row_dimensions()
        return _permute_indices(dims)

    def count_Row_dimensions(self):
        return [step.count_dimensions() for step in self.steps]


class Background(Node):
    allowed_parents = (Feature,)

    def accept(self, visitor):
        visitor.visit_background(self)

    def prepend_steps(self, scenario):
        try:
            return scenario.background_steps
        except AttributeError:
            background_steps = []
            for step in self.steps:
                new_step = copy.copy(step)
                new_step.parent = scenario
                background_steps.append(new_step)
            scenario.steps = background_steps + scenario.steps
            scenario.background_steps = background_steps
            return background_steps

    def count_Row_dimensions(self):
        return [0]


class Step(Node):
    allowed_parents = (Scenario, Background)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payload = ""

    def accept(self, visitor):
        visitor.visit_step(self, self.steps)

    def find_step(self, matcher):
        """Find method matching step.

        :param IStepMatcher matcher: object matching methods by given predicate
        :returns: (method, args, kwargs) tuple
        :rtype: tuple
        :raises MissingStepError: if method maching step not found
        """
        predicate = self.predicate
        augmented_predicate = self.__get_interpolated_predicate()
        method, args, kwargs = matcher.find(predicate, augmented_predicate)
        if method:
            return method, args, kwargs

        suggest, method_name, docstring = matcher.suggest(predicate)
        raise MissingStepError(predicate, suggest, method_name, docstring)

    def interpolated_source(self):
        augmented_predicate = self.__get_interpolated_predicate()
        return self.source.replace(self.predicate, augmented_predicate)

    def __get_interpolated_predicate(self):
        if self.parent is None:
            return self.predicate
        dims = self.parent.count_Row_dimensions()
        if set(dims) == {0}:
            return self.predicate
        replitrons = PLACEHOLDER_RE.findall(self.predicate)
        if not replitrons:
            return self.predicate
        self.copy = self.predicate[:]
        row_indices = self.parent.row_indices

        for replitron in replitrons:
            for x in range(0, len(row_indices)):
                table = self.parent.steps[x].steps

                try:
                    row = next(filter(lambda step: isinstance(step, Row), table))
                except StopIteration:
                    pass
                else:
                    for q, title in enumerate(row.harvest()):
                        self.replace_replitron(
                            x, q, row_indices, table, title, replitron
                        )

        return self.copy

    def replace_replitron(self, x, q, row_indices, table, title, replitron):
        if title != replitron:
            return
        at = row_indices[x] + 1

        assert at < len(table), "this should never happen"

        stick = table[at].harvest()
        found = stick[q]
        found = found.replace("\n", "\\n")
        self.copy = self.copy.replace("<%s>" % replitron, found)


class Given(Step):
    pass


class When(Step):
    pass


class Then(Step):
    pass


class And(Step):
    pass


class But(And):
    pass


class Examples(Node):
    allowed_parents = (Scenario,)

    def accept(self, visitor):
        visitor.visit_examples(self, self.steps)


class Row(Node):
    allowed_parents = (Step, Examples)

    def accept(self, visitor):
        visitor.visit_row(self)

    @classmethod
    def _get_pattern(cls, language):
        return r"^\s*(\|):?\s+"

    def harvest(self):
        row = re.split(r" \|", re.sub(r"\|$", "", self.predicate))
        row = [s.strip() for s in row]
        return row

    def count_dimension(self):
        return 0 if self.__is_header() else 1

    def __is_header(self):
        return self is self.parent.steps[0]


class Comment(Node):
    allowed_parents = (Node,)

    def accept(self, visitor):
        visitor.visit_comment(self)

    @classmethod
    def _get_pattern(cls, language):
        return r"\s*(\#)"

    def _validate_predicate(self):
        self.enforce("\n" not in self.predicate, "linefeed in comment")


def _special_range(n):
    return range(n) if n else [0]


def _permute_indices(arr):
    product_args = list(_imap(arr))
    result = list(itertools.product(*product_args))
    return result
    #  tx to Chris Rebert, et al, on the Python newsgroup for curing my brainlock here!!


def _imap(*iterables):
    iterables = [iter(i) for i in iterables]
    while True:
        try:
            args = [next(i) for i in iterables]
            yield _special_range(*args)
        except StopIteration:
            return
