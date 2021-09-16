#!/usr/bin/env bash

set -ex

source $(dirname $0)/config.sh

data_path_list=""
for symbol in "${TRAIN_SYMBOLS[@]}"
do
    data_path="$(GET_DATA_PATH $symbol)"
    data_path_list="$data_path_list,$data_path"
done
data_path_list=${data_path_list:1}

trainset_path="$(GET_TRAINSET_PATH JOINT)"

time python3 -m trainset \
    --data $data_path_list \
    --output $trainset_path \
    --predict-field $PREDICT_FIELD \
    --train-batch $BATCH \
    --train-fields $TRAIN_FIELDS \
    --normalization $NORMALIZATION
