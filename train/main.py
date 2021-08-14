


"""
learner = load_learner(fname="model.pkl")

x = 2
y = math.sin(x)

record = pd.Series(
    data=[x, y],
    index=["x", "y"])

row, clas, probs = learner.predict(record)
print("x={}, y={}".format(x, y))
print("Row:\n", row)
print("Clas:\n", clas)
print("Probs:\n", probs)
"""
