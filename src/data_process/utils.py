from datetime import datetime, timedelta

def get_date_arr(start_date, end_date, date_format="%m/%d/%y"):
    """
    Return a list of dates from start_date to end_date.
    """
    date_arr = []
    start_date = datetime.strptime(start_date, date_format).date()
    end_date = datetime.strptime(end_date, date_format).date()
    delta = end_date - start_date
    for i in range(delta.days + 1):
        curr_date = start_date + timedelta(days=i)
        date_arr.append(curr_date.strftime(date_format))
    return date_arr


def validate_datestr(date_str, date_format="%m/%d/%y"):
    """
    Validate a date string.
    """
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False

def is_weekend(date_str, date_format="%m/%d/%y"):
    """
    Return True if the date is a weekend.
    """
    date = datetime.strptime(date_str, date_format).date()
    return date.weekday() >= 5

def is_friday(date_str, date_format="%m/%d/%y"):
    """
    Return True if the date is Friday.
    """
    date = datetime.strptime(date_str, date_format).date()
    return date.weekday() == 4

def is_saturday(date_str, date_format="%m/%d/%y"):
    """
    Return True if the date is Saturday.
    """
    date = datetime.strptime(date_str, date_format).date()
    return date.weekday() == 5

def is_sunday(date_str, date_format="%m/%d/%y"):
    """
    Return True if the date is Sunday.
    """
    date = datetime.strptime(date_str, date_format).date()
    return date.weekday() == 6

def is_saturday_sunday(date_str, date_format="%m/%d/%y"):
    """
    Return True if the date is Saturday or Sunday.
    """
    return is_saturday(date_str, date_format) or is_sunday(date_str, date_format)

def is_same_day(date_str1, date_str2, date_format="%m/%d/%y"):
    """
    Return True if the two dates are the same.
    """
    date1 = datetime.strptime(date_str1, date_format).date()
    date2 = datetime.strptime(date_str2, date_format).date()
    return date1 == date2

def get_day_of_week_str(date_str, date_format="%m/%d/%y"):
    """
    Return day of week string of a date string.
    """
    day_of_week_list = [
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", 
        "Saturday", "Sunday"
    ]
    date = datetime.strptime(date_str, date_format).date()
    return day_of_week_list[date.weekday()]


def contain_same_day(date_str, date_str_arr, date_format="%m/%d/%y"):
    """
    Return True if the date_str is in the date_str_arr.
    """
    date = datetime.strptime(date_str, date_format).date()
    for d in date_str_arr:
        if date == datetime.strptime(d, date_format).date():
            return True
    return False

def keep_trail_parentheses_num(s) -> float:
    """
    Return number in the trailling parenthese of a string.

    e.g.
    keep_trail_parentheses("Marry Christmas (24)") -> 24
    """
    left_idx = s.rfind("(")
    right_idx = s.rfind(")")
    assert left_idx != -1 and right_idx != -1, "Invalid parentheses string"
    assert right_idx > left_idx, "Invalid parentheses string"
    return float(s[left_idx+1: right_idx])

def keep_trail_bracket_str(s) -> str:
    """
    Return string in the trailling bracket of a string.

    e.g.
    keep_trail_bracket_str("Marry Christmas (24)") -> Christmas
    """
    left_idx = s.rfind("[")
    right_idx = s.rfind("]")
    assert left_idx != -1 and right_idx != -1, "Invalid brackets string"
    assert right_idx > left_idx, "Invalid brackets string"
    return s[left_idx+1: right_idx]