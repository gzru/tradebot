from typing import List, Any, Mapping, Iterable, Optional, Sequence
from fastai.tabular.all import pd # type: ignore

"""
    1499040000000,      // Open time
    "0.01634790",       // Open
    "0.80000000",       // High
    "0.01575800",       // Low
    "0.01577100",       // Close
    "148976.11427815",  // Volume
    1499644799999,      // Close time
    "2434.19055334",    // Quote asset volume
    308,                // Number of trades
    "1756.87402397",    // Taker buy base asset volume
    "28.46694368",      // Taker buy quote asset volume
    "17928899.62484339" // Ignore.
"""

class Field:
    def __init__(self, name: str, ignore: bool = False):
        self.name: str = name
        self.ignore: bool = ignore

FIELDS: List[Field] = [
    Field("ot", ignore=True),
    Field("o"),
    Field("h"),
    Field("l"), 
    Field("c"),
    Field("v"),
    Field("ct", ignore=True),
    Field("qav"),
    Field("nt"),
    Field("tbbav"),
    Field("tbqav"),
    Field("i", ignore=True),
]

def _make_field_names() -> List[str]:
    result = list()
    for field in FIELDS:
        result.append(field.name)
    return result

def _make_field_names_no_ignore() -> List[str]:
    result = list()
    for field in FIELDS:
        if field.ignore:
            continue
        result.append(field.name)
    return result

def _make_field_names_index() -> Mapping[str, int]:
    mapping = dict()
    for i, field in enumerate(FIELDS):
        mapping[field.name] = i
    return mapping

NUM_FIELDS = len(FIELDS)
FIELD_NAMES = _make_field_names()
FIELD_NAMES_NO_IGNORE = _make_field_names_no_ignore()
FIELD_NAMES_INDEX = _make_field_names_index()


class Candle:
    def __init__(self, data: List[Any]):
        assert len(FIELDS) == len(data)
        self.data: List[float] = list()
        for value in data:
            if not isinstance(value, float):
                value = float(value)
            self.data.append(value)

    def get_field(self, name: str) -> float:
        return self.data[FIELD_NAMES_INDEX[name]]

    def get_data(self) -> List[float]:
        return Candle._data_filter_ignore(self.data)

    def get_data_all(self) -> List[float]:
        return self.data

    def normalize(self, offsets: Sequence[float], dividers: Sequence[float]) -> None:
        assert len(FIELDS) == len(offsets)
        assert len(FIELDS) == len(dividers)
        for i in range(len(FIELDS)):
            self.data[i] = (self.data[i] - offsets[i]) / dividers[i]

    def to_csv(self) -> str:
        return ", ".join(map(str, self.get_data()))

    def to_csv_all(self) -> str:
        return ", ".join(map(str, self.get_data_all()))

    def copy_from(self, candle: Any) -> None:
        for i, value in enumerate(candle.data):
            self.data[i] = value

    @classmethod
    def make_plain(cls):
        return cls([0.0] * NUM_FIELDS)

    @staticmethod
    def from_csv(record: str):
        return Candle(record.strip().split(", "))

    @staticmethod
    def field_name_list() -> List[str]:
        return FIELD_NAMES_NO_IGNORE

    @staticmethod
    def field_name_list_all() -> List[str]:
        return FIELD_NAMES

    @staticmethod
    def _data_filter_ignore(data: List[float]) -> List[float]:
        assert len(FIELDS) == len(data)
        result = list()
        for i, value in enumerate(data):
            if FIELDS[i].ignore:
                continue
            result.append(value)
        return result


def make_batch_name_list(batch_size: int) -> List[str]:
    names = Candle.field_name_list()
    names_seq = list()
    for i in range(batch_size):
        for name in names:
            names_seq.append("{}{}".format(name, i))
    return names_seq

def make_pandas_series(candles: Iterable[Candle], names: Iterable[str]) -> pd.Series:
    values = list()
    for candle in candles:
        for value in candle.get_data():
            values.append(value)
    return pd.Series(data=values, index=names)

def normalize_min_max(candles: List[Candle]):
    min_values: List[float] = list(candles[0].get_data_all())
    max_values: List[float] = list(candles[0].get_data_all())
    dividers: List[float] = [1.0] * len(FIELDS)
    for candle in candles[1:]:
        for i, value in enumerate(candle.get_data_all()):
            if min_values[i] > value:
                min_values[i] = value
            if max_values[i] < value:
                max_values[i] = value
    for i in range(len(FIELDS)):
        if min_values[i] != max_values[i]:
            dividers[i] = max_values[i] - min_values[i]
    for candle in candles:
        candle.normalize(min_values, dividers)

