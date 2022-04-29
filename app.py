from flask import Flask, redirect, render_template, request, session, url_for
import datetime
import pymongo
from twilio.rest import Client
from decouple import config

# FlASK
#############################################################
app = Flask(__name__)
app.permanent_session_lifetime = datetime.timedelta(days=365)
app.secret_key = "super secret key"
#############################################################

# MONGODB
#############################################################
mongodb_key = config('mongodb_key')
client = pymongo.MongoClient(
    mongodb_key, tls=True, tlsAllowInvalidCertificates=True)
db = client.Escuela
cuentas = db.alumno
#############################################################

# Twilio
#############################################################
account_sid = config('account_sid')
auth_token =  config('auth_token')
TwilioClient = Client(account_sid, auth_token)
#############################################################

@app.route('/')
def home():
    email = None
    if "email" in session:
        email = session["email"]
        usuario = cuentas.find_one({"correo": (email)})
        return render_template('index.html', error=usuario)
    else:
        return render_template('Login.html')


@app.route('/signup', methods=['POST'])
def signup():
    email = ""
    if 'email' in session:
        return render_template('index.html', error=email)
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        session['email'] = email
        session['password'] = password
        session['name'] = name
    return render_template('index.html', error=email)


@app.route("/login", methods=["GET", "POST"])
def login():
    email = None    
    if "email" in session: 
        email = session["email"]
        usuario = cuentas.find_one({"correo": (email)})
        return render_template('index.html', error=usuario)
    else:
        if (request.method == "GET"):
            return render_template("Login.html", error="email")
        else:
            email = request.form["email"]
            password = request.form["password"]

            try:
                user= cuentas.find_one({"correo":(email)})
                if(user!= None and user["contrasena"] == password):
                    session["email"] = email
                    usuario = cuentas.find_one({"correo": (email)})
                    return render_template("index.html", error=usuario)
                else:
                    return render_template("Login.html")

            except Exception as e:
                return "%s" % e

@app.route('/logout')
def logout():
    if "email" in session:
        session.clear()
        return redirect(url_for("home"))
        
@app.route("/usuarios")
def usuarios():
    cursor = cuentas.find({})
    users = []
    for doc in cursor:
        users.append(doc)
    return render_template("/usuarios.html", data=users)

@app.route("/insert",methods=["POST"])
def insertUsers():
    user = {
        "matricula": request.form["matricula"],
        "nombre": request.form["nombre"],
        "correo": request.form["correo"],
        "contrasena": request.form["contrasena"],
    }

    try:
        cuentas.insert_one(user)
        comogusten = TwilioClient.messages.create(
            from_="whatsapp:+14155238886",
            body="El usuario %s se agregó a tu pagina web" % (
                request.form["nombre"]),
            to="whatsapp:+5215568760514"
        )
        print(comogusten.sid)
        session["email"]= user["correo"]
        return render_template("index.html",error=user)
    except Exception as e:
        return "<p>El servicio no esta disponible =>: %s %s" % type(e), ec

@app.route("/find_one/<matricula>")
def find_one(matricula):
    try:
        user = cuentas.find_one({"matricula": (matricula)})
        if user == None:
            return "<p>La matricula %s nó existe</p>" % (matricula)
        else:
            return "<p>Encontramos: %s </p>" % (user)
    except Exception as e:
        return "%s" % e

@app.route("/delete_one/<matricula>")
def delete_one(matricula):
    try:
        user = cuentas.delete_one({"matricula": (matricula)})
        if user.deleted_count == None:
            return "<p>La matricula %s nó existe</p>" % (matricula)
        else:
            return redirect(url_for("usuarios"))
    except Exception as e:
        return "%s" % e
   

@app.route("/update", methods=["POST"])
def update():
    try:
        filter = {"matricula": request.form["matricula"]}
        user = {"$set": {
            "nombre": request.form["nombre"]
        }}
        cuentas.update_one(filter, user)
        return redirect(url_for("usuarios"))

    except Exception as e:
        return "error %s" % (e)

@app.route('/create')
def create():
    return render_template('CreateForm.html')

