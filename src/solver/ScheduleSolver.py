from ortools.sat.python import cp_model
from SchedulePrinter import SchedulePrinter
import numpy as np
import datetime

class ScheduleSolver():

    def __init__(self, preference_matrix, shift_matrix, num_people, 
                 num_shifts, num_days, max_time=10.0):
        self.pref_mat = preference_matrix
        self.shift_mat = shift_matrix
        self.num_people = num_people
        self.num_shifts = num_shifts
        self.num_days = num_days
        self.max_time = max_time
        self.shift_type = ['primary', "secondary"]

    def solve_schedule(self):
        # pref_matrix should go [people][days][shifts]
        assert self.pref_mat.shape == (self.num_people, self.num_days, self.num_shifts) and \
                self.shift_mat.shape == (self.num_days, self.num_shifts), \
                "ERROR: Preference Matrix is incorrectly shaped."

        peop_range = range(self.num_people)
        day_range = range(self.num_days)
        shift_range = range(self.num_shifts)
        total_primary_shifts = 0
        total_secondary_shifts = 0

        model = cp_model.CpModel()
        shifts = {}
        # create variables
        for p in peop_range:
            for d in day_range:
                for s in shift_range:
                    if s == 0:
                        total_primary_shifts += 1
                    elif s == 1:
                        total_secondary_shifts += 1
                    shifts[(p, d, s)] = model.NewBoolVar("shift_p{}d{}s{}".format(p, d, s))

        total_primary_shifts = total_primary_shifts // self.num_people
        total_secondary_shifts = total_secondary_shifts // self.num_people
        total_shifts = total_primary_shifts + total_secondary_shifts
        print("Total Primary Shifts: %i" % total_primary_shifts)
        print("Total Secondary Shifts: %i" % total_secondary_shifts)

        # Each shift has people_per_shift people.
        people_per_shift = 1
        for d in day_range:
            for s in shift_range:
                model.Add(sum(shifts[(p, d, s)] for p in peop_range) == people_per_shift)

        # no both primary and secondary shifts at the same day
        for d in day_range:
            for p in peop_range:
                model.Add(sum(shifts[(p, d, s)] for s in shift_range) <= 1)

        # Distribute the primary/secondary/daytime shifts evenly
        min_primary_shifts_per_person = total_primary_shifts // self.num_people
        if total_primary_shifts % self.num_people == 0:
            max_primary_shifts_per_person = min_primary_shifts_per_person
        else:
            max_primary_shifts_per_person = min_primary_shifts_per_person + 1
        print("Min Primary Shifts Per Person: %i" % min_primary_shifts_per_person)
        print("Max Primary Shifts Per Person: %i" % max_primary_shifts_per_person)
        min_secondary_shifts_per_person = total_secondary_shifts // self.num_people
        if total_secondary_shifts % self.num_people == 0:
            max_secondary_shifts_per_person = min_secondary_shifts_per_person
        else:
            max_secondary_shifts_per_person = min_secondary_shifts_per_person + 1
        print("Min Secondary Shifts Per Person: %i" % min_secondary_shifts_per_person)
        print("Max Secondary Shifts Per Person: %i" % max_secondary_shifts_per_person)

        # apply min_shifts_per_person and max_shifts_per_person constrains
        for p in peop_range:
            num_primary_shifts_worked = 0
            num_secondary_shifts_worked = 0 
            num_shifts_worked = 0
            for d in day_range:
                for s in shift_range:
                    num_shifts_worked += shifts[(p, d, s)]
                    if s == 0:
                        num_primary_shifts_worked += shifts[(p, d, s)]
                    elif s == 1:
                        num_secondary_shifts_worked += shifts[(p, d, s)]
            model.Add(min_primary_shifts_per_person <= num_primary_shifts_worked)
            model.Add(num_primary_shifts_worked <= max_primary_shifts_per_person)
            model.Add(min_secondary_shifts_per_person <= num_secondary_shifts_worked)
            model.Add(num_secondary_shifts_worked <= max_secondary_shifts_per_person)
        
            # accomondate request
            bool_array = []
            for p in peop_range:
                for d in day_range:
                    for s in shift_range:
                        bool_array.append(int(self.pref_mat[p][d][s]) * shifts[(p, d, s)])
            model.Maximize(sum(bool_array))
            
            # Creates the solver and solve.
        solver = cp_model.CpSolver()
        solver.parameters.linearization_level = 0
        solver.parameters.max_time_in_seconds = self.max_time
        print()
        print("solving...")
        print("max solving time:", self.max_time)
        solver.Solve(model)
        print(solver.StatusName())
        req_met = 0
        und_req_met = 0
        staff_dict = {i: {"primary": 0, "secondary": 0} for i in range(self.num_people)}
        if (solver.StatusName() != "INFEASIBLE"):
            for d in day_range:
                print('Day', d)
                for p in peop_range:
                    for s in shift_range:
                        if solver.Value(shifts[(p, d, s)]):
                            staff_dict[p][self.shift_type[s]] += 1
                            if self.pref_mat[p][d][s] > 1:
                                print('Staff', p, 'works shift', s, '(requested).')
                                req_met += 1
                            elif self.pref_mat[p][d][s] < 0:
                                print('Staff', p, 'works shift', s, '(undesired requested).')
                                und_req_met += 1
                            else:
                                print('Staff', p, 'works shift', s, '(not requested).')
                print()

            print(staff_dict)
            # Statistics.
            print()
            print('Statistics:')
            print(f" - total objective value: {solver.ObjectiveValue()}")
            print(f" - Number of shift requests met = {req_met}")
            print(f" - Number of undesired schedulig = {und_req_met}")
            print(f" - Total number of shifts = {total_shifts}")
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
