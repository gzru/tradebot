import argparse

from fastai.tabular.all import *
from structs.candle import make_batch_name_list


# Create the parser
parser = argparse.ArgumentParser(description="Train a model")

# Add the arguments
parser.add_argument("--trainset", type=str, required=True)
parser.add_argument("--output", type=str, required=True)
parser.add_argument("--predict-field", type=str, required=True)
parser.add_argument("--train-batch", type=int, required=True)
parser.add_argument("--train-cycles", type=int, default=30)

# Execute the parse_args() method
args = parser.parse_args()

field_names = make_batch_name_list(batch_size=args.train_batch)

loader = TabularDataLoaders.from_csv(args.trainset,
                                     path="",
                                     y_names=args.predict_field,
                                     cat_names=[args.predict_field],
                                     cont_names=field_names,
                                     proc=[Categorify])

#learner = tabular_learner(loader, metrics=[accuracy, rmse], layers=[300, 200, 100, 50, 20, 1])
learner = tabular_learner(loader, metrics=[accuracy])

# Exploring the learning rates
# learner.lr_find(start_lr = 1e-05,end_lr = 1e+05, num_it = 1000)

# Train
learner.fit_one_cycle(args.train_cycles)

# Save the resulting model
learner.export(fname=args.output)
