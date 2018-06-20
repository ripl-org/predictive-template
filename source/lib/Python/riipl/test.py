"""
Common assert-based tests for datasets.
"""

import math
import pandas as pd


def TestValue(series, value, frequency, comparison="<="):
    """
    Test the `frequency` of elements in `series` that have the given `value` and
    assert the `comparison`.

    Returns the actual `frequency`.
    """
    n = (series == value).sum()
    p = 0.1 * math.ceil(1000.0 * n / len(series))
    print series.name, "==", value, "for", n, "of", len(series), "(<{:.1f}%)".format(p)
    if   comparison == "<=":
        assert        n <= (frequency * len(series))
    elif comparison ==  "<":
        assert        n  < (frequency * len(series))
    elif comparison == "==":
        assert        n == (frequency * len(series))
    elif comparison ==  ">":
        assert        n  > (frequency * len(series))
    elif comparison == ">=":
        assert        n >= (frequency * len(series))
    else:
        raise ValueError("unknown comparison")
    return float(n) / len(series)


def TestMissing(series, frequency, comparison="<="):
    """
    Test the `frequency` of elements in `series` that are missing and assert
    the `comparison`.

    Returns the actual `frequency`.
    """
    n = (series.isnull()).sum()
    p = 0.1 * math.ceil(1000.0 * n / len(series))
    print series.name, "is missing for", n, "of", len(series), "(<{:.1f}%)".format(p)
    assert n <= (frequency * len(series))
    if   comparison == "<=":
        assert        n <= (frequency * len(series))
    elif comparison ==  "<":
        assert        n  < (frequency * len(series))
    elif comparison == "==":
        assert        n == (frequency * len(series))
    elif comparison ==  ">":
        assert        n  > (frequency * len(series))
    elif comparison == ">=":
        assert        n >= (frequency * len(series))
    else:
        raise ValueError("unknown comparison")
    return float(n) / len(series)


def CheckFailures(df, failures):
    """
    Given a DataFrame and boolean list of failures, return whether test passed
    and print examples of any failures.
    """
    if failures.sum() != 0:
        print(df[failures].head())
        return False
    return True


def TestNonNull(df, col):
    """
    Test a column from a dataframe to validate that values are not null.
    """
    print("Validating %s does not contain null values" % col)
    failures = df[col].isnull()
    return CheckFailures(df, failures)


def TestGreater(df, col, thresh):
    """
    Test a column from a dataframe to validate that all values are > threshold.
    """
    print("Validating %s is > %.2f" % (col, thresh))
    failures = df[col] <= thresh
    return CheckFailures(df, failures)


def TestGreaterEqual(df, col, thresh):
    """
    Test a column from a dataframe to validate that all values are >= threshold.
    """
    print("Validating %s is >= %.2f" % (col, thresh))
    failures = df[col] < thresh
    return CheckFailures(df, failures)


def TestLess(df, col, thresh):
    """
    Test a column from a dataframe to validate that all values are < threshold.
    """
    print("Validating %s is < %.2f" % (col, thresh))
    failures = df[col] >= thresh
    return CheckFailures(df, failures)


def TestLessEqual(df, col, thresh):
    """
    Test a column from a dataframe to validate that all values are <= threshold.
    """
    print("Validating %s is <= %.2f" % (col, thresh))
    failures = df[col] > thresh
    return CheckFailures(df, failures)


def TestBool(df, col):
    """
    Test a column from a dataframe to validate that all values are ones or zeroes.
    """
    print("Validating %s is boolean (0/1)" % col)
    failures = (df[col] != 0) & (df[col] != 1)
    return CheckFailures(df, failures)


def TestMaxValue(df, col, val):
    """
    Test a column from a dataframe to validate that the max value == val.
    """
    print("Validating max of %s == %.2f" % (col, val))
    ordered = df[col].sort_values(ascending=False)
    max_val = ordered.iloc[0]
    if max_val != val:
        print("Maximum value %.2f != %.2f" % (max_val, val))
        return False
    return True


def TestMinValue(df, col, val):
    """
    Test a column from a dataframe to validate that the min value == val.
    """
    print("Validating min of %s == %.2f" % (col, val))
    ordered = df[col].order()
    min_val = ordered.iloc[0]
    if min_val != val:
        print("Minimum value %.2f != %.2f" % (min_val, val))
        return False
    return True


# vim: expandtab sw=4 ts=4
