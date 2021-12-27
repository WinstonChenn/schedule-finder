import argparse, os
from datetime import datetime
import numpy as np
import pandas as pd
from solver.ScheduleModeler import ScheduleSolver
from solver.ScheduleInputProcessor import ScheduleInputProcessor
from solver.utils import get_solution_matrix, print_staff_shedule_stats


def main(args):
    data_dir = os.path.join(args.data_dir, args.data_name)
    staff_requirement_url = os.path.join(
        data_dir, args.staff_req_file_name
    )
    shift_requirement_url = os.path.join(
        data_dir, args.date_req_file_name
    )
    additional_staff_requirement_url = os.path.join(
        data_dir, args.additional_staff_req_file_name
    )
    schedule_processor = ScheduleInputProcessor(
        shift_requirement_url=shift_requirement_url,
        staff_requirement_url=staff_requirement_url,
        additional_staff_requirement_url=additional_staff_requirement_url,
        holidays=args.holidays, exclude_dates=args.excluding_dates,
    )
    start_date =schedule_processor.get_start_date()
    end_date = schedule_processor.get_end_date()
    num_days = schedule_processor.get_num_days()
    max_shifts = schedule_processor.get_max_shifts()
    num_staffs = schedule_processor.get_num_staffs()
    staff_arr = schedule_processor.get_staff_arr()
    date_arr = schedule_processor.get_date_arr()
    shift_arr = schedule_processor.get_shift_arr()
    pref_mat = schedule_processor.get_preference_matrix()
    print("Start schedule finding: ")
    print(" - Start date: {}".format(start_date))
    print(" - End date: {}".format(end_date))
    print(" - Number of days: {}".format(num_days))
    print(" - Max number of shifts: {}".format(max_shifts))
    print(" - Number of staffs: {}".format(num_staffs))
    print()
    solution_dir = os.path.join(data_dir, "solutions")
    if not os.path.exists(solution_dir):
        os.makedirs(solution_dir)
    solution_matrix_url = os.path.join(
        solution_dir,
        "schedule_solution_matrix_numStaffs{}_numDays{}_numShifts{}_maxTime{}.npy"
        .format(num_staffs, num_days, max_shifts, args.max_time)
    )
    if not os.path.isfile(solution_matrix_url):
        num_days = (datetime.strptime(end_date, args.date_format) -
                    datetime.strptime(start_date, args.date_format)).days + 1 \
                        - len(args.excluding_dates)
        dates, shifts, shift_mat = schedule_processor.load_day_requirements()
        assert pref_mat.shape[1:] == shift_mat.shape
        schedule_solver = ScheduleSolver(
            preference_matrix=pref_mat,
            shift_matrix=shift_mat,
            date_arr=date_arr,
            date_format=args.date_format,
            max_time=args.max_time,
        )
        solver, shifts = schedule_solver.solve_schedule()
        if (solver.StatusName() != "INFEASIBLE" or solver.StatusName() != "UNKNOWN"):
            print(f" - total objective value: {solver.ObjectiveValue()}")
            print(f" - wall time =  {solver.WallTime()}s")
            solution_matrix = get_solution_matrix(
                solver, shifts, num_days, num_staffs, max_shifts)
            np.save(solution_matrix_url, solution_matrix)
            print("Solution matrix saved to {}".format(solution_matrix_url))
        else:
            print(f"solution is {solver.StatusName()}!")
            exit(1)
    else:
        print("Solution matrix already exists at {}".format(solution_matrix_url))
        solution_matrix = np.load(solution_matrix_url)
    shift_stat_df = print_staff_shedule_stats(
        solution_matrix, pref_mat, staff_arr, date_arr, shift_arr, args.date_format
    )
    solution_excel_url = os.path.join(
        solution_dir,
        "schedule_solution_schedule_numStaffs{}_numDays{}_numShifts{}_maxTime{}.xlsx"
        .format(num_staffs, num_days, max_shifts, args.max_time)
    )
    solution_stats_url = os.path.join(
        solution_dir,
        "schedule_solution_stats_numStaffs{}_numDays{}_numShifts{}_maxTime{}.xlsx"
        .format(num_staffs, num_days, max_shifts, args.max_time)
    )
    shift_dict = {"Title": [], "Shift": [], "Full Name": [], 
                  "Building & Role": [], "Staff Type": [], 
                  "On-Call Date": [], "Day of Week": [], 
                  "Type": []}
    day_of_week_arr = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for date_idx, date in enumerate(date_arr):
        for shift_idx, shift in enumerate(shift_arr):
            shift_mat = solution_matrix[:, date_idx, shift_idx]
            assert sum(shift_mat) == 1, \
                f"More or less than 1 shift is scheduled for {date} {shift}"
            shift_dict["Title"].append("On-Call Assignment")
            shift_dict["Shift"].append(shift)
            shift_dict["Full Name"].append(staff_arr[np.argmax(shift_mat)])
            shift_dict["Building & Role"].append(f"Elm {shift}")
            shift_dict["Staff Type"].append("Resident Adviser")
            shift_dict["On-Call Date"].append(date)
            week_of_day_idx = datetime.strptime(date, args.date_format).weekday()
            shift_type = "Weekend" if week_of_day_idx==4 or week_of_day_idx==5 else "Weekday"
            shift_dict["Day of Week"].append(day_of_week_arr[week_of_day_idx])
            shift_dict["Type"].append(shift_type)
    shift_df = pd.DataFrame.from_dict(shift_dict)
    df_writer = pd.ExcelWriter(solution_excel_url, datetime_format=args.date_format)
    shift_df.to_excel(df_writer,index=False)
    df_writer.save()
    print("Schedule saved to {}".format(solution_excel_url))
    df_writer = pd.ExcelWriter(solution_stats_url, datetime_format=args.date_format)
    shift_stat_df.to_excel(df_writer,index=False)
    df_writer.save()
    print("Schedule stats saved to {}".format(solution_stats_url))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Schedule Finder Flags')
    parser.add_argument('--data_dir', type=str, required=True)
    parser.add_argument('--data_name', type=str, required=True)
    parser.add_argument('--date_req_file_name', type=str, default="shift_requirements.xlsx")
    parser.add_argument('--staff_req_file_name', type=str, default="staff_requirements.xlsx")
    parser.add_argument('--additional_staff_req_file_name', type=str, 
                        default="additional_staff_requirements.json")
    parser.add_argument('--max_time', type=int, default=10, 
                        help='Max time in minutes to run the solver')
    parser.add_argument('--date_format', type=str, default="%m/%d/%y")
    parser.add_argument('--holidays', nargs='+', type=str, required=True, help="holidays")
    parser.add_argument("--excluding_dates", type=str, nargs='+',
        help="dates to exclude from shift requirement, format: mm/dd/yy",
        default=[])
    args = parser.parse_args()   
    main(args)
