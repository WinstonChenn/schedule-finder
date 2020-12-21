import datetime
import pandas


class RefactorThis:

    def __init__(self, year_S, month_S, day_S,
                 year_E, month_E, day_E, max_shifts, num_staff):
        self.start_date = datetime.datetime(year_S, month_S, day_S)
        self.end_date = datetime.datetime(year_E, month_E, day_E)
        self.max_shifts = max_shifts
        self.num_staff = num_staff

    # provide file directory of csv to convert to pandas dataframe
    # should fit specs provided by InputProcessor.py
    def day_requirements(file_directory):
        pass

    # provide file directory of csv to convert to pandas dataframe
    # should fit specs provided by InputProcessor.py
    def staff_reqirements(file_directory):
        pass
