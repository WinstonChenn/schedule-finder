from ortools.sat.python import cp_model
from SchedulePrinter import SchedulePrinter
import numpy as np
import datetime

class ScheduleSolver():

    def __init__(self, preference_matrix, shift_matrix, num_people, num_shifts, num_days):
        self.pref_mat = preference_matrix
        self.shift_mat = shift_matrix
        self.num_people = num_people
        self.num_shifts = num_shifts
        self.num_days = num_days

    def solve_schedule(self):
        peop_range = range(self.num_people)
        day_range = range(self.num_days)
        shift_range = range(self.num_shifts)
        total_shifts = 0

        # pref_matrix should go [people][days][shifts]
        if(not self.pref_mat.shape == (self.num_people, self.num_days, self.num_shifts) and
                not self.shift_mat.shape == (self.num_days, self.num_shifts)):
            print("ERROR: Preference Matrix is incorrectly shaped.")
            return None
        
        # setup all variables
        model = cp_model.CpModel()
        shifts = {}
        for p in peop_range:
            for d in day_range:
                for s in shift_range:
                    valid = bool(self.shift_mat[d, s])
                    if valid:
                        total_shifts += 1
                    shifts[(p, d, s)] = model.NewBoolVar('shift_p%id%is%i' % (p, d, s))

        total_shifts = total_shifts // self.num_people
        # Each shift has people_per_shift people.
        people_per_shift = 1
        for d in day_range:
            for s in shift_range:
                valid = bool(self.shift_mat[d, s])
                if valid:
                    model.Add(sum(shifts[(p, d, s)] for p in peop_range) == people_per_shift)
                else:
                    model.Add(sum(shifts[(p, d, s)] for p in peop_range) == 0)

        for p in peop_range:
            for d in day_range:
                shifts_per_day = self.get_max_shifts(self.shift_mat[d])
                shift_array = []
                for s in shift_range:
                    valid = bool(self.shift_mat[d, s])
                    if valid:
                        shift_array.append(shifts[(p, d, s)])
                # XOR condition for 0, 2 (both night time shift) and 1, 3 (both day time shift)
                if (bool(self.shift_mat[d, 0]) and bool(self.shift_mat[d, 2])):
                    model.Add(sum([shifts[(p, d, 0)], shifts[(p, d, 2)]]) <= 1)
                if (bool(self.shift_mat[d, 1]) and bool(self.shift_mat[d, 3])):
                    model.Add(sum([shifts[(p, d, 1)], shifts[(p, d, 3)]]) <= 1)
                model.Add(sum(shift_array) <= shifts_per_day)

    # Distribute the shifts evenly
    # Each staff works min_shifts_per_nurse shifts.
    # If this is not possible, because the total number of shifts
    # is not divisible by the number of nurses, some staff will
    # be assigned one more shift.
        min_shifts_per_person = total_shifts // self.num_people
        if total_shifts % self.num_people == 0:
            max_shifts_per_person = min_shifts_per_person
        else:
            max_shifts_per_person = min_shifts_per_person + 1

        # apply min_shifts_per_person and max_shifts_per_person constrains
        for p in peop_range:
            num_shifts_worked = 0
            for d in day_range:
                for s in shift_range:
                    valid = bool(self.shift_mat[d, s])
                    if valid:
                        num_shifts_worked += shifts[(p, d, s)]
            model.Add(min_shifts_per_person <= num_shifts_worked)
            model.Add(num_shifts_worked <= max_shifts_per_person)
        
            bool_array = []
            for p in peop_range:
                for d in day_range:
                    for s in shift_range:
                        valid = bool(self.shift_mat[d, s])
                        if valid:
                            bool_array.append(int(self.pref_mat[p][d][s]) * shifts[(p, d, s)])
            # accomondate request
            model.Maximize(sum(bool_array))
            # Creates the solver and solve.
            solver = cp_model.CpSolver()
            print("solving")
            solver.Solve(model)
            print("solved")
        
            print(solver.StatusName())
            if (solver.StatusName() != "INFEASIBLE"):
                # for d in day_range:
                #     print('Day', d)
                #     for p in peop_range:
                #         for s in shift_range:
                #             valid = self.shift_mat[d, s] > -2
                #             if valid:
                #                 if solver.Value(shifts[(p, d, s)]) == 1:
                #                     if preference_matrix[p][d][s] >= 1:
                #                         print('Staff', p, 'works shift', s, '(requested).')
                #                     else:
                #                         print('Staff', p, 'works shift', s, '(not requested).')
            
                #     print()

                # # Statistics.
                # print()
                # print('Statistics')
                # print('  - Number of shift requests met = %i' % solver.ObjectiveValue(),
                #     '(out of', num_people * min_shifts_per_person, ')')
                # print('  - wall time       : %f s' % solver.WallTime())

                return solver, shifts


    # given the binary setting for 4 shifts, solve maximum
    # number of shifts one staff can have that day
    # Used Boolean Algebra
    # Truth table Solved
    # shift1(A) shift2(B) shift3(C) shift4(D)  max_shift_per_day_per_person
    #     0        0         0         0             0      0   (0)
    #     0        0         0         1             0      1   (1)
    #     0        0         1         0             0      1   (1)
    #     0        0         1         1             1      0   (2)

    #     0        1         0         0             0      1   (1)
    #     0        1         0         1             0      1   (1)
    #     0        1         1         0             1      0   (2)
    #     0        1         1         1             1      0   (2)

    #     1        0         0         0             0      1   (1)
    #     1        0         0         1             1      0   (2)
    #     1        0         1         0             0      1   (1)
    #     1        0         1         1             1      0   (2)

    #     1        1         0         0             1      0   (2)
    #     1        1         0         1             1      0   (2)
    #     1        1         1         0             1      0   (2)
    #     1        1         1         1             1      0   (2)

    # Boolean Logis solution to the previous Truth Table
    # col1_out: CB + AD + AB + CD
    # col2_out: A !D !B + !B !D C + D !C !A + !A B !C
    def get_max_shifts(self, shifts):
        A = bool(shifts[0])
        B = bool(shifts[1])
        C = bool(shifts[2])
        D = bool(shifts[3])
        out1 = int(C & B | A & D | A & B | C & D)
        out2 = int(A & (~D) & (~B) | (~B) & (~D) & C | D & (~C) & (~A) | (~A) & B & (~C))

        # convert to decimal
        max_shift = out1 * 2**1 + out2 * 2**0

        return max_shift
