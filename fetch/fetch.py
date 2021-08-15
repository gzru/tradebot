from structs.candle import Candle
from binance.spot import Spot # type: ignore
from typing import Optional


def fetch_candles(client: Spot, symbol: str, interval: str, limit: int = 500, end_time: Optional[int] = None):
    limit = min(limit, 1000)
    batch = client.klines(symbol=symbol, interval=interval, limit=limit, endTime=end_time)
    if not batch:
        return None
    candles = list()
    for record in batch:
        candles.append(Candle(record))
    return candles

def _write_candle(candle: Candle, fd):
    fd.write(candle.to_csv_all())
    fd.write("\n")

def fetch_last_candles_to_csv(client: Spot, symbol: str, interval: str, limit: int, output_fname: str) -> int:
    # Open output file
    output_fd = open(output_fname, "w")
    # Fetch loop
    end_time = None
    records_left = limit
    records_count = 0
    while records_left > 0:
        batch = fetch_candles(client, symbol=symbol, interval=interval, end_time=end_time, limit=records_left)
        if not batch:
            break
        # Drop latest record cause it most likely incomplete
        if not end_time:
            del batch[-1]
        for candle in reversed(batch):
            _write_candle(candle, output_fd)
            records_left -= 1
            records_count += 1
            if records_left <= 0:
                break
        end_time = int(batch[0].data[0]) - 1
    return records_count
