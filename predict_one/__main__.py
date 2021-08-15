import argparse

from binance.spot import Spot # type: ignore
from fastai.tabular.all import *
from structs.candle import make_batch_name_list, make_pandas_series
from fetch.fetch import fetch_candles


# Create the parser
parser = argparse.ArgumentParser(description="Predict next candle field")

# Add the arguments
parser.add_argument("--model", type=str, default="data/ADAUSDT.5m.model.100.pkl")
parser.add_argument("--symbol", type=str, default="ADAUSDT")
parser.add_argument("--interval", type=str, help="1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M", default="5m")
parser.add_argument("--predict-field", type=str, default="c")
parser.add_argument("--train-batch", type=int, default=100)

# Execute the parse_args() method
args = parser.parse_args()

# Load a model
learner = load_learner(fname=args.model)

# Create binance connector
client = Spot()

fetch_size = args.train_batch + 1
names = make_batch_name_list(args.train_batch)
while True:
    candles = fetch_candles(client,
                            symbol=args.symbol,
                            interval=args.interval,
                            limit=fetch_size)
    assert len(candles) == fetch_size

    last = candles[-1]
    prev = candles[-2]
    record = make_pandas_series(candles[:-1], names)
    row, clas, probs = learner.predict(record)

    time = client.time()["serverTime"]
    time_left = int(last.get_field("ct")) - time

    #print("Time: {}, left: {}".format(time, time_left))
    #print("Target: ot={}, ct={}".format(last.get_field("ot"), last.get_field("ct")))
    print("Clas: {}, Prev: {}".format(clas.item(), prev.get_field("c")))
    break

"""


x = 2
y = math.sin(x)

record = pd.Series(
    data=[x, y],
    index=["x", "y"])

row, clas, probs = learner.predict(record)
print("x={}, y={}".format(x, y))

"""
