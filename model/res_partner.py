#-*- coding: utf-8 -*-
'''Extend res.partner model'''
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
from openerp.osv import orm, fields

DISTRIBUTION_PREFERENCE = (
        ('email', 'Email'),
        ('print', 'Print'),
        ('both', 'Print & Email'),
)

class ResPartner(orm.Model):
    '''Extend partner with publication information'''
    _inherit = 'res.partner'

    _columns = {
        'subscription_ids': fields.one2many(
            'publication.subscription',
            'partner_id',
            'Subscriptions'
        ),
        'distribution_preference': fields.selection(
            DISTRIBUTION_PREFERENCE, 'Distribution preference'),
    }
    _defaults = {
            'distribution_preference': 'email',
    }

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
