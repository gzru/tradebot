#!/usr/bin/env bash

set -ex

source $(dirname $0)/config.sh

data_path_list=""
for symbol in "${TRAIN_SYMBOLS[@]}"
do
    data_path="${DATA_PATH/<SYMBOL>/$symbol}"
    data_path_list="$data_path_list,$data_path"
done
data_path_list=${data_path_list:1}

time python3 -m trainset \
    --data $data_path_list \
    --output $TRAINSET_PATH \
    --predict-field $PREDICT_FIELD \
    --train-batch $BATCH \
    --normalization $NORMALIZATION
