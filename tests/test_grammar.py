from unittest import TestCase

from morelia.decorators import tags
from morelia.grammar import Feature


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
