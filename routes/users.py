# SecureTracker users.py
# Admin features: view users, change roles, activate/deactivate accounts

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    session
)

from helpers import (
    login_required,
    admin_required,
    log_action
)

# blueprint for user managment
users_bp = Blueprint(
    "users",
    __name__,
    url_prefix="/users"
)

# user list
@users_bp.route("/")
@login_required
@admin_required

def index():

    # get database connection
    db = current_app.db

    # retrieve all registered users 
    users = db.execute(
        """
        SELECT
            id,
            username,
            email,
            full_name,
            role,
            active,
            created_at,
            last_login
        FROM users
        ORDER BY created_at DESC
        """
    )
    
    # display the user list
    return render_template(
        "users/index.html",
        users=users
    )



# change roles
@users_bp.route(
    "/<int:id>/role",
    methods=["POST"]
)

@login_required
@admin_required

def change_role(id):

    # get database connection
    db = current_app.db

    # read the selected role
    new_role = request.form.get(
        "role"
    )

    # list of valid user roles
    allowed_roles = [
        "Admin",
        "Supervisor",
        "Investigator",
        "Viewer"
    ]

    # reject invalid role values
    if new_role not in allowed_roles:

        flash(
            "Invalid role selected.",
            "danger"
        )

        return redirect(
            url_for(
                "users.index"
            )
        )

    # retrieve the selected user
    user = db.execute(
        """
        SELECT
            username,
            role
        FROM users
        WHERE id = ?
        """,
        id
    )

    # return if the user the does not exist
    if not user:

        flash(
            "User not found.",
            "danger"
        )

        return redirect(
            url_for(
                "users.index"
            )
        )

    # prevent administrators from removing their own admin role
    if id == session["user_id"] and new_role != "Admin":

        flash(
            "You cannot remove your own admin privileges.",
            "danger"
        )

        return redirect(
            url_for(
                "users.index"
            )
        )

    old_role = user[0]["role"]
    username = user[0]["username"]

    # update the user's role
    db.execute(
        """
        UPDATE users
        SET role = ?,
        updated_at = CURRENT_TIMESTAMP
        WHERE id = ?

        """,
        new_role,
        id
    )

    # record the role change
    log_action(
        db,
        session["user_id"],
        "CHANGE_ROLE",
        f"Changed {username}'s role from {old_role} to {new_role}"
    )

    flash(
        "User role updated.",
        "success"
    )

    return redirect(
        url_for(
            "users.index"
        )
    )

# enable/disable users
@users_bp.route(
    "/<int:id>/toggle",
    methods=["POST"]
)

@login_required
@admin_required

def toggle(id):

    # get database connection
    db = current_app.db

    # prevent administrators from disabling their own account
    if id == session["user_id"]:

        flash(
            "You cannot disable your own account.",
            "danger"
        )
       
        return redirect(
            url_for(
                "users.index"
            )
        )

    # retrieve the selected user
    user = db.execute(
        """
        SELECT
            username,
            active
        FROM users
        WHERE id = ?

        """,
        id
    )

    # return if the user does not exist
    if not user:

        flash(
            "User not found.",
            "danger"
        )

        return redirect(
            url_for(
                "users.index"
            )
        )


    username = user[0]["username"]
    current_status = user[0]["active"]

    # toggle the user's account status
    db.execute(
        """
        UPDATE users
        SET active =
        CASE
            WHEN active = 1
            THEN 0
            ELSE 1
        END,
        updated_at = CURRENT_TIMESTAMP
        WHERE id = ?

        """,
        id
    )

    # determine the updated account status
    new_status = (
        "disabled"
        if current_status
        else "activated"
    )

    # record the status change 
    log_action(
        db,
        session["user_id"],
        "TOGGLE_USER",
        f"{new_status.capitalize()} account for {username}"
    )

    flash(
        "Account status updated.",
        "success"
    )

    return redirect(
        url_for(
            "users.index"
        )
    )