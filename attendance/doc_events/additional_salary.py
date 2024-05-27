import frappe

def on_trash(doc,method='') :
    clear_employee_rewards_references(doc)


def on_cancel(doc,method='') :
    clear_employee_rewards_references(doc)


def clear_employee_rewards_references(doc):
    sql = f"""
        Update `tabEmployee Rewards` set ref_doctype = '' , ref_docname = ''
        where ref_doctype = '{doc.doctype}' and ref_docname = '{doc.name}'
    """
    frappe.db.sql(sql)
    frappe.db.commit()
    

    