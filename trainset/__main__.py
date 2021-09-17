from typing import Sequence, Deque, TextIO
import argparse
import collections

import pandas # type: ignore
import numpy

from structs import candle2
from structs import normalization
from structs import candle_traits


def load_data_frame(filename: str, traits: candle_traits.CandleTraits, index_field="ot"):
    source_traits = candle_traits.CandleTraits.base()
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


class Application:
    def __init__(self):
        self.args = None
        self.train_traits = None
        self.output_traits = None
        self.join_data_frame = None
        self.normalizer_factory = None

    def parse_args(self):
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
        self.args = parser.parse_args()

    def preload(self):
        self.train_traits = candle_traits.CandleTraits.from_csv(self.args.train_fields)
        self.output_traits = candle_traits.CandleTraits.from_csv(self.args.train_fields)

        # Preload join data if needed
        self.join_data_frame = None
        if self.args.join_data:
            assert self.args.join_fields
            # Load data
            join_traits = candle_traits.CandleTraits.from_csv(self.args.join_fields)
            self.join_data_frame = load_data_frame(self.args.join_data, join_traits)
            # Rename join fields to prevent collisions
            join_traits.rename(prefix=self.args.join_prefix)
            self.join_data_frame.set_axis(join_traits.fields, axis=1)
            # Join traits extend train traits
            self.output_traits.join(join_traits)

        # Prepare normalizer factory
        self.normalizer_factory = normalization.make_normalizer_factory(
            self.args.normalization,
            self.output_traits
        )

    def run(self):
        with open(self.args.output, "w") as output:
            self._write_header(output)
            for data_source in self.args.data.split(","):
                self._process_one_source(data_source, output)

    def _process_one_source(self, file_name: str, output: TextIO):
        # Preload data and intersect with join data
        data_frame = load_data_frame(file_name, self.train_traits)
        if self.join_data_frame is not None:
            data_frame = pandas.concat([data_frame, self.join_data_frame], axis=1, join="inner")

        batch: Deque[candle2.Candle] = collections.deque()
        for _, row in data_frame.iterrows():
            candle = candle2.Candle.from_numpy(row.to_numpy(), self.output_traits)
            batch.append(candle)
            if len(batch) <= self.args.train_batch:
                continue
            target = batch[0]
            # Eliminate from normalizartion
            batch.popleft()
            self._process_batch(target, batch, output)

    def _write_header(self, output: TextIO):
        fields = [self.args.predict_field]
        fields += self.output_traits.make_batch_fields(self.args.train_batch)
        output.write(",".join(fields))
        output.write("\n")

    def _process_batch(self, target: candle2.Candle,
                       batch: Sequence[candle2.Candle], output: TextIO):
        normalizer = self.normalizer_factory.make_normalizer(batch)
        # Extract target field from the first candle
        normalizer.apply(target)
        output.write(str(normalizer.result().get_field(self.args.predict_field,
                                                       self.output_traits)))
        output.write(",")
        # Rest of the batch
        parts = list()
        for candle in batch:
            normalizer.apply(candle)
            parts.append(normalizer.result().to_csv())
        output.write(",".join(parts))
        output.write("\n")


def main():
    app = Application()
    app.parse_args()
    app.preload()
    app.run()


if __name__ == '__main__':
    main()
