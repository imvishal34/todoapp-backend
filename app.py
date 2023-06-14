from flask import Flask, render_template, redirect, request, session, flash
from flask_mysqldb import MySQL
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME,JWT_SECRET_KEY

app = Flask(__name__)


# MySQL Configuration
app.config['MYSQL_HOST'] = DB_HOST
app.config['MYSQL_USER'] = DB_USER
app.config['MYSQL_PASSWORD'] = DB_PASSWORD
app.config['MYSQL_DB'] = DB_NAME
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY

mysql = MySQL(app)

# User registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        mysql.connection.commit()
        cur.close()

        flash('Registration Successful! Please login.')
        return redirect('/login')

    return render_template('register.html')

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect('/')
        else:
            flash('Invalid email or password')
            return redirect('/login')

    return render_template('login.html')

# User logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# Create task
@app.route('/create_task', methods=['POST'])
def create_task():
    if 'user_id' not in session:
        return redirect('/login')

    task_name = request.form['task_name']
    due_date = request.form['due_date']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO tasks (user_id, task_name, due_date) VALUES (%s, %s, %s)", (session['user_id'], task_name, due_date))
    mysql.connection.commit()
    cur.close()

    flash('Task created successfully')
    return redirect('/')

# Update task
@app.route('/update_task/<int:task_id>', methods=['POST'])
def update_task(task_id):
    if 'user_id' not in session:
        return redirect('/login')

    task_name = request.form['task_name']
    due_date = request.form['due_date']

    cur = mysql.connection.cursor()
    cur.execute("UPDATE tasks SET task_name = %s, due_date = %s WHERE id = %s AND user_id = %s", (task_name, due_date, task_id, session['user_id']))
    mysql.connection.commit()
    cur.close()

    flash('Task updated successfully')
    return redirect('/')

# Delete task
@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s AND user_id = %s", (task_id, session['user_id']))
    mysql.connection.commit()
    cur.close()

    flash('Task deleted successfully')
    return redirect('/')

# Mark task as completed
@app.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    if 'user_id' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()
    cur.execute("UPDATE tasks SET completed = 1 WHERE id = %s AND user_id = %s", (task_id, session['user_id']))
    mysql.connection.commit()
    cur.close()

    flash('Task completed')
    return redirect('/')

# Send email notification for tasks with alarms
def send_email_notification(task_id, task_name, user_email, alarm_date):
    # Configure and send email using smtplib or a library like Flask-Mail

    msg = MIMEMultipart()
    msg['From'] = 'your_email@example.com'
    msg['To'] = user_email
    msg['Subject'] = 'Task Alarm: ' + task_name

    message = 'This is a reminder for your task: ' + task_name
    msg.attach(MIMEText(message))

    # Add code to send the email using your email provider

# Check for task alarms
def check_task_alarms():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tasks WHERE due_date <= NOW() AND alarm_set = 1 AND alarm_sent = 0")
    tasks = cur.fetchall()
    cur.close()

    for task in tasks:
        task_id = task['id']
        task_name = task['task_name']
        user_email = task['user_email']
        alarm_date = task['due_date']

        send_email_notification(task_id, task_name, user_email, alarm_date)

        cur = mysql.connection.cursor()
        cur.execute("UPDATE tasks SET alarm_sent = 1 WHERE id = %s", (task_id,))
        mysql.connection.commit()
        cur.close()

# Home page
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tasks WHERE user_id = %s", (session['user_id'],))
    tasks = cur.fetchall()
    cur.close()

    check_task_alarms()

    return render_template('index.html', tasks=tasks)

if __name__ == '__main__':
    app.run(debug=True)
