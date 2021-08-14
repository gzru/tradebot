from typing import List

class Field:
    def __init__(self, name: str, ignore: bool = False):
        self.name: str = name
        self.ignore: bool = ignore

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

def make_field_list(batch_size: int):
    fields = list()
    for i in range(batch_size):
        for field in FIELDS:
            if field.ignore:
                continue
            fields.append("{}{}".format(field.name, i))
    return fields

def filter_fields_csv(record: str, strict: List[str] = []) -> str:
    fields_raw = record.split(", ")
    if len(fields_raw) != len(FIELDS):
        raise Exception("Fields count mismatch: {} != {}".format(len(fields_raw), len(FIELDS)))
    strict_field_names = set()
    if strict:
        strict_field_names.update(strict)
    fields = list()
    for i in range(len(FIELDS)):
        if FIELDS[i].ignore or (strict_field_names and FIELDS[i].name not in strict_field_names):
            continue
        fields.append(fields_raw[i])
    return ", ".join(fields)

