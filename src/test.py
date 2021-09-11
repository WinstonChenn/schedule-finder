from ortools.sat.python import cp_model
from solver.SchedulePrinter import SchedulePrinter
import numpy as np

num_people = 10
num_shifts = 2
num_days = 70

all_people = range(num_people)
all_shifts = range(num_shifts)
all_days = range(num_days)

model = cp_model.CpModel()
shifts = {}

# create variables
for p in all_people:
    for d in all_days:
        for s in all_shifts:
            shifts[(p, d, s)] = model.NewBoolVar("shift_p{}d{}s{}".format(p, d, s))

# create constraints
for d in all_days:
    for s in all_shifts:
        model.Add(sum(shifts[(p, d, s)] for p in all_people) == 1)

for d in all_days:
    for p in all_people:
        model.Add(sum(shifts[(p, d, s)] for s in all_shifts) <= 1)

min_shifts_per_people = (num_days * num_shifts) // num_people
if num_shifts * num_days % num_people == 0:
    max_shifts_per_people = min_shifts_per_people
else:
    max_shifts_per_people = min_shifts_per_people + 1

for p in all_people:
    num_shifts_worked = 0
    for d in all_days:
        for s in all_shifts:
            num_shifts_worked += shifts[(p, d, s)]
    model.Add(min_shifts_per_people <= num_shifts_worked)
    model.Add(num_shifts_worked <= max_shifts_per_people)


solver = cp_model.CpSolver()
solver.parameters.linearization_level = 0

a_few_solutions = range(5)
solution_printer = SchedulePrinter(
    shifts,
    num_people,
    num_days,
    num_shifts,
    a_few_solutions
)

# solver.SearchForAllSolutions(model, solution_printer)
# staff_dict = {i:0 for i in all_people}
# for p in all_people:
#     for d in all_days:
#         for s in all_shifts:
#             if solver.Value(shifts[(p, d, s)]):
#                 staff_dict[p] += 1

solver.parameters.max_time_in_seconds = 10.0
solver.Solve(model)
print("solving...")
print(solver.StatusName())
req_met = 0
staff_dict = {i: 0 for i in all_people}
if (solver.StatusName() != "INFEASIBLE"):
    for p in all_people:
        for d in all_days:
            for s in all_shifts:
                if solver.Value(shifts[(p, d, s)]):
                    staff_dict[p] += 1
print(staff_dict)

print()
print('Statistics')
print('  - conflicts       : %i' % solver.NumConflicts())
print('  - branches        : %i' % solver.NumBranches())
print('  - wall time       : %f s' % solver.WallTime())
print('  - solutions found : %i' % solution_printer.solution_count())

print(staff_dict)