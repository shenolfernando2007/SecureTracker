# SecureTracker cases.py
# Features: view cases, search cases, filter cases, create cases, view case details, update case status, add notes

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
    role_required,
    generate_case_number,
    log_action
)


# blueprint for all case-related routes
cases_bp = Blueprint(
    "cases",
    __name__,
    url_prefix="/cases"
)



# view all cases
@cases_bp.route("/")
@login_required

def index():

    # get database connection
    db = current_app.db

    # read search keyword
    search = request.args.get(
        "search",
        ""
    )

    # read selected status filter
    status = request.args.get(
        "status",
        ""
    )

    # read selected priority filter 
    priority = request.args.get(
        "priority",
        ""
    )

    # base query used to retrieve cases
    query = """
    SELECT

    cases.*,

    creator.username AS creator_name,

    investigator.username AS investigator_name


    FROM cases


    LEFT JOIN users creator

    ON cases.created_by = creator.id


    LEFT JOIN users investigator

    ON cases.assigned_to = investigator.id


    WHERE 1=1

    """

    # store SQL query parameters
    params = []

    # apply search filter if provided
    if search:


        query += """

        AND
        (
            cases.case_number LIKE ?

            OR cases.title LIKE ?

            OR cases.category LIKE ?
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

    # apply status filter
    if status:


        query += """

        AND cases.status = ?

        """


        params.append(
            status
        )

    # apply priority filter
    if priority:


        query += """

        AND cases.priority = ?

        """


        params.append(
            priority
        )


    # display newest cases first
    query += """

    ORDER BY cases.created_at DESC

    """
    # execute query
    cases = db.execute(
        query,
        *params
    )

    # show case list
    return render_template(
        "cases/cases.html",
        cases=cases
    )

# create cases
@cases_bp.route(
    "/create",
    methods=[
        "GET",
        "POST"
    ]
)

@login_required

@role_required(
    "Admin",
    "Supervisor",
    "Investigator"
)

def create():

    # get database connection
    db = current_app.db

    # retrieve active investigators and supervisors
    investigators = db.execute(
        """
        SELECT id, username

        FROM users

        WHERE role IN
        (
            'Investigator',
            'Supervisor'
        )

        AND active = 1

        """
    )


    if request.method == "POST":

        # read submitted form data
        title = request.form.get(
            "title"
        )

        description = request.form.get(
            "description"
        )


        category = request.form.get(
            "category"
        )


        priority = request.form.get(
            "priority"
        )


        assigned_to = request.form.get(
            "assigned_to"
        )

        # allow the case to be created without an assigned investigator
        if not assigned_to:

            assigned_to = None

        # validate required fields
        if not title or not description:


            flash(
                "Title and description are required.",
                "danger"
            )


            return redirect(
                url_for(
                    "cases.create"
                )
            )


        # generate a unique case number
        case_number = generate_case_number(
            db
        )


        # save the new case
        db.execute(
            """
            INSERT INTO cases

            (
                case_number,
                title,
                description,
                category,
                priority,
                created_by,
                assigned_to
            )


            VALUES

            (?, ?, ?, ?, ?, ?, ?)

            """,

            case_number,
            title,
            description,
            category,
            priority,
            session["user_id"],
            assigned_to
        )


        # record the activity in the audit log
        log_action(
            db,
            session["user_id"],
            "CREATE_CASE",
            f"Created {case_number}"
        )


        flash(
            "Case created successfully.",
            "success"
        )


        return redirect(
            url_for(
                "cases.index"
            )
        )


    # display the create case form
    return render_template(
        "cases/create.html",
        investigators=investigators
    )

# view single case
@cases_bp.route(
    "/<int:id>"
)

@login_required

def view(id):

    # get database connection
    db = current_app.db

    # retrieve the selected case
    case = db.execute(
        """
        SELECT *

        FROM cases

        WHERE id = ?

        """,

        id
    )


    # return 404 page if the case does not exist
    if not case:

        return render_template(
            "404.html"
        ),404


    # retrieve all notes for the case
    notes = db.execute(
        """
        SELECT

        case_notes.*,

        users.username


        FROM case_notes


        JOIN users


        ON case_notes.user_id = users.id


        WHERE case_id = ?


        ORDER BY created_at DESC

        """,

        id
    )


    # retrieve all evidence linked to the case
    evidence = db.execute(
        """
        SELECT *

        FROM evidence

        WHERE case_id = ?

        """,

        id
    )


    # display case details
    return render_template(
        "cases/view.html",

        case=case[0],

        notes=notes,

        evidence=evidence
    )



# add notes
@cases_bp.route(
    "/<int:id>/notes",
    methods=["POST"]
)

@login_required

def add_note(id):

    # get database connection
    db = current_app.db

    # read the submitted note
    note = request.form.get(
        "note"
    )

    # save the note if one was provided
    if note:


        db.execute(
            """
            INSERT INTO case_notes

            (
                case_id,
                user_id,
                note
            )

            VALUES

            (?, ?, ?)

            """,

            id,
            session["user_id"],
            note
        )


        # record the action in the audit log
        log_action(
            db,
            session["user_id"],
            "ADD_NOTE",
            f"Added note to case {id}"
        )

    # return to the case page
    return redirect(
        url_for(
            "cases.view",
            id=id
        )
    )



# update status
@cases_bp.route(
    "/<int:id>/status",
    methods=["POST"]
)

@login_required

def update_status(id):

    # get database connection
    db = current_app.db

    # read the selection status
    status = request.form.get(
        "status"
    )

    # list of valid case statuses
    allowed = [

        "Open",

        "Active Investigation",

        "Pending Review",

        "Closed"

    ]

    # reject invalid status values
    if status not in allowed:


        flash(
            "Invalid status.",
            "danger"
        )

        return redirect(
            url_for(
                "cases.view",
                id=id
            )
        )

    # update the case status
    db.execute(
        """
        UPDATE cases

        SET status = ?,

        updated_at = CURRENT_TIMESTAMP


        WHERE id = ?

        """,

        status,
        id
    )


    # record the status change
    log_action(
        db,
        session["user_id"],
        "UPDATE_STATUS",
        f"Case {id} changed to {status}"
    )



    flash(
        "Status updated.",
        "success"
    )



    return redirect(
        url_for(
            "cases.view",
            id=id
        )
    )

# edit cases 
@cases_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Supervisor", "Investigator")
def edit(id):
    
    # get database connection
    db = current_app.db

    # retrieve the selected case
    case = db.execute(
        "SELECT * FROM cases WHERE id = ?",
        id
    )

    # return 404 page if the case does not exist
    if not case:
        return render_template("404.html"), 404

    # retrieve active investigators and supervisors
    investigators = db.execute(
        """
        SELECT id, username
        FROM users
        WHERE role IN ('Investigator','Supervisor')
        AND active = 1
        """
    )

    if request.method == "POST":

        # read updated case information        
        title = request.form.get("title")
        description = request.form.get("description")
        category = request.form.get("category")
        priority = request.form.get("priority")
        assigned_to = request.form.get("assigned_to")

        # allow the case to remain unassigned
        if not assigned_to:

            assigned_to = None

        # update the case details
        db.execute(
            """
            UPDATE cases
            SET
                title=?,
                description=?,
                category=?,
                priority=?,
                assigned_to=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            title,
            description,
            category,
            priority,
            assigned_to,
            id
        )

        # record the edit in the audit log
        log_action(
            db,
            session["user_id"],
            "EDIT_CASE",
            f"Edited case {case[0]['case_number']}"
        )

        flash("Case updated successfully.", "success")

        return redirect(url_for("cases.view", id=id))

    # display the edit form
    return render_template(
        "cases/edit.html",
        case=case[0],
        investigators=investigators
    )

# delete cases   
@cases_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
@role_required("Admin")
def delete(id):
 
    # get database connection
    db = current_app.db

    # retrieve the case number before deletion
    case = db.execute(
        "SELECT case_number FROM cases WHERE id=?",
        id
    )

    # return 404 page if the case does not exist
    if not case:
        return render_template("404.html"),404

    # delete the selected case
    db.execute(
        "DELETE FROM cases WHERE id=?",
        id
    )

    # record the deletion in the audit log
    log_action(
        db,
        session["user_id"],
        "DELETE_CASE",
        f"Deleted {case[0]['case_number']}"
    )

    flash(
        "Case deleted successfully.",
        "success"
    )

    return redirect(
        url_for("cases.index")
    )

# reassign investigator
@cases_bp.route("/<int:id>/assign", methods=["POST"])
@login_required
@role_required("Admin", "Supervisor")
def assign(id):

    # get database connection
    db = current_app.db

    # read the selected investigator
    assigned_to = request.form.get("assigned_to")

    # update the assigned investigator
    db.execute(
        """
        UPDATE cases
        SET assigned_to=?,
            updated_at=CURRENT_TIMESTAMP
        WHERE id=?
        """,
        assigned_to,
        id
    )

    # record the reassignment in the audit log
    log_action(
        db,
        session["user_id"],
        "REASSIGN_CASE",
        f"Assigned investigator to case {id}"
    )

    flash(
        "Investigator updated.",
        "success"
    )

    return redirect(
        url_for("cases.view", id=id)
    )

# close case
@cases_bp.route("/<int:id>/close", methods=["POST"])
@login_required
@role_required("Admin", "Supervisor", "Investigator")
def close_case(id):
    
    # get database connection
    db = current_app.db

    # mark the case as closed
    db.execute(
        """
        UPDATE cases
        SET
            status='Closed',
            updated_at=CURRENT_TIMESTAMP
        WHERE id=?
        """,
        id
    )

    # record the case closure
    log_action(
        db,
        session["user_id"],
        "CLOSE_CASE",
        f"Closed case {id}"
    )

    flash(
        "Case closed successfully.",
        "success"
    )

    return redirect(
        url_for("cases.view", id=id)
    )