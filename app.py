# app.py (Backend)

from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database initialization
def initialize_database():
    conn = sqlite3.connect('tiffin_service.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS dishes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    dish_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (dish_id) REFERENCES dishes(id)
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    dish_id INTEGER,
                    rating INTEGER,
                    comment TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (dish_id) REFERENCES dishes(id)
                )''')
    conn.commit()
    conn.close()

initialize_database()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('tiffin_service.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            return redirect('/menu')
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

@app.route('/menu')
def menu():
    if 'user_id' not in session:
        return redirect('/login')
    conn = sqlite3.connect('tiffin_service.db')
    c = conn.cursor()
    c.execute('SELECT * FROM dishes')
    dishes = c.fetchall()
    conn.close()
    return render_template('menu.html', dishes=dishes)

@app.route('/order/<int:dish_id>', methods=['POST'])
def order(dish_id):
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    conn = sqlite3.connect('tiffin_service.db')
    c = conn.cursor()
    c.execute('INSERT INTO orders (user_id, dish_id) VALUES (?, ?)', (user_id, dish_id))
    conn.commit()
    conn.close()
    return redirect('/menu')

@app.route('/review/<int:dish_id>', methods=['POST'])
def review(dish_id):
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    rating = int(request.form['rating'])
    comment = request.form['comment']
    conn = sqlite3.connect('tiffin_service.db')
    c = conn.cursor()
    c.execute('INSERT INTO reviews (user_id, dish_id, rating, comment) VALUES (?, ?, ?, ?)',
              (user_id, dish_id, rating, comment))
    conn.commit()
    conn.close()
    return redirect('/menu')

if __name__ == '__main__':
    app.run(debug=True)
