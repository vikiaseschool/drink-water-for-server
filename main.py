from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = 'axdsd'

def get_db_connection():
    conn = sqlite3.connect("drink_diary.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            flash("Incorrect username or password.", "error")

        conn.close()

    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user:
            flash("User already exists!", "error")
        else:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash("Registration successful!", "success")
            return redirect(url_for("login"))

        conn.close()

    return redirect(url_for("index"))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            flash("Špatné uživatelské jméno nebo heslo.", "error")

        conn.close()

    return render_template("index.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    if request.method == "POST":
        category = request.form["category"]
        amount = request.form["amount"]

        add_drink_entry(user_id, category, amount)

    daily_data = get_drink_data(user_id, 'day')
    weekly_data = get_drink_data(user_id, 'week')
    monthly_data = get_drink_data(user_id, 'month')
    yearly_data = get_drink_data(user_id, 'year')

    return render_template("dashboard.html", daily_data=daily_data, weekly_data=weekly_data,
                           monthly_data=monthly_data, yearly_data=yearly_data)

def get_drink_data(user_id, period):
    connection = sqlite3.connect("drink_diary.db")
    cursor = connection.cursor()

    if period == 'day':
        cursor.execute("""
            SELECT category, 
                   SUM(amount) 
            FROM drink_entries 
            WHERE user_id = ? AND date(date) = date('now') 
            GROUP BY category
        """, (user_id,))
    elif period == 'week':
        cursor.execute("""
            SELECT category, 
                   SUM(amount) 
            FROM drink_entries 
            WHERE user_id = ? AND strftime('%W', date) = strftime('%W', 'now') 
            GROUP BY category
        """, (user_id,))
    elif period == 'month':
        cursor.execute("""
            SELECT category, 
                   SUM(amount) 
            FROM drink_entries 
            WHERE user_id = ? AND strftime('%m', date) = strftime('%m', 'now') 
            GROUP BY category
        """, (user_id,))
    elif period == 'year':
        cursor.execute("""
            SELECT category, 
                   SUM(amount) 
            FROM drink_entries 
            WHERE user_id = ? AND strftime('%Y', date) = strftime('%Y', 'now') 
            GROUP BY category
        """, (user_id,))

    data = cursor.fetchall()

    updated_data = []
    for category, total in data:
        if total < 0:
            updated_data.append((category, 0))
            cursor.execute("""
                UPDATE drink_entries
                SET amount = 0
                WHERE user_id = ? AND category = ?
            """, (user_id, category))
        else:
            updated_data.append((category, total))

    connection.commit()
    connection.close()

    return updated_data

def add_drink_entry(user_id, category, amount):
    conn = get_db_connection()
    cursor = conn.cursor()
    today = date.today()
    amount = int(round(float(amount)))

    cursor.execute('''INSERT INTO drink_entries (user_id, date, category, amount)
                      VALUES (?, ?, ?, ?)''', (user_id, today, category, amount))
    conn.commit()

    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True,  host="0.0.0.0", port=8871)
