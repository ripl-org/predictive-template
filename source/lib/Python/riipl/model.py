"""
Helper functions for working with predictive models.
"""

import cx_Oracle
import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import seaborn as sns
from io import StringIO
from riipl.test import *

pd.set_option("display.float_format", lambda x: "%.3f" % x)

_population = pd.DataFrame()
_population_subsets = pd.DataFrame()

def CachePopulation(table, keys):
    if isinstance(keys, str):
        keys = [keys]

    global _population
    if _population.empty:
        with cx_Oracle.connect("/") as cxn:
            _population = pd.read_sql("""
                            SELECT {k} FROM {t} ORDER BY {k}
                            """.format(t=table, k=",".join(keys)), cxn)
        print("[riipl.model] size of population:", len(_population))

    return _population


def CachePopulationSubsets(table, keys):
    if isinstance(keys, str):
        keys = [keys]

    global _population_subsets
    if _population_subsets.empty:
        with cx_Oracle.connect("/") as cxn:
            _population_subsets = pd.read_sql("""
                                              SELECT {k}, subset FROM {t} ORDER BY {k}
                                              """.format(t=table, k=",".join(keys)), cxn)
        print("[riipl.model] size of population:", len(_population_subsets))

    return _population_subsets


def PopulationSizes(table, keys):
    nsubsets = CachePopulationSubsets(table, keys)["SUBSET"].value_counts()
    return [nsubsets["TRAINING"], nsubsets["VALIDATION"], nsubsets["TESTING"]]


def Partition(population, seed, training=0.5, validation=0.25, testing=0.25):
    """
    Partition population into training, validation, and testing sets.
    """
    np.random.seed(int(seed))
    population["SUBSET"] = np.random.choice(["TRAINING", "VALIDATION", "TESTING"],
                                            len(population),
                                            p=[training, validation, testing])
    print("partitioned into", (population.SUBSET == "TRAINING").sum(), "training,",
                              (population.SUBSET == "VALIDATION").sum(), "validation,",
                              (population.SUBSET == "TESTING").sum(), "testing")
    return population


def TestPopulation(df, table, keys):
    """
    Validate that df has the same indexing as the population.
    """

    if not df.index.is_unique:
        print("[riipl.model] index is not unique")
        return False

    if not df.index.is_monotonic_increasing:
        print("[riipl.model] index is not sorted")
        return False

    population = CachePopulation(table, keys).set_index(keys)
    if not df.index.equals(population.index):
        print("[riipl.model] index does not match population")
        return False

    return True


def SaveFeatures(df, out, manifest_file, population, labels, bool_features=[]):

    keys = df.index.names
    assert TestPopulation(df, population, keys)

    for feature in df.columns:
        assert feature in labels, "[riipl.model] '{}' not in labels".format(feature)
        if feature in bool_features:
            assert TestBool(df, feature), "[riipl.model] '{}' is not boolean".format(feature)

    labels = {feature: labels[feature] for feature in df.columns}

    with open(manifest_file, "w") as manifest:
        for feature, label in labels.items():
            manifest.write("{}\t{}\n".format(feature, label))

    print(df.describe())

    df.to_csv(out, float_format="%g")


def SaveTensor(tensor, labels, fill_values, population_def, out, nsteps=None):
    """
    Save a 3D tensor as (sample, timestep, feature, value) tuples.
    """
    # Construct a sample index in each of the subsets
    population = CachePopulationSubsets(population_def[0], population_def[1])
    train = population.SUBSET == "TRAINING"
    population.loc[train, "SAMPLE"] = np.arange(int(train.sum()))
    validate = population.SUBSET == "VALIDATION"
    population.loc[validate, "SAMPLE"] = np.arange(int(validate.sum()))
    test = population.SUBSET == "TESTING"
    population.loc[test, "SAMPLE"] = np.arange(int(test.sum()))
    population.loc[:, "SAMPLE"] = population.SAMPLE.astype(int)

    population.loc[:,        "SUBSET"] = 0
    population.loc[validate, "SUBSET"] = 1
    population.loc[test,     "SUBSET"] = 2

    keep = {}
    for feature, values in tensor.items():
        values = values.merge(population, on=population_def[1], how="left")
        assert values.SAMPLE.notnull().all()
        # Find and index the non-zero features in the training subset
        train = values.SUBSET == 0
        if train.any():
            if "VALUE" in values.columns:
                # Min-max normalization
                m = float(min(0, values.loc[train, "VALUE"].min()))
                r = values.loc[train, "VALUE"].max() - m
                if r == 0:
                    print("dropping feature with zero variance:", feature)
                    continue
                values.loc[:, "VALUE"] = (values.VALUE - m) / r
                # Fill value
                if fill_values[feature] == "mean":
                    fill_values[feature] = values.loc[train, "VALUE"].mean()
                elif fill_values[feature] == "median":
                    fill_values[feature] = values.loc[train, "VALUE"].median()
            else:
                values.loc[:, "VALUE"] = 1.0
            if nsteps and not "TIMESTEP" in values.columns:
                n = len(values)
                values = pd.concat([values] * nsteps)
                values["TIMESTEP"] = (np.arange(n * nsteps) / n).astype(int)
            keep[feature] = values[["SUBSET", "SAMPLE", "TIMESTEP", "VALUE"]]
            assert keep[feature].notnull().values.all()
            print(feature, keep[feature].describe(), sep="\n")
        else:
            print("dropping feature missing from training data:", feature)

    with open(out, "wb") as f:
        pickle.dump({"labels": labels, "values": keep, "fill_values": fill_values}, f)


def ReadHDF5(filename, usecols=None, index_col=None):
    """
    Read a RIIPL column-store formatted HDF5 file into a pandas dataframe.
    """
    f = h5py.File(filename, "r")
    datasets = list(f.keys())
    if usecols is not None:
        for col in usecols: assert col in datasets
        datasets = usecols
    n = len(f[datasets[0]])
    for d in datasets[1:]:
         assert n == len(f[d])
    data = {}
    for d in datasets:
        data[d] = np.array(f[d])
    df = pd.DataFrame.from_dict(data)
    if index_col is not None:
        return df.set_index(index_col)
    else:
        return df


class FeaturePlots(object):
    """
    """

    def __init__(self, y):
        self.y = y.values
        self.html = ['<!DOCTYPE html>',
                     '<html xmlns="http://www.w3.org/1999/xhtml">',
                     '<head><title>Features</title></head>',
                     '<body>']

    def add(self, name, x, dummy=False):
        self.html.append("<h1>{}</h1>".format(name))
        plt.figure(figsize=(10, 2))
        x = x.values
        if dummy:
            sns.pointplot(x=x, y=self.y, orient="h", n_boot=100)
            plt.xlim((0, 1))
        else:
            sns.boxplot(x=x, y=self.y, orient="h")
        plt.tight_layout()
        svg = StringIO()
        plt.savefig(svg, format="svg")
        svg.seek(0)
        self.html.append(svg.getvalue())
        plt.close()

    def write(self, filename):
        with open(filename, "w") as f:
            print("\n".join(self.html), file=f)
            print("</body>\n</html>", file=f)

# vim: expandtab sw=4 ts=4
