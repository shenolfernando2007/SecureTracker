# SecureTracker helpers.py
# Common helper functions for auth, files, and logging

import hashlib
import os
from datetime import datetime
from functools import wraps

from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

# require user to be logged in
def login_required(view):  
    
    # redirect login if user not in session
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return wrapped

# require one of the given roles
def role_required(*roles):  
    
    # allow access only if user role matches
    def decorator(view):

        @wraps(view)
        def wrapped(*args, **kwargs):
            if session.get("role") not in roles:
                return render_template("403.html"), 403

            return view(*args, **kwargs)

        return wrapped

    return decorator

# require Admin role specifically
def admin_required(view):   

    # require administrator access
    @wraps(view)
    def wrapped(*args, **kwargs):

        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("auth.login"))

        if session.get("role") != "Admin":
            return render_template("403.html"), 403

        return view(*args, **kwargs)

    return wrapped

# check if file extension is allowed
def allowed_file(filename):
    # check whether the uploaded file has an allowed extension
    if not filename or "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in current_app.config["ALLOWED_EXTENSIONS"]

# generate SHA-256 hash for evidence integrity
def calculate_file_hash(filepath):
    # generate SHA-256 hash of a file

    sha = hashlib.sha256()

    with open(filepath, "rb") as file:
        while True:
            chunk = file.read(4096)

            if not chunk:
                break

            sha.update(chunk)

    return sha.hexdigest()

# insert an audit log entry with user, action, and IP
def log_action(db, user_id, action, description):
    
    # insert an audit log
    db.execute(
        """
        INSERT INTO audit_logs
        (
            user_id,
            action,
            description,
            ip_address
        )
        VALUES (?, ?, ?, ?)
        """,
        user_id,
        action,
        description,
        request.remote_addr
    )

# generate unique case number like CASE-2026-00001
def generate_case_number(db):

    year = datetime.now().year

    total = db.execute(
        """
        SELECT COUNT(*) AS total
        FROM cases
        WHERE case_number LIKE ?
        """,
        f"CASE-{year}-%"
    )[0]["total"]

    return f"CASE-{year}-{total + 1:05d}"

# convert raw file size in bytes into a human-readable format
def human_file_size(size):

    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"

        size /= 1024

    return f"{size:.1f} TB"

# save upload with unique timestamp name and return details
def save_uploaded_file(uploaded_file, upload_folder):

    os.makedirs(upload_folder, exist_ok=True)    # create folder if missing

    original = secure_filename(uploaded_file.filename)  

    extension = original.rsplit(".", 1)[1].lower()

    # unique filename: YYYYMMDDHHMMSSffffff.ext
    filename = (
        datetime.now().strftime("%Y%m%d%H%M%S%f")
        + "."
        + extension
    )

    filepath = os.path.join(upload_folder, filename)

    uploaded_file.save(filepath)

    return (
        filename,
        filepath,
        calculate_file_hash(filepath)
    )

# register custom error pages
def register_error_handlers(app):

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal(error):
        return render_template("500.html"), 500