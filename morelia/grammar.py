import copy
import itertools
import re

from morelia.exceptions import MissingStepError
from morelia.i18n import TRANSLATIONS


class Node:
    def __init__(self, keyword, predicate, steps=[]):
        super().__init__()
        self._labels = []
        self.parent = None
        self.additional_data = {}
        self.keyword = keyword
        self.predicate = predicate if predicate is not None else ""
        self.steps = steps

    def add_labels(self, tags):
        self._labels.extend(tags)

    def get_labels(self):
        labels = self._labels
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

    def connect_to_parent(self, steps=[], line_number=0):
        self.steps = []
        self.line_number = line_number

        mpt = self.my_parent_type()
        try:
            for step in steps[::-1]:
                if isinstance(step, mpt):
                    step.steps.append(self)
                    self.parent = step
                    break
        except TypeError:
            self.enforce(False, "Only one Feature per file")

        steps.append(self)
        return self

    def prefix(self):
        return ""

    def my_parent_type(self):
        return None

    @classmethod
    def get_pattern(cls, language):
        class_name = cls.__name__
        name = class_name.lower()
        name = TRANSLATIONS[language].get(name, class_name)
        return r"\s*(?P<keyword>" + name + r"):?(?:\s+(?P<predicate>.*))?$"

    def count_dimensions(self):
        """ Get number of rows. """
        return sum([step.count_dimension() for step in self.steps])

    def count_dimension(self):
        return 0

    def validate_predicate(self):
        return  # looks good! (-:

    def enforce(self, condition, diagnostic):
        if not condition:
            text = ""
            offset = 1
            if self.parent:
                text = self.parent.reconstruction()
                offset = 5
            text += self.reconstruction()
            text = text.replace("\n\n", "\n").replace("\n", "\n\t")
            raise SyntaxError(
                diagnostic, (self.get_filename(), self.line_number, offset, text)
            )

    def format_fault(self, diagnostic):
        parent_reconstruction = ""
        if self.parent:
            parent_reconstruction = self.parent.reconstruction().strip("\n")
        reconstruction = self.reconstruction()
        args = (
            self.get_filename(),
            self.line_number,
            parent_reconstruction,
            reconstruction,
            diagnostic,
        )
        return '\n  File "%s", line %s, in %s\n %s\n%s' % args

    def reconstruction(self):
        recon = "{}{}: {}".format(self.prefix(), self.keyword, self.predicate)
        recon += "\n" if recon[-1] != "\n" else ""
        return recon

    def get_real_reconstruction(self):
        return self.reconstruction() + "\n"

    def get_filename(self):
        node = self

        while node:
            if not node.parent:
                try:
                    return node.filename
                except AttributeError:
                    pass
            node = node.parent

        return None


class Feature(Node):
    def prepend_steps(self, scenario):
        background = self.steps[0]
        try:
            background.prepend_steps(scenario)
        except AttributeError:
            pass

    def reconstruction(self):
        predicate = self.predicate.replace("\n", "\n    ")
        recon = "{}{}: {}".format(self.prefix(), self.keyword, predicate)
        recon += "\n" if recon[-1] != "\n" else ""
        return recon

    def accept(self, visitor):
        visitor.visit_feature(self, self.steps)


class Scenario(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.row_indices = [0]

    def my_parent_type(self):
        return Feature

    def accept(self, visitor):
        self.parent.prepend_steps(self)
        self.enforce(
            0 < len(self.steps),
            "Scenario without step(s) - Step, Given, When, Then, And, or #",
        )
        schedule = visitor.permute_schedule(self)

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

    def reconstruction(self):
        return "\n" + self.keyword + ": " + self.predicate


class Background(Node):
    def my_parent_type(self):
        return Feature

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

    def accept(self, visitor):
        visitor.visit_background(self)

    def count_Row_dimensions(self):
        return [0]


class Step(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payload = ""

    def prefix(self):
        return "  "

    def my_parent_type(self):
        return (Scenario, Background)

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
        augmented_predicate = self._augment_predicate()
        method, args, kwargs = matcher.find(predicate, augmented_predicate)
        if method:
            return method, args, kwargs

        suggest, method_name, docstring = matcher.suggest(predicate)
        raise MissingStepError(predicate, suggest, method_name, docstring)

    def get_real_reconstruction(self):
        predicate = self._augment_predicate()
        recon = "    {} {}".format(self.keyword, predicate)
        recon += "\n" if recon[-1] != "\n" else ""
        return recon

    def _augment_predicate(self):
        if self.parent is None:
            return self.predicate
        dims = self.parent.count_Row_dimensions()
        if set(dims) == {0}:
            return self.predicate
        rep = re.compile(r"\<(\w+)\>")
        replitrons = rep.findall(self.predicate)
        if replitrons == []:
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


class Row(Node):
    def accept(self, visitor):
        visitor.visit_row(self)

    def harvest(self):
        row = re.split(r" \|", re.sub(r"\|$", "", self.predicate))
        row = [s.strip() for s in row]
        return row

    @classmethod
    def get_pattern(cls, language):
        return r"\s*(?P<keyword>\|):?\s+(?P<predicate>.*)"

    def my_parent_type(self):
        return (Step, Examples)

    def prefix(self):
        return " " * 8

    def reconstruction(self):
        recon = self.prefix() + "| " + self.predicate
        recon += "\n" if recon[-1] != "\n" else ""
        return recon

    def count_dimension(self):
        return 0 if self.__is_header() else 1

    def __is_header(self):
        return self is self.parent.steps[0]


class Examples(Node):
    def prefix(self):
        return " " * 4

    def my_parent_type(self):
        return Scenario

    def accept(self, visitor):
        visitor.visit_examples(self, self.steps)


class Comment(Node):
    def my_parent_type(self):
        return Node  # aka "any"

    @classmethod
    def get_pattern(cls, language):
        return r"\s*(?P<keyword>\#)(?P<predicate>.*)"

    def validate_predicate(self):
        self.enforce(self.predicate.count("\n") == 0, "linefeed in comment")

    def reconstruction(self):
        recon = "    # " + self.predicate
        recon += "\n" if recon[-1] != "\n" else ""
        return recon

    def accept(self, visitor):
        visitor.visit_comment(self)


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
