# RIPL Predictive Modeling Template

This template contains the base code underlying several predictive models
developed by [Research Improving People's Lives](https://ripl.org).  The
primary goal of the template is to enable reproducible and automated research
results, and to provide a standardized framework for creating predictive models
across different research projects. This template repo can be forked and
modified for the populations, outcomes, and features of a specific predictive
model. It is designed around a specific secure research computing environment
at RIPL that provides an Oracle database and a network-attached file system
with a results cache (`/data/cache/`) shared by all users. However, it could be
extended to other compute environments with some modification.

## Repo layout

| Subdirectory | Description |
| --- | --- |
| **input** | Raw data which will not be stored in the repo. This is typically a symlink to a read-only directly containing archival flat files. |
| **output** | Small output files that will be versioned in git. This is especially helpful for storing results that need to quickly accessed in the future without recomputing them. However, large files should be avoided since they will bloat the size of the git repo. |
| **scratch** | Staging area for large intermediate and output files. These files will be cached by SCons, so they often do not need to be recomputed again after they have been created the first time. SCons caches the output base on the full checksums of all dependencies. |
| **source/inputs** | Source files for staging, transforming, indexing flat files from **inputs**. |
| **source/populations** | Source files for defining populations of interest for the model. |
| **source/outcomes** | Source files for building the model's outcomes (typically depends on populations). |
| **source/features** | Source files for building model's features (typically depends on populations). |
| **source/models** | Source files for concatenating features into design matrices, then running and tuning models (typically depends on outcomes and features). |
| **source/figures** | Source files for generating figures (typically depends on models). |
| **source/tables** | Source files for generating tables (typically depends on models). |

## SCons

The template uses the extensible [SCons](http://scons.org) software
construction tool to define dependencies between analysis steps and to automate
an analysis run from start to finish. The top-level `SConstruct` makefile
defines the overall build structure by including makefiles from each of the
`source` subdirctories described above. We have tested the template with SCons
2.5.1 and 3.0.1 and Python 2.7.

### Constants

If you have several features that are all parametrized by the same value, such
as the random seed for a model or the start and end dates of a panel, you can
store these global values as constants in `CONSTANTS.py`:

    CONSTANTS = {
        "RANDOM_SEED": 1337,
        "START": 20010101,
        "END": 20160101
    }

All key/value pairs in `CONSTANTS` are exported to the SCons `env` object via
the extension in `source/lib/SCons/env.py`. For example, the start/end values
above could be accessed in the populations makefile (`source/populations/Make`)
as `env.START` and `env.END`.  The random seed might be accessed in the models
makefile (`source/models/Make`) as `env.RANDOM_SEED`.

### SQLTable node

The SQLTable extension in `source/libs/SCons/sql_table_node.py` allows SCons to
view a read-only Oracle SQL table as a file-like dependency. A rule can both
depend on a SQL table for its input, and generate a SQL table as its output.
The table must be constructed using the included Python library, which will
mark the table as read-only and compute a checksum by concatenating and hashing
all cells in the table. This checksum is stored as a table comment and can be
quickly accessed by SCons to determine if the table's contents have changed.

### Python, R, and Stata builders

The builder extensions in `source/lib/SCons/builders.py` make it easier to call
Python, R, and Stata scripts from a makefile, instead of using the more generic
`env.Command`.  In these functions, you must specify a list of targets first,
then a list of sources. The first source must be the code file to be run.
These functions all automatically produce a log of the execution. The log is
always stored in the output folder for the corresponding source subdirectory.
Examples are provided below.

#### Python

    env.Python(
        ["#output/features/feature1.csv", "#output/features/feature1.manifest"],
        ["feature1.py", "#inputs/feature1_data.csv"]
    )

The log file will be `output/features/feature1.py.log`.

#### R

    env.R(
        ["#output/features/feature1.csv", "#output/features/feature1.manifest"],
        ["feature1.R", "#input/feature1_data.csv"]
    )

The log file will be `output/features/feature1.R.log`.

#### Stata

    env.Stata(
        ["#output/features/feature1.csv", "#output/features/feature1.manifest"],
        ["feature1.do", "#input/feature1_data.csv"]
    )

The log file will be `output/features/feature1.do.log`.

## Python library

The primary feature of the library is a Connection object, which encapsulates a
connection to an Oracle database and provides helper methods for working with
SQL tables and statements.

The Connection object may used as a context manager. When used as a context
manager, database connections are automatically closed even in the event of an
unhandled exception. For this reason, it is recommended that Connections be
opened using the "with ... as ..." keyword.

#### `execute` method

Automatically pastes parameters into SQL statements.  Parameter names must be
enclosed in '%' and must resolve to a defined variable in the caller's local
scope.  If no matching parameter is found, the calling frame's global variables
are searched next. If no matching parameter is found a NameError is raised.

Example:

    with Connection() as cxn:
        max_spend = 10000
        cxn.execute("SELECT * FROM table WHERE spend <= %max_spend%")

#### `save_table` method

Based on Stata's `save_data` command, but for tables in an Oracle database.  It
can add a primary key index on the table, and will print out summary statistics
for the table.

Example:

    max_valid_amount = 8
    sql = """
          CREATE TABLE new_table AS
          SELECT *  
            FROM table
           WHERE amount < %max_valid_amount%
          """
    with Connection() as cxn:
        cxn.execute(sql)
        cxn.save_table("new_table", "key_variable")

#### `read_csv` method

Creates a SQL table from a csv file using Oracle's `sqlldr` utility. Requires a
schema list that maps columns to their Oracle types.

#### `read_dataframe` method

Like `read_csv`, but starts from a pandas dataframe, and can automatically
infer the schema based on the pandas column types.

