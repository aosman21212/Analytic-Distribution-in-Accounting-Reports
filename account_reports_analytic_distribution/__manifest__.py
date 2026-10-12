# -*- coding: utf-8 -*-
# =============================================================================
#  Analytic Distribution in Accounting Reports
# -----------------------------------------------------------------------------
#  Location  : King Abdulaziz Branch Road, Riyadh, Saudi Arabia
#  Email     : sales@leapai.ai
#  Phone     : +966 53 553 3627
#  Website   : https://leapai.ai
#  Developer : Abdulkaraim Osman — Tech Manager | Backend Engineer | DevOps Engineer
#              at Bab International Corp For Specialized Services
#  LinkedIn  : https://www.linkedin.com/in/abdulkaraim-o-385b7a110/
# =============================================================================
{
    'name': 'Analytic Distribution in Accounting Reports',
    'version': '19.0.1.0.0',
    'summary': 'Adds Analytic Distribution column to General Ledger and Partner Ledger reports',
    'author': 'leapai.ai',
    'maintainer': 'Abdulkaraim Osman',
    'support': 'sales@leapai.ai',
    'website': 'https://leapai.ai',
    'depends': ['account_reports', 'analytic'],
    'images': [
        'static/description/icon.png',
        'static/description/screenshot.jpg',
    ],
    'data': [
        'data/account_reports_analytic.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
