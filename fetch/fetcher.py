from typing import Optional, List, TextIO

from binance import spot # type: ignore

from structs import candle2
from structs import candle_traits


class Fetcher:
    def __init__(self, client: spot.Spot, result_traits: candle_traits.CandleTraits = None):
        self.client: spot.Spot = client
        self.source_traits: candle_traits.CandleTraits = candle_traits.CandleTraits.base()
        self.result_traits: candle_traits.CandleTraits = (result_traits if result_traits
                                                          else self.source_traits)

    def fetch_candles(self, symbol: str, interval: str, limit: int = 500,
                      end_time: Optional[int] = None) -> List[candle2.Candle]:
        candles = self._fetch_candles(symbol=symbol, interval=interval,
                                      limit=limit, end_time=end_time)
        return self._convert_to_result_traits(candles)

    def fetch_last_candles_to_csv(self, symbol: str, interval: str,
                                  limit: int, output_fname: str) -> int:
        # Open output file
        output_fd = open(output_fname, "w")
        # Fetch loop
        end_time = None
        end_time_biased = None
        records_left = limit
        records_count = 0
        while records_left > 0:
            batch = self._fetch_candles(symbol=symbol, interval=interval,
                                        end_time=end_time_biased, limit=records_left)
            if not batch:
                break
            len(batch)
            # Remember results time frame
            earliest_timestamp = int(batch[0].get_field("ot", self.source_traits))
            latest_timestamp = int(batch[-1].get_field("ot", self.source_traits))
            # Drop latest record cause it most likely incomplete
            # And check for duplicates
            if not end_time or latest_timestamp == end_time:
                del batch[-1]
            if not batch:
                continue
            batch = self._convert_to_result_traits(batch)
            for candle in reversed(batch):
                Fetcher._write_candle(candle, output_fd)
                records_left -= 1
                records_count += 1
                if records_left <= 0:
                    break
            end_time = earliest_timestamp
            end_time_biased = end_time - 1000
        return records_count

    def _fetch_candles(self, symbol: str, interval: str, limit: int = 500,
                       end_time: Optional[int] = None) -> List[candle2.Candle]:
        limit = max(min(limit, 1000), 10)
        batch = self.client.klines(symbol=symbol, interval=interval, limit=limit, endTime=end_time)
        if not batch:
            return list()
        candles = list()
        for record in batch:
            candles.append(candle2.Candle.from_data(record, self.source_traits))
        return candles

    def _convert_to_result_traits(self, candles: List[candle2.Candle]) -> List[candle2.Candle]:
        if self.result_traits is self.source_traits:
            return candles
        return [candle.convert(self.source_traits, self.result_traits) for candle in candles]

    @staticmethod
    def _write_candle(candle: candle2.Candle, output: TextIO):
        output.write(candle.to_csv())
        output.write("\n")
