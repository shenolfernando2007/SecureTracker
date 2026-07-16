# SecureTracker logs.py
# Tracks and displays: user actions, security events, system activity

from flask import (
    Blueprint,
    render_template,
    request,
    current_app
)

from helpers import (
    login_required,
    admin_required
)

# blueprint for audit logs
logs_bp = Blueprint(
    "logs",
    __name__,
    url_prefix="/logs"
)

# view logs
@logs_bp.route("/")
@login_required
@admin_required

def index():

    # get database connection
    db = current_app.db

    # read search keyword
    search = request.args.get(
        "search",
        ""
    )

    # base query used to retrieve audit logs
    query = """

    SELECT
    audit_logs.id,
    audit_logs.action,
    audit_logs.description,
    audit_logs.ip_address,
    audit_logs.timestamp,
    users.username
    FROM audit_logs
    LEFT JOIN users
    ON audit_logs.user_id = users.id
    WHERE 1=1

    """
    # store SQL query parameters
    params = []

    # apply search filter if provided
    if search:
        query += """
        AND
        (
            users.username LIKE ?
            OR audit_logs.action LIKE ?
            OR audit_logs.description LIKE ?
        )
        """

        term = f"%{search}%"

        params.extend(
            [
                term,
                term,
                term
            ]
        )

    # display the newest log entries first
    query += """
    ORDER BY audit_logs.timestamp DESC
    LIMIT 500
    """
    
    # execute the query
    logs = db.execute(
        query,
        *params
    )

    # display the audit logs
    return render_template(
        "logs/index.html",
        logs=logs
    )