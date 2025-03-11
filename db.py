import sqlite3

conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    age INTEGER
)
''')

conn.commit()
conn.close()