# dashboard.py
from flask import Blueprint, render_template, session
from utils.decorators import login_required

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        username=session.get("username"),
        role=session.get("role"),
        location=session.get("location")
    )