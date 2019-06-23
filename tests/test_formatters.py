import re
import unittest
from io import StringIO
from unittest.mock import Mock, patch

import pytest

from morelia.decorators import tags
from morelia.formatters import (
    Buffered,
    ColorTextFormatter,
    FileOutput,
    PlainTextFormatter,
    RemoteOutput,
    TerminalOutput,
    TextFormat,
)
from morelia.grammar import Feature, Scenario, Step


@tags(["unit"])
class PlainTextFormatterOutputTestCase(unittest.TestCase):
    def test_should_output_for_pass(self):
        stream = StringIO()
        obj = PlainTextFormatter(stream)

        line = "Given some number"
        status = "pass"
        duration = 0.01
        node = Mock(Step)
        obj.output(node, line, status, duration)

        expected = "%-60s # pass  0.010s\n" % line
        assert stream.getvalue() == expected

    def test_should_output_for_fail(self):
        stream = StringIO()
        obj = PlainTextFormatter(stream)

        line = "Given some number"
        status = "fail"
        duration = 0.01
        node = Mock(Step)
        obj.output(node, line, status, duration)

        expected = "%-60s # fail  0.010s\n" % line
        assert stream.getvalue() == expected

    def test_should_output_for_error(self):
        stream = StringIO()
        obj = PlainTextFormatter(stream)

        line = "Given some number"
        status = "error"
        duration = 0.01
        node = Mock(Step)
        obj.output(node, line, status, duration)

        expected = "%-60s # error 0.010s\n" % line
        assert stream.getvalue() == expected

    def test_should_output_for_not_step(self):
        stream = StringIO()
        obj = PlainTextFormatter(stream)

        line = "Scenario: some number"
        status = "pass"
        duration = 0.01
        node = Mock(Scenario)
        obj.output(node, line, status, duration)

        expected = "%s\n" % line
        assert stream.getvalue() == expected

    def test_should_output_for_feature(self):
        stream = StringIO()
        obj = PlainTextFormatter(stream)

        line = "Feature: some feature"
        status = "pass"
        duration = 0.01
        node = Mock(Feature)
        obj.output(node, line, status, duration)

        expected = "\n%s\n" % line
        assert stream.getvalue() == expected


@tags(["unit"])
class ColorTextFormatterOutputTestCase(unittest.TestCase):
    def test_should_output_for_pass(self):
        stream = StringIO()
        obj = ColorTextFormatter(stream)

        line = "Given some number"
        status = "pass"
        duration = 0.01
        node = Mock(Step)
        obj.output(node, line, status, duration)

        green = "\x1b[32m"
        reset = "\x1b[0m"
        expected = "{}{:<60} # 0.010s{}\n".format(green, line, reset)
        assert stream.getvalue() == expected

    def test_should_output_for_fail(self):
        stream = StringIO()
        obj = ColorTextFormatter(stream)

        line = "Given some number"
        status = "fail"
        duration = 0.01
        node = Mock(Step)
        obj.output(node, line, status, duration)

        red = "\x1b[31m"
        reset = "\x1b[0m"
        expected = "{}{:<60} # 0.010s{}\n".format(red, line, reset)
        assert stream.getvalue() == expected

    def test_should_output_for_error(self):
        stream = StringIO()
        obj = ColorTextFormatter(stream)

        line = "Given some number"
        status = "error"
        duration = 0.01
        node = Mock(Step)
        obj.output(node, line, status, duration)

        red = "\x1b[31m"
        reset = "\x1b[0m"
        expected = "{}{:<60} # 0.010s{}\n".format(red, line, reset)
        assert stream.getvalue() == expected

    def test_should_output_for_not_step(self):
        stream = StringIO()
        obj = ColorTextFormatter(stream)

        line = "Scenario: some number"
        status = "pass"
        duration = 0.01
        node = Mock(Scenario)
        obj.output(node, line, status, duration)

        expected = "%s\n" % line
        assert stream.getvalue() == expected

    def test_should_output_for_feature(self):
        stream = StringIO()
        obj = ColorTextFormatter(stream)

        line = "Feature: some feature"
        status = "pass"
        duration = 0.01
        node = Mock(Feature)
        obj.output(node, line, status, duration)

        expected = "\n%s\n" % line
        assert stream.getvalue() == expected


def test_terminal_output_writes_to_stderr():
    output = StringIO()
    with patch("morelia.formatters.sys.stderr", new=output):
        terminal = TerminalOutput()
        terminal.write("test")
        terminal.close()
    assert "test", output.getvalue()


def test_terminal_output_writes_to_stdout_when_dest_is_stdout():
    text = "test text"
    output = StringIO()
    with patch("morelia.formatters.sys.stdout", new=output):
        terminal = TerminalOutput(dest="stdout")
        terminal.write(text)
        terminal.close()
    assert text, output.getvalue()


def test_file_output_writes_to_file():
    text = "test text"
    open_func = Mock(name="open")
    terminal = FileOutput(path="some_file.log", open_func=open_func)
    terminal.write(text)
    terminal.close()
    file = open_func.return_value
    file.write.assert_called_once_with(text)
    file.close.assert_called_once_with()


def test_remote_output_sends_to_url():
    url = "http://example.com"
    text = "test text"
    transport = Mock(name="transport")
    terminal = RemoteOutput(url, transport)
    terminal.write(text)
    terminal.close()
    transport.post.assert_called_once_with(url, text)


def test_buffered_outputs_data_on_close():
    text = "test text"
    open_func = Mock(name="open")
    file = open_func.return_value
    terminal = Buffered(FileOutput(path="some_file.log", open_func=open_func))
    terminal.write(text)
    assert not file.write.called
    terminal.close()
    file.write.assert_called_once_with(text)
    file.close.assert_called_once_with()


def test_text_format_formats_pass_steps(text_formatter, output, node):
    text_formatter.step_started(node)
    text_formatter.step_finished(node)
    assert re.search(r"\s+# pass\s+0.\d{3}s", output.getvalue())


def test_text_format_formats_fail_steps(text_formatter, output, node):
    text_formatter.step_started(node)
    text_formatter.step_failed(node)
    text_formatter.step_finished(node)
    assert re.search(r"\s+# fail\s+0.\d{3}s", output.getvalue())


def test_text_format_formats_error_steps(text_formatter, output, node):
    text_formatter.step_started(node)
    text_formatter.step_errored(node)
    text_formatter.step_finished(node)
    assert re.search(r"\s+# error\s+0.\d{3}s", output.getvalue())


def test_text_format_formats_feature_with_new_line(text_formatter, output):
    node = Feature()
    text_formatter.feature_started(node)
    text_formatter.node_finished(node)
    assert re.search(r"\n", output.getvalue())


def test_text_format_formats_any_node(text_formatter, output, node):
    text_formatter.node_started(node)
    text_formatter.node_finished(node)
    assert re.search(r"", output.getvalue())


def test_text_format_closes_output_when_verification_finishes(text_formatter, output):
    text_formatter.verify_finished()
    assert output.closed


def test_text_format_formats_in_color(output, node):
    text_formatter = TextFormat(output, color=True)
    text_formatter.step_started(node)
    text_formatter.step_failed(node)
    text_formatter.step_finished(node)
    assert re.search("\x1b\\[31m\\s+#\\s+0.\\d{3}s\x1b\\[0m", output.getvalue())


@pytest.fixture
def text_formatter(output):
    return TextFormat(output)


@pytest.fixture
def output():
    return StringIO()


@pytest.fixture
def node():
    return Step()
