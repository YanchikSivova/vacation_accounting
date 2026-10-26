CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    vacation_days_available INTEGER NOT NULL
        CHECK (vacation_days_available BETWEEN 0 AND 28),
    vacation_days_total INTEGER NOT NULL
        CHECK (vacation_days_total BETWEEN 0 AND 28),
    CHECK (vacation_days_available <= vacation_days_total)
);

CREATE TABLE IF NOT EXISTS vacation_types (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    deducts_vacation_days INTEGER NOT NULL
        CHECK (deducts_vacation_days IN (0, 1))
);

CREATE TABLE IF NOT EXISTS leave_requests (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    vacation_type_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    duration INTEGER NOT NULL CHECK (duration > 0),
    status TEXT NOT NULL
        CHECK (status IN ('pending', 'approved', 'cancelled')),
    CHECK (start_date <= end_date),
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (vacation_type_id) REFERENCES vacation_types(id)
);

CREATE INDEX IF NOT EXISTS leave_requests_employee_dates_idx
    ON leave_requests (employee_id, start_date, end_date);

CREATE INDEX IF NOT EXISTS leave_requests_status_idx
    ON leave_requests (status);
