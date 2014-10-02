#-*- coding: utf-8 -*-
'''Define publication.subscription model'''
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


class Subscription(orm.Model):
    '''Link partners to publications'''
    _name = 'publication.subscription'

    _columns = {
        'partner_id': fields.many2one(
            'res.partner',
            'Partner',
            required=True,
        ),
        'publication_id': fields.many2one(
            'publication.publication',
            'Publication',
            required=True,
        ),
        'date_start': fields.date('Date start', required=True),
        'date_end': fields.date('Date end'),
        'email_distribution': fields.boolean('Receive by email'),
        'print_distribution': fields.boolean('Receive in print'),
        'copies': fields.integer('Number of copies'),
        'product_id': fields.many2one(
            'product.product',
            'Product',
        ),
    }                                                                          
    _order = 'date_start desc'

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
