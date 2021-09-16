from ortools.sat.python import cp_model
from SchedulePrinter import SchedulePrinter
import numpy as np
from datetime import datetime

class ScheduleSolver():

    def __init__(self, preference_matrix, shift_matrix, 
                 date_arr, date_format, max_time=10.0):
        # pref_matrix should have shape (people, days, shifts)
        # shift_matrix should have shape (days, shifts)
        self.pref_mat = preference_matrix
        self.shift_mat = shift_matrix
        self.date_arr = date_arr
        self.date_format = date_format
        self.num_people = self.pref_mat.shape[0]
        self.num_days = self.pref_mat.shape[1]
        self.num_shifts = self.pref_mat.shape[2]
        self.max_time = max_time
        assert self.num_days == self.shift_mat.shape[0]
        assert self.num_shifts == self.shift_mat.shape[1]
        assert self.num_days == len(self.date_arr)

    def solve_schedule(self):
        peop_range = range(self.num_people)
        day_range = range(self.num_days)
        shift_range = range(self.num_shifts)
        total_shifts = 0
        model = cp_model.CpModel()
        shifts = {}
        total_shifts_arr = [{"Weekend": 0, "Weekday": 0} for _ in shift_range]
        # create variables
        for p in peop_range:
            for d in day_range:
                for s in shift_range:
                    total_shifts += 1
                    if self.shift_mat[d][s]:
                        if self.is_weekend(self.date_arr[d]):
                            total_shifts_arr[s]["Weekend"] += 1
                        else:
                            total_shifts_arr[s]["Weekday"] += 1
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
        min_max_shifts_arr = [{key: [] for key in total_shifts_arr[0]} for _ in shift_range]
        for s in shift_range:
            for key in total_shifts_arr[s]:
                curr_total_shifts = total_shifts_arr[s][key] // self.num_people
                print(" - Total {} Shift {}: {}".format(key, s+1, curr_total_shifts))
                curr_min_shifts_per_person = curr_total_shifts // self.num_people
                if curr_total_shifts % self.num_people == 0:
                    curr_max_shifts_per_person = curr_min_shifts_per_person
                else:
                    curr_max_shifts_per_person = curr_min_shifts_per_person + 1
                min_max_shifts_arr[s][key] = [curr_min_shifts_per_person, curr_max_shifts_per_person]
                print(" - Min {} Shift {} Per Person: {}"
                    .format(key, s+1, curr_min_shifts_per_person))
                print(" - Max {} Shift {} Per Person: {}"
                    .format(key, s+1, curr_max_shifts_per_person))
                print()
        total_shifts = total_shifts // self.num_people
        print(" - Total Shifts: {}".format(total_shifts))
        min_total_shifts = total_shifts // self.num_people
        if total_shifts % self.num_people == 0:
            max_total_shifts = min_total_shifts
        else:
            max_total_shifts = min_total_shifts + 1
        print(" - Min Shift Per Person: {}".format(min_total_shifts))
        print(" - Max Shift Per Person: {}".format(max_total_shifts))
        print()

        # apply min_shifts_per_person and max_shifts_per_person constrains
        for p in peop_range:
            shifts_worked_arr = [{key: 0 for key in min_max_shifts_arr[0]}for _ in shift_range]
            total_shifts_worked = 0
            for d in day_range:
                for s in shift_range:
                    if self.shift_mat[d][s]:
                        total_shifts_worked += shifts[(p, d, s)]
                        if self.is_weekend(self.date_arr[d]):
                            shifts_worked_arr[s]["Weekend"] += shifts[(p, d, s)]
                        else:
                            shifts_worked_arr[s]["Weekday"] += shifts[(p, d, s)]
            for s in shift_range:
                for key in min_max_shifts_arr[s]:
                    min_shifts_per_person = min_max_shifts_arr[s][key][0]
                    max_shifts_per_person = min_max_shifts_arr[s][key][1]
                    model.Add(shifts_worked_arr[s][key] >= min_shifts_per_person)
                    model.Add(shifts_worked_arr[s][key] <= max_shifts_per_person)
            model.Add(min_total_shifts <= total_shifts_worked)
            model.Add(total_shifts_worked <= max_total_shifts)
        
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

    def is_weekend(self, date_str):
        date_idx = datetime.strptime(date_str, self.date_format).weekday()
        return date_idx == 4 or date_idx == 5

