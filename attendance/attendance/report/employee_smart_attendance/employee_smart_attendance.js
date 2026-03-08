// Copyright (c) 2024, Peter Maged and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Smart Attendance"] = {
  filters: [
    {
      fieldname: "company",
      label: __("Company"),
      fieldtype: "Link",
      options: "Company",
      default: frappe.defaults.get_user_default("Company"),
      reqd: 1,
    },
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      reqd: 1,
      default: frappe.datetime.month_start(),
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      reqd: 1,
      default: frappe.datetime.month_end(),
    },
    {
      fieldname: "month",
      label: __("Month"),
      fieldtype: "Select",
      options: [
        "",
        { value: "01", label: __("January") },
        { value: "02", label: __("February") },
        { value: "03", label: __("March") },
        { value: "04", label: __("April") },
        { value: "05", label: __("May") },
        { value: "06", label: __("June") },
        { value: "07", label: __("July") },
        { value: "08", label: __("August") },
        { value: "09", label: __("September") },
        { value: "10", label: __("October") },
        { value: "11", label: __("November") },
        { value: "12", label: __("December") },
      ],
      on_change: function (query_report) {
        var month = query_report.get_values().month;
        if (!month) return;
        var year = new Date().getFullYear();
        var from_date = year + "-" + month + "-01";
        var last_day = new Date(year, parseInt(month), 0).getDate();
        var to_date = year + "-" + month + "-" + String(last_day).padStart(2, "0");
        frappe.query_report.set_filter_value({ from_date: from_date, to_date: to_date });
      },
    },
    {
      fieldname: "smart_filter",
      label: __("Smart Filter"),
      fieldtype: "Select",
      options: [
        "",
        { value: "Present", label: __("Present") },
        { value: "Late / Short Hours", label: __("Late / Short Hours") },
        { value: "Missing Punch", label: __("Missing Punch") },
        { value: "Absent", label: __("Absent") },
      ],
    },
    {
      fieldname: "employee",
      label: __("Employee"),
      fieldtype: "Link",
      options: "Employee",
      get_query: () => {
        var company = frappe.query_report.get_filter_value("company");
        return { filters: { company: company } };
      },
    },
    {
      fieldname: "branch",
      label: __("Branch"),
      fieldtype: "Link",
      options: "Branch",
    },
    {
      fieldname: "department",
      label: __("Department"),
      fieldtype: "Link",
      options: "Department",
    },
    {
      fieldname: "shift_type",
      label: __("Shift Type"),
      fieldtype: "Link",
      options: "Shift Type",
    },
    {
      fieldname: "attendance_rule",
      label: __("Attendance Rule"),
      fieldtype: "Link",
      options: "Attendance Rule",
    },
  ],

  formatter: function (value, row, column, data, default_formatter) {
    value = default_formatter(value, row, column, data);
    if (column.fieldname === "status") {
      if (data && data.status === "Present") {
        value = `<span class="indicator-pill green">${data.status}</span>`;
      } else if (data && data.status === "Late / Short Hours") {
        value = `<span class="indicator-pill orange">${data.status}</span>`;
      } else if (data && data.status === "Missing Punch") {
        value = `<span class="indicator-pill yellow">${data.status}</span>`;
      } else if (data && data.status === "Absent") {
        value = `<span class="indicator-pill red">${data.status}</span>`;
      }
    }
    if (column.fieldname === "variance") {
      if (data) {
        var variance = parseFloat(data.variance_raw || 0);
        if (variance >= 0) {
          value = `<span style="color: #2ecc40; font-weight:bold;">${value}</span>`;
        } else {
          value = `<span style="color: #e74c3c; font-weight:bold;">${value}</span>`;
        }
      }
    }
    return value;
  },
};
