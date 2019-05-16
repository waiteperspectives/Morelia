import os
import unittest

from morelia.decorators import should_skip, tags


@tags(["unit"])
class ShouldSkipTestCase(unittest.TestCase):
    def test_should_skip(self):
        tags_list = ["tag1", "tag2"]
        test_data = [
            ("", False),
            ("-tag1", True),
            ("tag1", False),
            ("tag1 tag2", False),
            ("tag1 -tag2", True),
            ("-tag1 -tag2", True),
            ("tag3", True),
            ("-tag3", False),
            ("tag1 -tag3", False),
            ("tag1 tag2 -tag3", False),
            ("-tag1 -tag2 -tag3", True),
        ]
        for pattern, expected in test_data:
            result = should_skip(tags_list, pattern)
            assert result == expected


@tags(["unit"])
class TagsTestCase(unittest.TestCase):
    def setUp(self):
        self._skip_data = [([], "tag1"), (["tag1"], "-tag1")]
        self._pass_data = [(["tag1"], "tag1"), (["tag1"], ""), ([], "-tag1")]

    def dummy(self):
        pass

    def test_should_skip(self):
        old_morelia_tags = os.environ.get("MORELIA_TAGS", None)
        try:
            for tags_list, pattern in self._skip_data:
                with self.subTest(tags_list=tags_list, pattern=pattern):
                    os.environ["MORELIA_TAGS"] = pattern
                    with self.assertRaises(unittest.SkipTest):
                        decorated = tags(tags_list)(self.dummy)
                        decorated()
        finally:
            if old_morelia_tags is not None:
                os.environ["MORELIA_TAGS"] = old_morelia_tags

    def test_should_not_skip(self):
        old_morelia_tags = os.environ.get("MORELIA_TAGS", None)
        try:
            for tags_list, pattern in self._pass_data:
                with self.subTest(tags_list=tags_list, pattern=pattern):
                    os.environ["MORELIA_TAGS"] = pattern
                    decorated = tags(tags_list)(self.dummy)
                    try:
                        decorated()
                    except unittest.SkipTest:  # pragma: nocover
                        self.fail("Should not raise SkipTest")  # pragma: nocover
        finally:
            if old_morelia_tags is not None:
                os.environ["MORELIA_TAGS"] = old_morelia_tags
