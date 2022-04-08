from flask import Flask, redirect, render_template, request, session, url_for
import datetime

# FlASK
#############################################################
app = Flask(__name__)
app.permanent_session_lifetime = datetime.timedelta(days=365)
app.secret_key = "super secret key"
#############################################################

@app.route('/')
def home():
    email = None
    if "email" in session:
        email = session["email"]
        return render_template('index.html', error=email)
    else:
        return render_template('Login.html', error=email)


@app.route('/signup')
def signup():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    return render_template('index.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    email = None    
    if "email" in session:
        return render_template('index.html', error=session["email"])
    else:
        if (request.method == "GET"):
            return render_template("Login.html", error="email")
        else:
            email = request.form["email"]
            password = request.form["password"]
            session["email"] = email
            return render_template("index.html", error=email)

@app.route('/logout')
def logout():
    if "email" in session:
        session.clear()
        return redirect(url_for("home"))
        
  


