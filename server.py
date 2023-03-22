from flask import Flask, render_template, request, session, redirect, url_for, g
import sqlite3


app = Flask(__name__)
app.secret_key = 'jiejfirjeijrrcm4334qjdwx293r82ud2few2ed' #bad practice
app.config['SESSION_TYPE'] = 'filesystem'


# Database Setup (here bad practice)
def connectDb():
    conn = sqlite3.connect("HW.db")
    return conn

def createTables():
    db = connectDb()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        firstname TEXT NOT NULL,
        lastname Text NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL)
    """)

    db.commit

createTables() #creates the database

def checkUser():
    user_id = session.get("user_id")
    if user_id == None:
        g.user = None
    else:
        db = connectDb()
        g.user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


@app.route("/")
def routeToHome():
    return render_template("index.html")

@app.route("/profile")
def routeToProfile():
    checkUser()
    if g.user == None:
        return redirect(url_for("routeToLogin"))
    return render_template("profile.html")

@app.route("/dashboard")
def routeToDashboard():
    return render_template("profile.html")


# User Authentication & Registration
@app.route("/login", methods=["POST", "GET"])
def routeToLogin():
    if request.method == "POST":
        error = None

        username = request.form["username"]
        password = request.form["password"]

        db = connectDb()
        user = db.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()

        if user == None:
            error = "User does not exist! Please create an account."
            return render_template("user_auth/signin.html", error=error)
 
        elif password != user[5]:
            error = "Invalid Credentials!"
            return render_template("user_auth/login.html", error=error)

        else:
            session.clear()
            session["user_id"] = user[0]
            if user[6] == "admin":
                return redirect(url_for("routeToDashboard"))
            
            elif user[6] == "customer":
                return redirect(url_for("routeToProfile"))
        
    return render_template("user_auth/login.html")

@app.route("/signin", methods=["POST", "GET"])
def routeToSignin():
    print("In Signin")
    if request.method == "POST":
        error = None

        username = request.form["username"]
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"]
        password = request.form["password"]

        db = connectDb()
        usernames_list = db.execute("SELECT username FROM users").fetchall()

        if username in usernames_list:
            error = "Username Taken! Please select another username."
            return render_template("user_auth/signin.html", error=error)
        else:
            db.execute("INSERT INTO users(username, firstname, lastname, email, password, role) VALUES(?, ?, ?, ?, ?, 'customer')", (username, firstname, lastname, email, password))
            db.commit()
            return redirect(url_for("routeToLogin"))
        
    return render_template("user_auth/signin.html")


if __name__ == "__main__":
    app.run(debug=True)