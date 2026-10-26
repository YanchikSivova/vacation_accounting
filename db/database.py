import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / 'data' / 'vacation_accounting.sqlite'


def get_connection(
    db_path: str | Path | None = None,
) -> sqlite3.Connection:
    """Open a SQLite connection with named rows and foreign keys enabled."""
    database_path = Path(db_path) if db_path is not None else DB_PATH
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    return connection
