PRAGMA foreign_keys = ON;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,

    role TEXT NOT NULL DEFAULT 'Viewer'
        CHECK (
            role IN (
                'Admin',
                'Supervisor',
                'Investigator',
                'Viewer'
            )
        ),

    active INTEGER NOT NULL DEFAULT 1
        CHECK (active IN (0,1)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_users_username
ON users(username);

CREATE INDEX idx_users_role
ON users(role);

CREATE TABLE cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_number TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    priority TEXT NOT NULL
        CHECK (
            priority IN (
                'Low',
                'Medium',
                'High',
                'Critical'
            )
        ),

    status TEXT NOT NULL DEFAULT 'Open'
        CHECK (
            status IN (
                'Open',
                'Active Investigation',
                'Pending Review',
                'Closed'
            )
        ),

    created_by INTEGER NOT NULL,
    assigned_to INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    closed_at TIMESTAMP,

    FOREIGN KEY(created_by)
        REFERENCES users(id),

    FOREIGN KEY(assigned_to)
        REFERENCES users(id)
);

CREATE INDEX idx_cases_number
ON cases(case_number);

CREATE INDEX idx_cases_status
ON cases(status);

CREATE INDEX idx_cases_priority
ON cases(priority);

CREATE TABLE case_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    note TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,

    FOREIGN KEY(case_id)
        REFERENCES cases(id)
        ON DELETE CASCADE,

    FOREIGN KEY(user_id)
        REFERENCES users(id)
);

CREATE TABLE evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    evidence_type TEXT,
    original_filename TEXT,
    stored_filename TEXT,
    file_path TEXT,
    file_hash TEXT,
    uploaded_by INTEGER NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(case_id)
        REFERENCES cases(id)
        ON DELETE CASCADE,

    FOREIGN KEY(uploaded_by)
        REFERENCES users(id)
);

CREATE INDEX idx_evidence_case
ON evidence(case_id);

CREATE TABLE chain_of_custody (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evidence_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    performed_by INTEGER NOT NULL,
    remarks TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(evidence_id)
        REFERENCES evidence(id)
        ON DELETE CASCADE,

    FOREIGN KEY(performed_by)
        REFERENCES users(id)
);

CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    description TEXT NOT NULL,
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id)
        REFERENCES users(id)
);

CREATE INDEX idx_logs_timestamp
ON audit_logs(timestamp);

CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    logout_time TIMESTAMP,
    ip_address TEXT,

    FOREIGN KEY(user_id)
        REFERENCES users(id)
);

CREATE TABLE system_settings (
    setting_key TEXT PRIMARY KEY,
    setting_value TEXT
);

INSERT INTO system_settings
VALUES
(
    'application_name',
    'SecureTracker'
);

INSERT INTO system_settings
VALUES
(
    'version',
    '1.0'
);