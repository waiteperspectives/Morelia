import re
import unittest
from unittest.mock import Mock, sentinel

from morelia.decorators import tags
from morelia.grammar import Step
from morelia.visitors import TestVisitor


@tags(["unit"])
class TestVisitorVisitTestCase(unittest.TestCase):
    """ Test :py:meth:`TestVisitor.visit`. """

    def test_should_catch_SystemExit(self):
        node = Mock(Step)
        suite = Mock(name="suite")
        visitor = TestVisitor(suite, sentinel.matcher, re.compile(".*"))
        node.find_method.side_effect = [SystemExit]
        with self.assertRaises(SystemExit):
            visitor.visit_step(node)
