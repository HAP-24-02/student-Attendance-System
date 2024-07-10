# roll_no, name, division, contact, email, username, password, year, branch

class StudentDetails:
    def __init__(self, student):
        self.roll_no = student.roll_no
        self.name = student.name
        self.division = student.division
        self.contact = student.contact
        self.email = student.email
        self.year = student.year
        self.branch = student.branch

       