import frappe

def on_trash(doc,method='') :
    clear_employee_rewards_references(doc)


def on_cancel(doc,method='') :
    clear_employee_rewards_references(doc)


def clear_employee_rewards_references(doc):
    frappe.db.sql(
        """
        Update `tabEmployee Rewards` set ref_doctype = '' , ref_docname = ''
        where ref_doctype = %s and ref_docname = %s
        """,
        (doc.doctype, doc.name),
    )
    frappe.db.commit()
    

    