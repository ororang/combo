from flask import Flask, request, render_template, g
import sqlite3
import re

app = Flask(__name__)

DATABASE = 'database.db'
XOR_KEY = 'park'  # 비밀번호 암호화에 사용할 키

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

def xor_encrypt_decrypt(input_string, key):
    key = key * (len(input_string) // len(key)) + key[:len(input_string) % len(key)]
    return ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(input_string, key))

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = sanitize_input(request.form['username'])
        password = sanitize_input(request.form['password'])
        encrypted_password = xor_encrypt_decrypt(password, XOR_KEY)
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, encrypted_password))
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
        encrypted_password = xor_encrypt_decrypt(password, XOR_KEY)
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, encrypted_password))
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
        cursor.execute("SELECT * FROM users WHERE username LIKE ?", (f'%{query}%',))
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
