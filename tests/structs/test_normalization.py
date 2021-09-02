import unittest
from torch import zeros, ones
from structs.normalization import Normalizer, \
                                  PlainNormalizerFactory, \
                                  MinMaxNormalizerFactory, \
                                  StdNormalizerFactory
from structs.candle2 import Candle
from structs.candle_traits import CandleTraits


class TestMethods(unittest.TestCase):
    def test_normalizer(self):
        traits = CandleTraits.from_csv("a, b")
        offsets = zeros(traits.fields_count)
        offsets[0] = 2
        offsets[1] = 3
        divisors = zeros(traits.fields_count)
        divisors[0] = 2
        divisors[1] = 3
        normalizer = Normalizer(traits, offsets, divisors)
        candle0 = Candle.plain(traits)
        candle0.data[0] = 1
        normalizer.apply(candle0)
        self.assertEqual(-0.5, normalizer.result().data[0])
        self.assertEqual(-1, normalizer.result().data[1])
        candle1 = Candle.plain(traits)
        candle1.data[1] = 6
        normalizer.apply(candle1)
        self.assertEqual(-1, normalizer.result().data[0])
        self.assertEqual(1, normalizer.result().data[1])

    def test_plain_normalizer(self):
        traits = CandleTraits.from_csv("a, b")
        candles = [Candle.plain(traits),
                   Candle.plain(traits)]
        candles[0].data[0] = 1
        candles[0].data[1] = 2
        candles[1].data[0] = 3
        candles[1].data[1] = 4
        factory = PlainNormalizerFactory(traits)
        normalizer = factory.make_normalizer(candles)
        normalizer.apply(candles[0])
        self.assertEqual(1, normalizer.result().data[0])
        self.assertEqual(2, normalizer.result().data[1])
        normalizer.apply(candles[1])
        self.assertEqual(3, normalizer.result().data[0])
        self.assertEqual(4, normalizer.result().data[1])

    def test_min_max_normalizer(self):
        traits = CandleTraits.from_csv("a, b")
        candles = [Candle.plain(traits),
                   Candle.plain(traits)]
        candles[0].data[0] = 1
        candles[0].data[1] = 2
        candles[1].data[0] = 3
        candles[1].data[1] = 4
        factory = MinMaxNormalizerFactory(traits)
        normalizer = factory.make_normalizer(candles)
        normalizer.apply(candles[0])
        self.assertEqual(0, normalizer.result().data[0])
        self.assertEqual(0, normalizer.result().data[1])
        normalizer.apply(candles[1])
        self.assertEqual(1, normalizer.result().data[0])
        self.assertEqual(1, normalizer.result().data[1])

    def test_std_normalizer(self):
        traits = CandleTraits.from_csv("a, b")
        candles = [Candle.plain(traits),
                   Candle.plain(traits),
                   Candle.plain(traits)]
        candles[0].data[0] = 1
        candles[0].data[1] = 2
        candles[1].data[0] = 2
        candles[1].data[1] = 2
        candles[2].data[0] = 3
        candles[2].data[1] = 2
        factory = StdNormalizerFactory(traits)
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
