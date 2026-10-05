def has_overlap(new_start, new_end, existing_start, existing_end):
    return new_start < existing_end and new_end > existing_start
