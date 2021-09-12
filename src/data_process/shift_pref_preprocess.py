import argparse, os
import pandas as pd
from datetime import datetime, timedelta

def process_col_str(col_str):
    processed = col_str.strip("]").split("[")[-1].strip()
    if not processed in ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']:
        processed = "".join(list(filter(lambda c: not str.isalpha(c), processed))).strip()
    return processed

def process_pref_str(pref_str):
    return pref_str.strip(")").split(" (")[-1]

def get_dates_arr(date_str, input_date_format, output_date_format):
    if " - " in date_str:
        start_date, end_date = date_str.strip().split(" - ")
    else:
        start_date = end_date = date_str.strip()
    start_date = datetime.strptime(start_date, input_date_format) \
        .replace(year=datetime.today().year).date()
    end_date = (datetime.strptime(end_date, input_date_format)-timedelta(days=1)) \
        .replace(year=datetime.today().year).date()
    date_range = pd.date_range(start_date,end_date,freq='d')
    date_str_arr = [date.strftime(output_date_format) for date in date_range]
    return date_str_arr

def main(args):
    data_dir = os.path.join(args.data_dir, args.data_name)
    raw_data_url = os.path.join(data_dir, args.raw_data_name)
    processed_data_url = os.path.join(data_dir, args.processed_data_name)
    raw_df = pd.read_excel(raw_data_url)
    pref_cols = list(raw_df.loc[:, ~raw_df.columns.isin(
        ["Timestamp", "Name", "Additional comments"])].columns)
    short_pref_cols = list(map(process_col_str, pref_cols))
    assert len(pref_cols) == len(short_pref_cols)
    for i in range(len(pref_cols)):
        raw_df.rename(columns={pref_cols[i]: short_pref_cols[i]}, inplace=True)
        raw_df[short_pref_cols[i]] = raw_df[short_pref_cols[i]].apply(process_pref_str)
    # Expanding weekend columns & process holiday columns
    date_cols = list(filter(lambda str: "/" in str, raw_df.columns))
    for col in date_cols:
        date_str_arr = get_dates_arr(col, args.input_date_format, args.output_date_format)
        for date_str in date_str_arr:
            raw_df[date_str] = raw_df[col]
        raw_df.drop(col, axis=1, inplace=True)
    raw_df.drop(["Timestamp", "Additional comments"], axis=1, inplace=True)
    raw_df.rename(columns={"Name": "people"}, inplace=True)
    df_writer = pd.ExcelWriter(processed_data_url, datetime_format=args.output_date_format)
    raw_df.to_excel(df_writer,index=False)
    df_writer.save()
    print("Saved preprocessed data at {}".format(processed_data_url))




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Schedule Finder Flags')
    parser.add_argument('--data_dir', type=str, required=True)
    parser.add_argument('--data_name', type=str, required=True)
    parser.add_argument('--raw_data_name', type=str, required=True)
    parser.add_argument('--processed_data_name', type=str, required=True)
    parser.add_argument('--input_date_format', type=str, default="%m/%d")
    parser.add_argument('--output_date_format', type=str, default="%m/%d/%y")
    args = parser.parse_args()
    main(args)
