import argparse

from binance.spot import Spot # type: ignore
from fetch.fetch import fetch_last_candles_to_csv
from structs.candle import Candle


# Create the parser
parser = argparse.ArgumentParser(description="Fetch candles from binance")

# Add the arguments
parser.add_argument("--symbol", type=str, required=True)
parser.add_argument("--interval", type=str, help="1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M", required=True)
parser.add_argument("-n", type=int, required=True)
parser.add_argument("--output", type=str, required=True)

# Execute the parse_args() method
args = parser.parse_args()

# Create binance connector
client = Spot()

count = fetch_last_candles_to_csv(client,
                                  symbol=args.symbol,
                                  interval=args.interval,
                                  limit=args.n,
                                  output_fname=args.output)

print("Records fetched: {}".format(count))

