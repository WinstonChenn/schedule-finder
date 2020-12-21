import pandas
import os

# over write all staff requirements to -2 - 2 scale
# 1 -> -1
# 2 -> 0
# 3 -> 1
# 4 -> 2
# -2 reserved for unreal shifts
print(os.getcwd())
m = pandas.read_excel("../data/staff_requirements.xlsx")
print(m)