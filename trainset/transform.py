from structs.candle import Candle


def make_3cat_transform(target: float, before: float, change_fraction: float) -> int:
    ratio = target / before
    if ratio > (1 + change_fraction):
        return 2
    if ratio < (1 - change_fraction):
        return 0
    return 1
