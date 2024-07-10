
class FormDetails:
    def __init__(self,lecture_id,teacher_id, subject, lecture_date_str, year, branch,division, start_time_str, duration, hall_number):
        self.lecture_id = lecture_id
        self.teacher_id = teacher_id
        self.subject = subject
        self.lecture_date_str = lecture_date_str
        self.year = year
        self.branch = branch
        self.division = division
        self.start_time_str = start_time_str
        self.duration = duration
        self.hall_number = hall_number
    
    def to_dict(self):
        return {
            'lecture_id' : self.lecture_id,
            'teacher_id': self.teacher_id,
            'subject': self.subject,
            'lecture_date_str': self.lecture_date_str,
            'year': self.year,
            'branch': self.branch,
            'division' : self.division,
            'start_time_str': self.start_time_str,
            'duration': self.duration,
            'hall_number': self.hall_number
        }