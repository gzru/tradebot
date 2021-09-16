
TRAIN_SYMBOLS=(
    "BTCUSDT"
    "BNBUSDT"
    "ADAUSDT"
    "XRPUSDT"
    "DOGEUSDT"
    "DOTUSDT"
    "SOLUSDT"
)

INTERVAL="5m"
FETCH_N=60000
BATCH=100
PREDICT_FIELD="c"
NORMALIZATION="std"
TRAIN_CYCLES=30
TRAIN_FIELDS="c"

DATA_PATH_TMPL="data/<SYMBOL>.${INTERVAL}.csv"
GET_DATA_PATH() {
    local symbol="$1"
    echo "${DATA_PATH_TMPL/<SYMBOL>/$symbol}"
}

TRAINSET_PATH_TMPL="data/<SYMBOL>.${INTERVAL}.${NORMALIZATION}.trainset.${BATCH}.csv"
GET_TRAINSET_PATH() {
    local symbol="$1"
    echo "${TRAINSET_PATH_TMPL/<SYMBOL>/$symbol}"
}

MODEL_PATH_TMPL="data/${SYMBOL}.${INTERVAL}.${NORMALIZATION}.model.${BATCH}.pkl"
GET_MODEL_PATH() {
    local symbol="$1"
    echo "${MODEL_PATH_TMPL/<SYMBOL>/$symbol}"
}
