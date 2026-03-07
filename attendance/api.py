
from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import date
from dateutil.parser import parse



field_dict = {
    "Leave Application":"from_date",
    "Daily Overtime Request":"date",
    "Visit Form":"date",
    "Permission Application":"day",
}

allowed_roles = ["System Manager","HR Manager"]

def before_insert (doc,fun=''):
    user_roles = frappe.get_roles()
    is_manger = any((x in allowed_roles) for x in user_roles)
    if is_manger:
                return True
    
    employee_request_max_limit = frappe.db.get_single_value("Attendance Settings","employee_request_max_limit") or 0
    if not employee_request_max_limit :
        return True

    field = field_dict.get(doc.doctype)
    posting_date = getattr(doc,field)
    if posting_date :
        posting_date = parse(str(posting_date)).date()
        diff_days = (date.today() - posting_date).days + 1
        # frappe.msgprint(str('diff_days'))
        # frappe.msgprint(str(diff_days))
        # frappe.msgprint(str('employee_request_max_limit'))
        # frappe.msgprint(str(employee_request_max_limit))
         
        if employee_request_max_limit < diff_days :
            frappe.throw(_("Can't Create Request after {} Days".format(employee_request_max_limit)))
        

def validate (doc,fun=''):
    user_roles = frappe.get_roles()
    # is_manger = any((x in allowed_roles) for x in user_roles)
    is_manger = ("System Manager" in user_roles)
    if is_manger:
                return True
    
    approve_request_max_limit = frappe.db.get_single_value("Attendance Settings","approve_request_max_limit") or 0
    if not approve_request_max_limit :
        return True

    field = field_dict.get(doc.doctype)
    posting_date = getattr(doc,field)
    if posting_date :
        posting_date = parse(str(posting_date)).date()
        diff_days = (date.today() - posting_date).days + 1
        # frappe.msgprint(str('diff_days'))
        # frappe.msgprint(str(diff_days))
        # frappe.msgprint(str('approve_request_max_limit'))
        # frappe.msgprint(str(approve_request_max_limit))
         
        if approve_request_max_limit < diff_days :
            frappe.throw(_("Can't Edit Request after {} Days".format(approve_request_max_limit)))




def validate_salary_slip(self,fun=''):
    update_salary_slip_remark(self.name)
    for row in self.earnings :
        if getattr(row,'customer',None) :
            res = frappe.db.sql(
                """
                select count(*) from tabAttendance
                where customer = %s and docstatus = 1
                and date(attendance_date) between date(%s) and date(%s)
                and employee = %s
                """,
                (row.customer, self.start_date, self.end_date, self.employee),
            ) or []
            row.no_of_visits = (res[0][0] or 0) if res else 0

            frappe.db.sql(
                """
                update `tabSalary Detail` s
                set s.no_of_visits = %s
                where name = %s
                """,
                (row.no_of_visits, row.name),
            )
            frappe.db.commit()



def update_salary_slip_remark(name=None):
        base_sql = """
        update `tabSalary Detail` s
        set s.remark = (select t.remark from `tabAdditional Salary` t where t.name = s.additional_salary order by name limit 1)
        where ifnull(s.additional_salary,'') <> ''
        """
        if name:
            frappe.db.sql(base_sql + " and s.parent = %s", (name,))
        else:
            frappe.db.sql(base_sql)
        frappe.db.commit()
