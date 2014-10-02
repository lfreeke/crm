#-*- coding: utf-8 -*-
'''Extend product.product model'''
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


class Product(orm.Model):
    '''Extend product.product with publication information'''
    _inherit = 'product.product'

    _columns = {
        'publication_id': fields.many2one(
            'publication.publication', 'Publication'),
        'email_distribution': fields.boolean('Can be send by email'),
        'print_distribution': fields.boolean('Can be send in print'),
        'recurring_rule_type': fields.selection([                              
            ('daily', 'Day(s)'),                                               
            ('weekly', 'Week(s)'),                                             
            ('monthly', 'Month(s)'),                                           
            ('yearly', 'Year(s)'),                                             
            ], 'Recurrency',
            help="Invoice automatically repeat at specified interval"),
        'recurring_interval': fields.integer(
            'Repeat Every', help="Repeat every (Days/Week/Month/Year)"),
    }                                                                          
                                                                               
    _defaults = {                                                              
        'recurring_interval': 1,                                               
        'recurring_rule_type':'yearly'                                        
    } 

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
