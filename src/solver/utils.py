import numpy as np

def get_solution_matrix(solver, shifts, n_days, n_staffs, n_shifts):
    assert len(shifts) == n_days * n_staffs * n_shifts
    solu_mat = np.zeros((n_staffs, n_days, n_shifts))
    for p in range(n_staffs):
        for d in range(n_days):
            for s in range(n_shifts):
                solu_mat[p, d, s] = solver.Value(shifts[p, d, s])
    return solu_mat


def print_staff_shedule_stats(solution_mat, pref_mat, staff_arr, shift_arr):
    assert solution_mat.shape[0] == len(staff_arr)
    assert solution_mat.shape[2] == len(shift_arr)

    want_count = 0
    ok_count = 0
    no_pref_count = 0
    cant_count = 0
    total_count = 0
    staff_shift_arr = [[0 for _ in range(len(shift_arr))] for _ in range(len(staff_arr))]
    for p in range(solution_mat.shape[0]):
        for d in range(solution_mat.shape[1]):
            for s in range(solution_mat.shape[2]):
                if solution_mat[p, d, s] == 1:
                    total_count += 1
                    staff_shift_arr[p][s] += 1
                    if pref_mat[p][d][s] > 1:
                        want_count += 1
                    elif pref_mat[p][d][s] == 1:
                        ok_count += 1
                    elif pref_mat[p][d][s] == 0:
                        no_pref_count += 1
                    elif pref_mat[p][d][s] < 0:
                        cant_count += 1
    print("Staff shift taking statistics: ")
    for p in range(len(staff_arr)):
        print(
            f"{staff_arr[p]}: " + 
            " ".join([
                f"#{shift_arr[s]}={staff_shift_arr[p][s]}" 
                for s in range(len(shift_arr))
            ])
        )
    print(f" - Number of wanted shifts requests met: {want_count}")
    print(f" - Number of OK shifts met: {ok_count}")
    print(f" - Number of no preference shifts met: {no_pref_count}")
    print(f" - Number of cant shifts met: {cant_count}")
    print(f" - Total number of shifts {total_count}")


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