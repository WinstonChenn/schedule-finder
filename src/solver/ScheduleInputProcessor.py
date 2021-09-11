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
import datetime
import pandas as pd
import numpy as np


class ScheduleInputProcessor:

    def __init__(self, start_date, end_date, max_shifts, num_staff,
                 shift_requirement_url, staff_requirement_url, holidays,
                 date_format="%m/%d/%y"):
        self.date_format = date_format
        self.start_date = datetime.datetime.strptime(start_date, self.date_format)
        self.end_date = datetime.datetime.strptime(end_date, self.date_format)
        self.days = (self.end_date - self.start_date).days + 1
        self.max_shifts = max_shifts
        self.num_staff = num_staff
        self.shift_requirement_url = shift_requirement_url
        self.staff_requirement_url = staff_requirement_url
        
        self.holidays = holidays
        self.shift_req_df = pd.read_excel(self.shift_requirement_url, converters={'names':str,'ages':str})
        self.staff_req_df = pd.read_excel(self.staff_requirement_url, converters={'names':str,'ages':str})
        self.staff_req_df = self.stringfy_column_dates(self.staff_req_df)
        self.all_date_arr = self.shift_req_df['date'].tolist()
        self.weekend_arr = list(filter(self.is_weekend, self.all_date_arr))

        # data varification
        assert len(self.staff_req_df.columns)-1 == (5+len(self.weekend_arr)+len(self.holidays))
        assert set(self.weekend_arr) < set([
            col if type(col) == str else col.strftime(self.date_format) 
            for col in self.staff_req_df.columns
        ])
        assert start_date == self.shift_req_df.date.iloc[0]
        assert end_date == self.shift_req_df.date.iloc[-1]
        assert self.num_staff == len(self.staff_req_df.people)
        assert self.max_shifts == len(self.shift_req_df.columns) - 1

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
        day_of_week = datetime.datetime.strptime(date_str, self.date_format).weekday()
        if (day_of_week == 4 or day_of_week == 5):
            return True
        return False

    def get_weekday_str(self, date_str):
        assert not self.is_weekend(date_str)
        date = datetime.datetime.strptime(date_str, self.date_format)
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
        pref_mat = np.zeros((self.num_staff, self.days, self.max_shifts))
        for people_idx in range(self.num_staff):
            pref_setting = req_mat[people_idx] # 0-4: weekday; 5-24: weekend; 25-26: holiday
            for date_idx in range(self.days):
                for shift_idx in range(self.max_shifts):
                    if not shift_mat[date_idx, shift_idx]:
                        # set to -2 when no shift exist
                        pref_mat[people_idx, date_idx, shift_idx] = -2
                    else:
                        # set staff preference
                        date_str = dates[date_idx]
                        if date_str in self.holidays or date_str in self.weekend_arr:
                            pref_mat_idx = req_dates.index(date_str)
                        else:
                            pref_mat_idx = req_dates.index(self.get_weekday_str(date_str))
                        assert pref_mat_idx > -1
                        pref_mat[people_idx, date_idx, shift_idx] = pref_setting[pref_mat_idx]
        return pref_mat




