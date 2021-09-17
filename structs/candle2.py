from typing import Sequence, Any, List

import pandas # type: ignore
import torch
import numpy

from structs import candle_traits


class Candle:
    def __init__(self, data: torch.Tensor):
        self.data: torch.Tensor = data

    def get_field(self, name: str, traits: candle_traits.CandleTraits) -> float:
        return self.data[traits.fields_index[name]].item()

    def set_field(self, name: str, value: float, traits: candle_traits.CandleTraits):
        self.data[traits.fields_index[name]] = value

    def to_csv(self) -> str:
        return ",".join(map(str, map(torch.Tensor.item, self.data)))

    def copy_from(self, candle: Any) -> None:
        self.data.copy_(candle.data)

    def normalize(self, offsets: torch.Tensor, dividers: torch.Tensor) -> None:
        self.data -= offsets
        self.data /= dividers

    def denormalize(self, offsets: torch.Tensor, dividers: torch.Tensor) -> None:
        self.data *= dividers
        self.data += offsets

    def convert(self, source_traits: candle_traits.CandleTraits,
                dest_traits: candle_traits.CandleTraits):
        data = torch.zeros(dest_traits.fields_count)
        for i, field in enumerate(dest_traits.fields):
            j = source_traits.fields_index[field]
            data[i] = self.data[j]
        return Candle(data)

    @classmethod
    def plain(cls, traits: candle_traits.CandleTraits):
        return cls(torch.zeros(traits.fields_count))

    @classmethod
    def from_data(cls, data: Sequence[Any], traits: candle_traits.CandleTraits):
        assert traits.fields_count == len(data)
        tensor = torch.zeros(traits.fields_count)
        for i, value in enumerate(data):
            if not isinstance(value, float):
                value = float(value)
            tensor[i] = value
        return cls(tensor)

    @classmethod
    def from_numpy(cls, data: numpy.ndarray, traits: candle_traits.CandleTraits):
        assert traits.fields_count == len(data)
        assert data.dtype == numpy.float32
        return cls(torch.Tensor(data))

    @staticmethod
    def from_csv(record: str, traits: candle_traits.CandleTraits):
        return Candle.from_data(record.strip().split(","), traits)


def make_copy(candles: Sequence[Candle]) -> List[Candle]:
    return [Candle(candle.data.clone()) for candle in candles]

def make_pandas_series(candles: Sequence[Candle], names: Sequence[str]) -> pandas.Series:
    data = torch.cat([candle.data for candle in candles])
    return pandas.Series(data=data, index=names)

def make_pandas_data_frame(candles: Sequence[Candle],
                           traits: candle_traits.CandleTraits) -> pandas.DataFrame:
    data = torch.stack([candle.data for candle in candles])
    return pandas.DataFrame(data=data, columns=traits.fields)
