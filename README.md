# Employees Schedule Finding With Preference
This repo implements a simple and easy-to-use python scripts that solves the employees scheduling given preference problem.
## Requirements
- [Python](https://www.python.org/)
- [Google Or-Tools](https://developers.google.com/optimization)
- [Pandas](https://pandas.pydata.org/)
- [Numpy](https://numpy.org/)
## Problem Setup
- There are <b>n</b> days of work and each day has a maximum number of <b>s</b> shifts that need to be scheduled to <b>p</b> employees. 
- Each shift only needs 1 employee to fulfill. 
- Shifts within the same day can sometimes happen at the same time (up to user interpretation) and will need different employees to fulfill. 
- Each employee can also provide a discrete preference bewteen -2 (can't do it) to 2 (I want it) for all the shifts that will be scheduled. 
- One additional employee preference includes the maximum number of back to back days one would like to have shift(s) scheduled.

## Generating Shift Matrix
The first step of solve the schedule finding problem invovles generating a shift matrix.
The shift matrix is a binary matrix with shape <b>n</b> by <b>s</b>. n = number of days to schedule shifts, s = maximum number of shifts each day would have. 
One of the goal of this scheduling program is to fullfill all the shifts with shift matrix entry equals to 1.

`shift_matrix.py` can be used to generate shift matrix.
Following flags are designed to describe a shift matrix.
- `--date_format`: the format string used to by `datetime.strptime` to interprete date strings provided in arguments.
- `--start_date`: the first date in the shift matrix (in the formate of `--date_format`).
- `--end_date`: the last date in the shift matrix (in the formate of `--date_format`).
- `--excluding_dates`: dates between `--start_date` and `--end_date` that should be excluded from the shift matrix.
- `--max_num_shifts`: maximum number of shifts that each day in the shift matrix will have.(the same as the <b>s</b> metioned above)
- `--shifts_names`: a list of strings representing the names for each shift. The length of this argument need to equal `--max_num_shifts`.
- `--weekday_num_shifts`: number of valid shifts that weekdays will have. this argument needs to be less than or equal to `--max_num_shifts`. Based on the number given, the first n shifts on weekday days will be given 1 labels, and all the later shifts will be given 0 labels. 
- `--weekend_num_shifts`: Same as the `--weekday_num_shifts`, this argument needs to be less than or equal to `--max_num_shifts`. 
- `--special_weekdays`: A list of dates that are weekends by standard calendar, but should be considered as weekdays for shift number consideration.
- `--special_weekends`: Same as `--special_weekends, a list of dates that are weekdays by standard calendar, but should be considered as weekends for shift number consideration.

The generated shift matrix will be stored using following commands
- `--data_dir`: directory that will be used for storing all data
- `--data_name`: name for a subdirectory which will be created to store data for a specific schedule, which the program is currently working with.

The shift matrix file will be stored at following location: `args.data_dir/args.data_name/shift_matrix.xlsx` as a excel file. The first column of the excel file will be dates (written in the format of `--date_format`). The following columns will represent each shifts provided in `--shifts_names`.

## Generating Preference Matrix

## Solving Schedule

## Outputting Schedule

