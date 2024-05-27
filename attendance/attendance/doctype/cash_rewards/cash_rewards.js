// Copyright (c) 2023, Peter Maged and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cash Rewards', {
  refresh: function (frm) {
    frm.events.show_general_ledger(frm);
  },

  setup: function (frm) {
    frm.set_query('expense_account', function () {
      return {
        filters: {
          is_group: 0,
          company: frm.doc.company,
        },
      };
    });
    frm.set_query('expense_account', function () {
      return {
        filters: {
          is_group: 0,
          company: frm.doc.company,
        },
      };
    });
    frm.set_query('payment_account', function () {
      return {
        filters: {
          is_group: 0,
          company: frm.doc.company,
        },
      };
    });
    frm.set_query('employee_reward_account', function () {
      return {
        filters: {
          is_group: 0,
          company: frm.doc.company,
        },
      };
    });
    frm.set_query('cost_center', function () {
      return {
        filters: {
          is_group: 0,
          company: frm.doc.company,
        },
      };
    });
  },
  show_general_ledger: function (frm) {
    if (frm.doc.docstatus > 0) {
      frm.add_custom_button(
        __('Ledger'),
        function () {
          frappe.route_options = {
            voucher_no: frm.doc.name,
            from_date: frm.doc.posting_date,
            to_date: moment(frm.doc.modified).format('YYYY-MM-DD'),
            company: frm.doc.company,
            group_by: '',
            show_cancelled_entries: frm.doc.docstatus === 2,
          };
          frappe.set_route('query-report', 'General Ledger');
        },
        'fa fa-table',
      );
    }
  },
});
