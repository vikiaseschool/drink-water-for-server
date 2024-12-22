import sqlite3
import random
from datetime import datetime, timedelta

def create_database():
    connection = sqlite3.connect("drink_diary.db")
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drink_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            category TEXT NOT NULL,
            amount INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    ''')

    connection.commit()
    connection.close()
    print("Databáze byla vytvořena úspěšně.")

def create_demo_user():
    connection = sqlite3.connect("drink_diary.db")
    cursor = connection.cursor()

    username = 'demo'
    password = '1234'

    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)
    ''', (username, password))

    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    user_id = cursor.fetchone()[0]

    categories = ['Water', 'Soda', 'Alcoholic beverages', 'Caffeinated beverages']
    start_date = datetime.now() - timedelta(days=365)

    for i in range(365):
        current_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        for category in categories:
            if category == 'Water' or category == 'Soda':
                amount = random.randint(200, 1000)
            elif category == 'Alcoholic beverages':
                amount = random.randint(40, 400)
            else:
                amount = random.randint(50, 500)
            cursor.execute('''
                INSERT INTO drink_entries (user_id, date, category, amount) 
                VALUES (?, ?, ?, ?)
            ''', (user_id, current_date, category, amount))

    connection.commit()
    connection.close()
    print("Demo uživatel a záznamy byly vytvořeny.")

if __name__ == "__main__":
    create_database()
    create_demo_user()
