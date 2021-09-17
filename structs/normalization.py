from typing import Sequence, Optional

import torch

from structs import candle2
from structs import candle_traits


class Normalizer:
    def __init__(self, traits: candle_traits.CandleTraits,
                 offsets: torch.Tensor, dividers: torch.Tensor):
        self.offsets: torch.Tensor = offsets
        self.dividers: torch.Tensor = dividers
        self.candle: candle2.Candle = candle2.Candle.plain(traits)

    def apply(self, candle: candle2.Candle) -> None:
        self.candle.copy_from(candle)
        self.candle.normalize(self.offsets, self.dividers)

    def apply_inplace(self, candle: candle2.Candle) -> None:
        candle.normalize(self.offsets, self.dividers)

    def revert(self, candle: candle2.Candle) -> None:
        self.candle.copy_from(candle)
        self.candle.denormalize(self.offsets, self.dividers)

    def revert_inplace(self, candle: candle2.Candle) -> None:
        candle.denormalize(self.offsets, self.dividers)

    def result(self) -> candle2.Candle:
        return self.candle

class PlainNormalizerFactory:
    def __init__(self, traits: candle_traits.CandleTraits):
        self.traits: candle_traits.CandleTraits = traits
        self.offsets: torch.Tensor = torch.zeros(traits.fields_count)
        self.dividers: torch.Tensor = torch.ones(traits.fields_count)

    def make_normalizer(self, _candles: Sequence[candle2.Candle]):
        return Normalizer(self.traits, self.offsets, self.dividers)

class MinMaxNormalizerFactory:
    def __init__(self, traits: candle_traits.CandleTraits):
        self.traits: candle_traits.CandleTraits = traits
        self.min_values: torch.Tensor = torch.zeros(traits.fields_count)
        self.max_values: torch.Tensor = torch.zeros(traits.fields_count)
        self.dividers: torch.Tensor = torch.zeros(traits.fields_count)

    def make_normalizer(self, candles: Sequence[candle2.Candle]):
        self.min_values.copy_(candles[0].data)
        self.max_values.copy_(candles[0].data)
        self.dividers.fill_(1.0)
        for j in range(1, len(candles)):
            torch.minimum(self.min_values, candles[j].data, out=self.min_values)
            torch.maximum(self.max_values, candles[j].data, out=self.max_values)
        for i in range(self.traits.fields_count):
            if self.min_values[i] != self.max_values[i]:
                self.dividers[i] = self.max_values[i] - self.min_values[i]
        return Normalizer(self.traits, self.min_values, self.dividers)

class StdNormalizerFactory:
    def __init__(self, traits: candle_traits.CandleTraits):
        self.traits: candle_traits.CandleTraits = traits
        self.mean_values: torch.Tensor = torch.zeros(traits.fields_count)
        self.deviations: torch.Tensor = torch.zeros(traits.fields_count)
        self.temp: torch.Tensor = torch.zeros(traits.fields_count)

    def make_normalizer(self, candles: Sequence[candle2.Candle]):
        temp = torch.stack([candle.data for candle in candles])
        self.deviations, self.mean_values = torch.std_mean(temp, 0, unbiased=False)
        for i in range(self.traits.fields_count):
            if self.deviations[i] == 0.0:
                self.deviations[i] = 1.0
        return Normalizer(self.traits, self.mean_values, self.deviations)

def make_normalizer_factory(normalization: Optional[str], traits: candle_traits.CandleTraits):
    if not normalization:
        return PlainNormalizerFactory(traits)
    normalization = normalization.lower()
    if normalization == "minmax":
        return MinMaxNormalizerFactory(traits)
    if normalization == "std":
        return StdNormalizerFactory(traits)
    raise Exception("Unknown normalization")
