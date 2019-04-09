import inspect
import sys
import time
import traceback
from gettext import ngettext

from morelia.exceptions import MissingStepError


def noop():
    pass


class TestVisitor:
    """Visits all steps and run step methods."""

    def __init__(self, suite, matcher, formatter):
        self._setUp = suite.setUp
        self._tearDown = suite.tearDown
        self._suite = suite
        self._suite.setUp = self._suite.tearDown = noop
        self._matcher = matcher
        self._formatter = formatter
        self._exceptions = []
        self._scenarios_failed = 0
        self._scenarios_passed = 0
        self._scenarios_num = 0
        self._scenario_exception = None
        self._steps_num = 0

    def visit_feature(self, node, children=[]):
        try:
            self._feature_visit(node)
            self.__visit_children(children)
        finally:
            self._feature_after_visit(node)

    def _feature_visit(self, node):
        self._exceptions = []
        self._scenarios_failed = 0
        self._scenarios_passed = 0
        self._scenarios_num = 0
        line = node.interpolated_source()
        self._formatter.output(node, line, "", 0)

    def _feature_after_visit(self, node):
        if self._scenarios_failed:
            self._fail_feature()

    def _fail_feature(self):
        failed_msg = ngettext(
            "{} scenario failed", "{} scenarios failed", self._scenarios_failed
        )
        passed_msg = ngettext(
            "{} scenario passed", "{} scenarios passed", self._scenarios_passed
        )
        msg = "{}, {}".format(failed_msg, passed_msg).format(
            self._scenarios_failed, self._scenarios_passed
        )
        prefix = "-" * 66
        for step_line, tb, exc in self._exceptions:
            msg += "\n{}{}\n{}{}".format(prefix, step_line, tb, exc).replace(
                "\n", "\n    "
            )
        assert self._scenarios_failed == 0, msg

    def visit_scenario(self, node, children=[]):
        try:
            self._scenario_visit(node)
            self.__visit_children(children)
        finally:
            self._scenario_after_visit(node)

    def visit_step(self, node, children=[]):
        self._step_visit(node)
        self.__visit_children(children)

    def visit(self, node, children=[]):
        line = node.interpolated_source()
        self._formatter.output(node, line, "", 0)
        self.__visit_children(children)

    visit_background = visit_row = visit_examples = visit_comment = visit

    def __visit_children(self, children):
        for child in children:
            child.accept(self)

    def _scenario_visit(self, node):
        self._scenario_exception = None
        if self._scenarios_num != 0:
            self._setUp()
        self._scenarios_num += 1
        line = node.interpolated_source()
        self._formatter.output(node, line, "", 0)

    def _scenario_after_visit(self, node):
        if self._scenario_exception:
            self._exceptions.append(self._scenario_exception)
            self._scenarios_failed += 1
        else:
            self._scenarios_passed += 1
        self._tearDown()

    def _step_visit(self, node):
        if self._scenario_exception:
            return
        self._suite.step = node
        self._steps_num += 1
        reconstruction = node.interpolated_source()
        start_time = time.time()
        status = "pass"
        try:
            self.run_step(node)
        except (MissingStepError, AssertionError):
            status = "fail"
            etype, evalue, etraceback = sys.exc_info()
            tb = traceback.extract_tb(etraceback)[:-2]
            self._scenario_exception = (
                node.parent.interpolated_source() + reconstruction,
                "".join(traceback.format_list(tb)),
                "".join(traceback.format_exception_only(etype, evalue)),
            )
        except (SystemExit, Exception) as exc:
            status = "error"
            self._format_exception(node, exc)
            raise
        finally:
            end_time = time.time()
            duration = end_time - start_time
            self._formatter.output(node, reconstruction, status, duration)

    def _format_exception(self, node, exc):
        if len(exc.args):
            message = node.format_fault(exc.args[0])
            exc.args = (message,) + exc.args[1:]

    def run_step(self, node):
        method, args, kwargs = node.find_method(self._matcher)
        spec = None
        arglist = []
        spec = inspect.getfullargspec(method)
        arglist = spec.args + spec.kwonlyargs

        if "_labels" in arglist:
            kwargs["_labels"] = node.get_labels()
        if "_text" in arglist:
            kwargs["_text"] = node.payload
        method(*args, **kwargs)
