from typing import Iterable, Final, List, Mapping, Any


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

    def __init__(self, fields: Iterable[str]):
        self._set_fields(fields)

    def join(self, other: Any) -> None:
        self._set_fields(self.fields + other.fields)

    def rename(self, prefix: str) -> None:
        self._set_fields([prefix + field for field in self.fields])

    def to_csv(self) -> str:
        return ",".join(self.fields)

    def make_batch_fields(self, batch_size: int) -> List[str]:
        names_seq = list()
        for i in range(batch_size):
            for name in self.fields:
                names_seq.append("{}{}".format(name, i))
        return names_seq

    @classmethod
    def base(cls):
        return cls(cls.DEFAULT_FIELD_LIST)

    @classmethod
    def from_csv(cls, header: str):
        return cls(map(str.strip, header.strip().split(",")))

    def _set_fields(self, fields: Iterable[str]) -> None:
        self.fields: List[str] = list(fields)
        self.fields_count: int = len(self.fields)
        self.fields_index: Mapping[str, int] = dict()
        for i, field in enumerate(self.fields):
            assert field not in self.fields_index
            self.fields_index[field] = i
