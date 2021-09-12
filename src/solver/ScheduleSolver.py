from ortools.sat.python import cp_model
from SchedulePrinter import SchedulePrinter
import numpy as np
import datetime

class ScheduleSolver():

    def __init__(self, preference_matrix, shift_matrix, max_time=10.0):
        # pref_matrix should have shape (people, days, shifts)
        # shift_matrix should have shape (days, shifts)
        self.pref_mat = preference_matrix
        self.shift_mat = shift_matrix
        self.num_people = self.pref_mat.shape[0]
        self.num_days = self.pref_mat.shape[1]
        self.num_shifts = self.pref_mat.shape[2]
        self.max_time = max_time
        assert self.num_days == self.shift_mat.shape[0]
        assert self.num_shifts == self.shift_mat.shape[1]

    def solve_schedule(self):

        peop_range = range(self.num_people)
        day_range = range(self.num_days)
        shift_range = range(self.num_shifts)
        total_primary_shifts = 0
        total_secondary_shifts = 0

        model = cp_model.CpModel()
        shifts = {}
        total_shifts_arr = [0 for _ in shift_range]
        # create variables
        for p in peop_range:
            for d in day_range:
                for s in shift_range:
                    if self.shift_mat[d][s]:
                        total_shifts_arr[s] += 1
                        if s == 0:
                            total_primary_shifts += 1
                        elif s == 1:
                            total_secondary_shifts += 1
                        shifts[(p, d, s)] = model.NewBoolVar("shift_p{}d{}s{}".format(p, d, s))

        # Each shift has 1 staff.
        for d in day_range:
            for s in shift_range:
                if self.shift_mat[d][s]:
                    model.Add(sum(shifts[(p, d, s)] for p in peop_range) == 1)

        # Each staff only takes at most 1 shift
        for d in day_range:
            for p in peop_range:
                if self.shift_mat[d][s]:
                    model.Add(sum(shifts[(p, d, s)] for s in shift_range) <= 1)
        
        # Evenly distribute all shifts
        print("Shifts distributing statistics:")
        min_max_shifts_arr = [None for _ in shift_range]
        for s in shift_range:
            curr_total_shifts = total_shifts_arr[s] // self.num_people
            print(" - Total Shift {}: {}".format(s+1, curr_total_shifts))
            curr_min_shifts_per_person = curr_total_shifts // self.num_people
            if curr_total_shifts % self.num_people == 0:
                curr_max_shifts_per_person = curr_min_shifts_per_person
            else:
                curr_max_shifts_per_person = curr_min_shifts_per_person + 1
            min_max_shifts_arr[s] = [curr_min_shifts_per_person, curr_max_shifts_per_person]
            print(" - Min Shift {} Per Person: {}".format(s+1, curr_min_shifts_per_person))
            print(" - Max Shift {} Per Person: {}".format(s+1, curr_max_shifts_per_person))
            print()

        # apply min_shifts_per_person and max_shifts_per_person constrains
        for p in peop_range:
            num_primary_shifts_worked = 0
            num_secondary_shifts_worked = 0 
            shifts_worked_arr = [0 for _ in shift_range]
            num_shifts_worked = 0
            for d in day_range:
                for s in shift_range:
                    if self.shift_mat[d][s]:
                        shifts_worked_arr[s] += shifts[(p, d, s)]
            for s in shift_range:
                model.Add(min_max_shifts_arr[s][0] <= shifts_worked_arr[s])
                model.Add(shifts_worked_arr[s] <= min_max_shifts_arr[s][1])
        
            # accomondate request
            bool_array = []
            for p in peop_range:
                for d in day_range:
                    for s in shift_range:
                        if self.shift_mat[d][s]:
                            bool_array.append(int(self.pref_mat[p][d][s]) * shifts[(p, d, s)])
            model.Maximize(sum(bool_array))
            
            # Creates the solver and solve.
        solver = cp_model.CpSolver()
        solver.parameters.linearization_level = 0
        solver.parameters.max_time_in_seconds = self.max_time
        print(f"solving... (max time={self.max_time})")
        solver.Solve(model)
        print(solver.StatusName())
        return solver, shifts

