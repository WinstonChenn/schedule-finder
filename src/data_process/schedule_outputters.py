import json
import numpy as np
import pandas as pd
from datetime import datetime
from ortools.sat.python import cp_model
from .data_interfaces import ScheduleOutputterInterface
from .utils import is_friday_saturday, get_max_consecutive_len, \
                   get_day_of_week_str

class ElmScheduleOutputter(ScheduleOutputterInterface):
    def __init__(self, solver: cp_model.CpSolver, 
                 shift_vars: dict, date_list: list, 
                 staff_list: list, shift_list: list, 
                 date_format: str, pref_mat_dict: dict,
                 staff_unavailable_days_json: str=None) -> None:
        self.solver = solver
        self.shift_vars = shift_vars
        self.date_list = date_list
        self.staff_list = staff_list
        self.shift_list = shift_list
        self.num_people = len(self.staff_list)
        self.num_days = len(self.date_list)
        self.num_shifts = len(self.shift_list)
        self.pref_mat_dict = pref_mat_dict
        self.date_format = date_format
        if staff_unavailable_days_json is not None:
            self.staff_unavailable_days_dict = json.load(open(staff_unavailable_days_json))
        else:
            self.staff_unavailable_days_dict = {}
    
    def get_schedule_stats(self, verbose=True) -> pd.DataFrame:
        solution_mat = self.get_schedule_matrix()

        staff_count_arr = [{
            "want_count": 0, "ok_count": 0, 
            "no_pref_count": 0, "cant_count": 0, 
        } for _ in range(self.num_people)]
        staff_shift_arr = [
            [{"Weekend": 0, "Weekday": 0} for _ in range(self.num_shifts)]
        for _ in range(self.num_people)]
        total_shift_arr = [0 for _ in range(len(self.staff_list))]
        for p in range(solution_mat.shape[0]):
            staff = self.staff_list[p]
            for d in range(solution_mat.shape[1]):
                for s in range(solution_mat.shape[2]):
                    if solution_mat[p, d, s] == 1:
                        total_shift_arr[p] += 1
                        if is_friday_saturday(self.date_list[d], self.date_format):
                            shift_type = "Weekend"  
                        else:
                            shift_type = "Weekday"
                        staff_shift_arr[p][s][shift_type] += 1
                        if self.pref_mat_dict[staff][d][s] > 1:
                            staff_count_arr[p]["want_count"] += 1
                        elif self.pref_mat_dict[staff][d][s] == 1:
                            staff_count_arr[p]["ok_count"] += 1
                        elif self.pref_mat_dict[staff][d][s] == 0:
                            staff_count_arr[p]["no_pref_count"] += 1
                        elif self.pref_mat_dict[staff][d][s] < 0:
                            print(self.date_list[d], self.shift_list[s], self.staff_list[p], self.pref_mat_dict[staff][d][s])
                            staff_count_arr[p]["cant_count"] += 1

        shift_stat_dict = {"RA": []}
        for day_of_week in ["Weekday", "Weekend"]:
            for shift_type in self.shift_list:
                shift_stat_dict[f"{day_of_week} - {shift_type}"] = []
        shift_stat_dict["Total Shifts"] = []
        shift_stat_dict["Max Consecutive Shifts"] = []
        for key in staff_count_arr[0]:
            shift_stat_dict[key] = []
        shift_stat_dict
        if verbose:
            print("Staff shift taking statistics: ")
        for p, staff in enumerate(self.staff_list):
            if verbose:
                print(f"{staff}: ")
                print(f"\t#Total Shifts={total_shift_arr[p]}")
            shift_stat_dict["RA"].append(staff)
            shift_stat_dict["Total Shifts"].append(total_shift_arr[p])

            # Shift type statistics
            for s in range(len(self.shift_list)):
                for key in staff_shift_arr[p][s]:
                    if verbose:
                        print(f"\t#{key} {self.shift_list[s]}={staff_shift_arr[p][s][key]}")
                    shift_stat_dict[f"{key} - {self.shift_list[s]}"].append(staff_shift_arr[p][s][key])
            # Staff preference statistics
            for key in staff_count_arr[p]:
                if verbose:
                    print(f"\t#{key}={staff_count_arr[p][key]}")
                shift_stat_dict[key].append(staff_count_arr[p][key])

            # Get max consecutive shifts
            curr_solu_mat = solution_mat[p, :, :]
            reduced_curr_solu_mat = curr_solu_mat[:, 0]
            for i in range(1, curr_solu_mat.shape[1]):
                reduced_curr_solu_mat += curr_solu_mat[:, i]
            reduced_curr_solu_mat = np.minimum(reduced_curr_solu_mat, 1.0)
            max_consecutive = get_max_consecutive_len(reduced_curr_solu_mat)
            shift_stat_dict["Max Consecutive Shifts"].append(max_consecutive)
            if verbose:
                print()
        return pd.DataFrame.from_dict(shift_stat_dict)

    def _verify_schedule_matrix(self, solution_mat) -> None:
        assert solution_mat.shape[0] == self.num_people
        assert solution_mat.shape[1] == self.num_days
        assert solution_mat.shape[2] == self.num_shifts
    
    def get_schedule_matrix(self) -> np.ndarray:
        solu_mat = np.zeros((self.num_people, self.num_days, self.num_shifts))
        for p in range(self.num_people):
            for d in range(self.num_days):
                for s in range(self.num_shifts):
                    try:
                        solu_mat[p, d, s] = self.solver.Value(self.shift_vars[p, d, s])
                    except:
                        solu_mat[p, d, s] = 0
        self._verify_schedule_matrix(solu_mat)
        return solu_mat

    def get_schedule_df(self) -> pd.DataFrame:
        shift_dict = {
            "Title": [], "Shift": [], "Full Name": [], 
            "Building & Role": [], "Staff Type": [], 
            "On-Call Date": [], "Day of Week": [], 
            "Type": []
        }
        day_of_week_arr = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        solution_mat = self.get_schedule_matrix()
        for date_idx, date in enumerate(self.date_list):
            for shift_idx, shift in enumerate(self.shift_list):
                shift_mat = solution_mat[:, date_idx, shift_idx]
                if sum(shift_mat) > 0:
                    assert sum(shift_mat) == 1, \
                        f"More or less than 1 shift is scheduled for {date} {shift}"
                    shift_dict["Title"].append("On-Call Assignment")
                    shift_dict["Shift"].append(shift)
                    shift_dict["Full Name"].append(self.staff_list[np.argmax(shift_mat)])
                    if shift == "Daytime":
                        shift_dict["Building & Role"].append(f"West Region - Elm")
                    else:    
                        shift_dict["Building & Role"].append(f"Elm {shift}")
                    shift_dict["Staff Type"].append("Resident Adviser")
                    shift_dict["On-Call Date"].append(date)
                    week_of_day_idx = datetime.strptime(date, self.date_format).weekday()
                    shift_type = "Weekend" if week_of_day_idx==4 or week_of_day_idx==5 else "Weekday"
                    shift_dict["Day of Week"].append(day_of_week_arr[week_of_day_idx])
                    shift_dict["Type"].append(shift_type)
        shift_df = pd.DataFrame.from_dict(shift_dict)
        return shift_df

    def _verify_primary_secondary(self, solution_mat):
        """
        Verify that for the same day, primary shift and secondary shifts 
        are not the same staff
        """
        for d in range(self.num_days):
            curr_mat = solution_mat[:, d, :]
            assert np.argmax(curr_mat[:, 0]) != np.argmax(curr_mat[:, 1]), \
                f"Primary and secondary shifts in the same day ({self.date_list[d]}) "\
                f"are scheduled to the same staff"

    def _verify_one_staff_per_shift(self, solution_mat):
        """
        Verify that for each shift, there is only one staff assigned to it
        """
        for d in range(self.num_days):
            for s in range(self.num_shifts):
                curr_mat = solution_mat[:, d, s]
                assert sum(curr_mat) <= 1, \
                    f"More than 1 staff is scheduled for " \
                    f"{self.date_list[d]} {self.shift_list[s]}"

    def _verify_unavaialble_dates(self, solution_mat):
        for staff in self.staff_unavailable_days_dict:
            staff_idx = self.staff_list.index(staff)
            for d, date in enumerate(self.date_list):
                day_of_week = get_day_of_week_str(date, self.date_format)
                if day_of_week in self.staff_unavailable_days_dict[staff] or \
                   date in self.staff_unavailable_days_dict[staff]:
                    try:
                        unavailable_shift = self.staff_unavailable_days_dict[staff][day_of_week]
                    except:
                        unavailable_shift = self.staff_unavailable_days_dict[staff][date]
                    if unavailable_shift == "ALL":
                        unavailable_shift = self.shift_list
                    assert isinstance(unavailable_shift, list), \
                        f"Unavailable shift for {staff} on {date}/{day_of_week} is not a list"
                    for s in range(self.num_shifts):
                        if self.shift_list[s] in unavailable_shift:
                            assert solution_mat[staff_idx, d, s] == 0, \
                                f"Staff {staff} is scheduled for {self.date_list[d]} " \
                                f"{self.shift_list[s]}"


    def verify_schedule(self) -> bool:
        solution_mat = self.get_schedule_matrix()
        self._verify_primary_secondary(solution_mat)
        self._verify_one_staff_per_shift(solution_mat)
        self._verify_unavaialble_dates(solution_mat)
        self._verify_unavaialble_dates(solution_mat)
        return True



