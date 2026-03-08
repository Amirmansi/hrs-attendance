# Copyright (c) 2024, Peter Maged and contributors
# For license information, please see license.txt

from datetime import date, timedelta

import frappe
from frappe import _
from frappe.utils import flt, getdate


def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "fieldname": "employee",
            "label": _("Employee"),
            "fieldtype": "Link",
            "options": "Employee",
            "width": 130,
        },
        {
            "fieldname": "department",
            "label": _("Department"),
            "fieldtype": "Link",
            "options": "Department",
            "width": 130,
        },
        {
            "fieldname": "branch",
            "label": _("Branch"),
            "fieldtype": "Link",
            "options": "Branch",
            "width": 110,
        },
        {
            "fieldname": "attendance_date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "fieldname": "shift",
            "label": _("Shift"),
            "fieldtype": "Link",
            "options": "Shift Type",
            "width": 120,
        },
        {
            "fieldname": "first_in",
            "label": _("First In"),
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "fieldname": "last_out",
            "label": _("Last Out"),
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "fieldname": "device_id",
            "label": _("Device"),
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "fieldname": "actual_hours",
            "label": _("Actual Hrs"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 100,
        },
        {
            "fieldname": "expected_hours",
            "label": _("Expected Hrs"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 110,
        },
        {
            "fieldname": "variance",
            "label": _("Variance"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 100,
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 140,
        },
    ]


def get_data(filters):
    from_date = getdate(filters.get("from_date"))
    to_date = getdate(filters.get("to_date"))
    company = filters.get("company")
    smart_filter = filters.get("smart_filter")

    # Build employee WHERE conditions
    emp_conditions = "emp.status IN ('Active', 'Suspended')"
    if company:
        emp_conditions += " AND emp.company = %(company)s"
    if filters.get("employee"):
        emp_conditions += " AND emp.name = %(employee)s"
    if filters.get("branch"):
        emp_conditions += " AND emp.branch = %(branch)s"
    if filters.get("department"):
        emp_conditions += " AND emp.department = %(department)s"
    if filters.get("shift_type"):
        emp_conditions += " AND emp.default_shift = %(shift_type)s"
    if filters.get("attendance_rule"):
        emp_conditions += " AND emp.attendance_rule = %(attendance_rule)s"

    # Fetch all matching employees with their shift / attendance rule info
    employees = frappe.db.sql(
        f"""
        SELECT
            emp.name AS employee,
            emp.employee_name,
            emp.department,
            emp.branch,
            emp.default_shift,
            emp.attendance_rule
        FROM tabEmployee emp
        WHERE {emp_conditions}
        ORDER BY emp.name
        """,
        filters,
        as_dict=1,
    )

    if not employees:
        return []

    employee_names = [e.employee for e in employees]

    # Fetch expected hours per employee (from Shift Type or Attendance Rule)
    expected_hours_map = _build_expected_hours_map(employees)

    # Fetch all checkin logs in date range for these employees (optimized single query)
    checkin_logs = frappe.db.sql(
        """
        SELECT
            ec.employee,
            DATE(ec.time) AS attendance_date,
            MIN(ec.time) AS first_in_time,
            MAX(ec.time) AS last_out_time,
            COUNT(ec.name) AS log_count,
            MAX(ec.device_id) AS device_id,
            MAX(ec.shift) AS shift
        FROM `tabEmployee Checkin` ec
        WHERE ec.employee IN %(employees)s
          AND DATE(ec.time) BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY ec.employee, DATE(ec.time)
        ORDER BY ec.employee, DATE(ec.time)
        """,
        {
            "employees": employee_names,
            "from_date": from_date,
            "to_date": to_date,
        },
        as_dict=1,
    )

    # Build a lookup: (employee, date) -> log summary
    log_map = {}
    for log in checkin_logs:
        key = (log.employee, str(log.attendance_date))
        log_map[key] = log

    # Build employee info map
    emp_map = {e.employee: e for e in employees}

    # Generate rows for every (employee, workday) in the date range
    rows = []
    grace_minutes = 5  # 5-minute grace for "Present"

    current_date = from_date
    while current_date <= to_date:
        date_str = str(current_date)
        for emp in employees:
            emp_name = emp.employee
            key = (emp_name, date_str)
            log = log_map.get(key)

            expected_hrs = expected_hours_map.get(emp_name, 0.0)
            shift_name = emp.default_shift or (log.shift if log else None)

            if log is None:
                # No checkin at all → Absent
                status = "Absent"
                row = {
                    "employee": emp_name,
                    "employee_name": emp.employee_name,
                    "department": emp.department,
                    "branch": emp.branch,
                    "attendance_date": current_date,
                    "shift": shift_name,
                    "first_in": "",
                    "last_out": "",
                    "device_id": "",
                    "actual_hours": 0.0,
                    "expected_hours": expected_hrs,
                    "variance": flt(-expected_hrs, 2),
                    "variance_raw": -expected_hrs,
                    "status": status,
                }
            else:
                first_in = log.first_in_time
                last_out = log.last_out_time
                log_count = log.log_count or 0

                if log_count == 1:
                    status = "Missing Punch"
                    actual_hrs = 0.0
                else:
                    diff = last_out - first_in
                    actual_hrs = flt(diff.total_seconds() / 3600.0, 2)
                    grace_hrs = grace_minutes / 60.0
                    if actual_hrs >= (expected_hrs - grace_hrs):
                        status = "Present"
                    else:
                        status = "Late / Short Hours"

                variance = flt(actual_hrs - expected_hrs, 2)
                row = {
                    "employee": emp_name,
                    "employee_name": emp.employee_name,
                    "department": emp.department,
                    "branch": emp.branch,
                    "attendance_date": current_date,
                    "shift": shift_name,
                    "first_in": str(first_in.strftime("%H:%M:%S")) if first_in else "",
                    "last_out": str(last_out.strftime("%H:%M:%S")) if last_out else "",
                    "device_id": log.device_id or "",
                    "actual_hours": actual_hrs,
                    "expected_hours": expected_hrs,
                    "variance": variance,
                    "variance_raw": variance,
                    "status": status,
                }

            rows.append(row)

        current_date += timedelta(days=1)

    # Apply smart filter
    if smart_filter:
        rows = [r for r in rows if r.get("status") == smart_filter]

    return rows


def _build_expected_hours_map(employees):
    """Build a dict mapping employee -> expected working hours per day.

    Priority:
    1. Employee.default_shift → computed from Shift Type.start_time / end_time
    2. Employee.attendance_rule → Attendance Rule.working_hours_per_day
    """
    expected = {}

    # Collect unique shifts and attendance rules
    shifts = list({e.default_shift for e in employees if e.default_shift})
    rules = list({e.attendance_rule for e in employees if e.attendance_rule})

    shift_hours = {}
    if shifts:
        shift_data = frappe.db.sql(
            """
            SELECT name, start_time, end_time
            FROM `tabShift Type`
            WHERE name IN %(shifts)s
            """,
            {"shifts": shifts},
            as_dict=1,
        )
        for s in shift_data:
            # Calculate working hours from start_time and end_time (ERPNext v15 has no working_hours column)
            start_sec = s.start_time.total_seconds() if s.start_time else 0
            end_sec = s.end_time.total_seconds() if s.end_time else 0
            if end_sec >= start_sec:
                hours = (end_sec - start_sec) / 3600
            else:
                # Overnight shift (e.g. 22:00 -> 06:00)
                hours = (86400 - start_sec + end_sec) / 3600
            shift_hours[s.name] = flt(hours)

    rule_hours = {}
    if rules:
        rule_data = frappe.db.sql(
            """
            SELECT name, working_hours_per_day
            FROM `tabAttendance Rule`
            WHERE name IN %(rules)s
            """,
            {"rules": rules},
            as_dict=1,
        )
        for r in rule_data:
            rule_hours[r.name] = flt(r.working_hours_per_day or 0)

    for emp in employees:
        if emp.default_shift and emp.default_shift in shift_hours:
            expected[emp.employee] = shift_hours[emp.default_shift]
        elif emp.attendance_rule and emp.attendance_rule in rule_hours:
            expected[emp.employee] = rule_hours[emp.attendance_rule]
        else:
            expected[emp.employee] = 0.0

    return expected
