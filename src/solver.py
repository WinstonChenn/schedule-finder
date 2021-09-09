from ortools.sat.python import cp_model
from SchedulePrinter import SchedulePrinter
import numpy as np
import datetime
from ScheduleInputProcessor import ScheduleInputProcessor
from AdvacedSchedulePrinter import AdvancedSchedulePrinter


# given the binary setting for 4 shifts, solve maximum 
# number of shifts one staff can have that day

# Each person works at most shifts_per_day, shifts per day.
    # TODO: all multiple shift per day cases
    # shift1(A) shift2(B) shift3(C) shift4(D)  max_shift_per_day_per_person
    #     0        0         0         0             0      0
    #     0        0         0         1             0      1
    #     0        0         1         0             0      1
    #     0        0         1         1             1      0

    #     0        1         0         0             0      1
    #     0        1         0         1             0      1
    #     0        1         1         0             1      0
    #     0        1         1         1             1      0

    #     1        0         0         0             0      1
    #     1        0         0         1             1      0
    #     1        0         1         0             0      1
    #     1        0         1         1             1      0

    #     1        1         0         0             1      0
    #     1        1         0         1             1      0
    #     1        1         1         0             1      0
    #     1        1         1         1             1      0

    # col1_out: CB + AD + AB + CD
    # col2_out: A !D !B + !B !D C + D !C !A + !A B !C
def get_max_shifts(shifts):
    # col1_out: CB + AD + AB + CD
    # col2_out: A !D !B + !B !D C + D !C !A + !A B !C
    A = bool(shifts[0]); B = bool(shifts[1]); C = bool(shifts[2]); D = bool(shifts[3])
    out1 = int(C & B | A & D | A & B | C & D)
    out2 = int(A & (~D) & (~B) | (~B) & (~D) & C | D & (~C) & (~A) | (~A) & B & (~C))
    # convert to decimal
    max_shift = out1 * 2**1 + out2 * 2**0

    return max_shift
    

def solve_schedule(preference_matrix, shift_matrix, num_people, num_shifts, num_days):
    peop_range = range(num_people)
    day_range = range(num_days)
    shift_range = range(num_shifts)
    total_shifts = 0

    # pref_matrix should go [people][days][shifts]
    if(not preference_matrix.shape == (num_people, num_days, num_shifts)):
        print("ERROR: Preference Matrix is incorrectly shaped.")
        return None

    # setup all variables
    model = cp_model.CpModel()
    shifts = {}
    for p in peop_range:
        for d in day_range:
            for s in shift_range:
                valid = bool(shift_matrix[d, s])
                if valid:
                    total_shifts += 1
                shifts[(p, d, s)] = model.NewBoolVar('shift_p%id%is%i' % (p, d, s))

    total_shifts = total_shifts // num_people
    print(total_shifts)
    # Each shift has people_per_shift people.
    people_per_shift = 1
    for d in day_range:
        for s in shift_range:
            valid = bool(shift_matrix[d, s])
            if valid:
                model.Add(sum(shifts[(p, d, s)] for p in peop_range) == people_per_shift)
            else:
                model.Add(sum(shifts[(p, d, s)] for p in peop_range) == 0)

    # Each person works at most shifts_per_day, shifts per day.
    # TODO: all multiple shift per day cases
    # shift1(A) shift2(B) shift3(C) shift4(D)  max_shift_per_day_per_person
    #     0        0         0         0             0      0
    #     0        0         0         1             0      1
    #     0        0         1         0             0      1
    #     0        0         1         1             1      0

    #     0        1         0         0             0      1
    #     0        1         0         1             0      1
    #     0        1         1         0             1      0
    #     0        1         1         1             1      0

    #     1        0         0         0             0      1
    #     1        0         0         1             1      0
    #     1        0         1         0             0      1
    #     1        0         1         1             1      0

    #     1        1         0         0             1      0
    #     1        1         0         1             1      0
    #     1        1         1         0             1      0
    #     1        1         1         1             1      0

    # col1_out: CB + AD + AB + CD
    # col2_out: A !D !B + !B !D C + D !C !A + !A B !C

    for p in peop_range:
        for d in day_range:
            shifts_per_day = get_max_shifts(shift_matrix[d])
            shift_array = []
            for s in shift_range:
                valid = bool(shift_matrix[d, s])
                if valid:
                    shift_array.append(shifts[(p, d, s)])
            if (bool(shift_matrix[d, 0]) and bool(shift_matrix[d, 2])):
                model.Add(sum([shifts[(p, d, 0)], shifts[(p, d, 2)]]) <= 1)
            if (bool(shift_matrix[d, 1]) and bool(shift_matrix[d, 3])):
                model.Add(sum([shifts[(p, d, 1)], shifts[(p, d, 3)]]) <= 1)
            model.Add(sum(shift_array) <= shifts_per_day)

    # Try to distribute the shifts evenly, so that each nurse works
    # min_shifts_per_nurse shifts. If this is not possible, because the total
    # number of shifts is not divisible by the number of nurses, some nurses will
    # be assigned one more shift.
    min_shifts_per_person = total_shifts // num_people
    if total_shifts % num_people == 0:
        max_shifts_per_person = min_shifts_per_person
    else:
        max_shifts_per_person = min_shifts_per_person + 1

    # find solutions that make sure each person works the appropriate
    # amount of equally distributed shifts
    for p in peop_range:
        num_shifts_worked = 0
        for d in day_range:
            for s in shift_range:
                valid = bool(shift_matrix[d, s])
                if valid:
                    num_shifts_worked += shifts[(p, d, s)]
        model.Add(min_shifts_per_person <= num_shifts_worked)
        model.Add(num_shifts_worked <= max_shifts_per_person)
 
    bool_array = []
    for p in peop_range:
        for d in day_range:
            for s in shift_range:
                valid = bool(shift_matrix[d, s])
                if valid:
                    bool_array.append(int(preference_matrix[p][d][s]) * shifts[(p, d, s)])
    # accomondate request
    model.Maximize(sum(bool_array))
    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    solver.Solve(model)
   
    print(solver.StatusName())

    if (solver.StatusName() != "INFEASIBLE"):
        for d in day_range:
            print('Day', d)
            for p in peop_range:
                for s in shift_range:
                    valid = bool(shift_matrix[d, s])
                    if valid:
                        if solver.Value(shifts[(p, d, s)]) == 1:
                            if preference_matrix[p][d][s] >= 1:
                                print('Staff', p, 'works shift', s, '(requested).')
                            else:
                                print('Staff', p, 'works shift', s, '(not requested).')
    
            print()

        # Statistics.
        print()
        print('Statistics')
        print('  - Number of shift requests met = %i' % solver.ObjectiveValue(),
            '(out of', num_people * min_shifts_per_person, ')')
        print('  - wall time       : %f s' % solver.WallTime())


processor = ScheduleInputProcessor(
    start_date="1/3/21",
    end_date="3/12/21",
    max_shifts=4,
    num_staff=10,
    date_requirement_url="../data/date_requirements.xlsx",
    staff_requirement_url="../data/scaled_staff_req.xlsx",
    holidays=["1/18/21", "2/15/21"]
)

pref_mat = processor.get_preference_matrix()
num_days = (datetime.datetime.strptime("3/12/21", "%m/%d/%y") - datetime.datetime.strptime("1/3/21", "%m/%d/%y")).days + 1
dates, shifts, day_mat = processor.load_day_requirements()

solve_schedule(
    preference_matrix=pref_mat,
    shift_matrix=day_mat,
    num_people=pref_mat.shape[0],
    num_shifts=pref_mat.shape[2],
    num_days=num_days
)
