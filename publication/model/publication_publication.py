#-*- coding: utf-8 -*-
'''Extend publication.publication model'''
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
from openerp.tools.translate import _


class Publication(orm.Model):
    '''Publication information'''
    _name = 'publication.publication'

    def _get_active(self, cr, uid, ids, field_name, args, context=None):
        '''Apply date logic to determine if these roles are current'''
        res = {}
        today = fields.date.context_today(self, cr, uid, context=context)
        for this_obj in self.browse(cr, uid, ids, context=context):
            if ((not this_obj.date_start or this_obj.date_start <= today)
                    and (not this_obj.date_end or this_obj.date_end >= today)):
                res[this_obj.id] = True
            else:
                res[this_obj.id] = False
        return res

    _columns = {
        'code': fields.char('Code', size=16, required=True),
        'name': fields.char('Name', size=64, required=True),
        'date_start': fields.date('Date start', required=True),
        'date_end': fields.date('Date end'),
        'email_distribution': fields.boolean('Can be send by email'),
        'print_distribution': fields.boolean('Can be send in print'),
        'active': fields.function(
            _get_active,
            type='boolean',
            string='Active'),
    }
    _order = 'code'

    def _check_dates(self, cr, uid, ids, context=None):
        for this_obj in self.browse(cr, uid, ids, context=context):
            if (this_obj.date_end and this_obj.date_start
                    and this_obj.date_end < this_obj.date_start):
                raise orm.except_orm(
                    _('End date before start date'),
                    _("The publication's end date needs to be after the "
                      "publication's start date"))
        return True

    def _check_distributions(self, cr, uid, ids, context=None):
        for this_obj in self.browse(cr, uid, ids, context=context):
            if not (this_obj.email_distribution
                        or this_obj.print_distribution):
                raise orm.except_orm(
                    _('Select at least one type of distribution'),
                    _('Select either email, or print or both distribution'
                        ' methods')
                )
        return True

    _constraints = [
        (_check_dates, '', ['date_start', 'date_end']),
        (_check_distributions, '',
            ['email_distribution', 'print_distribution']),
    ]

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
