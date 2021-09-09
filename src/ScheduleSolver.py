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
        total_primary_shifts = 0
        total_secondary_shifts = 0
        total_daytime_shifts = 0

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
                    if bool(self.shift_mat[d, s]):
                        if s == 0:
                            total_primary_shifts += 1
                        elif s == 1:
                            total_secondary_shifts += 1
                        elif s == 2:
                            total_daytime_shifts += 1
                        shifts[(p, d, s)] = model.NewBoolVar('shift_p%id%is%i' % (p, d, s))

        total_primary_shifts = total_primary_shifts // self.num_people
        total_secondary_shifts = total_secondary_shifts // self.num_people
        total_daytime_shifts = total_daytime_shifts // self.num_people
        total_shifts = total_primary_shifts + total_secondary_shifts + total_daytime_shifts
        print("Total Primary Shifts: %i" % total_primary_shifts)
        print("Total Secondary Shifts: %i" % total_secondary_shifts)
        print("Total Daytime Shifts: %i" % total_daytime_shifts)

        # Each shift has people_per_shift people.
        people_per_shift = 1
        for d in day_range:
            for s in shift_range:
                if bool(self.shift_mat[d, s]):
                    model.Add(sum(shifts[(p, d, s)] for p in peop_range) == people_per_shift)

        # no both primary and secondary shifts at the same day
        for p in peop_range:
            for d in day_range:
                if bool(self.shift_mat[d, 0]) and bool(self.shift_mat[d, 1]):
                    model.Add((shifts[(p, d, 0)]+shifts[(p, d, 1)]) <= 1)

        # Distribute the primary/secondary/daytime shifts evenly
        min_primary_shifts_per_person = total_primary_shifts // self.num_people
        if total_primary_shifts % self.num_people == 0:
            max_primary_shifts_per_person = min_primary_shifts_per_person
        else:
            max_primary_shifts_per_person = min_primary_shifts_per_person + 1
        min_secondary_shifts_per_person = total_secondary_shifts // self.num_people
        if total_secondary_shifts % self.num_people == 0:
            max_secondary_shifts_per_person = min_secondary_shifts_per_person
        else:
            max_secondary_shifts_per_person = min_secondary_shifts_per_person + 1
        min_daytime_shifts_per_person = total_daytime_shifts // self.num_people
        if total_daytime_shifts % self.num_people == 0:
            max_daytime_shifts_per_person = min_daytime_shifts_per_person
        else:
            max_daytime_shifts_per_person = min_daytime_shifts_per_person + 1

        # apply min_shifts_per_person and max_shifts_per_person constrains
        for p in peop_range:
            num_primary_shifts_worked = 0
            num_secondary_shifts_worked = 0
            num_daytime_shifts_worked = 0
            for d in day_range:
                for s in shift_range:
                    valid = bool(self.shift_mat[d, s])
                    if valid:
                        if s == 0:
                            num_primary_shifts_worked += shifts[(p, d, s)]
                        elif s == 1:
                            num_secondary_shifts_worked += shifts[(p, d, s)]
                        elif s == 2:
                            num_daytime_shifts_worked += shifts[(p, d, s)]
            model.Add(min_primary_shifts_per_person <= num_primary_shifts_worked)
            model.Add(num_primary_shifts_worked <= max_primary_shifts_per_person)
            model.Add(min_secondary_shifts_per_person <= num_secondary_shifts_worked)
            model.Add(num_secondary_shifts_worked <= max_secondary_shifts_per_person)
            model.Add(min_daytime_shifts_per_person <= num_daytime_shifts_worked)
            model.Add(num_daytime_shifts_worked <= max_daytime_shifts_per_person)
        
            bool_array = []
            for p in peop_range:
                for d in day_range:
                    for s in shift_range:
                        if bool(self.shift_mat[d, s]):
                            bool_array.append(int(self.pref_mat[p][d][s]) * shifts[(p, d, s)])
            # accomondate request
            
            model.Maximize(sum(bool_array))
            # Creates the solver and solve.
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = 60.0
            print("solving")
            solver.Solve(model)
            print("solved")
        
            print(solver.StatusName())
            req_met = 0
            if (solver.StatusName() != "INFEASIBLE"):
                for d in day_range:
                    print('Day', d)
                    for p in peop_range:
                        for s in shift_range:
                            if bool(self.shift_mat[d, s]):
                                if solver.Value(shifts[(p, d, s)]) == 1:
                                    if self.pref_mat[p][d][s] > 1:
                                        print('Staff', p, 'works shift', s, '(requested).')
                                        req_met += 1
                                    else:
                                        print('Staff', p, 'works shift', s, '(not requested).')
            
                    print()

                # Statistics.
                print()
                print('Statistics:')
                print(f" - total objective value: {solver.ObjectiveValue()}")
                print(f" - Number of shift requests met = {req_met} out of {total_shifts}" )
                print(f" - wall time =  {solver.WallTime()}s")

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
