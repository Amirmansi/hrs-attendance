# attendance.py

from datetime import datetime

import frappe
from attendance.attendance.doctype.late_entry_early_exit_table.late_entry_early_exit_table import (
    LateEntryEarlyExitTable,
)
from frappe.utils import get_datetime
from hrms.hr.doctype.attendance.attendance import Attendance as AttendanceHRMS


def validate(doc: AttendanceHRMS, method: str = "") -> None:
    # We need Shift to be set
    if not doc.get("shift"):
        return

    shift_doc = frappe.get_doc("Shift Type", doc.shift)

    # If There if only one Checkin or Checkout
    if (
        doc.get("actual_start_datetime") is not None
        and doc.get("actual_end_datetime") is None
    ) or (
        doc.get("actual_start_datetime") is None
        and doc.get("actual_end_datetime") is not None
    ):
        if shift_doc.get("custom_consider_only_check_as"):
            doc.set("status", shift_doc.custom_consider_only_check_as)

    # If Both Checkin and Checkout are not present
    elif not doc.get("actual_start_datetime") and not doc.get("actual_end_datetime"):
        return

    # If Both Checkin and Checkout are present
    else:
        in_time: datetime = get_datetime(doc.actual_start_datetime)
        out_time: datetime = get_datetime(doc.actual_end_datetime)

        shift_start_time: datetime = datetime.combine(
            in_time.date(), datetime.min.time()
        ) + shift_doc.get("start_time")
        shift_end_time: datetime = datetime.combine(
            out_time.date(), datetime.min.time()
        ) + shift_doc.get("end_time")

        if in_time > shift_start_time and shift_doc.get("custom_late_entry_policy"):
            late_entry_policy_doc: LateEntryEarlyExitTable = frappe.get_doc(
                "Late Entry Early Exit Table",
                shift_doc.custom_late_entry_policy,
            )

            late, based_on, deduction = (
                late_entry_policy_doc.calculate_deduction_result(
                    shift_start_time, in_time
                )
            )

            if late:
                if based_on == "Status":
                    doc.set("status", deduction)
                elif based_on == "Percent":
                    doc.set("deduction", deduction)

        elif out_time < shift_end_time and shift_doc.get("custom_early_exit_policy"):
            early_exit_policy_doc: LateEntryEarlyExitTable = frappe.get_doc(
                "Late Entry Early Exit Table",
                shift_doc.custom_early_exit_policy,
            )

            early, based_on, deduction = (
                early_exit_policy_doc.calculate_deduction_result(
                    out_time, shift_end_time
                )
            )

            if early:
                if based_on == "Status":
                    doc.set("status", deduction)
                elif based_on == "Percent":
                    doc.set("deduction", deduction)
