# Copyright (c) 2023, Peter Maged and contributors
# For license information, please see license.txt

from erpnext import get_company_currency
from erpnext.accounts.doctype.account.account import get_account_currency
from erpnext.setup.utils import get_exchange_rate
import frappe
from frappe.model.document import Document


class CashRewards(Document):

    def on_submit(self):
        self.submit_additional_salary()
        self.submit_additional_salary(component_type="deduction")

        self.make_gl_entries()

    def submit_additional_salary(self, component_type='earning'):
        if not self.amount:
            return

        doc = frappe.new_doc("Additional Salary")
        doc.naming_series = "HR-ADS-.YY.-.MM.-"
        doc.employee = self.employee
        doc.employee_name = self.employee_name
        doc.department = self.department
        doc.company = self.company

        doc.salary_component = self.deduction_additional_salary if component_type == "deduction" else self.earning_additional_salary
        doc.type = component_type
        doc.amount = self.amount
        doc.remark = '' if not self.employee_rewards else frappe.db.get_value(
            "Employee Rewards", self.employee_rewards, 'reward_type')
        doc.overwrite_salary_structure_amount = 0
        doc.ref_doctype = self.doctype
        doc.ref_docname = self.name
        doc.payroll_date = self.posting_date
        doc.flags.ignore_permissions = True
        doc.flags.ignore_mandatory = True
        doc.amount_based_on_formula, doc.formula = frappe.db.get_value(
            "Salary Component", doc.salary_component, ["amount_based_on_formula", "formula"])
        doc.submit()
        # self.ref_doctype = doc.doctype
        # self.ref_docname = doc.name
        # self.db_set('ref_doctype',self.ref_doctype)
        # self.db_set('ref_docname',self.ref_docname)

    def make_gl_entries(self):
        gl_entries = []
        company_currency = get_company_currency(self.company)

        # Payment Account
        account = self.payment_account
        against_account = self.expense_account
        account_currency = get_account_currency(account)
        exchange_rate = get_exchange_rate(
            from_currency=company_currency, to_currency=account_currency, transaction_date=self.posting_date) or 1
        amount_in_account_currency = (self.amount) * exchange_rate

        gl_entries.append({
            "account": account,
            "debit_in_account_currency": 0,
            "debit": 0,
            "credit_in_account_currency": amount_in_account_currency,
            "credit": self.amount,
            "account_currency": account_currency,
            "against": against_account
        })



        # # Employee Debit vs payment Account
        # account = self.employee_reward_account
        # against_account = self.payment_account
        # account_currency = get_account_currency(account)
        # exchange_rate = get_exchange_rate(
        #     from_currency=company_currency, to_currency=account_currency, transaction_date=self.posting_date) or 1
        # amount_in_account_currency = (self.amount) * exchange_rate

        # gl_entries.append({
        #     "account": account,
        #     "debit_in_account_currency": amount_in_account_currency,
        #     "debit": self.amount,
        #     "credit_in_account_currency": 0,
        #     "credit": 0,
        #     "account_currency": account_currency,
        #     "against": against_account,
        #     "party_type": 'Employee',
        #     "party": self.employee
        # })

        # # Employee Credit vs Expense Account
        # account = self.employee_reward_account
        # against_account = self.expense_account
        # gl_entries.append({
        #     "account": account,
        #     "debit_in_account_currency": 0,
        #     "debit": 0,
        #     "credit_in_account_currency": amount_in_account_currency,
        #     "credit": self.amount,
        #     "account_currency": account_currency,
        #     "against": against_account,
        #     "party_type": 'Employee',
        #     "party": self.employee
        # })








        # Expense Account
        account = self.expense_account
        against_account = self.payment_account
        account_currency = get_account_currency(account)
        exchange_rate = get_exchange_rate(
            from_currency=company_currency, to_currency=account_currency, transaction_date=self.posting_date) or 1
        amount_in_account_currency = (self.amount) * exchange_rate

        gl_entries.append({
            "account": account,
            "debit": self.amount,
            "debit_in_account_currency": amount_in_account_currency,
            "credit_in_account_currency": 0,
            "credit": 0,
            "account_currency": account_currency,
            "against": against_account
        })

        # Create GL Entries
        for gl in gl_entries:
            gl.update({
                "doctype": "GL Entry",
                "posting_date": self.posting_date,
                "transaction_date": self.posting_date,
                "company": self.company,
                "voucher_type": self.doctype,
                "voucher_no": self.name,
                "project": self.project,
                "cost_center": self.cost_center,
            })
            gl = frappe.get_doc(gl)
            gl.flags.ignore_permissions = 1
            gl.validate()
            gl.submit()
        frappe.db.commit()

    def on_cancel(self):
        self.clear_employee_rewards_references()

    def on_trash(self):
        self.clear_employee_rewards_references()

    def clear_employee_rewards_references(self):
        sql = f"""
			Update `tabEmployee Rewards` set cash_rewards = '' 
			where  cash_rewards = '{self.name}'
		"""
        frappe.db.sql(sql)
        frappe.db.commit()
