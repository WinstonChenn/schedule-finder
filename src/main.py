import datetime
from ScheduleSolver import ScheduleSolver
from ScheduleInputProcessor import ScheduleInputProcessor
from AdvacedSchedulePrinter import AdvancedSchedulePrinter


MAX_SHIFTS = 4
NUM_STAFF = 10
START_DATE = "1/3/21"
END_DATE = "3/12/21"
DATE_FORMAT = "%m/%d/%y"
HOLIDAYS = ["1/18/21", "2/15/21"]

def main():
    schedule_processor = ScheduleInputProcessor(
        start_date=START_DATE,
        end_date=END_DATE,
        max_shifts=MAX_SHIFTS,
        num_staff=NUM_STAFF,
        date_requirement_url="../data/date_requirements.xlsx",
        staff_requirement_url="../data/scaled_staff_req.xlsx",
        holidays=HOLIDAYS
    )

    pref_mat = schedule_processor.get_preference_matrix()
    num_days = (datetime.datetime.strptime(END_DATE, DATE_FORMAT) -
                datetime.datetime.strptime(START_DATE, DATE_FORMAT)).days + 1
    dates, shifts, day_mat = schedule_processor.load_day_requirements()
    schedule_solver = ScheduleSolver(
        preference_matrix=pref_mat,
        shift_matrix=day_mat,
        num_people=NUM_STAFF,
        num_shifts=MAX_SHIFTS,
        num_days=num_days
    )
    schedule_solver.solve_schedule()


if __name__ == "__main__":
    main()
