# models/future_lec.py
from init import db

class PastLectures(db.Model):
    lec_id = db.Column(db.String(20), primary_key=True)
    teacher_id = db.Column(db.String(20), db.ForeignKey('teacher.id'))
    subject = db.Column(db.String(50))
    lecture_date = db.Column(db.Date)
    year = db.Column(db.Integer, nullable = False)
    branch = db.Column(db.String(50), nullable = False )
    start_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    hall_number = db.Column(db.Integer, nullable=False)
    division = db.Column(db.String(20))