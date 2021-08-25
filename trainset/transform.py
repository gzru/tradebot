from typing import List
from structs.candle import Candle, NUM_FIELDS


def make_3cat_transform(target: float, before: float, change_fraction: float) -> int:
    ratio = target / before
    if ratio > (1 + change_fraction):
        return 2
    if ratio < (1 - change_fraction):
        return 0
    return 1

class NormalizedView:
    def __init__(self, candles: List[Candle], offsets: List[float], dividers: List[float]):
        assert len(offsets) == NUM_FIELDS
        assert len(dividers) == NUM_FIELDS
        self._candles = candles
        self._offsets = offsets
        self._dividers = dividers

    def __iter__(self):
        self._iter = iter(self._candles)
        return self

    def __next__(self) -> Candle:
        candle: Candle = next(self._iter)
        candle.normalize(self._offsets, self._dividers)
        return candle

def make_min_max_normalized_view(candles: List[Candle]) -> NormalizedView:
    min_values: List[float] = list(candles[0].get_data_all())
    max_values: List[float] = list(candles[0].get_data_all())
    for candle in candles[1:]:
        for i, value in enumerate(candle.get_data_all()):
            if min_values[i] > value:
                min_values[i] = value
            if max_values[i] < value:
                max_values[i] = value
    dividers: List[float] = [1.0] * NUM_FIELDS
    for i in range(NUM_FIELDS):
        if min_values[i] != max_values[i]:
            dividers[i] = max_values[i] - min_values[i]
    return NormalizedView(candles, min_values, dividers)

def make_std_normalized_view(candles: List[Candle]) -> NormalizedView:
    mean_values: List[float] = [0.0] * NUM_FIELDS
    for candle in candles:
        for i, value in enumerate(candle.get_data_all()):
            mean_values[i] += value
    for i in range(NUM_FIELDS):
        mean_values[i] /= len(candles)
    deviations: List[float] = [0.0] * NUM_FIELDS
    for candle in candles:
        for i, value in enumerate(candle.get_data_all()):
            deviation = value - mean_values[i]
            deviations[i] +=  deviation * deviation
    for i in range(NUM_FIELDS):
        if deviations[i]:
            deviations[i] = (deviations[i] / len(candles)) ** 0.5
        else:
            deviations[i] = 1.0
    return NormalizedView(candles, mean_values, deviations)

