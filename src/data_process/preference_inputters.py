import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from .data_interfaces import PreferenceInputterInterface
from .utils import is_saturday, is_sunday, keep_trail_parentheses_num, \
    keep_trail_bracket_str, contain_same_day, is_weekend, \
    validate_datestr, is_saturday_sunday, is_friday, get_day_of_week_str

class ElmWinter2022PreferenceInputer(PreferenceInputterInterface):
    def __init__(
        self, file_path: str, shift_mat_df: pd.DataFrame,
        holidays: list, date_format: str = "%m/%d/%y", 
        staff_unavailable_json: str = None
    ):
        self.file_path = file_path
        self.staff_pref_df = pd.read_excel(self.file_path)

        self.shift_mat_df = shift_mat_df
        self.date_list = shift_mat_df['date'].tolist()
        self.holidays = holidays
        self.shifts_names = shift_mat_df.columns.tolist()
        self.shifts_names.remove('date')
        self.date_format = date_format
        self.dat_of_week = [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
        ]
        
        staff_unavailable_dict = json.load(open(staff_unavailable_json))
        # unavailable days varification
        for staff in staff_unavailable_dict.keys():
            assert staff in self.get_staff_names(), \
                "Staff unavailable dict keys are not in the staff list"
            for key in staff_unavailable_dict[staff]:
                    is_day_of_week =  key in self.dat_of_week
                    is_date = validate_datestr(key, self.date_format)
                    assert is_day_of_week or is_date, \
                        f"{staff}'s unavailable dict keys ({key}) is" \
                        f"not valid date string or valid day of week"
                    if staff_unavailable_dict[staff][key] == "ALL":
                        staff_unavailable_dict[staff][key] = self.shifts_names
                    assert isinstance(staff_unavailable_dict[staff][key], list), \
                        f"{staff}'s unavailable dict values ({staff_unavailable_dict[staff][key]}) " \
                        f"isn't a list"
        self.staff_unavailable_dict = staff_unavailable_dict
                        

    def get_staff_names(self) -> list:
        return self.staff_pref_df["Name"].tolist()

    def shift_to_column_name(self, date_str: str, shift_name) -> str:
        assert validate_datestr(date_str), "Invalid date string"
        assert contain_same_day(date_str, self.date_list, self.date_format), \
            "Date string does not in the date list provided"
        assert shift_name in self.shifts_names, "Invalid shift name"
        if shift_name == "Daytime":
            assert  is_saturday_sunday(date_str, self.date_format), \
                "Daytime shift is only available on Saturday and Sunday"
        if contain_same_day(date_str, self.holidays, self.date_format):
            if date_str == "01/17/22":
                column_name = "Holiday on-call preferences [1/17 Martin Luther King Jr. Day]"
            elif date_str == "02/21/22":
                column_name = "Holiday on-call preferences [2/21 Presidents' Day]"
            else:
                raise ValueError("Invalid holiday date")
        elif is_friday(date_str):
            curr_date = datetime.strptime(date_str, self.date_format)
            curr_date_str = datetime.strftime(curr_date, "%-m/%-d")
            next_date = curr_date + timedelta(days=1)
            next_date_str = datetime.strftime(next_date, "%-m/%-d")
            column_name = f"Weekend night-time on-call preferences (Friday & Saturday) " \
                           f"[{curr_date_str} - {next_date_str}]"
        elif is_saturday(date_str):
            curr_date = datetime.strptime(date_str, self.date_format)
            curr_date_str = datetime.strftime(curr_date, "%-m/%-d")
            next_date = curr_date + timedelta(days=1)
            next_date_str = datetime.strftime(next_date, "%-m/%-d")
            prev_date = curr_date - timedelta(days=1)
            prev_date_str = datetime.strftime(prev_date, "%-m/%-d")
            if shift_name == "Daytime":
                column_name = f"Weekend day-time on-call preferences (Saturday & Sunday) " \
                              f"[{curr_date_str} - {next_date_str}]"
            else:
                column_name = f"Weekend night-time on-call preferences (Friday & Saturday) " \
                              f"[{prev_date_str} - {curr_date_str}]"

        elif is_sunday(date_str):
            curr_date = datetime.strptime(date_str, self.date_format)
            curr_date_str = datetime.strftime(curr_date, "%-m/%-d")
            prev_date = curr_date - timedelta(days=1)
            prev_date_str = datetime.strftime(prev_date, "%-m/%-d")
            if shift_name == "Daytime":
                column_name = f"Weekend day-time on-call preferences (Saturday & Sunday) " \
                              f"[{prev_date_str} - {curr_date_str}]"
            else:
                column_name = f"Weekday on-call preferences [Sunday]"

        else:
            day_of_week = get_day_of_week_str(date_str, self.date_format)
            column_name = f"Weekday on-call preferences [{day_of_week}]"

        return column_name

    def parse_preference_string(self, pref_str: str) -> float:
        """
        Parse a preference string to return the preference value
        """
        return keep_trail_parentheses_num(pref_str)


    def get_staff_pref_matrix(self, staff: str) -> np.ndarray:
        pref_mat = np.zeros((self.shift_mat_df.shape[0], self.shift_mat_df.shape[1]-1))
        assert pref_mat.shape == (len(self.date_list), len(self.shifts_names)), \
            "Preference matrix shape does not match"
        unavailable_dict = self.staff_unavailable_dict.get(staff, {})
        for i, date in enumerate(self.date_list):
            day_of_week = get_day_of_week_str(date, self.date_format)
            is_unavailble_day = day_of_week in unavailable_dict.keys() or \
                                date in unavailable_dict.keys()
            for j, shift in enumerate(self.shifts_names):
                has_shift = self.shift_mat_df.loc[self.shift_mat_df["date"]==date, shift].values[0]
                if has_shift:
                    pref_value = None
                    if is_unavailble_day:
                        try:
                            unavailable_shift = unavailable_dict[day_of_week]
                        except KeyError:
                            unavailable_shift = unavailable_dict[date]
                        if shift in unavailable_shift:
                            pref_value = -2
                    if pref_value is None:
                        shift_col_name = self.shift_to_column_name(date, shift)
                        pref_str = self.staff_pref_df.loc[self.staff_pref_df["Name"]==staff, shift_col_name].values[0]
                        try:
                            pref_value = self.parse_preference_string(pref_str)
                        except:
                            pref_value = 0
                    pref_mat[i, j] = pref_value
                else:
                    pref_mat[i, j] = -2
        return pref_mat

    def get_staff_max_consecutive_shifts(self, staff: str) -> int:
        return self.staff_pref_df.loc[
            self.staff_pref_df["Name"]==staff, 
            "Maximum acceptable number of back-to-back on-call "
        ].values[0]
