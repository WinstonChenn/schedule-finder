# Employees Schedule Finding With Preference
This repo implements a simple and easy-to-use python scripts that solves the employees scheduling given preference problem.

![schedule](https://raw.githubusercontent.com/WinstonChenn/schedule-finder/main/cartoon.jpeg)
## Requirements
- [Python](https://www.python.org/)
- [Google Or-Tools](https://developers.google.com/optimization)
- [Pandas](https://pandas.pydata.org/)
- [Numpy](https://numpy.org/)
## Problem Setup
- There are <i>n</i> days of work and each day has a maximum number of <i>s</i> shifts that need to be scheduled to <i>p</i> employees. 
- Each shift only needs 1 employee to fulfill. 
- Shifts within the same day can sometimes happen at the same time (up to user interpretation) and will need different employees to fulfill. 
- Each employee can also provide a discrete preference bewteen -2 (can't do it) to 2 (I want it) for all the shifts that will be scheduled. 
- One additional employee preference includes the maximum number of back to back days one would like to have shift(s) scheduled.


## Usage
1. Setup preference inputter. 
    - The schedule finder program require using a preference inputter object to extract specific staff preferences from a staff preference file (usually in excel). 
    - We provided a interfance for such preference inputter in `src/data_process/data_interfaces` named `PreferenceInputterInterface`
    - An example of such preference inputter class can be found in `src/data_process/preference_inputters` named `ElmWinter2022PreferenceInputer`
    - Followings are the required methods for a valid preference inputter class:
        - `get_staff_name(self) -> list`: Return a list of staff names from raw data table.
        - `get_staff_pref_matrix(self, staff: str) -> numpy.ndarray`: Return the preference matrix for the given staff.
        - `get_staff_max_consecutive_shifts(self, staff: str) -> int`: Return the maximum number of consecutive shifts for the given staff.
    - Different preference file will likely require different parsing script to implement above methods, therefore we only provide an interface. 
2. Setup schedule outputter.
    - The schedule outputter objects determines how the solved schedule from google OR-tools' Constrained Programming Solver will be formatted to output to tabular format
    - We provided following interfance `ScheduleOutputterInterface` in `src/data_process/data_interfaces`
    - An example of such schedule outputter class can be found in `src/data_process/schedule_outputters` named `ElmScheduleOutputter`
    - Following are the required methods for a valid schedule outputter class:
        - `get_schedule_stats(self) -> pandas.DataFrame`: Print the shift statistics for each staff and return a pandas DataFrame that stores those statistics.
        - `get_schedule_df(self) -> pandas.DataFrame`: Return the schedule formatted in a pandas DataFrame.
        - `verify_schedule(self) -> bool`: Verify that the scheudle is valid.

3. Modify imports for customized preference inputter and schedule outputter.
    - in the `src/main.py` script, modify following two lines with your own inputter/outputter
        - https://github.com/WinstonChenn/schedule-finder/blob/e7998fe545cc511739a33395b7115dd98b5d4bdf/src/main.py#L7-L8

4. Run `src/main.py` with following args
    - file path args
        - `--data_dir`: the root data directory that stores all scheduling data
        - `--data_name`: name of the sub-directory within `data_dir` that stores scheduling data for the current scheduling finding task
        - `--raw_pref_file_name`: name of the raw preference file that will be used by `PreferenceInputter` object to extract perference data. Assumed to store in `data_dir/data_name/raw_data` folder.
        - `--unavailable_day_json_file_name`: specific shifts in specific dates/day of the week that any staffs can not work, can also be used by `PreferenceInputter` object as additional preference information. Assumed to store in `data_dir/data_name/raw_data` folder.
        - `--solution_file_name`: file name that schedule solution will be written to. Will be stored in `data_dir/data_name/solutions`.
    - Schedule requirements args
        - `--start_date`: the first date in the schedule matrix (in the formate of `--date_format`).
        - `--end_date`: the last date in the schedule matrix (in the formate of `--date_format`).
        - `--excluding_dates`: a list of dates between `--start_date` and `--end_date` that should be excluded from the schedule matrix (in the formate of `--date_format`).
        - `--max_num_shifts`: maximum number of shifts that each day in the schedule matrix will have.(the same as the <i>s</i> in the problem)
        - `--shifts_names`: a list of names for each shift. The length of this argument need to equal `--max_num_shifts`.
        - `--weekday_num_shifts`: number of valid shifts that weekdays will have. this argument needs to be less than or equal to `--max_num_shifts`. Based on the number given, the first n shifts on weekday days will be given 1 labels, and all the later shifts will be given 0 labels. 
        - `--weekend_num_shifts`: Same as the `--weekday_num_shifts`, this argument needs to be less than or equal to `--max_num_shifts`. 
        - `--special_weekdays`: A list of dates that are weekends by standard calendar, but should be considered as weekdays for shift number consideration.
        - `--special_weekends`: Same as `--special_weekends, a list of dates that are weekdays by standard calendar, but should be considered as weekends for shift number consideration.
    - Other args
        - `--date_format`: the format string used to by `datetime.strptime` to parse and generate all the date strings provided in staff preference and schedule requirement.
        - `--max_solve_time`: the maximum amount of time allowing google OR-tools to solve the schedule in seconds.

<!-- 
## Generating Schedule Matrix
The first step of solving this schedule finding problem is to generate a schedule matrix.
The schedule matrix is a matrix of shape <i>n</i> by <i>s</i> that only contains 0 or 1, where <i>n</i> represents number of days the schedule should include, <i>s</i> represents the maximum number of shifts each day would have. Entries in the schedule matrix that contain 0 represent no worker needs to be scheduled for that a shift, and entries that contain 1 represent 1 worker needs to be schedule for that shift.

`schedule_matrix.py` can be used to generate schedule matrix.
Following flags are designed to describe a schedule matrix.
- `--date_format`: the format string used to by `datetime.strptime` to interprete date strings provided in following arguments.
- `--start_date`: the first date in the schedule matrix (in the formate of `--date_format`).
- `--end_date`: the last date in the schedule matrix (in the formate of `--date_format`).
- `--excluding_dates`: a list of dates between `--start_date` and `--end_date` that should be excluded from the schedule matrix (in the formate of `--date_format`).
- `--max_num_shifts`: maximum number of shifts that each day in the schedule matrix will have.(the same as the <i>s</i> in the problem)
- `--shifts_names`: a list of names for each shift. The length of this argument need to equal `--max_num_shifts`.
- `--weekday_num_shifts`: number of valid shifts that weekdays will have. this argument needs to be less than or equal to `--max_num_shifts`. Based on the number given, the first n shifts on weekday days will be given 1 labels, and all the later shifts will be given 0 labels. 
- `--weekend_num_shifts`: Same as the `--weekday_num_shifts`, this argument needs to be less than or equal to `--max_num_shifts`. 
- `--special_weekdays`: A list of dates that are weekends by standard calendar, but should be considered as weekdays for shift number consideration.
- `--special_weekends`: Same as `--special_weekends, a list of dates that are weekdays by standard calendar, but should be considered as weekends for shift number consideration.

The generated schedule matrix will be stored using following flags
- `--data_dir`: directory that will be used for storing all data
- `--data_name`: name for a subdirectory which will be created to store data for a specific schedule, which the program is currently working with.

The schedule matrix file will be stored at following location: `args.data_dir/args.data_name/schedule_matrix.xlsx` as a excel file. The first column of the excel file will be dates (written in the format of `--date_format`). The following columns will represent each shifts provided in `--shifts_names`.

## Generating Preference Matrix

## Solving Schedule

## Outputting Schedule
 -->
