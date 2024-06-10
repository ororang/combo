import sqlite3

connection = sqlite3.connect('database.db')

with connection:
    connection.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    connection.execute("INSERT INTO users (username, password) VALUES ('admin', 'ororang')")
    connection.execute("INSERT INTO users (username, password) VALUES ('user1', 'password2')")
    connection.execute("INSERT INTO users (username, password) VALUES ('user2', 'password3')")

connection.close()
