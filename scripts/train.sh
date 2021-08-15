#!/usr/bin/env bash

symbol="ADAUSDT"
interval="5m"
batch=100
predict_field="CCAT"
train_cycles=30
data="data/${symbol}.${interval}.csv"
trainset="data/${symbol}.${interval}.trainset.${batch}.csv"
model="data/${symbol}.${interval}.model.${batch}.pkl"

# Pepare trainset
#python3 -m trainset --data $data --output $trainset --predict-field $predict_field --train-batch $batch

# Train the model
python3 -m train --trainset $trainset --output $model --predict-field $predict_field --train-batch $batch --train-cycles $train_cycles
