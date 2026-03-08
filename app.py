# app.py
from flask import Flask
from config import SECRET_KEY, DB_DIR, locations

from routes.login import login_bp
from routes.dashboard import dashboard_bp
from routes.users import users_bp
from routes.karts import karts_bp
from routes.pieces import pieces_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY

# REGISTER BLUEPRINTS
app.register_blueprint(login_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(users_bp)
app.register_blueprint(karts_bp)
app.register_blueprint(pieces_bp)

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=False)