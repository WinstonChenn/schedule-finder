import abc
import numpy as np
import pandas as pd

class PreferenceInputterInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, 'get_staff_name') and \
            callable(subclass.get_staff_name) and \
            hasattr(subclass, "get_staff_pref_matrix") and \
            callable(subclass.get_staff_pref_matrix) and \
            hasattr(subclass, "get_staff_max_consecutive_shifts") and \
            callable(subclass.get_staff_max_consecutive_shifts) or \
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

    @abc.abstractmethod
    def get_staff_max_consecutive_shifts(self, staff: str) -> int:
        """
        Return the maximum number of consecutive shifts for the given staff.
        """
        raise NotImplementedError


class ScheduleOutputterInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, 'get_schedule_stats') and \
            callable(subclass.get_schedule_df) and \
            hasattr(subclass, "get_schedule_df") and \
            callable(subclass.get_schedule_df) and \
            hasattr(subclass, "verify_schedule") and \
            callable(subclass.verify_schedule) or \
            NotImplemented
        )

    @abc.abstractmethod
    def verify_schedule(self) -> bool:
        """
        Verify the schedule is valid.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_schedule_stats(self) -> pd.DataFrame:
        """
        Print the per staff stats of the generated schedule
        and return it as a DataFrame.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_schedule_matrix(self) -> np.ndarray:
        """
        Return the schedule matrix in numpy ndarray.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_schedule_df(self) -> pd.DataFrame:
        """
        Return the schedule organized in DataFrame.
        """
        raise NotImplementedError

