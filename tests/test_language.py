from unittest import TestCase

from morelia import verify


class LanguageTest(TestCase):
    def setUp(self):
        self.executed = []

    def test_supports_languages_other_than_english(self):
        source = """# language: pl

            Właściwość: obsługa języków obcych
            Scenariusz: Dopasowuje kroki według języka
                Zakładając, że wykonany został krok przygotowujący
                Gdy wykonuję akcję
                Wtedy weryfikuję wynik
        """
        verify(source, self)
        assert ["given", "when", "then"] == self.executed

    def step_wykonany_zosta_krok_przygotowujacy(self):
        r"wykonany został krok przygotowujący"
        self.executed.append("given")

    def step_wykonuje_akcje(self):
        r"wykonuję akcję"
        self.executed.append("when")

    def step_weryfikuje_wynik(self):
        r"weryfikuję wynik"
        self.executed.append("then")
