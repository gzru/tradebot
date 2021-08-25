import argparse

from typing import Sequence, Deque, Optional, TextIO
from collections import deque
from structs.candle import Candle, make_batch_name_list, normalize_min_max
from trainset.transform import make_3cat_transform


# Create the parser
parser = argparse.ArgumentParser(description="Prepare csv dataset")

# Add the arguments
parser.add_argument("--data", type=str, required=True)
parser.add_argument("--output", type=str, required=True)
parser.add_argument("--predict-field", type=str, required=True)
parser.add_argument("--train-batch", type=int, default=100)
parser.add_argument("--normalization", type=str)

# Execute the parse_args() method
args = parser.parse_args()


def write_header(predict_field: str, train_batch: int, fd: TextIO):
    fields = [predict_field]
    fields += make_batch_name_list(batch_size=train_batch)
    fd.write(", ".join(fields))
    fd.write("\n")

def get_predict_field(batch: Sequence[Candle], predict_field: str) -> float:
    if predict_field == "CCAT":
        return make_3cat_transform(batch[0].get_field("c"),
                                   batch[1].get_field("c"),
                                   0.01)
    return batch[0].get_field(predict_field)

def get_normalized_batch(batch: Sequence[Candle], normalization: Optional[str]) -> Sequence[Candle]:
    if normalization == "MM":
        batch_norm = list(batch)
        normalize_min_max(batch_norm)
        return batch_norm
    return batch

def write_batch(predict_field: str, batch: Sequence[Candle], fd: TextIO) -> None:
    # Extract target field from the first candle
    fd.write(str(get_predict_field(batch, predict_field)))
    fd.write(", ")
    # Rest of the batch
    parts = list()
    for i in range(1, len(batch)):
        parts.append(batch[i].to_csv())
    fd.write(", ".join(parts))
    fd.write("\n")


source_fd = open(args.data, "r")
output_fd = open(args.output, "w")

write_header(args.predict_field, args.train_batch, output_fd)

batch: Deque[Candle] = deque()
for record in source_fd:
    candle = Candle.from_csv(record)
    batch.append(candle)
    if len(batch) > args.train_batch:
        preprocessed_batch = get_normalized_batch(batch, args.normalization)
        write_batch(args.predict_field, preprocessed_batch, output_fd)
        batch.popleft()
