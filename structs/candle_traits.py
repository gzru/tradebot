from typing import Iterable, Final, List, Mapping


class CandleTraits:
    DEFAULT_FIELD_LIST: Final = [
        "ot",
        "o",
        "h",
        "l", 
        "c",
        "v",
        "ct",
        "qav",
        "nt",
        "tbbav",
        "tbqav",
        "i",
    ]

    def __init__(self, fields: Iterable[str] = DEFAULT_FIELD_LIST):
        self.fields: List[str]  = list(fields)
        self.fields_count: int = len(self.fields)
        self.fields_index: Mapping[str, int] = dict()
        for i, field in enumerate(self.fields):
            self.fields_index[field] = i

    def make_batch_fields(self, batch_size: int) -> List[str]:
        names_seq = list()
        for i in range(batch_size):
            for name in self.fields:
                names_seq.append("{}{}".format(name, i))
        return names_seq

    @classmethod
    def from_csv(cls, header: str):
        return cls(map(str.strip, header.strip().split(",")))
