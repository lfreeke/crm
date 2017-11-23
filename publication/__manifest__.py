# -*- coding: utf-8 -*-
# Copyright 2014-2017 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Publication',
    'version': '10.0.1.0.0',
    'category': 'Customer Relationship Management',
    'author': 'Therp BV, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'summary': 'Maintain electronic or print publications for your relations.',
    'depends': [
        'sales_team',
        'contract',
        'web_m2x_options',
    ],
    'data': [
        'data/account_analytic_account.xml',
        'views/publication_publication.xml',
        'views/publication_subscription_address.xml',
        'views/res_partner.xml',
        'views/menu.xml',
        'security/ir.model.access.csv',
    ],
    'auto_install': False,
    'installable': True,
}
