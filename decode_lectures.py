# Example of decoding the unique name
def decode_lecture_details(column_name):
    parts = column_name.split('_')
    subject = parts[0]
    lecture_date_str = parts[1].replace("$", "-")
    formatted_lecture_time = parts[2].replace("$", ":")
    duration = parts[3]
    return {
        'subject': subject,
        'lecture_date_str': lecture_date_str,
        'formatted_lecture_time': formatted_lecture_time,
        'duration': duration
    }