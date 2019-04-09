import unittest
from unittest.mock import Mock, sentinel, ANY

from morelia.decorators import tags
from morelia.grammar import Step
from morelia.visitors import TestVisitor


@tags(["unit"])
class TestVisitorVisitTestCase(unittest.TestCase):
    """ Test :py:meth:`TestVisitor.visit`. """

    def test_should_catch_SystemExit(self):
        """ Scenario: SystemExit """
        # Arrange
        formatter = Mock()
        node = Mock(Step)
        suite = Mock()
        obj = TestVisitor(suite, sentinel.matcher, formatter)
        node.find_method.side_effect = [SystemExit]
        # Act
        # Assert
        with self.assertRaises(SystemExit):
            obj.visit_step(node)
        formatter.output.assert_called_once_with(node, ANY, "error", ANY)
