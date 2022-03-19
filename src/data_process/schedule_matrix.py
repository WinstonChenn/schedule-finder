import argparse, os
import pandas as pd
from data_process.utils import get_date_arr, validate_datestr, \
                               is_weekend, is_same_day, contain_same_day
from args import get_shift_req_args

def get_schedule_matrix(args):

    data_dir = os.path.join(args.data_dir, args.data_name)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    data_url = os.path.join(data_dir, "schedule_matrix.xlsx")
    if os.path.exists(data_url) and not args.overwrite:
        print(f"Shift matrix already exists at: {data_url} "
              f"use --overwrite to overwrite")
        return pd.read_excel(data_url)

    # Validating all the date string inputs
    assert validate_datestr(args.start_date, args.date_format), \
        "Invalid start date: {}".format(args.start_date)
    assert validate_datestr(args.end_date, args.date_format), \
        "Invalid end date: {}".format(args.end_date)
    assert all([validate_datestr(date_str) for date_str in args.excluding_dates]), \
        "Invalid date string in --excluding_dates"
    assert all([validate_datestr(date_str) for date_str in args.special_weekdays]), \
        "Invalid date string in --special_weekdays"
    assert all([validate_datestr(date_str) for date_str in args.special_weekends]), \
        "Invalid date string in --special_weekends"

    # Check if special weekdays/weekends overlaps
    assert set(args.special_weekdays).isdisjoint(args.special_weekends), \
        "Special weekdays and weekends overlap"

    # Validating shift numbers
    assert args.max_num_shifts == len(args.shifts_names), \
        "Number of shifts names in --shifts_names must be equal to --max_num_shifts"
    assert args.weekday_num_shifts <= args.max_num_shifts, \
        "--weekday_num_shifts must be less than or equal to --max_num_shifts"
    assert args.weekend_num_shifts <= args.max_num_shifts, \
        "--weekend_num_shifts must be less than or equal to --max_num_shifts"
    
    # creating date string between start & end dates
    date_arr = get_date_arr(args.start_date, args.end_date, args.date_format)
    date_arr = filter(lambda x: not contain_same_day(x, args.excluding_dates), date_arr)

    # creating pandas dataframe
    df_dict = {"date": []} | {f"{shift}": [] for shift in args.shifts_names}
    for date in date_arr:
        df_dict["date"].append(date)
        if (is_weekend(date, args.date_format) and \
            not contain_same_day(date, args.special_weekdays, args.date_format)) \
            or contain_same_day(date, args.special_weekends, args.date_format):
            num_shifts = args.weekend_num_shifts
        else:
            num_shifts = args.weekday_num_shifts
        for idx, shift in enumerate(args.shifts_names):
            if idx < num_shifts:
                df_dict[shift].append(1)
            else:
                df_dict[shift].append(0)
    df = pd.DataFrame(df_dict)
    df_writer = pd.ExcelWriter(data_url, datetime_format="mm/dd/yy")
    df.to_excel(df_writer,index=False)
    df_writer.save()
    print(f"Shift requirements saved at {data_url}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="shift requirement generator flags")
    parser.add_argument(
        "--data_dir", type=str, default="../data/", help="data directory"
    )
    parser.add_argument(
        "--data_name", type=str, required=True,
        help="name of the data to generate shift matrix for",
    )
    parser.add_argument(
        "--date_format", type=str, help="format string for start/end date",
        default="%m/%d/%y"
    )
    get_shift_req_args(parser)

    args = parser.parse_args()
    get_schedule_matrix(args)
