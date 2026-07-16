# SecureTracker auth.py
# Handles: registration, login, logout, initial administrator setup

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    current_app
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from helpers import log_action


# authentication blueprint
auth_bp = Blueprint(
    "auth",
    __name__
)

# user registration 
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # get database connection
    db = current_app.db

    if request.method == "POST":
        
        # read form data
        username = request.form.get("username")
        email = request.form.get("email")
        full_name = request.form.get("full_name")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # make sure required fields are filled
        if not username or not email or not password or not confirmation:
            flash("All fields are required.", "danger")
            return redirect(url_for("auth.register"))

        # check if passwords match
        if password != confirmation:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register"))

        # check whether username or email already exists
        existing = db.execute(
            """
            SELECT id
            FROM users
            WHERE username = ?
               OR email = ?
            """,
            username,
            email
        )

        if existing:
            flash("Username or email already exists.", "danger")
            return redirect(url_for("auth.register"))

        password_hash = generate_password_hash(password)       # hash password before storing it

        # create new user with Viewer role
        db.execute(
            """
            INSERT INTO users
            (
                username,
                email,
                password_hash,
                full_name,
                role,
                active
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            username,
            email,
            password_hash,
            full_name,
            "Viewer",
            0
        )

        flash(
            "Account created successfully. Wait for administrator approval.",
            "success"
        )

        return redirect(url_for("auth.login"))

    return render_template("register.html")      # show registration page

# user login
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    # get database connection
    db = current_app.db

    if request.method == "POST":

        # read login credentials
        username = request.form.get("username")
        password = request.form.get("password")

        # find matching user
        users = db.execute(
            """
            SELECT *
            FROM users
            WHERE username = ?
            """,
            username
        )

        # invalid username
        if len(users) != 1:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("auth.login"))

        user = users[0]

        # check password hash
        if not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "danger")
            return redirect(url_for("auth.login"))

        # prevent inactive users from logging in
        if user["active"] == 0:
            flash("Account disabled or awaiting approval.", "danger")
            return redirect(url_for("auth.login"))

        # remove any previous session data
        session.clear()

        # store logged-in user information
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]

       # update login timestamp 
        db.execute(
            """
            UPDATE users
            SET last_login = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            user["id"]
        )

        # record login activity
        log_action(
            db,
            user["id"],
            "LOGIN",
            "User logged into SecureTracker"
        )

        return redirect(url_for("dashboard.dashboard"))

    return render_template("login.html")  # show login page


# user logout 
@auth_bp.route("/logout")
def logout():

    # get database connection
    db = current_app.db

    # save logout activity if user is logged in
    if "user_id" in session:
        log_action(
            db,
            session["user_id"],
            "LOGOUT",
            "User logged out"
        )

    # clear session data
    session.clear()

    flash("Logged out successfully.", "success")

    return redirect(url_for("auth.login"))


# Initial Administrator Setup
@auth_bp.route("/setup-admin", methods=["GET", "POST"])
def setup_admin():

    db = current_app.db

   # check whether any users already exist
    existing = db.execute(
        """
        SELECT COUNT(*) AS total
        FROM users
        """
    )[0]["total"]

    # Only allow setup if there are no users
    if existing > 0:                             # allow setup only once
        return render_template("403.html"), 403

    if request.method == "POST":

        # read administrator details
        full_name = request.form.get("full_name")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # validate required fields
        if (
            not full_name
            or not username
            or not email
            or not password
            or not confirmation
        ):
            flash("All fields are required.", "danger")
            return redirect(url_for("auth.setup_admin"))

        # verify password confirmation
        if password != confirmation:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.setup_admin"))

        # hash password before storing it
        password_hash = generate_password_hash(password)

        # create administrator account
        db.execute(
            """
            INSERT INTO users
            (
                username,
                email,
                password_hash,
                full_name,
                role,
                active
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            username,
            email,
            password_hash,
            full_name,
            "Admin",
            1
        )

        flash(
            "Administrator account created successfully. You may now log in.",
            "success"
        )

        return redirect(url_for("auth.login"))

    return render_template("setup_admin.html")   # show admin setup page