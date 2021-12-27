import os
import numpy as np
import pandas as pd
from ortools.sat.python import cp_model
os.sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data_process.utils import is_friday_saturday

class ScheduleModeler():
    def __init__(self, shift_mat_df: pd.DataFrame, staff_list: list, 
                 date_format: str, pref_mat_dict: dict=None, 
                 max_consecutive_dict: dict=None):
        self.shift_mat_df = shift_mat_df
        self.shift_mat = shift_mat_df.loc[:, shift_mat_df.columns!="date"].to_numpy()
        self.pref_mat_dict = pref_mat_dict
        self.max_consecutive_dict = max_consecutive_dict
        self.date_list = self.shift_mat_df['date'].tolist()
        self.shift_list = self.shift_mat_df.columns.tolist()
        self.shift_list.remove('date')
        self.staff_list = staff_list
        self.date_format = date_format
        self.num_people = len(self.staff_list)
        self.num_days = len(self.date_list)
        self.num_shifts = len(self.shift_list)

    def get_model(self):
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
                    shifts[(p, d, s)] = model.NewBoolVar("shift_p{}d{}s{}".format(p, d, s))
                    if p == 0 and self.shift_mat[d][s]:
                        total_shifts += 1
                        if is_friday_saturday(self.date_list[d]):
                            total_shifts_arr[s]["Weekend"] += 1
                        else:
                            total_shifts_arr[s]["Weekday"] += 1

        # Each existing shift has 1 staff.
        # Each non-existing shift has 0 staff.
        for d in day_range:
            for s in shift_range:
                if self.shift_mat[d][s] == 0:
                    model.Add(sum(shifts[(p, d, s)] for p in peop_range) == 0)
                else:
                    model.Add(sum(shifts[(p, d, s)] for p in peop_range) == 1)

        # Each staff can't take primary or secondary on the same day.
        for p in peop_range:
            for d in day_range:
                model.Add(sum(shifts[(p, d, s)] for s in shift_range) <= 1)
                # model.Add(sum([shifts[(p, d, 0)],shifts[(p, d, 1)]])  <= 1)
                # model.Add(sum([shifts[(p, d, 0)],shifts[(p, d, 2)]]) <= 2)
                # model.Add(sum([shifts[(p, d, 1)],shifts[(p, d, 2)]]) <= 2)
                # model.AddBoolXOr([shifts[(p, d, 0)], shifts[(p, d, 1)]])
        
        # Evenly distribute all shifts
        print("Shifts distributing statistics:")
        min_max_shifts_arr = [{key: [] for key in total_shifts_arr[0]} for _ in shift_range]
        for s in shift_range:
            for key in total_shifts_arr[s]:
                curr_total_shifts = total_shifts_arr[s][key]
                print(" - Total {} {} Shift: {}".format(key, self.shift_list[s], curr_total_shifts))
                curr_min_shifts_per_person = curr_total_shifts // self.num_people
                if curr_total_shifts % self.num_people == 0:
                    curr_max_shifts_per_person = curr_min_shifts_per_person
                else:
                    curr_max_shifts_per_person = curr_min_shifts_per_person + 1
                min_max_shifts_arr[s][key] = [curr_min_shifts_per_person, curr_max_shifts_per_person]
                print(" - Min {} {} shift Per Person: {}"
                    .format(key, self.shift_list[s], curr_min_shifts_per_person))
                print(" - Max {} {} shift Per Person: {}"
                    .format(key, self.shift_list[s], curr_max_shifts_per_person))
                print()
        print(" - Total Shifts: {}".format(total_shifts))
        min_total_shifts = total_shifts // self.num_people
        if total_shifts % self.num_people == 0:
            max_total_shifts = min_total_shifts
        else:
            max_total_shifts = min_total_shifts + 1
        print(" - Min Shift Per Person: {}".format(min_total_shifts))
        print(" - Max Shift Per Person: {}".format(max_total_shifts))
        print()

        # applying min-max shift number constraints
        for p in peop_range:
            shifts_worked_arr = [{key: 0 for key in min_max_shifts_arr[0]} for _ in shift_range]
            total_shifts_worked = 0
            for d in day_range:
                for s in shift_range:
                    if self.shift_mat[d][s]:
                        total_shifts_worked += shifts[(p, d, s)]
                        if is_friday_saturday(self.date_list[d]):
                            shifts_worked_arr[s]["Weekend"] += shifts[(p, d, s)]
                        else:
                            shifts_worked_arr[s]["Weekday"] += shifts[(p, d, s)]
            # apply min-max constraints for different types of shifts
            for s in shift_range:
                for key in min_max_shifts_arr[s]:
                    min_shifts_per_person = min_max_shifts_arr[s][key][0]
                    max_shifts_per_person = min_max_shifts_arr[s][key][1]
                    model.Add(shifts_worked_arr[s][key] >= min_shifts_per_person)
                    model.Add(shifts_worked_arr[s][key] <= max_shifts_per_person)
            # apply min-max constraints total shift number
            model.Add(min_total_shifts <= total_shifts_worked)
            model.Add(total_shifts_worked <= max_total_shifts)
        
        # accomondate request
        if self.pref_mat_dict is not None:
            bool_array = []
            for p in peop_range:
                curr_pref_mat = self.pref_mat_dict[self.staff_list[p]]
                for d in day_range:
                    for s in shift_range:
                        if curr_pref_mat[d][s] < 0:
                            bool_array.append(int(curr_pref_mat[d][s]) * shifts[(p, d, s)]*5)
                        else:
                            bool_array.append(int(curr_pref_mat[d][s]) * shifts[(p, d, s)])
            model.Maximize(sum(bool_array))

        if self.max_consecutive_dict is not None:
            for p in peop_range:
                staff = self.staff_list[p]
                max_cons_shifts = self.max_consecutive_dict[staff]
                for d in range(self.num_days - max_cons_shifts):
                    shift_arr = []
                    for i in range(max_cons_shifts+1):
                        for s in shift_range:
                            curr_shift = shifts[(p, d + i, s)]
                            shift_arr.append(curr_shift)
                    model.Add(sum(shift_arr) <= max_cons_shifts)

        return model, shifts

