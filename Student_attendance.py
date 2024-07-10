from connection import connection

def update_attendance(table_name, lecture_id, present_roll_numbers):
    c, conn = connection()
    try:
        # Retrieve all roll numbers of students belonging to the specified year, branch, and division
        c.execute(f"SELECT roll_no FROM {table_name}")
        all_roll_numbers = [row[0] for row in c.fetchall()]

        # Add the new column 'lecture_id' to the table
        c.execute(f"ALTER TABLE {table_name} ADD COLUMN {lecture_id} INT")

        # Iterate over all roll numbers and update the 'lec_id' column based on attendance
        for roll_number in all_roll_numbers:
            if roll_number in present_roll_numbers:
                c.execute(f"UPDATE {table_name} SET {lecture_id} = 1 WHERE roll_no = %s", (roll_number,))
            else:
                c.execute(f"UPDATE {table_name} SET {lecture_id} = 0 WHERE roll_no = %s", (roll_number,))
        
        conn.commit()
        print("Attendance updated successfully")
    except Exception as e:
        print("Error updating attendance:", e)
        conn.rollback()
    conn.close()
