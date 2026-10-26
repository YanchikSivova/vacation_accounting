from pathlib import Path

from db.database import DB_PATH, PROJECT_ROOT, get_connection

SCHEMA_PATH = PROJECT_ROOT / 'sql' / 'schema.sql'


def create_database(db_path: str | Path | None = None) -> None:
    """Create the SQLite tables from the checked-in SQL schema."""
    database_path = Path(db_path) if db_path is not None else DB_PATH
    database_path.parent.mkdir(parents=True, exist_ok=True)
    schema = SCHEMA_PATH.read_text(encoding='utf-8')

    connection = get_connection(database_path)
    try:
        connection.executescript(schema)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == '__main__':
    create_database()
    print(f'SQLite schema created at {DB_PATH}')
