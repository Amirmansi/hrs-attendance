from __future__ import unicode_literals
from frappe import _


def get_data(data=''):
    return {
        'fieldname': 'cash_rewards',
        'non_standard_fieldnames': {
            # 'Leave Ledger Entry': 'reference_name',
            "Additional Salary": "ref_docname",

        },
        'transactions': [
            {
                'label': '',
                'items': ['Additional Salary']
            }
        ],
    }
