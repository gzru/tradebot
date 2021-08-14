import argparse

from collections import deque
from structs.klines import FIELDS, make_field_list, filter_fields_csv
from structs.candle import Candle, make_batch_name_list


# Create the parser
parser = argparse.ArgumentParser(description="Prepare csv dataset")

# Add the arguments
parser.add_argument("--data", type=str, default="data/ETHBTC.5m.csv")
parser.add_argument("--output", type=str, default="data/trainset.csv")
parser.add_argument("--predict-field", type=str, default="c")
parser.add_argument("--train-batch", type=int, default=100)

# Execute the parse_args() method
args = parser.parse_args()


def write_header(predict_field: str, train_batch: int, fd):
    fields = [predict_field]
    names = Candle.field_name_list()
    fields += make_batch_name_list(names=names, batch_size=train_batch)
    fd.write(", ".join(fields))
    fd.write("\n")

def write_batch(predict_field: str, batch, fd):
    # Extract target field from the first candle
    fd.write(batch[0].get_field(predict_field))
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

batch = deque()
for record in source_fd:
    candle = Candle.from_csv(record)
    batch.append(candle)
    if len(batch) > args.train_batch:
        write_batch(args.predict_field, batch, output_fd)
        batch.popleft()
