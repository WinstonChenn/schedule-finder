import argparse, os
from common_args import get_shift_req_args
from data_process.utils import get_date_arr, validate_datestr, \
                               is_weekend, is_same_day, contain_same_day
from data_process.raw_data_process import ElmWinter2022PreferenceProcessor
from gen_shift_matrix import get_shift_matrix

def main(args):
    # File setup
    data_dir = os.path.join(args.data_dir, args.data_name)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    raw_data_dir = os.path.join(data_dir, "raw_data")
    raw_data_url = os.path.join(raw_data_dir, args.raw_pref_file_name)
    assert os.path.isfile(raw_data_url), \
        f"Raw preference file: {raw_data_url} not found"
    output_dir = os.path.join(data_dir, "preference_matrices")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    shift_mat_df = get_shift_matrix(args)
    processor = ElmWinter2022PreferenceProcessor(
        raw_data_url, shift_mat_df=shift_mat_df,
        date_format=args.date_format
    )
    staff_names = processor.get_staff_names()
    staff_pref_matrices = {}
    for staff_name in staff_names:
        pref_matrix = processor.get_staff_pref_matrix(staff_names[0])
        staff_pref_matrices[staff_name] = pref_matrix
    breakpoint()


    


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
    get_shift_req_args(parser)

    args = parser.parse_args()
    main(args)
