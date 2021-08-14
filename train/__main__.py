from fastai.tabular.all import *
from structs.klines import make_field_list

data_path = "data"
trainset = "data/trainset.csv"
batch_size = 100
predict_fields = ["c"]
fields = make_field_list(batch_size)


dls = TabularDataLoaders.from_csv(trainset, path=data_path, y_names=predict_fields,
    cont_names = fields,
    procs = [])
    #procs = [Normalize])

learn = tabular_learner(dls, metrics=[rmse])
# , layers=[300, 200, 100, 50, 20, 1]
# Exploring the learning rates
#learn.lr_find(start_lr = 1e-05,end_lr = 1e+05, num_it = 1000)
learn.fit_one_cycle(30)
learn.export(fname="model.pkl")
