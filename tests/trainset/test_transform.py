import unittest
from trainset.transform import NormalizedView, \
                               make_min_max_normalized_view, \
                               make_std_normalized_view
from structs.candle import Candle, NUM_FIELDS


class TestMethods(unittest.TestCase):
    def test_normalized_view(self):
        candles = [Candle([0.0] * NUM_FIELDS), Candle([0.0] * NUM_FIELDS)]
        candles[0].data[0] = 1
        candles[1].data[1] = 6
        offsets = [0.0] * NUM_FIELDS
        offsets[0] = 2
        offsets[1] = 3
        divisors = [1.0] * NUM_FIELDS
        divisors[0] = 2
        divisors[1] = 3
        view = NormalizedView(candles, offsets, divisors)
        normalized_candles = list(view)
        self.assertEqual(-0.5, normalized_candles[0].data[0])
        self.assertEqual(-1, normalized_candles[0].data[1])
        self.assertEqual(-1, normalized_candles[1].data[0])
        self.assertEqual(1, normalized_candles[1].data[1])

    def test_min_max_normalized_view(self):
        candles = [Candle([0.0] * NUM_FIELDS), Candle([0.0] * NUM_FIELDS)]
        candles[0].data[0] = 1
        candles[0].data[1] = 2
        candles[1].data[0] = 3
        candles[1].data[1] = 4
        normalized_candles = list(make_min_max_normalized_view(candles))
        self.assertEqual(0, normalized_candles[0].data[0])
        self.assertEqual(0, normalized_candles[0].data[1])
        self.assertEqual(1, normalized_candles[1].data[0])
        self.assertEqual(1, normalized_candles[1].data[1])

    def test_std_normalized_view(self):
        candles = [Candle([0.0] * NUM_FIELDS),
                   Candle([0.0] * NUM_FIELDS),
                   Candle([0.0] * NUM_FIELDS)]
        candles[0].data[0] = 1
        candles[0].data[1] = 2
        candles[1].data[0] = 2
        candles[1].data[1] = 2
        candles[2].data[0] = 3
        candles[2].data[1] = 2
        normalized_candles = list(make_std_normalized_view(candles))
        self.assertAlmostEqual(-1.224, normalized_candles[0].data[0], delta=0.001)
        self.assertEqual(0, normalized_candles[0].data[1])
        self.assertEqual(0, normalized_candles[1].data[0])
        self.assertEqual(0, normalized_candles[1].data[1])
        self.assertAlmostEqual(1.224, normalized_candles[2].data[0], delta=0.001)
        self.assertEqual(0, normalized_candles[2].data[1])
