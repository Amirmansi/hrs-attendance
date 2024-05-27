// Copyright (c) 2023, Peter Maged and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Out Employee Report'] = {
  filters: [
    {
      fieldname: 'from_date',
      label: __('From Date'),
      fieldtype: 'Date',
      default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
      reqd: 1,
    },
    {
      fieldname: 'to_date',
      label: __('To Date'),
      fieldtype: 'Date',
      default: frappe.datetime.get_today(),
      reqd: 1,
    },

    {
      fieldname: 'company',
      label: __('Company'),
      fieldtype: 'Link',
      options: 'Company',
      default: frappe.defaults.get_user_default('Company'),
      reqd: 1,
    },
    {
      fieldname: 'branch',
      label: __('Branch'),
      fieldtype: 'Link',
      options: 'Branch',
    },
    {
      fieldname: 'department',
      label: __('Department'),
      fieldtype: 'Link',
      options: 'Department',
    },
    {
      fieldname: 'designation',
      label: __('Designation'),
      fieldtype: 'Link',
      options: 'Designation',
    },
    {
      fieldname: 'employee',
      label: __('Employee'),
      fieldtype: 'Link',
      options: 'Employee',
    },
  ],
};
