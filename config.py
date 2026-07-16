# SecureTracker config.py
# Application configuration settings

import os
from tempfile import mkdtemp


class Config:

    # flask secret key
    SECRET_KEY = os.environ.get("SECRET_KEY", "securetracker-secret-key")
    # sqlite database 
    DATABASE_URI = "sqlite:///securetrack.db"

    # file uploads
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
   
    # allowed file extensions for evidence
    ALLOWED_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "gif",
        "pdf",
        "doc",
        "docx",
        "txt",
        "csv",
        "zip"
    }

    # flask-session settings
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = mkdtemp()
    SESSION_USE_SIGNER = True

    # dev settings
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0

    # valid case statuses
    CASE_STATUS = [
        "Open",
        "Active Investigation",
        "Pending Review",
        "Closed"
    ]

    # valid user roles - must match database and decorators
    USER_ROLES = [
        "Admin",
        "Supervisor",
        "Investigator",
        "Viewer"
    ]