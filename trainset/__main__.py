import argparse

from collections import deque
from structs.candle import Candle, make_batch_name_list
from trainset.transform import make_3cat_transform


# Create the parser
parser = argparse.ArgumentParser(description="Prepare csv dataset")

# Add the arguments
parser.add_argument("--data", type=str, required=True)
parser.add_argument("--output", type=str, required=True)
parser.add_argument("--predict-field", type=str, required=True)
parser.add_argument("--train-batch", type=int, default=100)

# Execute the parse_args() method
args = parser.parse_args()


def write_header(predict_field: str, train_batch: int, fd):
    fields = [predict_field]
    fields += make_batch_name_list(batch_size=train_batch)
    fd.write(", ".join(fields))
    fd.write("\n")

def get_predict_field(predict_field: str, batch) -> str:
    if predict_field == "CCAT":
        return str(make_3cat_transform(float(batch[0].get_field("c")),
                                       float(batch[1].get_field("c")),
                                       0.01))
    return batch[0].get_field(predict_field)

def write_batch(predict_field: str, batch, fd):
    # Extract target field from the first candle
    fd.write(get_predict_field(predict_field, batch))
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
