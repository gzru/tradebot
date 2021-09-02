from structs.candle2 import Candle
from structs.candle_traits import CandleTraits
from binance.spot import Spot # type: ignore
from typing import Optional, List, TextIO


class Fetcher:
    def __init__(self, client: Spot, traits: CandleTraits = CandleTraits()):
        self.client: Spot = client
        self.traits: CandleTraits = traits

    def fetch_candles(self, symbol: str, interval: str, limit: int = 500, end_time: Optional[int] = None) -> List[Candle]:
        limit = min(limit, 1000)
        batch = self.client.klines(symbol=symbol, interval=interval, limit=limit, endTime=end_time)
        if not batch:
            return list()
        candles = list()
        for record in batch:
            candles.append(Candle.from_data(record, self.traits))
        return candles

    def fetch_last_candles_to_csv(self, symbol: str, interval: str, limit: int, output_fname: str) -> int:
        # Open output file
        output_fd = open(output_fname, "w")
        # Fetch loop
        end_time = None
        records_left = limit
        records_count = 0
        while records_left > 0:
            batch = self.fetch_candles(symbol=symbol, interval=interval, end_time=end_time, limit=records_left)
            if not batch:
                break
            # Drop latest record cause it most likely incomplete
            if not end_time:
                del batch[-1]
            for candle in reversed(batch):
                self._write_candle(candle, output_fd)
                records_left -= 1
                records_count += 1
                if records_left <= 0:
                    break
            end_time = int(batch[0].get_field("ot", self.traits)) - 1
        return records_count

    def _write_candle(self, candle: Candle, fd: TextIO):
        fd.write(candle.to_csv())
        fd.write("\n")
