from flask import Flask, request, render_template, g
import sqlite3
import re

app = Flask(__name__)

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def sanitize_input(user_input):
    # Remove forbidden characters and keywords
    forbidden_patterns = [r'"', r"'", r",", r'\bor\b', r'\band\b']
    for pattern in forbidden_patterns:
        user_input = re.sub(pattern, '', user_input, flags=re.IGNORECASE)
    return user_input

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = sanitize_input(request.form['username'])
        password = sanitize_input(request.form['password'])
        
        db = get_db()
        cursor = db.cursor()
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cursor.execute(query)
        user = cursor.fetchone()
        
        if user:
            return "Login successful!"
        else:
            error = "Invalid username or password."

    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = sanitize_input(request.form['username'])
        password = sanitize_input(request.form['password'])
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        db.commit()
        return "Registration successful!"
    return render_template('register.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        query = sanitize_input(request.form['query'])
        
        db = get_db()
        cursor = db.cursor()
        sql_query = "SELECT * FROM users WHERE username LIKE ?"
        cursor.execute(sql_query, (f'%{query}%',))
        results = cursor.fetchall()
    return render_template('search.html', results=results)

@app.route('/login', methods=['GET'])
def show_login():
    return render_template('login.html')

@app.route('/register', methods=['GET'])
def show_register():
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
