-- 1. Список сотрудников: выборка без фильтра.
SELECT id, name, vacation_days_available, vacation_days_total
FROM employees
ORDER BY name, id;

-- 2. Постраничная выборка сотрудников (LIMIT и OFFSET).
SELECT id, name, vacation_days_available, vacation_days_total
FROM employees
ORDER BY name, id
LIMIT ? OFFSET ?;

-- 3. Справочник типов отпуска.
SELECT id, name, deducts_vacation_days
FROM vacation_types
ORDER BY id;

-- 4. Поиск сотрудника по первичному ключу (WHERE).
SELECT id, name, vacation_days_available, vacation_days_total
FROM employees
WHERE id = ?;

-- 5. Поиск заявок по статусу (WHERE, параметризованный запрос).
SELECT id, employee_id, vacation_type_id, start_date, end_date, duration,
       status
FROM leave_requests
WHERE status = ?
ORDER BY start_date, id;

-- 6. Все заявки с именем сотрудника и названием типа отпуска (JOIN).
SELECT leave_requests.id, employees.name AS employee_name,
       vacation_types.name AS vacation_name, leave_requests.start_date,
       leave_requests.end_date, leave_requests.duration, leave_requests.status
FROM leave_requests
JOIN employees ON leave_requests.employee_id = employees.id
JOIN vacation_types ON leave_requests.vacation_type_id = vacation_types.id
ORDER BY leave_requests.start_date, leave_requests.id;

-- 7. Активные заявки (JOIN и фильтрация по состоянию).
SELECT leave_requests.id, employees.name AS employee_name,
       vacation_types.name AS vacation_name, leave_requests.start_date,
       leave_requests.end_date, leave_requests.duration, leave_requests.status
FROM leave_requests
JOIN employees ON leave_requests.employee_id = employees.id
JOIN vacation_types ON leave_requests.vacation_type_id = vacation_types.id
WHERE leave_requests.status IN ('pending', 'approved')
ORDER BY leave_requests.start_date, leave_requests.id;

-- 8. Сотрудники, свободные на выбранную дату (параметризованный WHERE).
SELECT employees.id, employees.name
FROM employees
WHERE NOT EXISTS (
    SELECT 1
    FROM leave_requests
    WHERE leave_requests.employee_id = employees.id
      AND leave_requests.status IN ('pending', 'approved')
      AND leave_requests.start_date <= ?
      AND leave_requests.end_date >= ?
)
ORDER BY employees.name, employees.id;

-- 9. Сводное количество заявок (COUNT).
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
FROM leave_requests;

-- 10. Количество активных заявок (COUNT).
SELECT COUNT(*) AS active_request_count
FROM leave_requests
WHERE status IN ('pending', 'approved');

-- 11. Количество заявок выбранного сотрудника (COUNT и WHERE).
SELECT COUNT(*) AS request_count
FROM leave_requests
WHERE employee_id = ?;

-- 12. Количество заявок по статусам (COUNT и GROUP BY).
SELECT status, COUNT(*) AS request_count
FROM leave_requests
GROUP BY status
ORDER BY status;

-- 13. Активные заявки по сотрудникам (COUNT, SUM и GROUP BY).
SELECT
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
ORDER BY employees.name, employees.id;

-- 14. Количество активных заявок по типам отпуска (JOIN и GROUP BY).
SELECT vacation_types.name AS vacation_name,
       COUNT(leave_requests.id) AS active_request_count
FROM vacation_types
LEFT JOIN leave_requests
    ON vacation_types.id = leave_requests.vacation_type_id
    AND leave_requests.status IN ('pending', 'approved')
GROUP BY vacation_types.id, vacation_types.name
ORDER BY vacation_types.id;

-- 15. Сотрудники, у которых больше одной активной заявки (HAVING).
SELECT employees.name AS employee_name,
       COUNT(leave_requests.id) AS active_request_count
FROM employees
JOIN leave_requests ON employees.id = leave_requests.employee_id
WHERE leave_requests.status IN ('pending', 'approved')
GROUP BY employees.id, employees.name
HAVING COUNT(leave_requests.id) > 1
ORDER BY active_request_count DESC, employee_name;

-- 16. Общее количество сотрудников для пагинации списка.
SELECT COUNT(*) AS employee_count
FROM employees;
