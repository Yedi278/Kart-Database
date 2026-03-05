import os
from flask import Flask, render_template, request, redirect, session, url_for, flash
from database import Database
from functools import wraps


locations = {
    "Bicocca": "bicocca.db",
    "Meda": "meda.db",
    "Torino": "torino.db",
    "Marcianise": "marcianise.db",
    "Catania": "catania.db",
    "Udine": "udine.db"
}

app = Flask(__name__)
app.secret_key = "SUPER_SECRET_KEY_CHANGE_THIS"  # CAMBIA IN PRODUZIONE

dir_curr = os.path.abspath(os.path.dirname(__file__))
dir_db = os.path.join(dir_curr, 'db')

# -----------------------
# DATABASE HANDLER
# -----------------------

def get_db():
    location = session.get("location")
    if not location:
        return None

    db_name = locations.get(location)
    if not db_name:
        return None

    return Database(os.path.join(dir_db, db_name))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# -----------------------

@app.route("/")
def login():
    return render_template("login.html", locations=list(locations.keys()))


@app.route("/login", methods=["POST"])
def do_login():

    username = request.form.get("username")
    password = request.form.get("password")
    location = request.form.get("location")

    if not username or not password or not location:
        flash("Compila tutti i campi")
        return redirect(url_for("login"))

    if location not in locations:
        flash("Sede non valida")
        return redirect(url_for("login"))

    db = Database(os.path.join(dir_db, locations[location]))

    user = db.verify_user(username, password)

    if not user:
        flash("Credenziali non valide")
        return redirect(url_for("login"))

    # SESSION SETUP
    session["user_id"] = user["user_id"]
    session["username"] = user["user_username"]
    session["role"] = user["user_role"]
    session["location"] = location

    return redirect(url_for("dashboard"))


@app.route("/dashboard")
@login_required
def dashboard():

    if session["role"] == None:
        flash("Ruolo utente non definito")
        return redirect(url_for("login"))
    
    return render_template(
        "dashboard.html",
        username=session["username"],
        role=session["role"],
        location=session["location"]
    )

@app.route("/repairs")
@login_required
def repairs():
    return "Gestione Riparazioni"


@app.route("/karts")
@login_required
def karts():
    return "Gestione Kart"


@app.route("/pieces")
@login_required
def pieces():
    return "Gestione Pezzi"


@app.route("/users", methods=["GET", "POST"])
@login_required
def users():
    if session.get("role") != 0:
        flash("Accesso negato: permessi insufficienti")
        return redirect(url_for("dashboard"))

    # CREAZIONE NUOVO UTENTE
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")
        location = request.form.get("location")

        if not username or not password or role is None or not location:
            flash("Compila tutti i campi")
            return redirect(url_for("users"))

        db = Database(os.path.join(dir_db, locations[location]))
        db.create_user(username, password, int(role))

        flash(f"Utente creato nella sede {location}")
        return redirect(url_for("users"))

    all_users = []

    for loc_name, db_file in locations.items():
        db = Database(os.path.join(dir_db, db_file))
        users = db.get_all_users()

        for u in users:
            user_dict = dict(u)
            user_dict["location"] = loc_name
            all_users.append(user_dict)

    return render_template("users.html", users=all_users, locations=locations.keys())

@app.route("/users/update_role/<location>/<int:user_id>", methods=["POST"])
@login_required
def update_role(location, user_id):

    if session.get("role") != 0:
        return redirect(url_for("dashboard"))

    new_role = request.form.get("role")

    db = Database(os.path.join(dir_db, locations[location]))
    db.update_user_role(user_id, int(new_role))

    flash("Ruolo aggiornato")
    return redirect(url_for("users"))

@app.route("/users/delete/<location>/<int:user_id>")
@login_required
def delete_user(location, user_id):

    if session.get("role") != 0:
        return redirect(url_for("dashboard"))

    if user_id == session.get("user_id") and location == session.get("location"):
        flash("Non puoi eliminare il tuo account")
        return redirect(url_for("users"))

    db = Database(os.path.join(dir_db, locations[location]))
    db.delete_user(user_id)

    flash("Utente eliminato")
    return redirect(url_for("users"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)