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
import pandas
import numpy as np


class ScheduleInputProcessor:

    def __init__(self, start_date, end_date, max_shifts, num_staff,
                 date_requirement_url, staff_requirement_url, holidays):
        self.start_date = datetime.datetime.strptime(start_date, "%m/%d/%y")
        self.end_date = datetime.datetime.strptime(end_date, "%m/%d/%y")
        self.days = (self.end_date - self.start_date).days + 1
        self.max_shifts = max_shifts
        self.num_staff = num_staff
        self.date_requirement_url = date_requirement_url
        self.staff_requirement_url = staff_requirement_url
        self.holidays = holidays

    # provide file directory of csv to convert to pandas dataframe
    # should fit specs provided by InputProcessor.py
    def load_day_requirements(self):
        df = pandas.read_excel(self.date_requirement_url)
        df['date'] = df.date.dt.strftime("%m/%d/%y")
        row_entries = df['date'].tolist()
        col_entries = df.loc[:, df.columns != "date"].columns.tolist()
        matrix = df.loc[:, df.columns != "date"].to_numpy()
        return row_entries, col_entries, matrix

    # provide file directory of csv to convert to pandas dataframe
    # should fit specs provided by InputProcessor.py
    def load_staff_requirements(self):
        df = pandas.read_excel(self.staff_requirement_url)

        col_rename_dic = {}
        for col_name in df.columns:
            if (type(col_name) == str):
                col_rename_dic[col_name] = col_name
            else:
                col_rename_dic[col_name] = col_name.strftime("%m/%d/%y")
        df = df.rename(columns=col_rename_dic)
        row_entries = df['people'].tolist()
        col_entries = df.loc[:, df.columns != 'people'].columns.tolist()
        matrix = df.loc[:, df.columns != 'people'].to_numpy()
        return row_entries, col_entries, matrix

    def get_preference_matrix(self):
        dates, shifts, day_mat = self.load_day_requirements()
        people, req_dates, req_mat = self.load_staff_requirements()
        pref_mat = np.zeros((self.num_staff, self.days, self.max_shifts))
        for people_idx in range(self.num_staff):
            pref_setting = req_mat[people_idx] # 0-4: weekday; 5-24: weekend; 25-26: holiday
            for date_idx in range(self.days):
                shifts_setting = day_mat[date_idx]
                for shift_idx in range(self.max_shifts):
                    if not shifts_setting[shift_idx]:
                        # set to -2 when no shift exist
                        pref_mat[people_idx, date_idx, shift_idx] = -2
                    else:
                        # set staff preference
                        date_str = dates[date_idx]
                        date = datetime.datetime.strptime(date_str, "%m/%d/%y")
                        day_of_week = date.weekday() # 0-6 Mon-Sun
                        # if holiday: get holiday preference (25-26)
                        if date_str in self.holidays:
                            # get index of holiday in req_mat
                            holiday_idx = req_dates.index(date_str)
                            if (holiday_idx != -1):
                                pref_mat[people_idx, date_idx, shift_idx] = pref_setting[holiday_idx]
                            else:
                                print("Couldn't find holiday in staff preference")
                                print("holiday:", date_str)
                                print("staff preference dates:", req_dates)
                                exit(1)
                        else: 
                            # if weekday: get weekday preference (0-4)
                            if (day_of_week < 4 or day_of_week == 6):
                                if day_of_week == 6:
                                    weekday_idx = 0
                                else:
                                    weekday_idx = day_of_week+1
                                pref_mat[people_idx, date_idx, shift_idx] = pref_setting[weekday_idx]
                            # if weekend: get weekend preference (5-24)
                            else:
                                weekend_idx = req_dates.index(date_str)
                                if (weekend_idx != -1):
                                    pref_mat[people_idx, date_idx, shift_idx] = pref_setting[weekend_idx]
                                else:
                                    print("Couldn't find weekend in staff preference")
                                    print("weekend:", date_str)
                                    print("staff preference dates:", req_dates)
                                    exit(1)
        return pref_mat




