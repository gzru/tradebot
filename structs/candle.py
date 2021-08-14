from typing import List, Any, Mapping

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

FIELD_NAMES = _make_field_names()
FIELD_NAMES_NO_IGNORE = _make_field_names_no_ignore()
FIELD_NAMES_INDEX = _make_field_names_index()


class Candle:
    def __init__(self, data: List[Any]):
        assert len(FIELDS) == len(data)
        self.data = list()
        for value in data:
            if not isinstance(value, str):
                value = str(value)
            self.data.append(value)

    def to_csv(self) -> str:
        data = Candle._data_filter_ignore(self.data)
        return ", ".join(data)

    def to_csv_all(self) -> str:
        return ", ".join(self.data)

    def get_field(self, name: str) -> str:
        return self.data[FIELD_NAMES_INDEX[name]]

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
    def _data_filter_ignore(data: List[str]) -> List[str]:
        assert len(FIELDS) == len(data)
        result = list()
        for i, value in enumerate(data):
            if FIELDS[i].ignore:
                continue
            result.append(value)
        return result


def make_batch_name_list(names: List[str], batch_size: int) -> List[str]:
    names_seq = list()
    for i in range(batch_size):
        for name in names:
            names_seq.append("{}{}".format(name, i))
    return names_seq
