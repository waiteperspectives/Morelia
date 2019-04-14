import gc
import statistics
import traceback
from unittest import TestCase, skipUnless

from morelia.parser import Parser, execute_script

try:
    import tracemalloc
except ImportError:
    HAS_TRACEMALLOC = False
else:
    HAS_TRACEMALLOC = True


class TracebackHidingTest(TestCase):
    def setUp(self):
        script = "Feature: Sample\nScenario: Sample\nGiven exceptional"
        self.feature = Parser().parse_features(script)

    def test_hides_irrevelant_traceback_parts(self):
        try:
            execute_script(self.feature, self)
        except Exception as exc:
            tb = traceback.format_tb(exc.__traceback__)
            # should have only 3 lines:
            # - one with test_hides_irrevelant_traceback_parts frame
            # - one with execute_script frame
            # - one with step causing error
            assert len(tb) == 3

    @skipUnless(HAS_TRACEMALLOC, "Needs tracemalloc")
    def test_does_not_leak_too_much(self):
        tracemalloc.start()
        gc.collect()
        series = []
        snapshot1 = tracemalloc.take_snapshot()
        for i in range(100):
            try:
                execute_script(self.feature, self)
            except Exception:
                pass
            gc.collect()
            snapshot2 = tracemalloc.take_snapshot()
            stats = snapshot2.compare_to(snapshot1, "lineno")
            snapshot1 = snapshot2
            series.append(sum(stat.size / 1024 for stat in stats))
        tracemalloc.stop()
        series = series[1:]  # ignore first run, which creates regex
        cv = statistics.stdev(series) / statistics.mean(series)
        assert cv < 0.1

    def step_exceptional(self):
        assert False
