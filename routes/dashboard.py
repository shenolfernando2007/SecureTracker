# SecureTracker dashboard.py
# Displays: case statistics, evidence statistics, recent activity

from flask import (
    Blueprint,
    render_template,
    current_app,
    session
)

from helpers import login_required

# blueprint for dashboard
dashboard_bp = Blueprint(
    "dashboard",
    __name__
)

# dashboard
@dashboard_bp.route(
    "/dashboard"
)

@login_required

def dashboard():

    # get database connection
    db = current_app.db

    # retrieve summary statistics from the dashboard
    statistics = db.execute(
        """
        SELECT
        (
            SELECT COUNT(*)
            FROM cases
        )
        AS total_cases,
        (
            SELECT COUNT(*)
            FROM cases
            WHERE status != 'Closed'
        )
        AS active_cases,
        (
            SELECT COUNT(*)
            FROM cases
            WHERE status = 'Closed'
        )
        AS closed_cases,
        (
            SELECT COUNT(*)
            FROM evidence
        )
        AS total_evidence,
        (
            SELECT COUNT(*)
            FROM users
        )
        AS total_users

        """
    )[0]

    # retrieve the five most recently created cases
    recent_cases = db.execute(
        """
        SELECT
        cases.id,
        cases.case_number,
        cases.title,
        cases.status,
        cases.priority,
        users.username AS creator
        FROM cases
        JOIN users
        ON cases.created_by = users.id
        ORDER BY cases.created_at DESC
        LIMIT 5

        """
    )

    # retrieve the ten most recent activity logs
    activity = db.execute(
        """
        SELECT
        audit_logs.action,
        audit_logs.description,
        audit_logs.timestamp,
        users.username
        FROM audit_logs
        LEFT JOIN users
        ON audit_logs.user_id = users.id
        ORDER BY audit_logs.timestamp DESC
        LIMIT 10

        """
    )

    # display the dashboard
    return render_template(
        "dashboard.html",
        statistics=statistics,
        recent_cases=recent_cases,
        activity=activity,
        username=session.get(
            "username"
        )
    )