from __future__ import unicode_literals
from frappe import _


def get_data(data=''):
    return {
        'fieldname': 'employee_rewards',
        'non_standard_fieldnames': {
            # 'Leave Ledger Entry': 'reference_name',
        },
        "internal_links": {
                "Additional Salary": "ref_docname",
                # "Payment Entry": "payment_entry"
            },
        'transactions': [
            {
                'label': '',
                'items': ['Additional Salary']
            },
            {
                'label': '',
                'items': ['Cash Rewards']
            }
        ],
    }
