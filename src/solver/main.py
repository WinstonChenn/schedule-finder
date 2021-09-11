import datetime, argparse, os
from ScheduleSolver import ScheduleSolver
from ScheduleInputProcessor import ScheduleInputProcessor
from AdvacedSchedulePrinter import AdvancedSchedulePrinter


MAX_SHIFTS = 2
NUM_STAFF = 10
START_DATE = "01/03/21"
END_DATE = "03/13/21"
DATE_FORMAT = "%m/%d/%y"
HOLIDAYS = ["01/18/21", "02/15/21"]

def main(args):
    shift_requirement_url = os.path.join(args.data_dir, args.data_name, args.date_req_file_name)
    staff_requirement_url = os.path.join(args.data_dir, args.data_name, args.staff_req_file_name)
    schedule_processor = ScheduleInputProcessor(
        start_date=START_DATE,
        end_date=END_DATE,
        max_shifts=MAX_SHIFTS,
        num_staff=NUM_STAFF,
        shift_requirement_url=shift_requirement_url,
        staff_requirement_url=staff_requirement_url,
        holidays=HOLIDAYS
    )

    pref_mat = schedule_processor.get_preference_matrix()
    num_days = (datetime.datetime.strptime(END_DATE, DATE_FORMAT) -
                datetime.datetime.strptime(START_DATE, DATE_FORMAT)).days + 1
    dates, shifts, day_mat = schedule_processor.load_day_requirements()
    assert pref_mat.shape[1:] == day_mat.shape
    schedule_solver = ScheduleSolver(
        preference_matrix=pref_mat,
        shift_matrix=day_mat,
        num_people=NUM_STAFF,
        num_shifts=MAX_SHIFTS,
        num_days=num_days, 
        max_time=args.max_time,
    )
    schedule_solver.solve_schedule()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Schedule Finder Flags')
    parser.add_argument('--data_dir', type=str, required=True)
    parser.add_argument('--data_name', type=str, required=True)
    parser.add_argument('--date_req_file_name', type=str, default="shift_requirements.xlsx")
    parser.add_argument('--staff_req_file_name', type=str, default="scaled_staff_req.xlsx")
    parser.add_argument('--max_time', type=float, default=10.0, 
                        help='Max time in minutes to run the solver')
    args = parser.parse_args()   
    main(args)
