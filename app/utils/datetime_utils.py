from datetime import datetime


def combine_date_time(date_value, time_value):
    return datetime.combine(date_value, time_value)
