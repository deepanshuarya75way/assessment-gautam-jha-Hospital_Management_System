import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "hospital.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

def get_db_connection(db_file=None):
    """
    Establish a connection to the SQLite database.
    Enforces Foreign Key constraints on every connection instance.
    """
    target_db = db_file or DB_PATH
    conn = sqlite3.connect(target_db)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_file=None):
    """Initialize the database tables using schema.sql."""
    conn = get_db_connection(db_file)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_script = f.read()
    conn.executescript(schema_script)
    conn.commit()
    conn.close()

def query_db(query, args=(), one=False, db_file=None):
    """Helper function to execute read queries and return dictionaries."""
    conn = get_db_connection(db_file)
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    
    dict_results = [dict(row) for row in rv]
    return (dict_results[0] if dict_results else None) if one else dict_results

def execute_db(query, args=(), db_file=None):
    """Helper function to execute insert, update, delete queries."""
    conn = get_db_connection(db_file)
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id
