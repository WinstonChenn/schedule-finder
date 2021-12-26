import abc
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from .utils import is_saturday, is_sunday, keep_trail_parentheses_num, \
    keep_trail_bracket_str, contain_same_day, is_weekend, \
    validate_datestr, is_saturday_sunday, is_friday, get_day_of_week_str

class RawPreferenceProcessorInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, 'get_staff_name') and \
            callable(subclass.get_staff_name) and \
            hasattr(subclass, "get_staff_pref_matrix") and \
            callable(subclass.get_staff_pref_matrix) or \
            NotImplemented
        )
            

    @abc.abstractmethod
    def get_staff_names(self) -> list:
        """
        Return a list of staff names from raw data table.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def shift_to_column_name(self, date_str: str, shift_name) -> str:
        """
        Map a given shift to the corresponding column name in the raw data table.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def parse_preference_string(self, value: str) -> float:
        """
        Parse a preference string to return the preference value
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_staff_pref_matrix(self, staff: str) -> np.ndarray:
        """
        Return the preference matrix for a given staff.
        """
        raise NotImplementedError

class ElmWinter2022PreferenceProcessor(RawPreferenceProcessorInterface):
    def __init__(
        self, file_path: str, shift_mat_df: pd.DataFrame,
        date_format: str = "%m/%d/%y"
    ):
        self.file_path = file_path
        self.staff_pref_df = pd.read_excel(self.file_path)

        self.shift_mat_df = shift_mat_df
        self.date_list = shift_mat_df['date'].tolist()
        self.shifts_names = shift_mat_df.columns.tolist()
        self.shifts_names.remove('date')
        self.date_format = date_format

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
        if is_friday(date_str):
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
        for i, date in enumerate(self.date_list):
            for j, shift in enumerate(self.shifts_names):
                has_shift = self.shift_mat_df.loc[self.shift_mat_df["date"]==date, shift].values[0]
                if has_shift:
                    shift_col_name = self.shift_to_column_name(date, shift)
                    pref_str = self.staff_pref_df.loc[self.staff_pref_df["Name"]==staff, shift_col_name].values[0]
                    pref_value = self.parse_preference_string(pref_str)
                    pref_mat[i, j] = pref_value
        return pref_mat
