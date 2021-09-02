#!/usr/bin/env bash

set -ex

source $(dirname $0)/config.sh

time python3 -m fetch \
    --symbol $SYMBOL \
    --interval $INTERVAL \
    -n $FETCH_N \
    --output $DATA_PATH

