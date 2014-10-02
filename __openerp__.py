# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "Publication",
    "version": "1.0",
    "author": "Therp BV",
    "complexity": "normal",
    "description": """
This module allows to register publications that a partner can receive.

Publications can be in print of electronic, and be free or paid for.

Paid publications can be linked to a contract (recurring analytic account).
    """,
    "category": "CRM",
    "depends": [
        'analytic',
        'account',
        # aaa_recurring is from community project contract-management
        # in 8.0 (odoo) this is part of standard account_analytic_analysis
        # Installing the module will also result in installing some hr
        # modules.
        'account_analytic_analysis_recurring',
        'web_m2x_options',
    ],
    "data": [
        'view/res_partner.xml',
        'view/menu.xml',
        'security/ir.model.access.csv',
    ],
    "js": [
    ],
    "css": [
    ],
    "qweb": [
    ],
    "auto_install": False,
    "installable": True,
    "external_dependencies": {
        'python': [],
    },
}
