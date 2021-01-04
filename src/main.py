import datetime
from ScheduleSolver import ScheduleSolver
from ScheduleInputProcessor import ScheduleInputProcessor
from AdvacedSchedulePrinter import AdvancedSchedulePrinter


def main():
    schedule_processor = ScheduleInputProcessor(
        start_date="1/3/21",
        end_date="3/12/21",
        max_shifts=4,
        num_staff=10,
        date_requirement_url="../data/date_requirements.xlsx",
        staff_requirement_url="../data/scaled_staff_req.xlsx",
        holidays=["1/18/21", "2/15/21"]
    )

    pref_mat = schedule_processor.get_preference_matrix()
    num_days = (datetime.datetime.strptime("3/12/21", "%m/%d/%y") - datetime.datetime.strptime("1/3/21", "%m/%d/%y")).days + 1
    dates, shifts, day_mat = schedule_processor.load_day_requirements()

    breakpoint()
    schedule_solver = ScheduleSolver(
        preference_matrix=pref_mat,
        shift_matrix=day_mat,
        num_people=pref_mat.shape[0],
        num_shifts=pref_mat.shape[2],
        num_days=num_days
    )

    schedule_solver.solve_schedule()


if __name__ == "__main__":
    main()
