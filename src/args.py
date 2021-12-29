
def get_shift_req_args(parser):
    parser.add_argument(
        "--start_date", type=str, help="shift start date(inclusive), format: mm/dd/yy",
        required=True
    )
    parser.add_argument(
        "--end_date", type=str, help="shift end date(inclusive), format: mm/dd/yy",
        required=True
    )
    parser.add_argument(
        "--excluding_dates", type=str, nargs='+',
        help="dates to exclude from shift requirement, format: mm/dd/yy",
        default=[]
    )
    parser.add_argument(
        "--max_num_shifts", type=int, help="maximum number of shifts per day",
        default=3
    )
    parser.add_argument(
        "--shifts_names", type=str, nargs='+',
        help="shift names, default: Primary, Secondary, Daytime",
        default=["Primary", "Secondary", "Daytime"]
    )
    parser.add_argument(
        "--weekday_num_shifts", type=int, help="number of shifts per weekday",
        default=2
    )
    parser.add_argument(
        "--weekend_num_shifts", type=int, help="number of shifts per weekend",
        default=3
    )
    parser.add_argument(
        "--special_weekdays", type=str, nargs='+',
        help="weekend days that should be consiedered as weekdays, format: mm/dd/yy",
        default=[]
    )
    parser.add_argument(
        "--special_weekends", type=int, nargs='+',
        help="weekdays that should be consiedered as weekends, format: mm/dd/yy",
        default=[]
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="overwrite existing shift matrix"
    )
    return parser
