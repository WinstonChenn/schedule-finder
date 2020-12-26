from ortools.sat.python import cp_model
from SchedulePrinter import SchedulePrinter
import numpy as np

def solve_schedule(preference_matrix, num_people, num_shifts, num_days):
    peop_range = range(num_people)
    day_range = range(num_days)
    shift_range = range(num_shifts)

    # pref_matrix should go [people][days][shifts]
    if(not preference_matrix.shape == (num_people, num_days, num_shifts)):
        print("ERROR: Preference Matrix is incorrectly shaped.")
        return None

    model = cp_model.CpModel()
    shifts = {}
    for p in peop_range:
        for d in day_range:
            for s in shift_range:
                shifts[(p, d,
                        s)] = model.NewBoolVar('shift_p%id%is%i' % (p, d, s))

    # Each shift has people_per_shift people.
    people_per_shift = 1
    for d in day_range:
        for s in shift_range:
            model.Add(sum(shifts[(p, d, s)] for p in peop_range) == people_per_shift)

    # Each person works at most shifts_per_day, shifts per day.
    shifts_per_day = 1 
    for p in peop_range:
        for d in day_range:
            model.Add(sum(shifts[(p, d, s)] for s in shift_range) <= shifts_per_day)

    # Try to distribute the shifts evenly, so that each nurse works
    # min_shifts_per_nurse shifts. If this is not possible, because the total
    # number of shifts is not divisible by the number of nurses, some nurses will
    # be assigned one more shift.
    min_shifts_per_person = (num_shifts * num_days) // num_people
    if num_shifts * num_days % num_people == 0:
        max_shifts_per_person = min_shifts_per_person
    else:
        max_shifts_per_person = min_shifts_per_person + 1

    # find solutions that make sure each person works the appropriate
    # amount of equally distributed shifts
    for p in peop_range:
        num_shifts_worked = 0
        for d in day_range:
            for s in shift_range:
                num_shifts_worked += shifts[(p, d, s)]
        model.Add(min_shifts_per_person <= num_shifts_worked)
        model.Add(num_shifts_worked <= max_shifts_per_person)

    model.Maximize(
        sum(preference_matrix[p][d][s] * shifts[(p, d, s)] for p in peop_range
            for d in day_range for s in shift_range))
    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    solver.Solve(model)

    for d in day_range:
        print('Day', d)
        for p in peop_range:
            for s in shift_range:
                if solver.Value(shifts[(p, d, s)]) == 1:
                    if preference_matrix[p][d][s] == 1:
                        print('Nurse', p, 'works shift', s, '(requested).')
                    else:
                        print('Nurse', p, 'works shift', s, '(not requested).')
        print()

    # Statistics.
    print()
    print('Statistics')
    print('  - Number of shift requests met = %i' % solver.ObjectiveValue(),
          '(out of', num_people * min_shifts_per_person, ')')
    print('  - wall time       : %f s' % solver.WallTime())