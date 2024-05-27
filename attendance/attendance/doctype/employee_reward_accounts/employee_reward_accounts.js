// Copyright (c) 2023, Peter Maged and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Reward Accounts', {
  // refresh: function(frm) {

  // }
  setup: function (frm) {
    // frm.set_query('deduction_additional_salary', function () {
    //   return {
    //     filters: {
    //       type: 'deduction',
    //     },
    //   };
    // });
    // frm.set_query('earning_additional_salary', function () {
    //   return {
    //     filters: {
    //       type: 'earning',
    //     },
    //   };
    // });
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
});
