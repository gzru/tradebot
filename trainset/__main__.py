import argparse

from typing import Sequence, Deque, Optional, TextIO
from collections import deque
from structs.candle import Candle, make_batch_name_list
from structs.normalize import Normalizer, \
                              PlainNormalizerFactory, \
                              MinMaxNormalizerFactory, \
                              StdNormalizerFactory


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


def make_normalizer_factory(normalization: Optional[str]):
    if not normalization:
        return PlainNormalizerFactory()
    elif normalization == "MINMAX":
        return MinMaxNormalizerFactory()
    elif normalization == "STD":
        return StdNormalizerFactory()
    else:
        raise Exception("Unknown normalization")

def write_header(predict_field: str, train_batch: int, fd: TextIO):
    fields = [predict_field]
    fields += make_batch_name_list(batch_size=train_batch)
    fd.write(", ".join(fields))
    fd.write("\n")

def write_batch(predict_field: str, batch: Sequence[Candle], normalizer: Normalizer, fd: TextIO) -> None:
    # Extract target field from the first candle
    normalizer.apply(batch[0])
    fd.write(str(normalizer.result().get_field(predict_field)))
    fd.write(", ")
    # Rest of the batch
    parts = list()
    for i in range(1, len(batch)):
        normalizer.apply(batch[i])
        parts.append(normalizer.result().to_csv())
    fd.write(", ".join(parts))
    fd.write("\n")


source_fd = open(args.data, "r")
output_fd = open(args.output, "w")
normalizer_factory = make_normalizer_factory(args.normalization)

write_header(args.predict_field, args.train_batch, output_fd)

batch: Deque[Candle] = deque()
for record in source_fd:
    candle = Candle.from_csv(record)
    batch.append(candle)
    if len(batch) > args.train_batch:
        normalizer = normalizer_factory.make_normalizer(batch)
        write_batch(args.predict_field, batch, normalizer, output_fd)
        batch.popleft()
