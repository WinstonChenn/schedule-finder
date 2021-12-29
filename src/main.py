import argparse, os
import pandas as pd
from ortools.sat.python import cp_model
from args import get_shift_req_args
from data_process.utils import get_date_arr, validate_datestr, \
                               is_weekend, is_same_day, contain_same_day
from data_process.preference_inputters import ElmWinter2022PreferenceInputer
from data_process.schedule_outputters import ElmScheduleOutputter
from shift_matrix import get_shift_matrix
from solver.ScheduleModeler import ScheduleModeler
from solver.utils import get_solution_matrix, print_staff_shedule_stats

def main(args):
    # File setup
    data_dir = os.path.join(args.data_dir, args.data_name)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    raw_data_dir = os.path.join(data_dir, "raw_data")
    raw_data_url = os.path.join(raw_data_dir, args.raw_pref_file_name)
    unavailable_day_url = os.path.join(
        raw_data_dir, args.unavailble_day_json_file_name
    )
    assert os.path.isfile(raw_data_url), \
        f"Raw preference file: {raw_data_url} not found"
    assert os.path.isfile(unavailable_day_url), \
        f"Unavailable day json file: {unavailable_day_url} not found"

    # Input shift requirements
    shift_mat_df = get_shift_matrix(args)
    date_list = shift_mat_df["date"].tolist()
    shift_list = list(filter(
        lambda x: x != "date", shift_mat_df.columns.tolist()
    ))

    # Input Staff preferences
    processor = ElmWinter2022PreferenceInputer(
        raw_data_url, shift_mat_df=shift_mat_df,
        date_format=args.date_format, holidays=args.holidays, 
        staff_unavailable_json=unavailable_day_url
    )
    staff_names = processor.get_staff_names()
    staff_pref_matrices = {}
    staff_max_consecutive_dict = {}
    for staff_name in staff_names:
        pref_matrix = processor.get_staff_pref_matrix(staff_name)
        max_consecutive = processor.get_staff_max_consecutive_shifts(staff_name)
        staff_pref_matrices[staff_name] = pref_matrix
        staff_max_consecutive_dict[staff_name] = max_consecutive

    modeler = ScheduleModeler(
        shift_mat_df=shift_mat_df, 
        pref_mat_dict=staff_pref_matrices,
        staff_list=staff_names, 
        date_format=args.date_format,
        max_consecutive_dict=staff_max_consecutive_dict,
    )
    schedule_model, shift_vars = modeler.get_model()

    # solving cp-model
    solver = cp_model.CpSolver()
    # solver.parameters.linearization_level = 0
    solver.parameters.max_time_in_seconds = args.max_solve_time
    # solver.parameters.enumerate_all_solutions = True
    print(f"solving... (max time={args.max_solve_time})")
    solver.Solve(schedule_model)
    print(solver.StatusName())

    if solver.StatusName() != "INFEASIBLE":
        schedule_outputter = ElmScheduleOutputter(
            solver=solver, shift_vars=shift_vars, 
            date_list=date_list, staff_list=staff_names, 
            shift_list=shift_list, date_format=args.date_format,
            pref_mat_dict=staff_pref_matrices, 
            staff_unavailable_days_json=unavailable_day_url
        )
        schedule_outputter.verify_schedule()
        stats_df = schedule_outputter.get_schedule_stats(verbose=False)
        schedule_df = schedule_outputter.get_schedule_df()
        print("Solution Schedule Stats:")
        print(stats_df)
        

        solution_dir = os.path.join(data_dir, "solutions")
        if not os.path.exists(solution_dir):
            os.makedirs(solution_dir)
        solution_excel_url = os.path.join(solution_dir, args.solution_file_name)
        states_excel_url = os.path.join(solution_dir, "states.xlsx")
        
        df_writer = pd.ExcelWriter(solution_excel_url, datetime_format=args.date_format)
        schedule_df.to_excel(df_writer,index=False)
        df_writer.save()
        print("Schedule saved to {}".format(solution_excel_url))
        df_writer = pd.ExcelWriter(states_excel_url, datetime_format=args.date_format)
        stats_df.to_excel(df_writer,index=False)
        df_writer.save()
        print("Schedule stats saved to {}".format(states_excel_url))


    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="shift requirement generator flags")
    parser.add_argument(
        "--data_dir", type=str, default="../data/", help="data directory"
    )
    parser.add_argument(
        "--data_name", type=str, required=True,
        help="name of the data to generate shift requirement for",
    )
    parser.add_argument(
        "--date_format", type=str, help="format string for start/end date",
        default="%m/%d/%y"
    )
    parser.add_argument(
        "--raw_pref_file_name", type=str, help="name of the raw preference file",
        required=True
    )
    parser.add_argument(
        "--unavailble_day_json_file_name", type=str,
        help="name of the json file containing unavailable days for each staff",
    ),
    parser.add_argument(
        "--max_solve_time", type=int, help="max time in seconds to solve schedule",
        default=10
    )
    parser.add_argument(
        "--solution_file_name", type=str, help="name of the solution file",
        default="solution.xlsx"
    )
    parser.add_argument(
        "--holidays", type=str, nargs='+',
        help="holidays, format: mm/dd/yy",
        default=[]
    )
    get_shift_req_args(parser)

    args = parser.parse_args()
    main(args)
