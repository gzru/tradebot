from typing import Sequence, List, Optional
from torch import Tensor, zeros, ones, maximum, minimum
from structs.candle2 import Candle
from structs.candle_traits import CandleTraits


class Normalizer:
    def __init__(self, traits: CandleTraits, offsets: Tensor, dividers: Tensor):
        self.offsets: Tensor = offsets
        self.dividers: Tensor = dividers
        self.candle: Candle = Candle.plain(traits)

    def apply(self, candle: Candle) -> None:
        self.candle.copy_from(candle)
        self.candle.normalize(self.offsets, self.dividers)

    def apply_inplace(self, candle: Candle) -> None:
        candle.normalize(self.offsets, self.dividers)

    def revert(self, candle: Candle) -> None:
        self.candle.copy_from(candle)
        self.candle.denormalize(self.offsets, self.dividers)

    def revert_inplace(self, candle: Candle) -> None:
        candle.denormalize(self.offsets, self.dividers)

    def result(self) -> Candle:
        return self.candle

class PlainNormalizerFactory:
    def __init__(self, traits: CandleTraits):
        self.traits: CandleTraits = traits
        self.offsets: Tensor = zeros(traits.fields_count)
        self.dividers: Tensor = ones(traits.fields_count)

    def make_normalizer(self, candles: Sequence[Candle]):
        return Normalizer(self.traits, self.offsets, self.dividers)

class MinMaxNormalizerFactory:
    def __init__(self, traits: CandleTraits):
        self.traits: CandleTraits = traits
        self.min_values: Tensor = zeros(traits.fields_count)
        self.max_values: Tensor = zeros(traits.fields_count)
        self.dividers: Tensor = zeros(traits.fields_count)

    def make_normalizer(self, candles: Sequence[Candle]):
        self.min_values.copy_(candles[0].data)
        self.max_values.copy_(candles[0].data)
        self.dividers.fill_(1.0)
        for j in range(1, len(candles)):
            minimum(self.min_values, candles[j].data, out=self.min_values)
            maximum(self.max_values, candles[j].data, out=self.max_values)
        for i in range(self.traits.fields_count):
            if self.min_values[i] != self.max_values[i]:
                self.dividers[i] = self.max_values[i] - self.min_values[i]
        return Normalizer(self.traits, self.min_values, self.dividers)

class StdNormalizerFactory:
    def __init__(self, traits: CandleTraits):
        self.traits: CandleTraits = traits
        self.mean_values: Tensor = zeros(traits.fields_count)
        self.deviations: Tensor = zeros(traits.fields_count)
        self.temp: Tensor = zeros(traits.fields_count)

    def make_normalizer(self, candles: Sequence[Candle]):
        self.mean_values.fill_(0.0)
        self.deviations.fill_(0.0)
        """
        for i in range(NUM_FIELDS):
            self.mean_values[i] = 0.0
            self.deviations[i] = 0.0
        """
        for candle in candles:
            self.mean_values.add_(candle.data)
            """
            for i, value in enumerate(candle.get_data_all()):
                self.mean_values[i] += value
            """
        self.mean_values.div_(len(candles))
        """
        for i in range(NUM_FIELDS):
            self.mean_values[i] /= len(candles)
        """
        for candle in candles:
            self.temp.copy_(candle.data)
            self.temp.sub_(self.mean_values)
            self.temp.mul_(self.temp)
            self.deviations.add_(self.temp)
            """
            for i, value in enumerate(candle.get_data_all()):
                deviation = value - self.mean_values[i]
                self.deviations[i] +=  deviation * deviation
            """
        for i in range(self.traits.fields_count):
            if self.deviations[i] != 0.0:
                self.deviations[i] = (self.deviations[i] / len(candles)) ** 0.5
            else:
                self.deviations[i] = 1.0
        return Normalizer(self.traits, self.mean_values, self.deviations)

def make_normalizer_factory(traits: CandleTraits, normalization: Optional[str]):
    if not normalization:
        return PlainNormalizerFactory(traits)
    normalization = normalization.lower()
    if normalization == "minmax":
        return MinMaxNormalizerFactory(traits)
    elif normalization == "std":
        return StdNormalizerFactory(traits)
    else:
        raise Exception("Unknown normalization")
