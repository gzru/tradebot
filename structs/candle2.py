import pandas
import torch
from typing import Sequence, Any, TextIO, List
from torch import Tensor, zeros
from numpy import ndarray, float32, char, savetxt
from structs.candle_traits import CandleTraits


class Candle:
    def __init__(self, data: Tensor):
        self.data: Tensor = data

    def get_field(self, name: str, traits: CandleTraits) -> float:
        return self.data[traits.fields_index[name]].item()

    def set_field(self, name: str, value: float, traits: CandleTraits):
        self.data[traits.fields_index[name]] = value

    def to_csv(self) -> str:
        return ",".join(map(str, map(Tensor.item, self.data)))

    def copy_from(self, candle: Any) -> None:
        self.data.copy_(candle.data)

    def normalize(self, offsets: Tensor, dividers: Tensor) -> None:
        self.data -= offsets
        self.data /= dividers

    def denormalize(self, offsets: Tensor, dividers: Tensor) -> None:
        self.data *= dividers
        self.data += offsets

    def convert(self, source_traits: CandleTraits, dest_traits: CandleTraits):
        data = zeros(dest_traits.fields_count)
        for i, field in enumerate(dest_traits.fields):
            j = source_traits.fields_index[field]
            data[i] = self.data[j]
        return Candle(data)

    @classmethod
    def plain(cls, traits: CandleTraits):
        return cls(zeros(traits.fields_count))

    @classmethod
    def from_data(cls, data: Sequence[Any], traits: CandleTraits):
        assert traits.fields_count == len(data)
        tensor = zeros(traits.fields_count)
        for i, value in enumerate(data):
            if not isinstance(value, float):
                value = float(value)
            tensor[i] = value
        return cls(tensor)

    @classmethod
    def from_numpy(cls, data: ndarray, traits: CandleTraits):
        assert traits.fields_count == len(data)
        assert data.dtype == float32
        return cls(Tensor(data))

    @staticmethod
    def from_csv(record: str, traits: CandleTraits):
        return Candle.from_data(record.strip().split(","), traits)


def make_copy(candles: Sequence[Candle]) -> List[Candle]:
    return [Candle(candle.data.clone()) for candle in candles]

def make_pandas_series(candles: Sequence[Candle], names: Sequence[str]) -> pandas.Series:
    data = torch.cat([candle.data for candle in candles])
    return pandas.Series(data=data, index=names)

def make_pandas_data_frame(candles: Sequence[Candle], traits: CandleTraits) -> pandas.DataFrame:
    data = torch.stack([candle.data for candle in candles])
    return pandas.DataFrame(data=data, columns=traits.fields)
