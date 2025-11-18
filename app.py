from flask import Flask, render_template, request, redirect, url_for, flash
from database import Database
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

db = Database()

# Initialize database
db.create_database_and_tables()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        course = request.form['course']
        year = request.form['year']
        
        # Validation
        if not all([student_id, name, email, course, year]):
            flash('Please fill all required fields!', 'error')
            return render_template('add_student.html')
        
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Please enter a valid email address!', 'error')
            return render_template('add_student.html')
        
        # Insert student
        query = """
            INSERT INTO students (student_id, name, email, phone, course, year)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (student_id, name, email, phone, course, year)
        
        result = db.execute_query(query, params)
        if result:
            flash('Student added successfully!', 'success')
            return redirect(url_for('view_students'))
        else:
            flash('Error adding student. Student ID or Email might already exist.', 'error')
    
    return render_template('add_student.html')

@app.route('/view_students')
def view_students():
    query = "SELECT * FROM students ORDER BY created_at DESC"
    students = db.execute_query(query)
    return render_template('view_students.html', students=students)

@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        course = request.form['course']
        year = request.form['year']
        
        # Validation
        if not all([name, email, course, year]):
            flash('Please fill all required fields!', 'error')
            return redirect(url_for('edit_student', student_id=student_id))
        
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Please enter a valid email address!', 'error')
            return redirect(url_for('edit_student', student_id=student_id))
        
        # Update student
        query = """
            UPDATE students 
            SET name = %s, email = %s, phone = %s, course = %s, year = %s
            WHERE id = %s
        """
        params = (name, email, phone, course, year, student_id)
        
        result = db.execute_query(query, params)
        if result:
            flash('Student updated successfully!', 'success')
        else:
            flash('Error updating student.', 'error')
        
        return redirect(url_for('view_students'))
    
    # Get student data for editing
    query = "SELECT * FROM students WHERE id = %s"
    student = db.execute_query(query, (student_id,))
    if student:
        return render_template('edit_student.html', student=student[0])
    else:
        flash('Student not found!', 'error')
        return redirect(url_for('view_students'))

@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    query = "DELETE FROM students WHERE id = %s"
    result = db.execute_query(query, (student_id,))
    
    if result:
        flash('Student deleted successfully!', 'success')
    else:
        flash('Error deleting student.', 'error')
    
    return redirect(url_for('view_students'))

@app.route('/search_students', methods=['GET'])
def search_students():
    search_term = request.args.get('search', '')
    query = """
        SELECT * FROM students 
        WHERE name LIKE %s OR student_id LIKE %s OR email LIKE %s OR course LIKE %s
        ORDER BY created_at DESC
    """
    search_pattern = f"%{search_term}%"
    students = db.execute_query(query, (search_pattern, search_pattern, search_pattern, search_pattern))
    return render_template('view_students.html', students=students, search_term=search_term)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    