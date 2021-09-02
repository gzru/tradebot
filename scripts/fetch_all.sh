#!/usr/bin/env bash

set -ex

source $(dirname $0)/config.sh

symbol_list=$(printf ",%s" "${TRAIN_SYMBOLS[@]}")
symbol_list=${symbol_list:1}

time python3 -m fetch \
    --symbol $symbol_list \
    --interval $INTERVAL \
    -n $FETCH_N \
    --output $DATA_PATH

