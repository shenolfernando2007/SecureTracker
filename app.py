# SecureTracker app.py
# Main application entry point

import os
from datetime import datetime

from flask import Flask, redirect, url_for
from flask_session import Session
from cs50 import SQL

from config import Config
from helpers import register_error_handlers

app = Flask(__name__) # create flask application
app.config.from_object(Config) # configure

os.makedirs(              # create upload directory if it doesn't exist
    Config.UPLOAD_FOLDER,
    exist_ok=True
)

Session(app)  # Session setup

db = SQL(Config.DATABASE_URI) # configure the database connection using the URI from the configuration
app.db = db                   # make database accessible throughout the app

register_error_handlers(app)  # error Handlers

@app.context_processor
def inject_current_year():
    # Makes the current year available in all templates (used in the footer)
    return {"current_year": datetime.now().year}

# Register blueprints
from routes.auth import auth_bp                            
from routes.dashboard import dashboard_bp
from routes.cases import cases_bp
from routes.evidence import evidence_bp
from routes.users import users_bp
from routes.logs import logs_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(cases_bp)
app.register_blueprint(evidence_bp)
app.register_blueprint(users_bp)
app.register_blueprint(logs_bp)


# root directory
@app.route("/")
def index():
    """Redirect root to dashboard"""
    return redirect(url_for("dashboard.dashboard"))

if __name__ == "__main__":
    # allow access from other devices on LAN 
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
