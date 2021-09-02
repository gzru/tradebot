from typing import Sequence, Any
from torch import Tensor, zeros
from structs.candle_traits import CandleTraits


class Candle:
    def __init__(self, data: Tensor):
        self.data: Tensor = data

    def get_field(self, name: str, traits: CandleTraits) -> float:
        return self.data[traits.fields_index[name]].item()

    def set_field(self, name: str, value: float, traits: CandleTraits):
        self.data[traits.fields_index[name]] = value

    def to_csv(self) -> str:
        return ", ".join(map(str, map(Tensor.item, self.data)))

    def copy_from(self, candle: Any) -> None:
        self.data.copy_(candle.data)

    def normalize(self, offsets: Tensor, dividers: Tensor) -> None:
        self.data -= offsets
        self.data /= dividers

    def denormalize(self, offsets: Tensor, dividers: Tensor) -> None:
        self.data *= dividers
        self.data += offsets

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

    @staticmethod
    def from_csv(record: str, traits: CandleTraits):
        return Candle.from_data(record.strip().split(", "), traits)
