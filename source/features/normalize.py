import numpy as np
import pandas as pd
import sys

population_file, features_file, out_file = sys.argv[1:]

index = ["SAMPLE_ID"]
protected = frozenset(("SAMPLE_ID", "SUBSET", "y"))

# Load population with partitions
X = pd.read_csv(population_file, usecols=index+["SUBSET"], index_col=index)
train = (X.SUBSET == "TRAINING")

x = pd.read_csv(features_file, index_col=index)
pd.testing.assert_index_equal(X.index, x.index)

# Infer variable types
for name, t in zip(x.columns, x.dtypes):

    # Protected names
    assert name not in protected

    # Drop empty variables
    if len(x.loc[train, name].unique()) == 1:
        print("dropping empty variable '{}'".format(name))
        continue

    if t == "object":
        # Create dummy variables from values observed in training data
        values = x.loc[train, name].value_counts()
        # Don't create a variable for the most frequent value, to avoid collinearity
        for val in values.index[1:]:
            dummy_name = "{}_{}".format(name, val.upper().replace(" ", "_"))
            X[dummy_name] = (x[name] == val).astype(int)
    else:
        assert t == "float" or t == "int"
        # Don't scale dummy variables
        if ((x[name] == 0) | (x[name] == 1)).all():
            X[name] = x[name].astype(int)
        else:
            m = x.loc[train, name].mean()
            s = x.loc[train, name].std()
            if s != 0:
                X[name] = x[name].subtract(m).divide(s)
            else:
                print("warning: {} has 0 stdev".format(name))
        # Impute missing values
        if X[name].isnull().any():
            print("Filling missing", name, "with mean value")
            X[name + "_MISSING"] = X[name].isnull().astype(int)
            X.loc[:, name] = X[name].fillna(0)

del X["SUBSET"]

# Save to csv
X.to_csv(out_file)

# vim: expandtab sw=4 ts=4
