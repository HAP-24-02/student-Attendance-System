from init import db

class Student(db.Model):
    roll_no = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    division = db.Column(db.String(10), nullable=False)
    contact = db.Column(db.String(15))
    email = db.Column(db.String(50))
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    branch = db.Column(db.String(50), nullable = False )