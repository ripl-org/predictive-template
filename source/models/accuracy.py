import pandas as pd
import sys

y_pred_file, out_file = sys.argv[1:]

y = pd.read_csv(y_pred_file).sort_values("y_pred", ascending=False)
decile = len(y) // 10

with open(out_file, "w") as f:
    print("decile,size,outcomes", file=f)
    for i in range(1, 11):
        y_i = y.iloc[(i-1)*decile:i*decile]
        print("{},{},{}".format(i, decile, y_i["y_test"].sum()), file=f)

# vim: expandtab sw=4 ts=4
