# Copyright (c) 2025, Peter Maged and contributors
# For license information, please see license.txt

from datetime import datetime, timedelta
from typing import Literal

# import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt

from attendance.attendance.doctype.late_entry_early_exit_child_table.late_entry_early_exit_child_table import (
    LateEntryEarlyExitChildTable,
)


class LateEntryEarlyExitTable(Document):
    def calculate_deduction_result(
        self,
        start_time: datetime,
        end_time: datetime,
    ) -> tuple[bool, Literal["", "Percent", "Status"], str | float]:
        diff = end_time - start_time

        if diff <= timedelta(minutes=0):
            return False, "", ""

        highest_late_entry_policy: LateEntryEarlyExitChildTable | None = None
        for row in self.get("policy_table", default=[]):
            if timedelta(minutes=row.get("from_minutes")) <= diff:
                if cint(row.get("to_minutes")) == 0:
                    highest_late_entry_policy = row
                    break

            if diff < timedelta(minutes=row.get("to_minutes")):
                highest_late_entry_policy = row

        if highest_late_entry_policy:
            based_on = highest_late_entry_policy.get("based_on")
            deduction: str | float = ""
            if based_on == "Status":
                deduction = highest_late_entry_policy.get("status")
            elif based_on == "Percent":
                deduction = flt(highest_late_entry_policy.get("deduction_percent"))

            return True, based_on, deduction

        return False, "", ""
