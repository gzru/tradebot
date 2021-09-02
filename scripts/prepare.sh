#!/usr/bin/env bash

set -ex

source $(dirname $0)/config.sh

time python3 -m trainset \
    --data $DATA_PATH \
    --output $TRAINSET_PATH \
    --predict-field $PREDICT_FIELD \
    --train-batch $BATCH \
    --normalization $NORMALIZATION
