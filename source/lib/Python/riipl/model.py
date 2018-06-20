"""
Helper functions for working with predictive models.
"""

import cx_Oracle
import h5py
import numpy as np
import pandas as pd
from riipl.test import *

pd.set_option("display.float_format", lambda x: "%.3f" % x)

_population = pd.DataFrame()

def CachePopulation(table, keys):
    if isinstance(keys, str):
        keys = [keys]

    global _population
    if _population.empty:
        with cx_Oracle.connect("/") as cxn:
            _population = pd.read_sql("""
                            SELECT {k} FROM {t} ORDER BY {k}
                            """.format(t=table, k=",".join(keys)), cxn)
        print "[riipl.model] size of population:", len(_population)

    return _population


def TestPopulation(df, table, keys):
    """
    Test a dataframe with RIIPL_ID and MONTH_DT columns to validate that
    they have the exact same indexing as the population.
    """
    if isinstance(keys, str):
        keys = [keys]
    
    population = CachePopulation(table, keys)

    if type(df.index) == pd.RangeIndex:
        df = df.set_index(keys)
    else:
        df = df.reset_index()
        df = df.set_index(keys)

    if not df.index.is_monotonic:
            print "[riipl.model] dataframe not sorted on keys: {}".format(','.join(keys))
            return False

    df = df.reset_index()

    for key in keys:
        if key not in df.columns:
            print "[riipl.model] dataframe does not have {} column:".format(key)
            print str(df.columns)
            return False

        if not df[key].equals(population[key]):
            print "[riipl.model] {} does not match:".format(key)
            df["POPULATION_{}".format(key)] = population[key]
            df = df[[key, "POPULATION_{}".format(key)]]
            print df[df[key] != df["POPULATION_{}".format(key)]].head()
            return False

    return True


def SaveFeatures(df, out, manifest_file, population_def, labels_dict, bool_features = []):
    population_table = population_def[0]
    keys = population_def[1]
    if isinstance(keys, str):
        keys = [keys]

    assert TestPopulation(df, population_table, keys)

    if type(df.index) == pd.RangeIndex:
        df = df.set_index(keys)
    else:
        df = df.reset_index()
        df = df.set_index(keys)

    df_cols = df.columns.tolist()
    
    for feature in df_cols:
        assert TestNonNull(df, feature), "[riipl.model] '{}' fails not-null test".format(feature)
        assert feature in labels_dict, "[riipl.model] '{}' not in labels_dict".format(feature)
        if feature in bool_features:
            assert TestBool(df, feature)

    labels_dict = {feature: labels_dict[feature] for feature in df_cols}

    with open(manifest_file, 'w') as manifest:
        for feature, label in labels_dict.iteritems():
            manifest.write("{}\t{}\n".format(feature, label))

    print df.describe()

    df.to_csv(out)


def ReadHDF5(filename, usecols=None, index_col=None):
    """
    Read a RIIPL column-store formatted HDF5 file into a pandas dataframe.
    """
    f = h5py.File(filename, "r")
    datasets = f.keys()
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


# vim: expandtab sw=4 ts=4
