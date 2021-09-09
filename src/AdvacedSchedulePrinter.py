import datetime
import pandas as pd


class AdvancedSchedulePrinter():

    def __init__(self, solver, shifts, start_date, end_date, max_shifts, num_staff, shift_mat):
        self.shifts = shifts
        self.output_url = "../data/solved_schedule.xlsx"
        self.data = {'Date': [], 'Day of Week': [], 'Shift Type': [], 'Staff Name': []}
        self.start_date = datetime.datetime.strptime(start_date, "%m/%d/%y")
        self.end_date = datetime.datetime.strptime(end_date, "%m/%d/%y")
        self.max_shifts = max_shifts
        self.num_staff = num_staff
        self.shift_mat = shift_mat # tell us which shift is valid
        assert (self.end_date - self.start_date).days == shift_mat.shape[0]
        self.num_days = shift_mat.shape[0]
        self.week_of_day_switcher = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday"
        }
        self.shift_type_swithcer = {
            0: "Building Night Time Primary Shift",
            1: "Building Night Time Secondary Shift",
            2: "Building Day Time Shift",
            3: "Place Holder",
        }

    def print_schedule(self):
        for d in range(self.num_days):
            for s in range(self.max_shifts):
                valid = bool(self.shift_mat[d, s])
                if valid:
                    for p in range(self.num_staff):
                        if self.solver.Value(self.shifts[(d, s, p)]) == 1:
                            curr_date = self.start_date + datetime.timedelta(days=d)
                            self.data['Date'].append(curr_date)
                            self.data['Day of week'].append(self.week_of_day_switcher[curr_date.weekday()])
                            self.data['Shift Type'].append(self.shift_type_swithcer[s])
                            self.data['Staff Name'].append("Staff {}".format(p+1))

        df = self.data
        excel_writer = pd.ExcelWriter(self.output_url, datetime_format="mm/dd/yy")

        df.to_excel(excel_writer, index=False)
        excel_writer.save()



