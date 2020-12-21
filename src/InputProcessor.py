# input requirements
# 1. Starting Date, Ending Date (All inclusive) [CLI]
# 2. max #shifts per day [CLI]
# 3. Number of staffs [CLI]

# 4. each days requirements (#shifts, holiday) 
# [tablar data, col1: date, col2: shift1 (y/n), col3: shift2(y/n), col4: shift3(y/n), col5: shift4(y/n), col6: hoiday (y/n))]

# 5. Each staff requirements (scale: -2 - 2) [tabular data, row: each staff, col [i, ii, iii, ix]]
# -2: not real shift, -1: can't work 0: neutral 1: ok 2: want
#   i: preference on weekdays weekdays (Sunday - Thursday) [5 columnb]
#   ii: preference on weekends (pre-generate a list of weekends based on start/end date) [#weekends columns]
#   iii: prefernce on holidays[#holidays columns]
#   ix. longest shift streak [1 column]


# output
# prefernce matrix
# number of staffs * number of days * max #shifts per day

# constrain: 
# For all real shifts (sometimes more than 1 real shift perday), at least staff put non-negative prefernce


