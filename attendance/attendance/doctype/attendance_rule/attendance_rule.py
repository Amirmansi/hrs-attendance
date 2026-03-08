# Copyright (c) 2021, Peter Maged and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class AttendanceRule(Document):
	def validate(self):
		self.validate_work_details()
		self.validate_late_rule()
		self.validate_overtime_rule()
		self.validate_absent_rule()
		self.validate_fingerprint_penalty()
		self.validate_late_penalty()
		self.validate_less_time()
		self.validate_shift_bonus()
		self.validate_leaves_without_pay()
		self.validate_visit_form()

	def validate_work_details(self):
		if not self.working_hours_per_day or self.working_hours_per_day <= 0:
			frappe.throw(_("Working Hours Per Day must be greater than zero."))
		if not self.working_days_per_month or self.working_days_per_month <= 0:
			frappe.throw(_("Working Days Per Month must be greater than zero."))
		if self.working_type == "Monthly Target Hour" and (
			not self.working_hours_per_month or self.working_hours_per_month <= 0
		):
			frappe.throw(_("Target Hours Per Month must be greater than zero when Working Type is 'Monthly Target Hour'."))

	def validate_late_rule(self):
		if self.enable_late_rule:
			if self.late_salary and not self.salary_component:
				frappe.throw(_("Late Salary Component is required when 'Deduct From Salary' is enabled in Late Rule."))
			if self.late_leave_balance and not self.late_leave_component:
				frappe.throw(_("Late Leave Component is required when 'Deduct From Leave Balance' is enabled in Late Rule."))

	def validate_overtime_rule(self):
		if self.enable_overtime:
			for row in self.overtime_rules or []:
				if not row.overtime_salary_component:
					frappe.throw(_("Overtime Salary Component is required in Overtime Rules row {0}.").format(row.idx))

	def validate_absent_rule(self):
		if self.enable_absent:
			if self.absent_salary and not self.absent_salary_component:
				frappe.throw(_("Absent Salary Component is required when 'Deduct From Salary' is enabled in Absent Rule."))
			if self.absent_leave_balance and not self.absent_leave_component:
				frappe.throw(_("Absent Leave Component is required when 'Deduct From Leave Balance' is enabled in Absent Rule."))
			if (self.absent_factor or 0) < 0:
				frappe.throw(_("Absent Factor cannot be negative."))

	def validate_fingerprint_penalty(self):
		if self.enable_fingerprint_penalty:
			if not self.fingerprint_penalty_salary_component:
				frappe.throw(_("Fingerprint Penalty IN Salary Component is required when Fingerprint Penalty is enabled."))

	def validate_late_penalty(self):
		if self.enable_late_penalty:
			if self.deduct_late_penalty_from_salary and not self.late_penalty_salary_component:
				frappe.throw(_("Late Penalty Salary Component is required when 'Deduct From Salary' is enabled in Late Penalty."))
			if self.deduct_late_penalty_from_leave_balance and not self.late_penalty_leave_type:
				frappe.throw(_("Late Penalty Leave Type is required when 'Deduct From Leave Balance' is enabled in Late Penalty."))

	def validate_less_time(self):
		if self.less_time:
			if self.less_salary and not self.less_time_salary_component:
				frappe.throw(_("Less Time Salary Component is required when 'Deduct From Salary' is enabled in Less Time Details."))

	def validate_shift_bonus(self):
		if self.enable_shift_bonus and not self.shift_bonus_component:
			frappe.throw(_("Shift Bonus Salary Component is required when Shift Bonus is enabled."))

	def validate_leaves_without_pay(self):
		if self.enable_leaves and not self.leaves_salary_component:
			frappe.throw(_("Leaves Salary Component is required when Leaves Without Pay is enabled."))

	def validate_visit_form(self):
		if self.enable_site_visit and not self.visit_form_salary_component:
			frappe.throw(_("Visit Salary Component is required when Visit Calculation is enabled."))
