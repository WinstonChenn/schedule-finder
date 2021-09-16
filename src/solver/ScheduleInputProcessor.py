# input requirements
# 1. Starting Date, Ending Date (All inclusive) [CLI]
# 2. max #shifts per day [CLI]
# 3. Number of staffs [CLI]

# 4. each days requirements (#shifts, holiday) 
# [tablar data, col1: date, col2: shift1 (y/n), col3: shift2(y/n), col4: shift3(y/n), col5: shift4(y/n), col6: hoiday (y/n))]

# 5. Each staff requirements (scale: -2 - 2) [tabular data, row: each staff, col [i, ii, iii, ix]]
# -2: not real shift, -1: can't work 0: neutral 1: ok 2: want
#   i: preference on weekdays weekdays (Sunday - Thursday) [5 columnb]
#   ii: preference on weekends (pre-generate a list of weekends based on start/end date) [#weekends columns]
#   iii: prefernce on holidays[#holidays columns]
#   ix. longest shift streak [1 column]


# output
# prefernce matrix
# number of staffs * number of days * max #shifts per day

# constrain: 
# For all real shifts (sometimes more than 1 real shift perday), at least staff put non-negative prefernce
from datetime import datetime
import pandas as pd
import numpy as np
import os, json


class ScheduleInputProcessor:
    def __init__(self, shift_requirement_url, staff_requirement_url, 
                 additional_staff_requirement_url, holidays, exclude_dates,
                 date_format="%m/%d/%y"):
        self.date_format = date_format
        self.shift_requirement_url = shift_requirement_url
        self.staff_requirement_url = staff_requirement_url
        self.holidays = holidays
        self.day_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        assert os.path.isfile(shift_requirement_url)
        assert os.path.isfile(staff_requirement_url)
        self.shift_req_df = pd.read_excel(
            self.shift_requirement_url, converters={'names':str,'ages':str}
        )
        self.staff_req_df = pd.read_excel(
            self.staff_requirement_url, converters={'names':str,'ages':str}
        )
        self.staff_req_df = self.stringfy_column_dates(self.staff_req_df)
        for date in exclude_dates:
            if date in self.staff_req_df.columns:
                self.staff_req_df.drop(columns=date, inplace=True)
        self.all_date_arr = self.shift_req_df['date'].tolist()
        for date in self.staff_req_df.columns:
            if self.validate_date_str(date) and date not in self.all_date_arr:
                print(date)
                self.staff_req_df.drop(columns=date, inplace=True)
        self.weekend_arr = list(filter(self.is_weekend, self.all_date_arr))
        self.exclude_dates = exclude_dates

        # data varification
        assert len(self.staff_req_df.columns)-1 == (5+len(self.weekend_arr)+len(self.holidays))
        assert set(self.weekend_arr) < set([
            col if type(col) == str else col.strftime(self.date_format) 
            for col in self.staff_req_df.columns
        ])
        self.additional_staff_req_arr = [{} for _ in range(len(self.get_staff_arr()))]
        if os.path.isfile(additional_staff_requirement_url):
            self.additional_staff_req_dict = json.load(open(additional_staff_requirement_url))
            staff_names = list(self.additional_staff_req_dict.keys())
            for staff_name in staff_names:
                assert staff_name in self.get_staff_arr()
                staff_idx = self.get_staff_arr().index(staff_name)
                curr_additional_staff_dict = self.additional_staff_req_dict[staff_name]
                for date in curr_additional_staff_dict.keys():
                    assert date in self.day_of_week or \
                        (self.validate_date_str(date) and date in self.all_date_arr)
                    assert all([shift in self.get_shift_arr() 
                                for shift in curr_additional_staff_dict[date]])
                    shift_idx_arr = [self.get_shift_arr().index(shift) 
                                     for shift in curr_additional_staff_dict[date]]
                    if date in self.day_of_week:
                        for idx, date_str in enumerate(self.all_date_arr):
                            weekday_idx = datetime.strptime(date_str, self.date_format).weekday()
                            if self.day_of_week[weekday_idx] == date:
                                self.additional_staff_req_arr[staff_idx][idx]=shift_idx_arr
                    else:
                        idx = self.all_date_arr.index(date)
                        self.additional_staff_req_arr[staff_idx][idx]=shift_idx_arr
    def stringfy_column_dates(self, df):
        col_rename_dic = {}
        for col_name in df.columns:
            if (type(col_name) == str):
                col_rename_dic[col_name] = col_name
            else:
                col_rename_dic[col_name] = col_name.strftime(self.date_format)
        df = df.rename(columns=col_rename_dic)
        return df

    def is_weekend(self, date_str):
        day_of_week = datetime.strptime(date_str, self.date_format).weekday()
        if (day_of_week == 4 or day_of_week == 5):
            return True
        return False

    def get_weekday_str(self, date_str):
        assert not self.is_weekend(date_str)
        date = datetime.strptime(date_str, self.date_format)
        day_of_week = date.weekday()
        weekday_dict = {
            0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 6: "Sunday"
        }
        return weekday_dict[day_of_week]

    # provide file directory of csv to convert to pd dataframe
    # should fit specs provided by InputProcessor.py
    def load_day_requirements(self):
        df = self.shift_req_df
        row_entries = df['date'].tolist()
        col_entries = df.loc[:, df.columns != "date"].columns.tolist()
        matrix = df.loc[:, df.columns != "date"].to_numpy()
        return row_entries, col_entries, matrix

    # provide file directory of csv to convert to pd dataframe
    # should fit specs provided by InputProcessor.py
    def load_staff_requirements(self):
        df = self.staff_req_df
        row_entries = df['people'].tolist()
        col_entries = df.loc[:, df.columns != 'people'].columns.tolist()
        matrix = df.loc[:, df.columns != 'people'].to_numpy()
        return row_entries, col_entries, matrix

    def get_preference_matrix(self):
        dates, shifts, shift_mat = self.load_day_requirements()
        people, req_dates, req_mat = self.load_staff_requirements()
        pref_mat = np.zeros((self.get_num_staffs(), self.get_num_days(), self.get_max_shifts()))
        for people_idx in range(self.get_num_staffs()):
            pref_setting = req_mat[people_idx]
            additional_pref_setting = self.additional_staff_req_arr[people_idx]
            for date_idx in range(self.get_num_days()):
                for shift_idx in range(self.get_max_shifts()):
                    if (not shift_mat[date_idx, shift_idx]) or \
                        (date_idx in additional_pref_setting.keys() and 
                            shift_idx in additional_pref_setting[date_idx]):
                        # set to -2 when no shift exist
                        pref_mat[people_idx, date_idx, shift_idx] = -2
                    else:
                        # set staff preference
                        date_str = dates[date_idx]
                        if date_str in self.holidays or date_str in self.weekend_arr:
                            try:
                                pref_mat_idx = req_dates.index(date_str)
                            except:
                                breakpoint()
                        else:
                            pref_mat_idx = req_dates.index(self.get_weekday_str(date_str))
                        assert pref_mat_idx > -1
                        pref_mat[people_idx, date_idx, shift_idx] = pref_setting[pref_mat_idx]
        return pref_mat

    def get_start_date(self):
        try:
            return self.start_date
        except AttributeError:
            self.start_date = self.shift_req_df.date.iloc[0]
            return self.start_date

    def get_end_date(self):
        try:
            return self.end_date
        except AttributeError:
            self.end_date = self.shift_req_df.date.iloc[-1]
            return self.end_date

    def get_num_days(self):
        try:
            return self.num_days
        except AttributeError:
            self.num_days = len(self.all_date_arr)
            start_date = datetime.strptime(self.get_start_date(), self.date_format)
            end_date = datetime.strptime(self.get_end_date(), self.date_format)
            assert self.num_days == (end_date-start_date).days + 1 - len(self.exclude_dates)
            return self.num_days

    def get_max_shifts(self):
        try:
            return self.max_shifts
        except AttributeError:
            self.max_shifts = len(self.shift_req_df.columns) - 1
            return self.max_shifts

    def get_num_staffs(self):
        try:
            return self.num_staff
        except AttributeError:
            self.num_staff = len(self.staff_req_df.people)
            return self.num_staff

    def get_staff_arr(self):
        return self.staff_req_df['people'].tolist()
    
    def get_date_arr(self):
        return self.all_date_arr

    def get_shift_arr(self):
        return self.shift_req_df.loc[:, self.shift_req_df.columns != "date"] \
            .columns.tolist()

    def get_additional_staff_requirement(self):
        try:
            return self.additional_staff_req_dict
        except AttributeError:
            return {}

    def validate_date_str(self, date_text):
        try:
            datetime.strptime(date_text, self.date_format)
            return True
        except ValueError:
            # raise ValueError(f"Incorrect data format, should be {self.date_format}")
            return False