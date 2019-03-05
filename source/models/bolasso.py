import pandas as pd
import sys

manifest_file = sys.argv[1]
beta_files    = sys.argv[2:-2]
matrix_file   = sys.argv[-2]
csv_file      = sys.argv[-1]

# Load manifest
manifest = pd.read_csv(manifest_file, sep="\t", header=None, names=["var", "desc"])\
             .drop_duplicates("var")\
             .set_index("var")

beta = pd.read_csv(beta_files[0], names=["var", "coef"], skiprows=1, index_col="var")

bolasso = pd.DataFrame(index=beta.index)
bolasso["bootstrap0"] = (beta.coef != 0).astype(int)

for i, beta_file, in enumerate(beta_files[1:], start=1):
    beta = pd.read_csv(beta_files[i], names=["var", "coef"], skiprows=1, index_col="var")
    pd.testing.assert_index_equal(bolasso.index, beta.index)
    bolasso["bootstrap{}".format(i)] = (beta.coef != 0).astype(int)

bolasso.to_csv(matrix_file)

bolasso["freq"] = bolasso.sum(axis=1)
bolasso = bolasso.join(manifest).sort_values("freq", ascending=False).reset_index()
bolasso[["freq", "var", "desc"]].to_csv(csv_file, index=False)

# vim: expandtab sw=4 ts=4
