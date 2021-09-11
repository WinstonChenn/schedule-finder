from ScheduleInputProcessor import ScheduleInputProcessor

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
breakpoint()
