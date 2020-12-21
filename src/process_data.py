import pandas
import os

# over write all staff requirements to -2 - 2 scale
# use lower case y for two year encoding
# 1 -> -1
# 2 -> 0
# 3 -> 1
# 4 -> 2
# -2 reserved for unreal shifts
# print(os.getcwd())
m = pandas.read_excel("data/staff_requirements.xlsx")

# print(type(m.loc[1]["Sunday"]))

for i in range(0, 10):          # ranges over the rows
    for column_head in m.columns[1:]: # ranges over the columns
        # print(m.loc[i][column_head], i, column_head)
        m.loc[i][column_head] = int(m.loc[i][column_head][0]) - 2

m.to_excel("data/scaled_staff_req.xlsx")