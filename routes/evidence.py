# SecureTracker evidence.py
# Handles: uploading evidence, viewing evidence, chain of custody

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

import os

from helpers import (
    login_required,
    role_required,
    allowed_file,
    save_uploaded_file,
    log_action
)

from flask import send_file

# blueprint for all evidences
evidence_bp = Blueprint(
    "evidence",
    __name__,
    url_prefix="/evidence"
)

# add evidence
@evidence_bp.route(
    "/case/<int:case_id>/add",
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

def add(case_id):

    # get database connection
    db = current_app.db

    # retrieve the selected case
    case = db.execute(
        """
        SELECT *
        FROM cases
        WHERE id = ?

        """,

        case_id
    )


    # return 404 page if the case does not exist
    if not case:

        return render_template(
            "404.html"
        ),404

    if request.method == "POST":

        # read the submitted evidence details
        name = request.form.get(
            "name"
        )

        description = request.form.get(
            "description"
        )

        evidence_type = request.form.get(
            "evidence_type"
        )

        file = request.files.get(
            "file"
        )

        # evidence name is required
        if not name:

            flash(
                "Evidence name required.",
                "danger"
            )

            return redirect(
                request.url
            )

        # default values when no file is updated
        stored_filename = None
        filepath = None
        file_hash = None

        # process uploaded files
        if file and file.filename:

            # check if the uploaded file type is allowed
            if not allowed_file(
                file.filename
            ):

                flash(
                    "Unsupported file type.",
                    "danger"
                )

                return redirect(
                    request.url
                )

            # save the uploaded file and generate its hash
            (
                stored_filename,
                filepath,
                file_hash

            ) = save_uploaded_file(
                file,
                current_app.config["UPLOAD_FOLDER"]
            )

        # save the evidence info
        db.execute(
            """
            INSERT INTO evidence
            (
                case_id,
                name,
                description,
                evidence_type,
                original_filename,
                stored_filename,
                file_path,
                file_hash,
                uploaded_by
            )
            VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?)

            """,

            case_id,
            name,
            description,
            evidence_type,
            file.filename
            if file and file.filename
            else None,
            stored_filename,
            filepath,
            file_hash,
            session["user_id"]

        )

        # retrieve the ID of the newly created evidence
        evidence_id = db.execute(
            """
            SELECT last_insert_rowid()
            AS id
            """
        )[0]["id"]



        # create the initial chain of custody record
        db.execute(
            """
            INSERT INTO chain_of_custody
            (
                evidence_id,
                action,
                performed_by,
                remarks
            )
            VALUES
            (?, ?, ?, ?)

            """,
            
            evidence_id,
            "UPLOAD",
            session["user_id"],
            "Evidence uploaded"

        )

        # record the upload in the audit log
        log_action(
            db,
            session["user_id"],
            "UPLOAD_EVIDENCE",
            f"Uploaded evidence to case {case_id}"

        )

        # display the upload form
        flash(
            "Evidence uploaded successfully.",
            "success"
        )

        return redirect(
            url_for(
                "cases.view",
                id=case_id
            )
        )

    # display the upload form
    return render_template(
        "evidence/add.html",
        case=case[0]
    )

# view the evidence
@evidence_bp.route(
    "/<int:id>"
)

@login_required

def view(id):

    # get database connection
    db = current_app.db

    # retrieve the selected evidence
    evidence = db.execute(
        """
        SELECT
        evidence.*,
        users.username
        FROM evidence
        JOIN users
        ON evidence.uploaded_by = users.id
        WHERE evidence.id = ?
        """,

        id
    )

    # return 404 page if the evidence does not exist
    if not evidence:

        return render_template(
            "404.html"
        ),404

    # retrieve the chain of custody records
    custody = db.execute(
        """
        SELECT
        chain_of_custody.*,
        users.username
        FROM chain_of_custody
        JOIN users
        ON chain_of_custody.performed_by = users.id
        WHERE evidence_id = ?
        ORDER BY timestamp DESC

        """,

        id
    )

    # display evidence details and custody history
    return render_template(
        "evidence/view.html",
        evidence=evidence[0],
        custody=custody
    )

# download the evidence file
@evidence_bp.route("/<int:id>/download")
@login_required
def download(id):

    # get database connection
    db = current_app.db

    # retrieve the selected evidence
    evidence = db.execute(
        """
        SELECT *
        FROM evidence
        WHERE id = ?
        """,
        id
    )

    # return 404 page if the evidence does not exist
    if not evidence:
        return render_template("404.html"), 404

    # get the stored file path
    file_path = evidence[0]["file_path"]

    # check if the file still exists
    if not file_path or not os.path.exists(file_path):
        flash("File not found.", "danger")
        return redirect(url_for("evidence.view", id=id))

    # record the download in the chain of custody
    db.execute(
        """
        INSERT INTO chain_of_custody
        (
            evidence_id,
            action,
            performed_by,
            remarks
        )
        VALUES (?, ?, ?, ?)
        """,
        id,
        "DOWNLOAD",
        session["user_id"],
        "Evidence downloaded"
    )

    # record the download in the audit log
    log_action(
        db,
        session["user_id"],
        "DOWNLOAD_EVIDENCE",
        f"Downloaded evidence {id}"
    )

    # send the file to the user
    return send_file(
        file_path,
        as_attachment=True,
        download_name=evidence[0]["original_filename"]
    )

# delete the evidence
@evidence_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
@role_required("Admin", "Supervisor")
def delete(id):

    # get database connection
    db = current_app.db

    # retrieve the selected evidence
    evidence = db.execute(
        """
        SELECT *
        FROM evidence
        WHERE id = ?
        """,
        id
    )

    # return 404 page if the evidence does not exist
    if not evidence:
        return render_template("404.html"),404

    # delete the evidence file from filesystem
    item = evidence[0]

    # remove file from filesystem
    if item["file_path"] and os.path.exists(item["file_path"]):
        os.remove(item["file_path"])

    # delete the evidence record
    db.execute(
        "DELETE FROM evidence WHERE id=?",
        id
    )

    # record the delete in the audit log
    log_action(
        db,
        session["user_id"],
        "DELETE_EVIDENCE",
        f"Deleted evidence {id}"
    )

    flash(
        "Evidence deleted successfully.",
        "success"
    )

    return redirect(
        url_for(
            "cases.view",
            id=item["case_id"]
        )
    )

# list all evidences
@evidence_bp.route("/")
@login_required
def index():

    # get database connection
    db = current_app.db

    # retrieve all evidence records
    evidence = db.execute(
        """
        SELECT
            evidence.*,
            cases.case_number
        FROM evidence
        JOIN cases
            ON evidence.case_id = cases.id
        ORDER BY evidence.uploaded_at DESC
        """
    )

    # display the evidence list
    return render_template(
        "evidence/index.html",
        evidence=evidence
    )

# add new custody record
@evidence_bp.route("/<int:id>/custody", methods=["POST"])
@login_required
def add_custody(id):

    # get database connection
    db = current_app.db

    # read submitted custody info
    remarks = request.form.get("remarks")
    action = request.form.get("action")

   # save the custody record
    db.execute(
        """
        INSERT INTO chain_of_custody
        (
            evidence_id,
            action,
            performed_by,
            remarks
        )
        VALUES (?, ?, ?, ?)
        """,
        id,
        action,
        session["user_id"],
        remarks
    )
 
    # record the update in the audit log
    log_action(
        db,
        session["user_id"],
        "CHAIN_OF_CUSTODY",
        f"Updated chain of custody for evidence {id}"
    )

    flash(
        "Chain of custody updated.",
        "success"
    )

    return redirect(
        url_for(
            "evidence.view",
            id=id
        )
    )