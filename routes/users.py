from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
from database import Database
from config import locations, DB_DIR
from utils.decorators import login_required, admin_required

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/", methods=["GET", "POST"])
@login_required
@admin_required
def users():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")
        location = request.form.get("location")

        # Validazione campi
        if not username or not password or role is None or not location:
            flash("Compila tutti i campi", "danger")
            return redirect(url_for("users.users"))

        # Validazione sede
        if location not in locations:
            flash("Sede non valida", "danger")
            return redirect(url_for("users.users"))

        db_path = os.path.join(DB_DIR, locations[location])
        db = Database(db_path)

        db.create_user(username, password, int(role))

        flash(f"Utente creato nella sede {location}", "success")
        return redirect(url_for("users.users"))


    all_users = []

    for loc_name, db_file in locations.items():
        db_path = os.path.join(DB_DIR, db_file)

        # Se il DB non esiste lo saltiamo
        if not os.path.exists(db_path):
            continue

        db = Database(db_path)
        users = db.get_all_users()

        for u in users:
            user_dict = dict(u)
            user_dict["location"] = loc_name
            all_users.append(user_dict)

    return render_template(
        "users.html",
        users=all_users,
        locations=locations.keys()
    )

@users_bp.route("/delete/<int:user_id>/<location>", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id, location):

    if location not in locations:
        flash("Sede non valida", "danger")
        return redirect(url_for("users.users"))

    db_path = os.path.join(DB_DIR, locations[location])
    db = Database(db_path)

    db.delete_user(user_id)

    flash(f"Utente eliminato dalla sede {location}", "warning")
    return redirect(url_for("users.users"))


@users_bp.route("/update_role/<int:user_id>/<location>", methods=["POST"])
@login_required
@admin_required
def update_role(user_id, location):

    new_role = request.form.get("new_role")

    if new_role is None:
        flash("Ruolo non valido", "danger")
        return redirect(url_for("users.users"))

    if location not in locations:
        flash("Sede non valida", "danger")
        return redirect(url_for("users.users"))

    db_path = os.path.join(DB_DIR, locations[location])
    db = Database(db_path)

    db.update_user_role(user_id, int(new_role))

    flash(f"Ruolo utente aggiornato nella sede {location}", "success")
    return redirect(url_for("users.users"))