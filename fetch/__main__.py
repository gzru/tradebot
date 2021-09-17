"""Tool to fetch last candles for given list of symbols and store them as csv files.

"""

import argparse

from binance import spot # type: ignore

from fetch import fetcher


def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="Fetch candles from binance")

    # Add the arguments
    parser.add_argument("--symbol", type=str, required=True)
    parser.add_argument("--interval", type=str,
                        help="1m, 3m, 5m, 15m, 30m, 1h, ...", required=True)
    parser.add_argument("-n", type=int, required=True)
    parser.add_argument("--output", type=str, required=True)

    # Execute the parse_args() method
    args = parser.parse_args()

    # Unpack symbol list
    symbols = args.symbol.split(",")

    # Create binance connector
    client = spot.Spot()

    fetcher_inst = fetcher.Fetcher(client)
    for symbol in symbols:
        # Replace <SYMBOL> template
        output = args.output.replace("<SYMBOL>", symbol)
        count = fetcher_inst.fetch_last_candles_to_csv(symbol=symbol,
                                                       interval=args.interval,
                                                       limit=args.n,
                                                       output_fname=output)

        print("Symbol: {}, records fetched: {}, file: {}".format(symbol, count, output))

if __name__ == '__main__':
    main()
