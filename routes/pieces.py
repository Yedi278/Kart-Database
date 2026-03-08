from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.decorators import login_required
from utils.other import get_db

pieces_bp = Blueprint("pieces", __name__, url_prefix="/pieces")


@pieces_bp.route("/", methods=["GET", "POST"])
@login_required
def pieces():

    db = get_db()

    if not db:
        flash("Sede non valida", "danger")
        return redirect(url_for("dashboard.dashboard"))

    # CREAZIONE PEZZO
    if request.method == "POST":
        name = request.form.get("name")
        model = request.form.get("model")
        quantity = request.form.get("quantity")
        note = request.form.get("note")

        if not name:
            flash("Nome pezzo obbligatorio", "danger")
            return redirect(url_for("pieces.pieces"))

        if not model:
            model = ""

        if not quantity:
            quantity = 0

        if not note:
            note = ""

        db.create_piece(name, model, int(quantity), note)

        flash("Pezzo creato", "success")
        return redirect(url_for("pieces.pieces"))

    # FILTRI
    name = request.args.get("name")
    model = request.args.get("model")
    restock = request.args.get("restock")

    pieces = db.get_filtered_pieces(name, model, restock)

    return render_template(
        "pieces.html",
        pieces=pieces
    )


@pieces_bp.route("/delete/<int:piece_id>", methods=["POST"])
@login_required
def delete_piece(piece_id):

    db = get_db()

    db.delete_piece(piece_id)

    flash("Pezzo eliminato", "warning")

    return redirect(url_for("pieces.pieces"))


@pieces_bp.route("/update/<int:piece_id>", methods=["POST"])
@login_required
def update_piece(piece_id):

    db = get_db()

    name = request.form.get("name")
    model = request.form.get("model")
    quantity = request.form.get("quantity")
    note = request.form.get("note")
    restock = request.form.get("restock")

    if not name:
        flash("Nome pezzo obbligatorio", "danger")
        return redirect(url_for("pieces.pieces"))

    if not model:
        model = ""

    if not quantity:
        quantity = 0

    if not note:
        note = ""

    if not restock:
        restock = 0

    db.update_piece(piece_id, name, model, int(quantity), note, int(restock))

    flash("Pezzo aggiornato", "success")

    return redirect(url_for("pieces.pieces"))