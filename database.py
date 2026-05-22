import sqlite3

DB_NAME = "job_applications.db"

def init_db():
    """Create the job applications table if it doesn't exist"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # cursor.execute("""
    #     CREATE TABLE IF NOT EXISTS applications (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         company TEXT,
    #         role TEXT,
    #         subject TEXT,
    #         date_applied TEXT,
    #         status TEXT
    #     )
    # """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            role TEXT,
            subject TEXT,
            date_applied TEXT,
            status TEXT,
            unique_key text UNIQUE
        )
    """)


    conn.commit()
    conn.close()
    

def add_application(company, role, subject, date_applied, status="Applied",unique_key=None):
    """Insert a new job application record"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Build unique key: company + role + date_applied
    if unique_key is None:
        unique_key = f"{company}_{role}_{date_applied}"

    cursor.execute("""
        INSERT OR REPLACE INTO applications (company, role, subject, date_applied, status, unique_key)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (company, role, subject, date_applied, status, unique_key))

    

    conn.commit()
    conn.close()

def get_all_applications():
    """Retrieve all job applications"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM applications")
    rows = cursor.fetchall()

    conn.close()
    return rows

def update_status(app_id, new_status):
    """Update the status of a job application"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE applications
        SET status = ?
        WHERE id = ?
    """, (new_status, app_id))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Initialize database
    init_db()

    # Example usage
    add_application("Google", "Data Engineer", "Application for Data Engineer", "2026-05-17")
    apps = get_all_applications()
    for app in apps:
        print(app)
