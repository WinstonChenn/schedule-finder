import argparse, os
from datetime import date, timedelta, datetime
import pandas as pd

def main(args):
    start_date = datetime.strptime(args.start_date, args.date_format).date()
    end_date = datetime.strptime(args.end_date, args.date_format).date()
    delta = end_date - start_date
    date_str_arr = []
    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        date_str = day.strftime(args.date_format)
        if not date_str in args.excluding_dates:
            date_str_arr.append(date_str)
    if args.num_shifts == 2:
        shift_arr = ["Primary", "Secondary"]
    elif args.num_shifts == 3:
        shift_arr = ["Primary", "Secondary", "Daytime"]
    else:
        shift_arr = [f"Shift {i+1}" for i in range(args.num_shifts)]
    columns = ["date"] + shift_arr
    data = [[date_str] + [1 for i in range(args.num_shifts)] 
            for date_str in date_str_arr]
    df = pd.DataFrame(data, columns=columns)
    data_dir = os.path.join(args.data_dir, args.data_name)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    data_url = os.path.join(data_dir, "shift_requirements.xlsx")
    df_writer = pd.ExcelWriter(data_url, datetime_format="mm/dd/yy")
    df.to_excel(df_writer,index=False)
    df_writer.save()
    print(f"Shift requirements saved at {data_url}")



if __name__ == "__main__" :
    parser = argparse.ArgumentParser(description="shift requirement generator flags")
    parser.add_argument(
        "--data_dir", type=str, default="../../data/", help="data directory")
    parser.add_argument(
        "--data_name", type=str, required=True,
        help="name of the data to generate shift requirement for",
    )
    parser.add_argument(
        "--date_format",
        type=str,
        help="format string for start/end date",
        default="%m/%d/%y"
    )
    parser.add_argument(
        "--start_date", 
        type=str, 
        help="shift start date(inclusive), format: mm/dd/yy",
        required=True
    )
    parser.add_argument(
        "--end_date", 
        type=str, 
        help="shift end date(inclusive), format: mm/dd/yy",
        required=True
    )
    parser.add_argument(
        "--num_shifts",
        type=int,
        help="number of shifts per day",
        default=2
    )
    parser.add_argument(
        "--excluding_dates",
        type=str,
        nargs='+',
        help="dates to exclude from shift requirement, format: mm/dd/yy",
        default=[]
    )
    args = parser.parse_args()
    main(args)