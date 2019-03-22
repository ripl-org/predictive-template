from .connection import Connection
from .model import *
from .sql_exceptions import *
from .test import *

def bootstrap(data, N, statistic, seed):
    replicates = sorted(statistic(data.sample(n=len(data),
                                              replace=True,
                                              random_state=seed+i))
                        for i in range(N))
    ci_lower = replicates[int(0.025 * N)]
    ci_upper = replicates[int(0.975 * N)]
    return statistic(data), ci_lower, ci_upper

# vim: syntax=python expandtab sw=4 ts=4
