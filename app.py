from flask import Flask, render_template, request, redirect, url_for, session, jsonify,session
from flask_session import Session
import sqlite3
from flask_login import LoginManager
from flask_socketio import SocketIO, emit
import re
import Levenshtein
import json


regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'  

def validEMail(email):   

    if(re.search(regex,email)):   
        return True
    else:   
        return False




app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = 'j8x91nB5y3qoCtVuK2lHgmp4d'
app.config['SESSION_TYPE'] = 'filesystem'


# Connect to database
conn = sqlite3.connect('database.db')
print("Database opened successfully")
mess = sqlite3.connect('messages.db')
print("Database opened successfully")

# Create users table
conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT, email TEXT, msgssent TEXT, followers TEXT)')
print("Table created successfully")
mess.execute('CREATE TABLE IF NOT EXISTS messages (username TEXT, message TEXT)')
print("Table created successfully")

conn.close()
mess.close()


clients = 0

@socketio.on("connect", namespace="/")
def connect():
    # global variable as it needs to be shared
    global clients
    clients += 1
    print(clients)
    with open("./globaldata.json", "r") as f:
                data = json.load(f)
    

    data['totalusers'] += (clients)
    new = json.dumps(data, indent=4)
                
                
    with open("./globaldata.json", "w") as f:
                f.write(new)
    

@socketio.on("disconnect", namespace="/")
def disconnect():
    global clients
    clients -= 1
    print(clients)
    
    


def check_sql_injection(username, password):
    # List of common SQL injection keywords
    keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "UNION", "JOIN", "FROM", "WHERE", "HAVING", "OR", "AND", "LIKE", "GROUP", "ORDER", "BY", "EXEC", "EXECUTE", "DECLARE", "TRUNCATE", "RENAME", "CREATE", "TABLE", "INDEX", "VIEW", "PROCEDURE", "FUNCTION"]
    
    # Check if username or password contains any SQL injection keywords
    for keyword in keywords:
        if keyword in username or keyword in password:
            return True
    
    # No SQL injection keywords found
    return False


def sqlATTEMPT():
    keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "UNION", "JOIN", "FROM", "WHERE", "HAVING", "OR", "AND", "LIKE", "GROUP", "ORDER", "BY", "EXEC", "EXECUTE", "DECLARE", "TRUNCATE", "RENAME", "CREATE", "TABLE", "INDEX", "VIEW", "PROCEDURE", "FUNCTION"]
    return "Sorry, the username or password you entered contains malicious code. Please check that your input does not include any of the following blacklisted words: " + ', '.join(keywords)


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_sql_injection(password, password):
            return sqlATTEMPT()

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        row = cursor.fetchone()
        if row:
            
            session['username'] = row[0]
            session['email'] = row[2]  # add email value to session
            session['msgssent'] = int(row[3])
            return redirect(url_for('home'))
        else:
            error = "Invalid login credentials. Please try again."
            return render_template('login.html', error=error)
    return render_template('login.html')



# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_sql_injection(username, password):
            return sqlATTEMPT()
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        if row is not None:
            return render_template('signup.html', error="Username Taken. Please try again.")

        else:


            password2 = request.form['confirm_password']
            if password != password2:
                return 	render_template('signup.html', error="Passwords do not match. Please try again.")
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password, email, msgssent) VALUES (?, ?, ?, ?)', (username, password, "None", "0"))  # add email value to database as None
            conn.commit()
            conn.close()
            session['username'] = username
            session['email'] = None  # add None value to session
            session['msgssent'] = "0"
            return redirect(url_for('home'))
    else:
        return render_template('signup.html')
    
def get_messages():
    conn = sqlite3.connect("messages.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages")
    messages = cursor.fetchall()
    conn.close()
    return messages


@socketio.on('get_messages')
def handle_get_messages():
    # Send all the messages to the client
    conn = sqlite3.connect("messages.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages")
    messages = cursor.fetchall()
    conn.close()
    emit('messages', {'messages': messages})



@socketio.on('message')
def handle_message(message):
    username = session.get('username')
    if not username or not message:
        return

    try:
        conn = sqlite3.connect("messages.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages VALUES (?, ?)", (username, message))
        conn.commit()

        session['msgssent'] = int(session.get('msgssent')) + 1

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        msgssent = int(session['msgssent'])
        cursor.execute("UPDATE users SET msgssent = ? WHERE username = ?", (msgssent, username))
        conn.commit()
        conn.close()  # close connection
        with open("./globaldata.json", "r") as f:
                data = json.load(f)
    

        data['totalmessages'] += 1
        new = json.dumps(data, indent=4)


        with open("./globaldata.json", "w") as f:
                    f.write(new)

        messages = get_messages()
        socketio.emit('messages', {'messages': messages})
        

    except sqlite3.Error as e:
        print(f"Error executing SQL query: {e}")

    finally:
        if conn:
            conn.close()



@app.route('/user/<username>')
def users(username):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        
        conn.close()
        if row is not None:
                return render_template('userpage.html', username=row[0], messagessent=row[3], followers=row[4])
        else:
            return render_template('404.html')


@app.route('/', methods=['GET', 'POST'])
def home():
    if 'username' in session:
        if request.method == 'POST':
            username = session['username']
            message = request.form.get('message')
            if username and message:
                conn = sqlite3.connect("messages.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO messages VALUES (?, ?)", (username, message))
                conn.commit()
                conn.close()

            return redirect(url_for('home'))

        else:
            messages = get_messages()
            return render_template('home.html', username=session['username'], messages=messages, usersonline=clients)
    else:
        return redirect(url_for('login'))

@app.route('/profile', methods=['GET','POST'])
def profile():
    if request.method == 'POST':
        email = request.form['email']
        if validEMail(email):
            
            if check_sql_injection(email, "NONE"):
                return sqlATTEMPT()
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET email = ? WHERE username = ?', (email, session['username']))

            conn.commit()
            conn.close()
            session['email'] = email
            # add email value to session
        return redirect(url_for('profile'))
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (session['username'],))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    session['msgssent'] = row[3]
    return render_template('profile.html', current_user=session)



#search
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['search_query']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username LIKE ?", ('%' + query + '%',))
        results = cursor.fetchall()
        results = sorted(results, key=lambda x: Levenshtein.distance(x[0], query))[:15]
        results = [result[0] for result in results]
        conn.close()
        
        # perform search and return results
        return render_template('search_results.html', results=results)
    else:
        return render_template('search.html')



# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    try:
        if session['username'] == 'admin':
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute('SELECT * FROM users')
            users = c.fetchall()
            conn.close()
            with open("./globaldata.json", "r") as f:
                data = json.load(f)
            allmessages = data['totalmessages']
            
            allusers = len(users)
            
            
            
            
                

            return render_template('admin.html', users=users, online=clients, messages=allmessages, allusers=allusers)
        else:
            return render_template('404.html')
    except:
        return render_template('404.html', error="404")
    
    
    


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error=e), 404

if __name__ == '__main__':
    app.run(debug=True)
    socketio.run(app)
