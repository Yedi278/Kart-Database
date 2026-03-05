from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import os
from database import Database
from config import DB_DIR, locations
from utils.decorators import login_required

karts_bp = Blueprint("karts", __name__, url_prefix="/karts")


def get_db():
    location = session.get("location")

    if not location or location not in locations:
        return None

    db_path = os.path.join(DB_DIR, locations[location])
    return Database(db_path)


@karts_bp.route("/", methods=["GET", "POST"])
@login_required
def karts():

    db = get_db()
    if not db:
        flash("Sede non valida", "danger")
        return redirect(url_for("dashboard.dashboard"))

    # CREAZIONE KART
    if request.method == "POST":
        num = request.form.get("num")
        model = request.form.get("model")
        note = request.form.get("note")

        if not num:
            flash("Numero kart obbligatorio", "danger")
            return redirect(url_for("karts.karts"))

        try:
            db.create_kart(int(num), model, note)
            flash("Kart creato con successo", "success")
        except Exception as e:
            flash("Numero già esistente", "danger")

        return redirect(url_for("karts.karts"))

    karts = db.get_all_karts()

    return render_template("karts.html", karts=karts)


@karts_bp.route("/delete/<int:kart_id>", methods=["POST"])
@login_required
def delete_kart(kart_id):
    db = get_db()
    db.delete_kart(kart_id)
    flash("Kart eliminato", "warning")
    return redirect(url_for("karts.karts"))

@karts_bp.route("/update/<int:kart_id>", methods=["POST"])
@login_required
def update_kart(kart_id):
    db = get_db()

    num = request.form.get("num")
    model = request.form.get("model")
    note = request.form.get("note")
    if not num:
        flash("Numero kart obbligatorio", "danger")
        return redirect(url_for("karts.karts"))
    if not model:
        flash("Modello kart obbligatorio", "danger")
        return redirect(url_for("karts.karts"))
    if not note:
        note = ""
    status = request.form.get("status")

    db.update_kart(kart_id, int(num), model, note, int(status))

    flash("Kart aggiornato", "success")
    return redirect(url_for("karts.karts"))