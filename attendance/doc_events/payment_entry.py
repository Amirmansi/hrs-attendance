import frappe

def on_trash(doc,method='') :
    pass
    # clear_employee_rewards_references(doc)


def on_cancel(doc,method='') :
    pass
    # clear_employee_rewards_references(doc)


def clear_employee_rewards_references(doc):
    sql = f"""
        Update `tabEmployee Rewards` set payment_entry = '' 
        where  payment_entry = '{doc.name}'
    """
    frappe.db.sql(sql)
    frappe.db.commit()
    