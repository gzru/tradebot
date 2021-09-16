import argparse
import pandas
import numpy

from typing import Sequence, Deque, Optional, TextIO
from collections import deque
from structs.candle2 import Candle
from structs.normalization import Normalizer, make_normalizer_factory
from structs.candle_traits import CandleTraits


# Create the parser
parser = argparse.ArgumentParser(description="Prepare csv dataset")

# Add the arguments
parser.add_argument("--data", type=str, required=True)
parser.add_argument("--output", type=str, required=True)
parser.add_argument("--predict-field", type=str, required=True)
parser.add_argument("--train-fields", type=str, required=True)
parser.add_argument("--train-batch", type=int, required=True)
parser.add_argument("--normalization", type=str)
parser.add_argument("--join-data", type=str)
parser.add_argument("--join-fields", type=str)
parser.add_argument("--join-prefix", type=str, default="j_")

# Execute the parse_args() method
args = parser.parse_args()

# Unpack data source list
data_sources = args.data.split(",")


def load_data_frame(filename: str, traits: CandleTraits, index_field="ot"):
    source_traits = CandleTraits.base()
    data_frame = None
    if index_field in traits.fields_index:
        data_frame = pandas.read_csv(filename,
                                     names=source_traits.fields,
                                     usecols=traits.fields,
                                     dtype=numpy.float32)
        data_frame.index = data_frame[index_field]
    else:
        data_frame = pandas.read_csv(filename,
                                     names=source_traits.fields,
                                     usecols=traits.fields + [index_field],
                                     dtype=numpy.float32)
        data_frame.index = data_frame.pop(index_field)
    return data_frame

def write_header(predict_field: str, traits: CandleTraits, train_batch: int, fd: TextIO):
    fields = [predict_field]
    fields += traits.make_batch_fields(train_batch)
    fd.write(",".join(fields))
    fd.write("\n")

def write_batch(target: Candle, target_field: str, traits: CandleTraits, batch: Sequence[Candle], normalizer: Normalizer, fd: TextIO):
    # Extract target field from the first candle
    normalizer.apply(target)
    fd.write(str(normalizer.result().get_field(target_field, traits)))
    fd.write(",")
    # Rest of the batch
    parts = list()
    for candle in batch:
        normalizer.apply(candle)
        parts.append(normalizer.result().to_csv())
    fd.write(",".join(parts))
    fd.write("\n")


train_traits = CandleTraits.from_csv(args.train_fields)
output_traits = CandleTraits.from_csv(args.train_fields)

# Preload join data if needed
join_data_frame = None
if args.join_data:
    assert args.join_fields
    # Load data
    join_traits = CandleTraits.from_csv(args.join_fields)
    join_data_frame = load_data_frame(args.join_data, join_traits)
    # Rename join fields to prevent collisions 
    join_traits.rename(prefix=args.join_prefix)
    join_data_frame.set_axis(join_traits.fields, axis=1)
    # Join traits extend train traits
    output_traits.join(join_traits)

# Prepare normalizer factory
normalizer_factory = make_normalizer_factory(args.normalization, output_traits)

with open(args.output, "w") as output_fd:
    write_header(args.predict_field, output_traits, args.train_batch, output_fd)
    for data_source in data_sources:
        # Preload data and intersect with join data
        data_frame = load_data_frame(data_source, train_traits)
        if join_data_frame is not None:
            data_frame = pandas.concat([data_frame, join_data_frame], axis=1, join="inner")

        batch: Deque[Candle] = deque()
        for index, row in data_frame.iterrows():
            candle = Candle.from_numpy(row.to_numpy(), output_traits)
            batch.append(candle)
            if len(batch) <= args.train_batch:
                continue
            target = batch[0]
            # Eliminate from normalizartion
            batch.popleft()
            normalizer = normalizer_factory.make_normalizer(batch)
            write_batch(target, args.predict_field, output_traits, batch, normalizer, output_fd)

