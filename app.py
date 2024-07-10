from datetime import date, datetime
import time
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from connection import connection
from decode_lectures import decode_lecture_details
from studDetails import StudentDetails
from teacher import Teacher
from init import db
from tedetails import TeacherDetails
from future_lec import FutureLec
from student import Student
from lecture_details import FormDetails
from flask_mysqldb import MySQL
# from MySQLdb import escape_string 
from Student_attendance import update_attendance
from verify_response import reorder_response
from form_response import get_forms_service_response
from google_form import google_form
from lecture_details import FormDetails
import openpyxl
from past_lecture import PastLectures

app = Flask(__name__)
app.config['SECRET_KEY'] = 'python'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:ADMIN@localhost:3306/student_attendance'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'ADMIN'
app.config['MYSQL_DB'] = 'student_attendance'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('clghome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        teacher_login = Teacher.query.filter_by(username=username, password=password).first()

        if teacher_login:
            # For simplicity, just set a session variable indicating the user is logged in
            session['teacher_id'] = teacher_login.id
            return redirect(url_for('teho'))
        else:
            return render_template('telo.html', error='Invalid username or password')

    return render_template('telo.html')


@app.route('/teho')
def teho():
    c,conn = connection()
    c.execute('DELETE FROM future_lec WHERE lecture_date < CURDATE()')
    c.execute('DELETE FROM future_lec WHERE lecture_date = CURDATE() AND start_time < CURTIME()')
    conn.commit()
    conn.close()
    teacher_id = session.get('teacher_id')

    if teacher_id:
        teacher = Teacher.query.get(teacher_id)

        if teacher:
            # Create an instance of TeacherDetails
            teacher_details = TeacherDetails(teacher)
            upcoming_lectures = FutureLec.query.filter_by(teacher_id=teacher_id).all()
            past_lecture = PastLectures.query.filter_by(teacher_id = teacher_id).all()
            print(past_lecture)
            # Pass the instance to the template
            return render_template('teho.html', teacher_details=teacher_details, upcoming_lectures=upcoming_lectures , past_lecture = past_lecture)
        else:
            return render_template('error.html', message='Teacher not found')
    else:
        return redirect(url_for('login'))


@app.route('/login_student', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Student.query.filter_by(username=username, password=password).first()

        if user:
            # For simplicity, just set a session variable indicating the user is logged in
            session['student_roll_no'] = user.roll_no
            return redirect(url_for('stho'))
        else:
            return render_template('stlo.html', error='Invalid username or password')

    return render_template('stlo.html')

@app.route('/stho')
def stho():
    student_id = session.get('student_roll_no')
    c, conn = connection()
    if student_id:
        student = Student.query.get(student_id)

        if student:
            student_details = StudentDetails(student) 
            # Extract student details
            roll_no = student.roll_no
            branch = student.branch
            year = student.year
            division = student.division
            # Fetch attendance data for the student from the corresponding table
            attendance_table_name = f'{branch}_{year}_{division}'
            # Construct the SQL query to retrieve attendance data for the student
            sql_query = f"SELECT * FROM {attendance_table_name} WHERE roll_no = %s LIMIT 1"


            # Execute the SQL query
            c.execute(sql_query, (roll_no,))

            
                # Fetch the first row (if any)
            attendance_data = c.fetchone()
            column_names = [desc[0] for desc in c.description]
            conn.close()
            if not attendance_data:
                return render_template('error.html', message='Attendance data not found for the student')

            # Extracting roll number and attendance status from the tuple
            roll_no_det = attendance_data[0]
            attendance_statuses = attendance_data
            print(attendance_data)
            print(column_names)
            print(roll_no_det)
            print(attendance_statuses)
            # Extract lecture details from the attendance data and decode them
            formatted_lectures = []
            for column_name, attendance_status in zip(column_names, attendance_statuses):
                print(column_name)
                print(attendance_status)
                if column_name == 'roll_no':
                    continue  # Skip the 'roll_no' column

                # Decode the lecture details using the column name
                lecture_details = decode_lecture_details(column_name)
                lecture_subject = lecture_details['subject']
                lecture_date = lecture_details['lecture_date_str']
                lecture_start_time = lecture_details['formatted_lecture_time']
                lecture_duration = lecture_details['duration']

                # Determine attendance status
                attendance = "Present" if attendance_status == 1 else "Absent"

                # Creating formatted lecture details for each lecture
                formatted_lecture_details = {
                    'lecture_subject': lecture_subject,
                    'lecture_date': lecture_date,
                    'lecture_start_time': lecture_start_time,
                    'lecture_duration': f"{lecture_duration} hours",
                    'attendance_status': attendance
                }

                # Adding formatted lecture details to the list
                formatted_lectures.append(formatted_lecture_details)

            print(formatted_lectures)

            return render_template('stho.html', student=student_details, lectures=formatted_lectures)
        else:
            return render_template('error.html', message='Student Not Found')
    else:
        return redirect(url_for('stlo'))


@app.route('/index1')
def index1():
    return render_template('index.html')


@app.route('/success', methods=['GET'])
def success():
    form_details_dict = session['form_details']
    form_details = FormDetails(**form_details_dict) 
    formatted_lecture_time = form_details.start_time_str.replace(":", "$")
    lecture = form_details.lecture_date_str.replace("-" , "$")
    # Construct the table name dynamically
    table_name = f'form_{form_details.subject}_{form_details.year}_{form_details.branch}_{form_details.division}_{lecture}_{formatted_lecture_time}_{form_details.duration}'
    
    lec_id = session.get('lec_id')
    # Move the lecture to past lectures table
    c, conn = connection()
    c.execute(f'SELECT * FROM future_lec WHERE lec_id = %s', (lec_id,))
    lecture_row = c.fetchone()
    c.execute('INSERT INTO past_lectures (lec_id, teacher_id, subject, lecture_date, year, branch, start_time, duration, hall_number, division) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
              (lecture_row[0], lecture_row[1], lecture_row[2], lecture_row[3], lecture_row[4], lecture_row[5], lecture_row[6], lecture_row[7], lecture_row[8], lecture_row[9]))
    c.execute('DELETE FROM future_lec WHERE lec_id = %s', (lec_id,))
    conn.commit()
    conn.close()
    
    # Query the MySQL table to get attendance details
    c, conn = connection()
    c.execute(f'SELECT * FROM {table_name}')
    attendance_details = c.fetchall()
    conn.close()
    
    # Pass attendance details to the template
    return render_template('success.html', attendance_details=attendance_details, form_details=form_details)


@app.route('/past_details',methods=['GET','POST'])
def past_details():
    teacher_id = session.get('teacher_id')
    past_lecture = PastLectures.query.filter_by(teacher_id = teacher_id).all()
    return render_template('past_lectures.html',past_lecture = past_lecture)


@app.route('/past_details_specific',methods=['GET','POST'])
def past_details_specific():
    c,conn = connection()
    # teacher_id = session.get('teacher_id')
    lec_id = request.form.get('lec_id')
    # session['lec_id_past'] = lec_id
    # Retrieve lecture details from database based on lecture_id
    lecture_details = PastLectures.query.get(lec_id)
    today = date.today()
    # print(lecture_details)
    formatted_lecture_time = str(lecture_details.start_time).replace(":", "$")
    lecture = str(lecture_details.lecture_date).replace("-" , "$")
    table_name = f'form_{lecture_details.subject}_{lecture_details.year}_{lecture_details.branch}_{lecture_details.division}_{lecture}_{formatted_lecture_time}_{lecture_details.duration}'
    print(table_name)
    # form_eg_2_comp_a_2024$04$17_15$00$00_2
    c.execute(f'SELECT * FROM {table_name}')
    attendance_details = c.fetchall()
    print(type(attendance_details))
    conn.close()
    if lecture_details and attendance_details:
        return render_template('lec_details_specific.html', lecture_details=lecture_details, today = today, attendance_details = attendance_details)
    else:
        return "Lecture details not found or mismatched lecture ID"

@app.route('/add_lecture', methods=['GET','POST'])
def add_lecture():
    success_message = None
    error_message = None

    try:
        subject = request.form['subject']
        lecture_date_str = request.form['lectureDate']
        year = int(request.form['year'])
        branch = request.form['branch']
        start_time_str = request.form['start_time']
        duration = int(request.form['duration'])
        hall_number = int(request.form['hall_number'])
        division = request.form['division']

        # Convert string date and time to datetime objects
        lecture_date = datetime.strptime(lecture_date_str, "%Y-%m-%d").date()
        start_time = datetime.strptime(start_time_str, "%H:%M").time()

        # Get the current teacher's ID from the session
        teacher_id = session.get('teacher_id')

        # Generate lec_id based on your criteria
        hours, minutes = start_time_str.split(":")
        lec_id = lecture_date.strftime("%d-%m-%Y") + f'_{teacher_id}_{hours}-{minutes}_{subject}'

        # Create a new FutureLec entry
        new_lecture = FutureLec(
            lec_id=lec_id,
            teacher_id=teacher_id,
            subject=subject,
            lecture_date=lecture_date,
            year=year,
            branch=branch,
            start_time=start_time,
            duration=duration,
            hall_number=hall_number,
            division = division
        )

        # Add and commit the new entry to the database
        db.session.add(new_lecture)
        db.session.commit()

        success_message = "Lecture added successfully!"
        return render_template('LectureAdd.html', success_message=success_message)

    except Exception as e:
        print(f"Error: {str(e)}")
        db.session.rollback()
        error_message = f"Failed to add lecture. Error: {str(e)}. Please try again."
        return render_template('LectureAdd.html', error_message=error_message)


def get_lecture_details(lecture_id):
    # Assuming db is your SQLAlchemy session and Lecture is your SQLAlchemy model representing lectures Teacher.query.get(teacher_id)
    lecture = FutureLec.query.get(lecture_id)

    if lecture:
        print(lecture)
        return lecture
    else:
        return None

#lec_id store procedure
@app.route('/store_lecture_details', methods=['GET', 'POST'])
def store_lecture_details():
    lec_id = request.form.get('lec_id')
    session['lec_id'] = lec_id
    # Retrieve lecture details from database based on lecture_id
    lecture_details = get_lecture_details(lec_id)
    today = date.today()
    if lecture_details:
        return render_template('lec_details.html', lecture_details=lecture_details,today = today)
    else:
        return "Lecture details not found or mismatched lecture ID"

#Previous to return page
@app.route('/return_to_previous_page', methods=['POST'])
def return_to_previous_page():
    previous_url = request.form['previous_url']
    return redirect(previous_url)

def construct_google_form_url(form_id):
    return f"https://docs.google.com/forms/d/{form_id}/edit#settings"

@app.route('/submit_form', methods=['POST'])
def submit_form():
    # Get lecture details from URL parameters
    lecture_id = request.args.get('lecture_id')
    teacher_id = request.args.get('teacher_id')
    lecture_date = request.args.get('lecture_date')
    subject = request.args.get('subject')
    start_time = request.args.get('start_time')
    year = request.args.get('year')
    branch = request.args.get('branch')
    duration = request.args.get('duration')
    hall_number = request.args.get('hall_number')
    division = request.args.get('division')

    # Now you have all the lecture details, proceed with your logic
    responder_url,form_id,result = google_form(subject, lecture_date, year, branch, start_time, division)
    form_details = FormDetails(lecture_id,teacher_id,subject, lecture_date, year, branch, division, start_time, duration, hall_number)
    form_details_dict = form_details.to_dict()

    # Constructing the URL of the QR code image
    qr_code_url = url_for('static', filename=f'{subject}_{year}-{branch}.png')

    # Storing form_id and current time
    session['form_id'] = form_id
    session['form_details'] = form_details_dict

    form_url = construct_google_form_url(form_id)

    return render_template('form_submit.html', responder_url=responder_url, qr_code_url=qr_code_url, form_url = form_url)

def create_table(table_name):
    cursor = mysql.connection.cursor()
    cursor.execute(f'CREATE TABLE {table_name} (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), roll_no VARCHAR(50), respondant_email VARCHAR(255), timestamp VARCHAR(50))')
    cursor.connection.commit()
    print("Table created Successfully")

def insert_user(table_name, name, Roll_no, email, timestamp):
    c, conn = connection()
    try:
        c.execute(f"INSERT INTO {table_name} (name, roll_no, respondant_email, timestamp) VALUES (%s, %s, %s, %s)",
                  (name, Roll_no, email, timestamp))
        conn.commit()
        print("User inserted successfully")
    except Exception as e:
        print("Error inserting user:", e)
        conn.rollback()
    conn.close()




@app.route('/spreadsheet_DB', methods=['POST'])
def spreadsheet_DB():
    if session.get('form_id'):
        form_id = session['form_id']
        form_details_dict = session['form_details'] 
        forms_service = get_forms_service_response()
        # Fetch responses from the Google Form
        form_responses = forms_service.forms().responses().list(formId=form_id).execute()
        get_result = forms_service.forms().get(formId=form_id).execute()
        # responder_url = get_result.get('responderUri', '')
        form_details = FormDetails(**form_details_dict)
        if not form_responses:
            return render_template('no_responses.html')  # Handle case with no responses
        
        #creating a excel file
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        
                # Add FormDetails to the worksheet
        form_details_values = [
            form_details.teacher_id,
            form_details.subject,
            form_details.lecture_date_str,
            form_details.year,
            form_details.branch,
            form_details.division,
            form_details.start_time_str,
            form_details.duration,
            form_details.hall_number     
        ]

        worksheet.append(['Form Details'])
        worksheet.append(['Teacher_id','Subject', 'Lecture Date', 'Year', 'Branch','DIvision', 'Start Time', 'Duration', 'Hall Number'])
        worksheet.append(form_details_values)
        worksheet.append([' '])        
        worksheet.append(['ATTENDANCE DETAILS'])
        headers = ['Name', 'Roll_No','Time Stamp','Email']
        worksheet.append(headers)

        formatted_lecture_time = form_details.start_time_str.replace(":", "$")
        lecture = form_details.lecture_date_str.replace("-" , "$")
        # Create a table for the current form dynamically
        table_name = f'form_{form_details.subject}_{form_details.year}_{form_details.branch}_{form_details.division}_{lecture}_{formatted_lecture_time}_{form_details.duration}'
        create_table(table_name)

        arr = []
        for response in form_responses['responses']:
            respondent_email = response['respondentEmail']
            last_submitted_time = response['lastSubmittedTime']
            answers_values = []  # Corrected variable name
            excel_values = []
            for question_id, question_data in response['answers'].items():
                value = question_data['textAnswers']['answers'][0]['value']
                answers_values.append(value)
            answers_values = reorder_response(answers_values)
            arr.append(answers_values[1])
            excel_values = answers_values
            excel_values.append(respondent_email)
            excel_values.append(last_submitted_time)
            insert_user(table_name,answers_values[0],answers_values[1],respondent_email,last_submitted_time)
            #save one response to excel file
            worksheet.append(excel_values)  

        #excel filename 
        filename = f"responses_{form_details.subject}_{form_details.year}-{form_details.branch}_{form_details.division}_{form_details.lecture_date_str}.xlsx"

        # Save the workbook to a local file
        workbook.save(filename)

        table_2 = f"{form_details.branch}_{form_details.year}_{form_details.division}" 
        lecture_id = f"{form_details.subject}_{lecture}_{formatted_lecture_time}_{form_details.duration}" 
        
        #inserting attendance of certain lecture 
        update_attendance(table_2,lecture_id,arr)

            
        return redirect(url_for('success'))
    else:
        return redirect(url_for('index'))



db.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
