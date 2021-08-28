from typing import Sequence, List
from structs.candle import Candle, NUM_FIELDS


class Normalizer:
    def __init__(self, offsets: Sequence[float], dividers: Sequence[float]):
        assert len(offsets) == NUM_FIELDS
        assert len(dividers) == NUM_FIELDS
        self.offsets = offsets
        self.dividers = dividers
        self.candle: Candle = Candle.make_plain()

    def apply(self, candle: Candle) -> None:
        self.candle.copy_from(candle)
        self.candle.normalize(self.offsets, self.dividers)

    def result(self) -> Candle:
        return self.candle

class PlainNormalizerFactory:
    def __init__(self):
        self.offsets: List[float] = [0.0] * NUM_FIELDS
        self.dividers: List[float] = [1.0] * NUM_FIELDS

    def make_normalizer(self, candles: Sequence[Candle]):
        return Normalizer(self.offsets, self.dividers)

class MinMaxNormalizerFactory:
    def __init__(self):
        self.min_values: List[float] = [0.0] * NUM_FIELDS
        self.max_values: List[float] = [0.0] * NUM_FIELDS
        self.dividers: List[float] = [0.0] * NUM_FIELDS

    def make_normalizer(self, candles: Sequence[Candle]):
        for i, value in enumerate(candles[0].get_data_all()):
            self.min_values[i] = value
            self.max_values[i] = value
            self.dividers[i] = 1.0
        for j in range(1, len(candles)):
            for i, value in enumerate(candles[j].get_data_all()):
                if self.min_values[i] > value:
                    self.min_values[i] = value
                if self.max_values[i] < value:
                    self.max_values[i] = value
        for i in range(NUM_FIELDS):
            if self.min_values[i] != self.max_values[i]:
                self.dividers[i] = self.max_values[i] - self.min_values[i]
        return Normalizer(self.min_values, self.dividers)

class StdNormalizerFactory:
    def __init__(self):
        self.mean_values: List[float] = [0.0] * NUM_FIELDS
        self.deviations: List[float] = [0.0] * NUM_FIELDS

    def make_normalizer(self, candles: Sequence[Candle]):
        for i in range(NUM_FIELDS):
            self.mean_values[i] = 0.0
            self.deviations[i] = 0.0
        for candle in candles:
            for i, value in enumerate(candle.get_data_all()):
                self.mean_values[i] += value
        for i in range(NUM_FIELDS):
            self.mean_values[i] /= len(candles)
        for candle in candles:
            for i, value in enumerate(candle.get_data_all()):
                deviation = value - self.mean_values[i]
                self.deviations[i] +=  deviation * deviation
        for i in range(NUM_FIELDS):
            if self.deviations[i]:
                self.deviations[i] = (self.deviations[i] / len(candles)) ** 0.5
            else:
                self.deviations[i] = 1.0
        return Normalizer(self.mean_values, self.deviations)
