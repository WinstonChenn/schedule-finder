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


class ScheduleInputProcessor:

    def __init__(self, start_date, end_date, max_shifts, num_staff,
                 date_requirement_url, staff_requirement_url):
        try:
            self.start_date = datetime.datetime.striptime(start_date, "%d/%m/%y")
            self.end_date = datetime.datetime.striptime(end_date, "%d/%m/%y")
        finally:
            print("input date format: d/m/y\n e.g. 20/12/20")

        self.max_shifts = max_shifts
        self.num_staff = num_staff
        self.date_requirement_url = date_requirement_url
        self.staff_reqirement_url = staff_requirement_url

    # provide file directory of csv to convert to pandas dataframe
    # should fit specs provided by InputProcessor.py
    def load_day_requirements(self):
        pass

    # provide file directory of csv to convert to pandas dataframe
    # should fit specs provided by InputProcessor.py
    def loadstaff_reqirements(self):
        pass
