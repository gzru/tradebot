#!/usr/bin/env bash

set -ex

source $(dirname $0)/config.sh

time python3 -m train \
    --trainset $TRAINSET_PATH \
    --output $MODEL_PATH \
    --predict-field $PREDICT_FIELD \
    --train-batch $BATCH \
    --train-cycles $TRAIN_CYCLES
