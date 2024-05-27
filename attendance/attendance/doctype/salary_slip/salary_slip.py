# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals

import datetime
import math
from erpnext.payroll.doctype.salary_slip.salary_slip import SalarySlip

import frappe
from frappe import _, msgprint
from frappe.model.naming import make_autoname
from frappe.utils import (
    add_days,
    cint,
    cstr,
    date_diff,
    flt,
    formatdate,
    get_first_day,
    getdate,
    money_in_words,
    rounded,
)
from frappe.utils.background_jobs import enqueue
from six import iteritems

import erpnext
from erpnext.accounts.utils import get_fiscal_year
from erpnext.hr.utils import get_holiday_dates_for_employee, validate_active_employee
from erpnext.loan_management.doctype.loan_repayment.loan_repayment import (
    calculate_amounts,
    create_repayment_entry,
)
from erpnext.payroll.doctype.additional_salary.additional_salary import get_additional_salaries
from erpnext.payroll.doctype.employee_benefit_application.employee_benefit_application import (
    get_benefit_component_amount,
)
from erpnext.payroll.doctype.employee_benefit_claim.employee_benefit_claim import (
    get_benefit_claim_amount,
    get_last_payroll_period_benefits,
)
from erpnext.payroll.doctype.payroll_entry.payroll_entry import get_start_end_dates
from erpnext.payroll.doctype.payroll_period.payroll_period import (
    get_payroll_period,
    get_period_factor,
)
from erpnext.utilities.transaction_base import TransactionBase


class AttendanceSalarySlip(SalarySlip):

    def add_additional_salary_components(self, component_type):
        calculate_amount_based_on_formula = frappe.db.get_single_value(
            "Payroll Settings", "calculate_amount_based_on_formula_on_additional_salary")
        if not calculate_amount_based_on_formula:
            return super(AttendanceSalarySlip, self).add_additional_salary_components(component_type)
        else:
            additional_salaries = get_additional_salaries(
                self.employee, self.start_date, self.end_date, component_type
            )
            # frappe.msgprint(str(additional_salaries))
            data, default_data = self.get_data_for_eval()
            for additional_salary in additional_salaries:
                amount = 1
                additional_salary.condition, additional_salary.abbr = frappe.db.get_value(
                    "Salary Component", additional_salary.component, ["condition", "salary_component_abbr"])
                additional_salary.amount_based_on_formula, additional_salary.formula = frappe.db.get_value(
                    "Additional Salary", additional_salary.name, ["amount_based_on_formula", "formula"])
                try:
                    amount = self.eval_condition_and_formula(
                        additional_salary, data, precision=0)
                except Exception as e:
                    frappe.msgprint(_("Error While add Additional Salary {} , {}").format(
                        additional_salary.component, _(str(e))))
                amount *= additional_salary.amount
                self.update_component_row(
                    get_salary_component_data(additional_salary.component),
                    amount,
                    component_type,
                    additional_salary,
                    is_recurring=additional_salary.is_recurring,
                )
                default_data[additional_salary.abbr] = amount

    def eval_condition_and_formula(self, d, data, precision=1):
        # try:
        condition = d.condition.strip().replace("\n", " ") if d.condition else None
        if condition:
            if not frappe.safe_eval(condition, self.whitelisted_globals, data):
                return None
        amount = d.amount
        if d.amount_based_on_formula:
            formula = d.formula.strip().replace("\n", " ") if d.formula else None
            if formula:
                if precision:
                    amount = flt(frappe.safe_eval(
                        formula, self.whitelisted_globals, data), d.precision("amount"))
                else:
                    amount = flt(frappe.safe_eval(
                        formula, self.whitelisted_globals, data))
        if amount:
            data[d.abbr] = amount

        return amount

def get_salary_component_data(component):
    return frappe.get_value(
        "Salary Component",
        component,
        [
            "name as salary_component",
            "depends_on_payment_days",
            "salary_component_abbr as abbr",
            "do_not_include_in_total",
            "is_tax_applicable",
            "is_flexible_benefit",
            "variable_based_on_taxable_salary",
        ],
        as_dict=1,
    )
