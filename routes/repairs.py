# repairs.py
from flask import Blueprint, render_template, request, redirect, session
from database import Database
from utils.other import get_db

repairs_bp = Blueprint("repairs", __name__, url_prefix="/repairs")


@repairs_bp.route("/", methods=["GET", "POST"])
def repairs():

    db = get_db()

    if not db:
        return redirect("/")

    if request.method == "POST":

        kart_id = request.form.get("kart_id")
        note = request.form.get("note")

        user_id = session["user_id"]

        repair_id = db.create_repair(kart_id, user_id, note)

        piece_ids = request.form.getlist("piece_id")
        quantities = request.form.getlist("quantity")

        for p, q in zip(piece_ids, quantities):

            if p and q:
                db.add_piece_to_repair(repair_id, p, q)

        db.update_repair_timestamp(repair_id)

        return redirect("/repairs")

    kart_num = request.args.get("kart_num")
    kart_model = request.args.get("kart_model")
    piece = request.args.get("piece")
    
    repairs = db.get_filtered_repairs(kart_num, kart_model, piece)

    for r in repairs:
        r["pieces"] = db.get_pieces_for_repair(r["repair_id"])

    karts = db.get_all_karts()
    pieces = db.get_all_pieces()

    return render_template(
        "repairs.html",
        repairs=repairs,
        karts=karts,
        pieces=pieces
    )