# Copyright (c) 2023, Peter Maged and contributors
# For license information, please see license.txt


from unittest import result
import frappe
from frappe import _


def execute(filters=None):
    columns, data = [], []
    components = get_components(filters)
    columns = get_columns(components)
    data = get_data(filters,components)
    return columns, data


def get_columns(components=[]):
    columns = [
        {
            "fieldname": "employee",
            "label": _("Employee"),
            "fieldtype": "Link",
            "options": "Employee",
            "width": 250
        },
        {
            "fieldname": "employee_name",
            "label": _("Employee Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "designation",
            "label": _("Designation"),
            "fieldtype": "Link",
            "options": "Designation",
            "width": 120
        },

        {
            "fieldname": "annual_increase_limit",
            "label": _("Annual Increase Limit"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 120
        },
        {
            "fieldname": "year_increase",
            "label": _("Years Increments"),
            "fieldtype": "Percent",
            "precision": 2,
            "width": 120
        },


        {
            "fieldname": "total_visits",
            "label": _("Total Visits"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 120
        },

        {
            "fieldname": "project",
            "label": _("Project"),
            "fieldtype": "Link",
            "options": "Project",
            "width": 90
        },
        {
            "fieldname": "customer",
            "label": _("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
            "width": 90
        },
        {
            "fieldname": "experience_years",
            "label": _("Experience Years"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 90
        },
        {
            "fieldname": "grade",
            "label": _("Grade"),
            "fieldtype": "Link",
            "options": "Employee Grade",
            "width": 120
        },
    ]

    for comp in components:
        columns.append({
            "fieldname": comp,
            "label": _(comp),
            "fieldtype": "Float",
            "precision": 2,
            "width": 150
        })

    columns.append({
        "fieldname": "amount",
        "label": _("Total Components"),
        "fieldtype": "Float",
        "precision": 2,
        "width": 100
    })

    columns.append({
        "fieldname": "total_increase",
        "label": _("Total Increase"),
        "fieldtype": "Float",
        "precision": 2,
        "width": 100
    })

    columns.append({
        "fieldname": "total_amount_increase",
        "label": _("Total Components Increase"),
        "fieldtype": "Float",
        "precision": 2,
        "width": 100
    })

    columns.append({
        "fieldname": "total_amount",
        "label": _("Total"),
        "fieldtype": "Float",
        "precision": 2,
        "width": 100
    })

    return columns


def get_data(filters,components=[]):
    conditions = get_employee_filters(filters or {})
    columns = ""
    component_option_cond = """
    and ( 
        component_option.type in ('All') 
        or (component_option.type in ('Grade') and component_option.grade = emp.grade )
        or (component_option.type in ('Expatriate') and emp.expatriate = 1 ) 
        or (component_option.type in ('Resident') and emp.expatriate <> 1 ) 
        or (component_option.type in ('Years of Service') and component_option.number_of_years = emp.experience_years ) 
        
        )
    """

    for comp in components :
        columns += f""" 
        
        (
            select SUM(amount) from `tabComponent Detail` comp 
            inner join `tabComponent Option` component_option on component_option.name = comp.component_option        
            where comp.parent = visit.name 
            {component_option_cond} 
            and comp.salary_component = '{comp}'
        ) as `{comp}`
        ,
        """
    columns += f""" 

            ifnull((
                select SUM(amount) from `tabComponent Detail` comp 
                inner join `tabComponent Option` component_option on component_option.name = comp.component_option
                where comp.parent = visit.name 
                {component_option_cond} 
                and comp.include_in_yearly_increments = 1
            ),0) as `amount_increase`
            ,
    """

    sql = f"""

    select 
        * ,
        (year_increase * amount_increase / 100) as total_increase ,
        ( amount + (year_increase * amount_increase / 100) ) as total_amount_increase ,
        (total_visits * ( amount + (year_increase * amount_increase / 100) ) ) as total_amount
    from
    ( select 
            emp.name as employee ,
            emp.employee_name ,
            emp.designation ,
            emp.grade ,
            emp.annual_increase_limit ,
            # count(DISTINCT log.name) as total_visits ,
            SUM(
                CASE 
                    WHEN log.work_day = 'Full Day'  THEN 1 
                    WHEN log.work_day = 'Day and Half'  THEN 1.5
                    WHEN log.work_day = 'Half Day'  THEN 0.5 
                    WHEN log.work_day = 'Three Half (0.75)'  THEN 0.75
                    WHEN log.work_day = 'Day and Quarter (1.25)'  THEN 1.25
                    WHEN log.work_day = 'Quarter'  THEN 0.25
                    Else 1 
                END

            ) as total_visits ,
            emp.experience_years ,
            log.project ,
            log.customer ,
            log.shift ,
            {columns}
            ifnull(
                (
                    select SUM(visit_percent.percent) from `tabSite Visit Percent` visit_percent
                    where visit_percent.parent = visit.name 
                    and visit_percent.from_year <= emp.annual_increase_limit
                ) 
            , 0) as year_increase , 
            (
                select SUM(amount) from `tabComponent Detail` comp 
                inner join `tabComponent Option` component_option on component_option.name = comp.component_option
                where comp.parent = visit.name 
                {component_option_cond} 
            ) as amount 
    from
        tabEmployee emp
    inner join tabAttendance log on
        log.employee = emp.name
    Left join `tabSite Visit Fee` visit on
            log.shift = visit.shift
            and log.customer = visit.customer
            and emp.designation = visit.designation
            and visit.docstatus = 1

    where emp.name like '%OUT%'
    {conditions}
    group by
        emp.name ,
        log.shift,
        log.customer
    ) t
    """
    return frappe.db.sql(sql, as_dict=1)


def get_employee_filters(filters):
    from_date, to_date = filters.get('from_date'), filters.get('to_date')

    conditions = f"and log.docstatus = 1 and log.attendance_date Between date('{from_date}') And date('{to_date}')"
    data = filters.get("company")
    if data:
        conditions += f" and emp.company = '{data}' "

    data = filters.get("employee")
    if data:
        conditions += f" and emp.name = '{data}' "

    data = filters.get("branch")
    if data:
        conditions += f" and emp.branch = '{data}' "
    data = filters.get("grade")
    if data:
        conditions += f" and emp.grade = '{data}' "
    data = filters.get("designation")
    if data:
        conditions += f" and emp.designation = '{data}' "
    data = filters.get("department")
    if data:
        conditions += f" and emp.department = '{data}' "
    return conditions


def get_components(filters=None):
    conditions = get_employee_filters(filters or {})
    sql = f"""
		select
			Distinct(comp.salary_component) as salary_component
		from
			tabEmployee emp
		inner join tabAttendance log on
			log.employee = emp.name
		inner join `tabSite Visit Fee` visit on
			log.shift = visit.shift
			and log.customer = visit.customer
            and emp.designation = visit.designation
            and visit.docstatus = 1
		inner join `tabComponent Detail` comp on
			visit.name = comp.parent
        where emp.name like '%OUT%'
        {conditions}

    """
    return frappe.db.sql_list(sql)
