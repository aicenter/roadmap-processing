import numpy as np
import pandas
from pandas import DataFrame
a = 5.9975
b = np.float64(a)

df = DataFrame([a])
df2 = DataFrame.from_csv("float.csv", header=None, index_col=None)


c = a == b