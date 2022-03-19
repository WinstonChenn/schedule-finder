python schedule_matrix.py \
    --data_dir "../data" \
    --data_name "elm_spring_2022" \
    --date_format "%m/%d/%y" \
    --start_date "3/27/22" \
    --end_date "6/2/22" \
    --max_num_shifts 2 \
    --shifts_names "Primary" "Secondary" \
    --weekday_num_shifts 2 \
    --weekend_num_shifts 2 \
    --special_weekends "5/30/22"
    # --special_weekdays "1/2/22" \
    # --overwrite
