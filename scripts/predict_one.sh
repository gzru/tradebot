#!/usr/bin/env bash

set -e

source $(dirname $0)/config.sh

python3 -m predict_one \
    --model $MODEL_PATH \
    --symbol $SYMBOL \
    --interval $INTERVAL \
    --predict-field $PREDICT_FIELD \
    --train-batch $BATCH \
    --normalization $NORMALIZATION

