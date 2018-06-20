import os
from CONSTANTS import CONSTANTS

execfile("./source/lib/SCons/setup.py")

env.CacheDir(os.path.join("/data/cache", env.RIIPL_PROJECT))

# SQL functions
env.SConscript("source/lib/SQL/Make")

# Tests - these are primary for testing modifications
# to the template and can be removed from production code
env.SConscript("test/lib/Python/Make")
env.SConscript("test/lib/SQL/Make")

# Inputs
env.SConscript("source/inputs/Make")

# Populations
env.SConscript("source/populations/Make")

# Outcomes
env.SConscript("source/outcomes/Make")

# Features
env.SConscript("source/features/Make")

# Models
env.SConscript("source/models/Make")

# Figures
env.SConscript("source/figures/Make")

# Tables
env.SConscript("source/tables/Make")
