from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from morelia import File, Url, verify

feature_dir = Path(__file__).parent / "features"
fixtures_dir = Path(__file__).parent / "fixtures"


class VerifyTest(TestCase):
    def setUp(self):
        self.sample_feature = fixtures_dir / "sample.feature"
        self.sample_test = SampleTest()

    @patch("morelia.requests")
    def test_verify(self, requests):
        self.requests = requests
        feature_file = feature_dir / "verify.feature"
        verify(feature_file, self)

    def step_sample_feature_in_string_exists(self):
        self.text = self.sample_feature.read_text()

    def step_morelia_verifies_feature_from_given_string(self):
        verify(self.text, self.sample_test)

    def step_sample_feature_in_file_exists(self):
        self.file_path = self.sample_feature

    def step_morelia_verifies_feature_from_given_file(self):
        verify(File(self.file_path), self.sample_test)

    def step_morelia_verifies_feature_from_given_file_passed_as_string(self):
        verify(self.file_path, self.sample_test)

    def step_sample_feature_at_url_exists(self):
        self.requests.get.return_value.text = self.sample_feature.read_text()
        self.url = "http://example.com/sample.feature"

    def step_morelia_verifies_feature_from_given_url(self):
        verify(Url(self.url), self.sample_test)

    def step_morelia_verifies_feature_from_given_url_passed_as_string(self):
        verify(self.url, self.sample_test)

    def step_no_error_is_raised(self):
        assert True


class SampleTest:
    def step_I_have_entered_number_into_the_calculator(self, number):
        r"I have entered (\d+) into the calculator"

    def step_the_result_should_be_number_on_the_screen(self, number):
        r"the result should be (\d+) on the screen"

    def step_I_press_add(self):
        r"I press add"
