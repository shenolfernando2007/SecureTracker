# SecureTracker

#### Video Demo: https://youtu.be/mUXGofcxZrg?si=_AwUfGyuZrnlSQop

#### Description:

SecureTracker is a secure case and evidence management system built with Flask, SQLite, and CS50's SQL library. It is designed for law enforcement and investigative teams to manage cases, track evidence with chain of custody, and maintain audit logs of all user actions.
 
## Why I Built This
 
Proper case and evidence management software — the kind with role-based access, chain-of-custody tracking, and audit logging — is usually priced for large organizations with large budgets. Small investigative teams need the same rigor but rarely have access to it. I built SecureTracker so that any small team can self-host a genuinely secure, auditable system without paying for an enterprise license.
 
**Note:** This project was originally submitted as my final project for [Harvard's CS50](https://cs50.harvard.edu/x/gallery/).


## Features

- **User Authentication**: Registration, login, logout with password hashing (Werkzeug/scrypt)
- **Role-Based Access Control**: Admin, Supervisor, Investigator, and Viewer roles
- **Case Management**: Create, view, edit, delete, assign, and close cases
- **Evidence Management**: Upload files with SHA-256 hashing, download, delete evidence
- **Chain of Custody**: Full audit trail for all evidence actions (upload, transfer, review, analysis, archive, download)
- **Case Notes**: Add notes to cases with user attribution and timestamps
- **Audit Logging**: All critical actions are logged with user ID, action, description, and IP address
- **Search & Filter**: Search cases by keyword, filter by status and priority
- **Responsive UI**: Bootstrap 5-based interface with dark navbar and card-based layouts
- **Network Access**: Runs on all interfaces (`0.0.0.0`) for LAN and public deployment


## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with CS50 SQL library
- **Frontend**: Bootstrap 5, Jinja2 templating
- **Sessions**: Flask-Session (filesystem-based)
- **Security**: Werkzeug password hashing, session management, CSRF protection via Flask-WTF


## Installation

1. **Clone or download** the repository.

   ```bash
    git clone https://github.com/shenolfernando2007/securetracker.git
    cd SecureTracker
   ```

2. **Install dependencies**:
   ```bash
    pip install -r requirements.txt
   ```
   > **On Debian/Ubuntu/Kali (Python 3.11+):** you may see `error: externally-managed-environment`. This happens because newer Debian-based systems block system-wide pip installs by default. Use a virtual environment instead:
   > ```bash
   > python3 -m venv venv
   > source venv/bin/activate
   > pip install -r requirements.txt
   > ```
   > If `python3 -m venv` fails, install it first with `sudo apt install python3-venv`, then retry. Remember to run `source venv/bin/activate` again each time you open a new terminal, before running the app.

3. **Initialize the database** (if starting fresh):

   SecureTracker uses the SQLite command-line tool to build the schema. Verify it's installed:

   ```bash
    sqlite3 --version
   ```

   If it's missing:
 
   - **Windows** — download from [sqlite.org/download.html](https://sqlite.org/download.html) and add `sqlite3.exe` to your `PATH`
   - **Linux (Debian/Ubuntu)** — `sudo apt install sqlite3`
   - **Fedora** — `sudo dnf install sqlite`
   - **Arch** — `sudo pacman -S sqlite`
   - **macOS (Homebrew)** — `brew install sqlite`
   
   Then create the database:
 
   ```bash
     sqlite3 securetrack.db 
   ```
   ```sql
     .read sql/securetrack.sql
   .quit
   ```

   > **Note (Linux/macOS):** some Python environments have a package named `routes` that can conflict with this project's `routes/` directory, raising `ModuleNotFoundError: No module named 'routes.auth'`. The included `routes/__init__.py` prevents this — no action needed.

4. **Run the application**:
 ```bash
  python app.py
 ```

5. **Open your browser** and navigate to:
   ```
   http://127.0.0.1:5000
   ```

   Or from another device on the same network:
   ```
   http://YOUR_LOCAL_IP:5000
   ```


## First-Time Setup

On a fresh, empty database, visit:
 
```
http://127.0.0.1:5000/setup-admin
```
 
to create the first administrator account. This route only works while the `users` table is empty — once any user exists, it returns `403` permanently.
 
After setup, log in as the admin, create additional users via `/register`, and promote them to Supervisor / Investigator via `/users`.


## User Roles & Permissions
 
|      Role         | View Cases   | Create Cases | Edit Cases | Delete Cases | Assign Cases | Close Cases | 
|-------------------|--------------|--------------|------------|--------------|--------------|-------------|
| **Admin**         |     ✓        |     ✓       |     ✓      |     ✓        |     ✓       |     ✓       | 
| **Supervisor**    |     ✓        |     ✓       |     ✓      |     ✗        |     ✓       |     ✓       | 
| **Investigator**  |     ✓        |     ✓       |     ✓      |     ✗        |     ✗       |     ✓       | 
| **Viewer**        |     ✓        |     ✗       |     ✗      |     ✗        |     ✗       |     ✗       | 

# Other Permissions

|      Role        | Upload Evidence | Manage Users | View Audit Logs |
|------------------|-----------------|--------------|-----------------|
| **Admin**        |      ✓          |     ✓       |       ✓         |
| **Supervisor**   |      ✓          |     ✗       |       ✗         |
| **Investigator** |      ✗          |     ✗       |       ✗         |
| **Viewer**       |      ✗          |     ✗       |       ✗         |


## Usage

### Creating an Admin
1. Visit `/setup-admin` and create your administrator account
2. Log in with the credentials you just created

### Promoting Users
If users already exist, an admin can:
- Go to `/users` to view all users
- Toggle account active/inactive status
- Change user roles (Admin, Supervisor, Investigator, Viewer)

### Managing Cases
- **Create Case**: `/cases/create` — Admin, Supervisor, and Investigator only
- **View Cases**: `/cases` — All authenticated users
- **Case Details**: `/cases/<id>` — All authenticated users
- **Edit Case**: `/cases/<id>/edit` — Admin, Supervisor, and Investigator only
- **Delete Case**: `/cases/<id>/delete` — Admin only
- **Assign Investigator**: `/cases/<id>/assign` — Admin and Supervisor only
- **Close Case**: `/cases/<id>/close` — Admin, Supervisor, and Investigator only
- **Add Note**: `/cases/<id>/notes` — All authenticated users

### Managing Evidence
- **Add Evidence**: `/evidence/case/<case_id>/add` — Admin, Supervisor, and Investigator only
- **View Evidence**: `/evidence/<id>` — All authenticated users
- **Download Evidence**: `/evidence/<id>/download` — All authenticated users (logged in chain of custody)
- **Delete Evidence**: `/evidence/<id>/delete` — Admin and Supervisor only
- **All Evidence**: `/evidence/` — All authenticated users
- **Add Custody Record**: `/evidence/<id>/custody` — All authenticated users

### Audit Logs
- **View Logs**: `/logs` — Admin only
- Search logs by username, action, or description


## Project Structure

```
.
├── app.py                      # Flask application entry point
├── config.py                   # Application configuration
├── helpers.py                  # Helper functions (decorators, file handling, hashing)
├── requirements.txt            # Python dependencies
├── sql/
│   └── securetrack.sql         # SQLite database 
├── routes/
│   ├── auth.py                 # Authentication routes (login, logout, register, setup)
│   ├── dashboard.py            # Dashboard statistics and recent activity
│   ├── cases.py                # Case management routes
│   ├── evidence.py             # Evidence management routes
│   ├── users.py                # User management routes (admin only)
│   └── logs.py                 # Audit log routes (admin only)
├── templates/
│   ├── layout.html             # Base template with navbar and flash messages
│   ├── login.html              # Login form
│   ├── register.html           # Registration form
│   ├── setup_admin.html        # Initial admin setup form
│   ├── dashboard.html          # Dashboard with statistics
│   ├── 403.html                # Access denied page
│   ├── 404.html                # Page not found page
│   ├── 500.html                # Server error page
│   ├── cases/
│   │   ├── cases.html          # Case list with search/filter
│   │   ├── view.html           # Single case view with notes and evidence
│   │   ├── create.html         # Create new case form
│   │   └── edit.html           # Edit existing case form
│   ├── evidence/
│   │   ├── add.html            # Add evidence form
│   │   ├── view.html           # Evidence detail with chain of custody
│   │   └── index.html          # All evidence list
│   ├── users/
│   │   └── index.html          # User management table
│   └── logs/
│       └── index.html          # Audit log table with search
├── static/
│   └── styles.css              # Custom CSS styles
└── uploads/                    # Uploaded evidence files (gitignored)
```


## Database Tables & Schema

The database consists of 7 main tables:

- **users** — User accounts with roles and active status
- **cases** — Case records with status, priority, and assignment
- **case_notes** — Notes attached to cases
- **evidence** — Uploaded evidence files with SHA-256 hashes
- **chain_of_custody** — Audit trail for evidence actions
- **audit_logs** — System-wide action logs
- **user_sessions** — Login/logout session tracking
- **system_settings** — Application configuration key-value pairs

See `sql/securetrack.sql` for the full sql code.


## Security Features

- Password hashing using `werkzeug.security.generate_password_hash`
- Session-based authentication with Flask-Session
- CSRF protection via Flask-WTF
- Role-based access control decorators (`@login_required`, `@role_required`, `@admin_required`)
- SHA-256 file integrity verification for all uploaded evidence
- Complete audit trail of all user actions (login, logout, case CRUD, evidence operations)
- IP address logging for all actions
- Foreign key constraints for referential integrity
- File type validation for uploads


## Deploying to Production

The app runs on `0.0.0.0:5000` by default, so it's reachable from other devices on the same LAN as-is. For anything beyond that:
 
**Set `debug=False`** in `app.py` before exposing it to the internet — Flask's interactive debugger can allow arbitrary code execution if left on in production. This project already ships with `debug=False`.
 
**Set a real `SECRET_KEY`:**
 
```bash
export SECRET_KEY="your-strong-random-key-here"
```

**Recommended platforms:** [Render](https://render.com), [Railway](https://railway.app), [Fly.io](https://fly.io), and [PythonAnywhere](https://www.pythonanywhere.com) all support deploying straight from GitHub with HTTPS included.

**Self-hosting / VPS:** use a production WSGI server instead of Flask's dev server:
 
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Production Checklist

Before deploying to production:

1. **Disable debug mode**: Set `debug=False` in `app.py`
2. **Set SECRET_KEY**: Use a strong random key via environment variable:
   ```bash
   export SECRET_KEY="your-very-secure-random-key-here"
   ```
3. **Use production WSGI server**: Replace `app.run()` with Gunicorn or uWSGI
4. **Enable HTTPS**: Use SSL certificates (Let's Encrypt or platform-managed)
5. **Configure firewall**: Only expose necessary ports (80/443)
6. **Regular backups**: Backup `securetrack.db` and `uploads/` directory
7. **Update dependencies**: Keep Flask and all packages up to date


## Development Notes

- Debug mode is disabled by default (`debug=False` in `app.py`) 
- The `/setup-admin` route is disabled once any user exists in the database
- Uploaded files are stored in the `uploads/` directory with timestamp-based filenames to prevent collisions
- Maximum upload size is 16 MB (configurable in `config.py`)
- The app uses CS50's SQL library which provides a simple interface to SQLite databases


## Known Issues & Fixes

- **Case creation/edit fails when "Unassigned" is selected**: Fixed — empty `assigned_to` values are now converted to `NULL` in the database
- **Root route 404**: Fixed — `/` now redirects to `/dashboard`


## License

Released under the [MIT License](LICENSE) — free to use, modify, and self-host.
 
Contributions and forks are welcome. If you run into a bug or have an idea for a feature, open an issue or a pull request.
