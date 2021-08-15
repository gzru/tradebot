#!/usr/bin/env bash

symbol="ADAUSDT"
interval="5m"
n=40000

output="data/${symbol}.${interval}.csv"

python3 -m fetch --symbol $symbol --interval $interval -n $n --output $output
