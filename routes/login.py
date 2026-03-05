# login.py
from flask import Blueprint, render_template, request, redirect, session, url_for, flash
import os
from database import Database
from config import locations, DB_DIR

login_bp = Blueprint("login", __name__)

@login_bp.route("/")
def login():
    return render_template("login.html", locations=list(locations.keys()))

@login_bp.route("/login")
def login_page():
    return redirect(url_for("login.login"))

@login_bp.route("/login", methods=["POST"])
def do_login():

    username = request.form.get("username")
    password = request.form.get("password")
    location = request.form.get("location")

    if not username or not password or not location:
        flash("Compila tutti i campi")
        return redirect(url_for("login.do_login"))

    if location not in locations:
        flash("Sede non valida")
        return redirect(url_for("login.do_login"))

    db = Database(os.path.join(DB_DIR, locations[location]))
    user = db.verify_user(username, password)

    if not user:
        flash("Credenziali non valide")
        return redirect(url_for("login.do_login"))

    session["user_id"] = user["user_id"]
    session["username"] = user["user_username"]
    session["role"] = user["user_role"]
    session["location"] = location
    
    return redirect(url_for("dashboard.dashboard"))

@login_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login.login"))