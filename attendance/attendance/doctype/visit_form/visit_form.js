// Copyright (c) 2022, Peter Maged and contributors
// For license information, please see license.txt

frappe.ui.form.on('Visit Form', {
	refresh: function(frm) {
		frm.events.expense_btn(frm)
	},
	expense_btn:function(frm){
		
		frm.add_custom_button(__("Expense Claim"), function () {

			frappe.new_doc("Expense Claim", {
				employee: frm.doc.employee_name,
				visit_form:frm.doc.name
			});

		},"Create")

	
	}
});
