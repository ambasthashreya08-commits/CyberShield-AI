
import sqlite3
from pathlib import Path
from contextlib import contextmanager


# --------------------------------------------------
# DATABASE CONFIGURATION
# --------------------------------------------------

DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "vulnerabilities.db"
)

ALLOWED_STATUSES = {
    "Needs Validation",
    "Confirmed",
    "False Positive"
}


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

@contextmanager
def get_connection():

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        yield conn
    finally:
        conn.close()


# --------------------------------------------------
# DATABASE INITIALIZATION AND MIGRATION
# --------------------------------------------------

def initialize_database():

    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT,
                affected_url TEXT,
                cwe_id TEXT,
                evidence TEXT,
                risk_score REAL,
                status TEXT DEFAULT 'Needs Validation',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                solution TEXT,
                analyst_notes TEXT
            )
        """)

        # Safely add new columns to existing databases.
        # Existing vulnerability records are preserved.

        existing_columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(vulnerabilities)"
            ).fetchall()
        }

        if "solution" not in existing_columns:
            conn.execute("""
                ALTER TABLE vulnerabilities
                ADD COLUMN solution TEXT
            """)

        if "analyst_notes" not in existing_columns:
            conn.execute("""
                ALTER TABLE vulnerabilities
                ADD COLUMN analyst_notes TEXT
            """)

        conn.commit()


# --------------------------------------------------
# SAVE VULNERABILITY
# --------------------------------------------------

def save_vulnerability(data):

    if not isinstance(data, dict):
        raise TypeError(
            "Vulnerability data must be a dictionary."
        )

    with get_connection() as conn:

        cursor = conn.execute("""
            INSERT INTO vulnerabilities (
                name,
                severity,
                description,
                affected_url,
                cwe_id,
                evidence,
                risk_score,
                status,
                solution,
                analyst_notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("name", "Unknown"),
            data.get("severity", "Informational"),
            data.get("description", ""),
            data.get("affected_url", ""),
            data.get("cwe_id", ""),
            data.get("evidence", ""),
            data.get("risk_score", 0),
            data.get("status", "Needs Validation"),
            data.get("solution", ""),
            data.get("analyst_notes", "")
        ))

        conn.commit()

        return cursor.lastrowid


# --------------------------------------------------
# GET ALL VULNERABILITIES
# --------------------------------------------------

def get_vulnerabilities():

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT *
            FROM vulnerabilities
            ORDER BY risk_score DESC
        """).fetchall()

        return [dict(row) for row in rows]


# --------------------------------------------------
# UPDATE VULNERABILITY VALIDATION STATUS
# --------------------------------------------------

def update_vulnerability_status(
    vulnerability_id: int,
    status: str,
    analyst_notes: str = ""
):

    if status not in ALLOWED_STATUSES:
        raise ValueError(
            f"Invalid status. Allowed values: {ALLOWED_STATUSES}"
        )

    with get_connection() as conn:

        cursor = conn.execute("""
            UPDATE vulnerabilities
            SET status = ?,
                analyst_notes = ?
            WHERE id = ?
        """, (
            status,
            analyst_notes,
            vulnerability_id
        ))

        conn.commit()

        return cursor.rowcount > 0
