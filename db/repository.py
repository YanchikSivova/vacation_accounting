from datetime import date
import sqlite3

from db.database import get_connection

REQUEST_STATUSES = ('pending', 'approved', 'cancelled')


def _fetch_all(
    query: str,
    parameters: tuple = (),
) -> list[sqlite3.Row]:
    connection = get_connection()
    try:
        return connection.execute(query, parameters).fetchall()
    finally:
        connection.close()


def _fetch_one(
    query: str,
    parameters: tuple = (),
) -> sqlite3.Row | None:
    connection = get_connection()
    try:
        return connection.execute(query, parameters).fetchone()
    finally:
        connection.close()


def list_employees(limit: int = 10, offset: int = 0) -> list[sqlite3.Row]:
    return _fetch_all(
        """
        SELECT
            id,
            name,
            vacation_days_available,
            vacation_days_total
        FROM employees
        ORDER BY name, id
        LIMIT ? OFFSET ?
        """,
        (limit, offset),
    )


def count_employees() -> int:
    row = _fetch_one('SELECT COUNT(*) AS employee_count FROM employees')
    return row['employee_count']


def find_employee(employee_id: int) -> sqlite3.Row | None:
    return _fetch_one(
        """
        SELECT
            id,
            name,
            vacation_days_available,
            vacation_days_total
        FROM employees
        WHERE id = ?
        """,
        (employee_id,),
    )


def list_vacation_types() -> list[sqlite3.Row]:
    return _fetch_all(
        """
        SELECT id, name, deducts_vacation_days
        FROM vacation_types
        ORDER BY id
        """
    )


def list_requests(
    status: str | None = None,
    active_only: bool = False,
) -> list[sqlite3.Row]:
    return _fetch_all(
        """
        SELECT
            leave_requests.id,
            leave_requests.employee_id,
            employees.name AS employee_name,
            leave_requests.vacation_type_id,
            vacation_types.name AS vacation_name,
            vacation_types.deducts_vacation_days,
            leave_requests.start_date,
            leave_requests.end_date,
            leave_requests.duration,
            leave_requests.status
        FROM leave_requests
        JOIN employees
            ON leave_requests.employee_id = employees.id
        JOIN vacation_types
            ON leave_requests.vacation_type_id = vacation_types.id
        WHERE (
            (? = 1 AND leave_requests.status IN ('pending', 'approved'))
            OR (
                ? = 0
                AND (? IS NULL OR leave_requests.status = ?)
            )
        )
        ORDER BY leave_requests.start_date, leave_requests.id
        """,
        (int(active_only), int(active_only), status, status),
    )


def find_request(request_id: int) -> sqlite3.Row | None:
    return _fetch_one(
        """
        SELECT
            leave_requests.id,
            leave_requests.employee_id,
            employees.name AS employee_name,
            leave_requests.vacation_type_id,
            vacation_types.name AS vacation_name,
            leave_requests.start_date,
            leave_requests.end_date,
            leave_requests.duration,
            leave_requests.status
        FROM leave_requests
        JOIN employees
            ON leave_requests.employee_id = employees.id
        JOIN vacation_types
            ON leave_requests.vacation_type_id = vacation_types.id
        WHERE leave_requests.id = ?
        """,
        (request_id,),
    )


def find_available_employees(on_date: date) -> list[sqlite3.Row]:
    selected_date = on_date.isoformat()
    return _fetch_all(
        """
        SELECT
            employees.id,
            employees.name,
            employees.vacation_days_available,
            employees.vacation_days_total
        FROM employees
        WHERE NOT EXISTS (
            SELECT 1
            FROM leave_requests
            WHERE leave_requests.employee_id = employees.id
                AND leave_requests.status IN ('pending', 'approved')
                AND leave_requests.start_date <= ?
                AND leave_requests.end_date >= ?
        )
        ORDER BY employees.name, employees.id
        """,
        (selected_date, selected_date),
    )


def request_statistics() -> dict[str, object]:
    summary = _fetch_one(
        """
        SELECT
            COUNT(*) AS total_requests,
            COALESCE(
                SUM(
                    CASE
                        WHEN status IN ('pending', 'approved') THEN 1
                        ELSE 0
                    END
                ),
                0
            ) AS active_requests
        FROM leave_requests
        """
    )
    by_employee = _fetch_all(
        """
        SELECT
            employees.id,
            employees.name AS employee_name,
            COUNT(
                CASE
                    WHEN leave_requests.status IN ('pending', 'approved')
                    THEN leave_requests.id
                END
            ) AS active_request_count,
            COALESCE(
                SUM(
                    CASE
                        WHEN leave_requests.status IN ('pending', 'approved')
                            AND vacation_types.deducts_vacation_days = 1
                        THEN leave_requests.duration
                        ELSE 0
                    END
                ),
                0
            ) AS active_paid_days
        FROM employees
        LEFT JOIN leave_requests
            ON employees.id = leave_requests.employee_id
        LEFT JOIN vacation_types
            ON leave_requests.vacation_type_id = vacation_types.id
        GROUP BY employees.id, employees.name
        ORDER BY employees.name, employees.id
        """
    )
    by_vacation_type = _fetch_all(
        """
        SELECT
            vacation_types.id,
            vacation_types.name AS vacation_name,
            COUNT(
                CASE
                    WHEN leave_requests.status IN ('pending', 'approved')
                    THEN leave_requests.id
                END
            ) AS active_request_count
        FROM vacation_types
        LEFT JOIN leave_requests
            ON vacation_types.id = leave_requests.vacation_type_id
        GROUP BY vacation_types.id, vacation_types.name
        ORDER BY vacation_types.id
        """
    )
    high_activity = _fetch_all(
        """
        SELECT
            employees.id,
            employees.name AS employee_name,
            COUNT(leave_requests.id) AS active_request_count
        FROM employees
        JOIN leave_requests
            ON employees.id = leave_requests.employee_id
        WHERE leave_requests.status IN ('pending', 'approved')
        GROUP BY employees.id, employees.name
        HAVING COUNT(leave_requests.id) > 1
        ORDER BY active_request_count DESC, employees.name
        """
    )
    return {
        'summary': summary,
        'by_employee': by_employee,
        'by_vacation_type': by_vacation_type,
        'high_activity': high_activity,
    }
