import MySQLdb

def connection():
    conn = MySQLdb.connect(host="localhost",
                           user = "root",
                           passwd = "ADMIN",
                           db = "student_attendance")
    c = conn.cursor()
    return c, conn


# @app.route('/success', methods=['GET'])
# def success():
#     # Construct the table name dynamically
#     table_name = f'form_{form_details.subject}_{form_details.year}_{form_details.branch}_{form_details.division}_{lecture}_{formatted_lecture_time}_{form_details.duration}'

#     # Query the MySQL table to get attendance details
#     cursor = mysql.connection.cursor()
#     cursor.execute(f'SELECT * FROM {table_name}')
#     attendance_details = cursor.fetchall()
#     cursor.close()

#     # Pass attendance details to the template
#     return render_template('success.html', attendance_details=attendance_details)