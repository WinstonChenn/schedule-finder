import argparse, os
from datetime import datetime
import numpy as np
from ScheduleSolver import ScheduleSolver
from ScheduleInputProcessor import ScheduleInputProcessor
from utils import get_solution_matrix, print_staff_shedule_stats


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
        holidays=args.holidays
    )
    start_date =schedule_processor.get_start_date()
    end_date = schedule_processor.get_end_date()
    num_days = schedule_processor.get_num_days()
    max_shifts = schedule_processor.get_max_shifts()
    num_staffs = schedule_processor.get_num_staffs()
    staff_arr = schedule_processor.get_staff_arr()
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
    solution_url = os.path.join(
        solution_dir,
        "schedule_solution_numStaffs{}_numDays{}_numShifts{}_maxTime{}.npy"
        .format(num_staffs, num_days, max_shifts, args.max_time)
    )
    if not os.path.isfile(solution_url):
        num_days = (datetime.strptime(end_date, args.date_format) -
                    datetime.strptime(start_date, args.date_format)).days + 1
        dates, shifts, shift_mat = schedule_processor.load_day_requirements()
        assert pref_mat.shape[1:] == shift_mat.shape
        schedule_solver = ScheduleSolver(
            preference_matrix=pref_mat,
            shift_matrix=shift_mat,
            max_time=args.max_time,
        )
        solver, shifts = schedule_solver.solve_schedule()
        if (solver.StatusName() != "INFEASIBLE"):
            print(f" - total objective value: {solver.ObjectiveValue()}")
            print(f" - wall time =  {solver.WallTime()}s")
            solution_matrix = get_solution_matrix(
                solver, shifts, num_days, num_staffs, max_shifts)
            np.save(solution_url, solution_matrix)
            print("Solution matrix saved to {}".format(solution_url))
        else:
            print("No feasible solution found!")
            exit(1)
    else:
        print("Solution matrix already exists at {}".format(solution_url))
        solution_matrix = np.load(solution_url)
    print_staff_shedule_stats(solution_matrix, pref_mat, staff_arr, shift_arr)


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
    args = parser.parse_args()   
    main(args)
