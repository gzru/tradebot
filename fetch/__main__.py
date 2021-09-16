import argparse

from binance.spot import Spot # type: ignore
from fetch.fetch import Fetcher


# Create the parser
parser = argparse.ArgumentParser(description="Fetch candles from binance")

# Add the arguments
parser.add_argument("--symbol", type=str, required=True)
parser.add_argument("--interval", type=str, help="1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M", required=True)
parser.add_argument("-n", type=int, required=True)
parser.add_argument("--output", type=str, required=True)

# Execute the parse_args() method
args = parser.parse_args()

# Unpack symbol list
symbols = args.symbol.split(",")

# Create binance connector
client = Spot()

fetcher = Fetcher(client)
for symbol in symbols:
    # Replace <SYMBOL> template
    output = args.output.replace("<SYMBOL>", symbol)
    count = fetcher.fetch_last_candles_to_csv(symbol=symbol,
                                                interval=args.interval,
                                                limit=args.n,
                                                output_fname=output)

    print("Symbol: {}, records fetched: {}, file: {}".format(symbol, count, output))
