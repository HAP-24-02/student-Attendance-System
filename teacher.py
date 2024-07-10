from init import db

class Teacher(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(15))
    email = db.Column(db.String(50))
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    Address = db.Column(db.String(100), nullable = False )