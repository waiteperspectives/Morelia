from unittest import TestCase
from unittest.mock import sentinel, Mock, ANY

from morelia.decorators import tags
from morelia.formatters import IFormatter
from morelia.grammar import Feature
from morelia.matchers import IStepMatcher
from morelia.parser import AST
from morelia.visitors import TestVisitor


@tags(["unit"])
class ASTEvaluateTestCase(TestCase):
    """ Test :py:meth:`AST.evaluate`. """

    def test_should_use_provided_matcher(self):
        """ Scenariusz: matcher given as parameter """
        # Arrange
        test_visitor_class = Mock(TestVisitor)
        matcher_class = Mock(IStepMatcher)
        feature = Mock(Feature)
        steps = [feature]
        obj = AST(steps, test_visitor_class=test_visitor_class)
        # Act
        obj.evaluate(sentinel.suite, matchers=[matcher_class])
        # Assert
        test_visitor_class.assert_called_once_with(
            sentinel.suite, matcher_class.return_value, ANY
        )

    def test_should_use_provided_formatter(self):
        """ Scenariusz: formatter given as parameter """
        # Arrange
        test_visitor = Mock(TestVisitor)
        formatter = Mock(IFormatter)
        feature = Mock(Feature)
        steps = [feature]
        obj = AST(steps, test_visitor_class=test_visitor)
        # Act
        obj.evaluate(sentinel.suite, formatter=formatter)
        # Assert
        test_visitor.assert_called_once_with(sentinel.suite, ANY, formatter)


@tags(["unit"])
class LabeledNodeGetLabelsTestCase(TestCase):
    def test_should_return_node_labels(self):
        """ Scenario: node labels """
        # Arrange
        expected = ["label1", "label2"]
        obj = Feature(None, None)
        obj.add_labels(expected)
        # Act
        result = obj.get_labels()
        # Assert
        self.assertEqual(result, expected)

    def test_should_return_node_and_parent_labels(self):
        """ Scenario: node and parent labels """
        # Arrange
        expected = ["label1", "label2"]
        obj = Feature(None, None)
        obj.add_labels(["label1"])
        parent = Feature(None, None)
        parent.add_labels(["label2"])
        obj.parent = parent
        # Act
        result = obj.get_labels()
        # Assert
        self.assertEqual(result, expected)
