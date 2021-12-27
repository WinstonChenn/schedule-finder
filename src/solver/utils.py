import numpy as np
import pandas as pd
from datetime import datetime

def get_solution_matrix(solver, shifts, n_days, n_staffs, n_shifts):
    solu_mat = np.zeros((n_staffs, n_days, n_shifts))
    for p in range(n_staffs):
        for d in range(n_days):
            for s in range(n_shifts):
                try:
                    solu_mat[p, d, s] = solver.Value(shifts[p, d, s])
                except:
                    solu_mat[p, d, s] = 0
    return solu_mat


def print_staff_shedule_stats(
    solution_mat, pref_mat_dict, staff_arr, date_arr, shift_arr, date_format
):
    assert solution_mat.shape[0] == len(staff_arr)
    assert solution_mat.shape[1] == len(date_arr)
    assert solution_mat.shape[2] == len(shift_arr)

    want_count = 0
    ok_count = 0
    no_pref_count = 0
    cant_count = 0
    total_count = 0
    staff_shift_arr = [[{"Weekend": 0, "Weekday": 0}for _ in range(len(shift_arr))] for _ in range(len(staff_arr))]
    total_shift_arr = [0 for _ in range(len(staff_arr))]
    for p in range(solution_mat.shape[0]):
        staff = staff_arr[p]
        for d in range(solution_mat.shape[1]):
            for s in range(solution_mat.shape[2]):
                if solution_mat[p, d, s] == 1:
                    total_count += 1
                    total_shift_arr[p] += 1
                    week_of_day_idx = datetime.strptime(date_arr[d], date_format).weekday()
                    shift_type = "Weekend" if week_of_day_idx==4 or week_of_day_idx==5 else "Weekday"
                    staff_shift_arr[p][s][shift_type] += 1
                    if pref_mat_dict[staff][d][s] > 1:
                        want_count += 1
                    elif pref_mat_dict[staff][d][s] == 1:
                        ok_count += 1
                    elif pref_mat_dict[staff][d][s] == 0:
                        no_pref_count += 1
                    elif pref_mat_dict[staff][d][s] < 0:
                        print(date_arr[d], shift_arr[s], staff_arr[p])
                        cant_count += 1

    shift_stat_dict = {"RA": []}
    for day_of_week in ["Weekday", "Weekend"]:
        for shift_type in shift_arr:
            shift_stat_dict[f"{day_of_week} - {shift_type}"] = []
    shift_stat_dict["Total Shifts"] = []
    print("Staff shift taking statistics: ")
    for p, staff in enumerate(staff_arr):
        print(f"{staff}: ")
        print(f"\t#Total Shifts={total_shift_arr[p]}")
        shift_stat_dict["RA"].append(staff)
        shift_stat_dict["Total Shifts"].append(total_shift_arr[p])
        for s in range(len(shift_arr)):
            for key in staff_shift_arr[p][s]:
                print(f"\t#{key} {shift_arr[s]}={staff_shift_arr[p][s][key]}")
                shift_stat_dict[f"{key} - {shift_arr[s]}"].append(staff_shift_arr[p][s][key])
        print()
    print(f" - Number of wanted shifts requests met: {want_count}")
    print(f" - Number of OK shifts met: {ok_count}")
    print(f" - Number of no preference shifts met: {no_pref_count}")
    print(f" - Number of cant shifts met: {cant_count}")
    print(f" - Total number of shifts {total_count}")
    return pd.DataFrame.from_dict(shift_stat_dict)


# given the binary setting for 4 shifts, solve maximum
# number of shifts one staff can have that day
# Used Boolean Algebra
# Truth table Solved
# shift1(A) shift2(B) shift3(C) shift4(D)  max_shift_per_day_per_person
#     0        0         0         0             0      0   (0)
#     0        0         0         1             0      1   (1)
#     0        0         1         0             0      1   (1)
#     0        0         1         1             1      0   (2)

#     0        1         0         0             0      1   (1)
#     0        1         0         1             0      1   (1)
#     0        1         1         0             1      0   (2)
#     0        1         1         1             1      0   (2)

#     1        0         0         0             0      1   (1)
#     1        0         0         1             1      0   (2)
#     1        0         1         0             0      1   (1)
#     1        0         1         1             1      0   (2)

#     1        1         0         0             1      0   (2)
#     1        1         0         1             1      0   (2)
#     1        1         1         0             1      0   (2)
#     1        1         1         1             1      0   (2)

# Boolean Logis solution to the previous Truth Table
# col1_out: CB + AD + AB + CD
# col2_out: A !D !B + !B !D C + D !C !A + !A B !C
def get_max_shifts(shifts):
    A = bool(shifts[0])
    B = bool(shifts[1])
    C = bool(shifts[2])
    D = bool(shifts[3])
    out1 = int(C & B | A & D | A & B | C & D)
    out2 = int(A & (~D) & (~B) | (~B) & (~D) & C | D & (~C) & (~A) | (~A) & B & (~C))

    # convert to decimal
    max_shift = out1 * 2**1 + out2 * 2**0

    return max_shift