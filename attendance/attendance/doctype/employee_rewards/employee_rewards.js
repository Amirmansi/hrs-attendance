// Copyright (c) 2021, Peter Maged and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Rewards', {
  refresh: function (frm) {
    if (frm.doc.docstatus == 1) {
      if (frm.doc.action_type == 'Cash Rewards' && !frm.doc.cash_rewards) {
        // add cutom button
        frm.add_custom_button(
          __('Cash Rewards'),
          () => {
            frm.call({
              method: 'create_cash_reward',
              doc: frm.doc,
              callback: function (r) {
                frm.refresh();
              },
            });
          },
          __('Create'),
        );
      }
    }
  },
});
