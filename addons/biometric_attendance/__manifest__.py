# {
#     'name': 'Biometric Attendance API',
#     'version': '1.0',
#     'summary': 'REST API for biometric-based attendance',
#     'category': 'Human Resources',
#     'author': 'Casa Altair Technologies',
#     'depends': ['hr', 'hr_attendance'],
#     'installable': True,
#     'auto_install': False,
#     'application': False,
# }
# -*- coding: utf-8 -*-
{
    'name': 'Biometric Attendance',
    'version': '2',
    'summary': 'Biometric-based attendance system integration',
    'description': 'Allows employees to check in/out via API using biometric UID and logs data',
    'category': 'Human Resources',
    'author': 'Casa Altair Technologies',
    'website': 'https://casaaltair.com',
    'depends': [
        'base',
        'hr',
        'hr_attendance',
        'hr_holidays',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/biometric_log_views.xml',
    ],
    'assets': {
        # Optional: Add web assets if needed in future
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'icon': 'biometric_attendance/static/description/icon.png',
}
