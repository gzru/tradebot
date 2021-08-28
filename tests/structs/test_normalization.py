import unittest
from structs.normalization import Normalizer, \
                                  PlainNormalizerFactory, \
                                  MinMaxNormalizerFactory, \
                                  StdNormalizerFactory
from structs.candle import Candle, NUM_FIELDS


class TestMethods(unittest.TestCase):
    def test_normalizer(self):
        offsets = [0.0] * NUM_FIELDS
        offsets[0] = 2
        offsets[1] = 3
        divisors = [1.0] * NUM_FIELDS
        divisors[0] = 2
        divisors[1] = 3
        normalizer = Normalizer(offsets, divisors)
        candle0 = Candle.make_plain()
        candle0.data[0] = 1
        normalizer.apply(candle0)
        self.assertEqual(-0.5, normalizer.result().data[0])
        self.assertEqual(-1, normalizer.result().data[1])
        candle1 = Candle.make_plain()
        candle1.data[1] = 6
        normalizer.apply(candle1)
        self.assertEqual(-1, normalizer.result().data[0])
        self.assertEqual(1, normalizer.result().data[1])

    def test_plain_normalizer(self):
        candles = [Candle.make_plain(),
                   Candle.make_plain()]
        candles[0].data[0] = 1
        candles[0].data[1] = 2
        candles[1].data[0] = 3
        candles[1].data[1] = 4
        factory = PlainNormalizerFactory()
        normalizer = factory.make_normalizer(candles)
        normalizer.apply(candles[0])
        self.assertEqual(1, normalizer.result().data[0])
        self.assertEqual(2, normalizer.result().data[1])
        normalizer.apply(candles[1])
        self.assertEqual(3, normalizer.result().data[0])
        self.assertEqual(4, normalizer.result().data[1])

    def test_min_max_normalizer(self):
        candles = [Candle.make_plain(),
                   Candle.make_plain()]
        candles[0].data[0] = 1
        candles[0].data[1] = 2
        candles[1].data[0] = 3
        candles[1].data[1] = 4
        factory = MinMaxNormalizerFactory()
        normalizer = factory.make_normalizer(candles)
        normalizer.apply(candles[0])
        self.assertEqual(0, normalizer.result().data[0])
        self.assertEqual(0, normalizer.result().data[1])
        normalizer.apply(candles[1])
        self.assertEqual(1, normalizer.result().data[0])
        self.assertEqual(1, normalizer.result().data[1])

    def test_std_normalizer(self):
        candles = [Candle.make_plain(),
                   Candle.make_plain(),
                   Candle.make_plain()]
        candles[0].data[0] = 1
        candles[0].data[1] = 2
        candles[1].data[0] = 2
        candles[1].data[1] = 2
        candles[2].data[0] = 3
        candles[2].data[1] = 2
        factory = StdNormalizerFactory()
        normalizer = factory.make_normalizer(candles)
        normalizer.apply(candles[0])
        self.assertAlmostEqual(-1.224, normalizer.result().data[0], delta=0.001)
        self.assertAlmostEqual(0, normalizer.result().data[1], delta=0.001)
        normalizer.apply(candles[1])
        self.assertAlmostEqual(0, normalizer.result().data[0], delta=0.001)
        self.assertAlmostEqual(0, normalizer.result().data[1], delta=0.001)
        normalizer.apply(candles[2])
        self.assertAlmostEqual(1.224, normalizer.result().data[0], delta=0.001)
        self.assertAlmostEqual(0, normalizer.result().data[1], delta=0.001)
