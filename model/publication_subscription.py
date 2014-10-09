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

    def get_root_analytic_account_id(self, cr, uid):
        '''Return id of standard analytic account to use as parent in
        subscription contract.'''
        try:
            return self._root_analytic_account_id
        except AttributeError:
            data_model = self.pool['ir.model.data']
            (dummy_model, self._root_analytic_account_id) = (
                data_model.get_object_reference(
                    cr, uid, 'publication',
                    'publication_root_analytic_account')
            )
        return self._root_analytic_account_id

    def get_product_uom_unit_id(self, cr, uid):
        '''We need unit product uom for contract line'''
        try:
            return self._product_uom_unit_id
        except AttributeError:
            data_model = self.pool['ir.model.data']
            (dummy_model, self._product_uom_unit_id) = (
                data_model.get_object_reference(
                    cr, uid, 'product', 'product_uom_unit')
            )
        return self._product_uom_unit_id

    def unlink(self, cr, uid, ids, context=None):
        '''Unlink contract that exists only to support subscription'''
        analytic_model = self.pool['account.analytic.account']
        for this_obj in self.browse(cr, uid, ids, context=context):
            # Save contract id if present
            contract_id = (
                this_obj.contract_id and this_obj.contract_id.id or False)
            # First delete subscription, otherwise referential constraint error
            super(Subscription, self).unlink(
                cr, uid, [this_obj.id], context=context)
            # Now, if there was a contract, delete it
            if contract_id:
                analytic_model.unlink(
                    cr, uid, [contract_id], context=context)
        return True

    def _synchronize_contract(self, cr, uid, ids, context=None):
        '''Make sure subscriptions remain synchronized with contracts.
        Contracts themselves should not be modified directly, because
        synchronization is one way only.'''
        analytic_model = self.pool['account.analytic.account']
        # analytic account invoice line is NOT !!!! an invoice line, but
        # a specification of the products and amounts in the contract!!
        line_model = self.pool['account.analytic.invoice.line']
        for this_obj in self.browse(cr, uid, ids, context=context):
            contract_id = (
                this_obj.contract_id and this_obj.contract_id.id or False)
            product_id = (
                this_obj.product_id and this_obj.product_id.id or False)
            # If there is a contract, but no product, delete contract:
            if contract_id and not product_id:
                super(Subscription, self).write(
                    cr, uid, [this_obj.id], {'contract_id': False},
                    context=context
                )
                analytic_model.unlink(cr, uid, [contract_id], context=context)
            else:
                # We need a contract, fill values
                vals = {
                    'type': 'contract',
                    'code': (
                        this_obj.publication_id.code +
                        str(this_obj.partner_id.id)),
                    'name': (
                        this_obj.publication_id.name + ': ' +
                        this_obj.partner_id.name),
                    'date_start': this_obj.date_start,
                    'date': this_obj.date_end,
                    'recurring_invoices': True,
                    'recurring_interval':
                        this_obj.product_id.recurring_interval,
                    'recurring_rule_type':
                        this_obj.product_id.recurring_rule_type,
                }
                # Create contract:
                if not contract_id:
                    vals['partner_id'] = this_obj.partner_id.id
                    vals['parent_id'] = (
                        self.get_root_analytic_account_id(cr, uid))
                    contract_id = analytic_model.create(
                        cr, uid, vals, context=context)
                    # Store newly created contract on subscription
                    super(Subscription, self).write(
                        cr, uid, [this_obj.id], {'contract_id': contract_id},
                        context=context)
                else:
                    # Update contract:
                    analytic_model.write(
                        cr, uid, [contract_id], vals, context=context)
                # Create or update analytic invoice line (NOT! an invoice line)
                line_vals = {
                    'analytic_account_id': contract_id,
                    'uom_id': self.get_product_uom_unit_id(cr, uid),
                    'product_id': product_id,
                    'price_unit': this_obj.product_id.list_price,
                    'quantity': this_obj.copies,
                    'name': this_obj.product_id.name,
                }
                line_ids = line_model.search(
                    cr, uid, [('analytic_account_id', '=', contract_id),],
                    context=context)
                if line_ids:
                    line_model.write(
                        cr, uid, line_ids, line_vals, context=context)
                else:
                    line_model.create(
                        cr, uid, line_vals, context=context)
        return True


    def write(self, cr, uid, ids, vals, context=None):
        '''Update contracts when subscriptions are updated'''
        if 'copies' in vals and vals['copies'] < 1:
            vals['copies'] = 1
        res = super(Subscription, self).write(
            cr, uid, ids, vals, context=context)
        self._synchronize_contract(cr, uid, ids, context=context)
        return res

    def create(self, cr, uid, vals, context=None):
        '''Create contract if publication is linked to a product'''
        if 'copies' in vals and vals['copies'] < 1:
            vals['copies'] = 1
        new_id = super(Subscription, self).create(
            cr, uid, vals, context=context)
        if 'product_id' in vals and vals['product_id']:
            self._synchronize_contract(cr, uid, [new_id], context=context)
        return new_id

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
        # Contract_id should really be one2one, if that were still existing
        'contract_id': fields.many2one(
            'account.analytic.account',
            'Contract',
        ),
    }
    _defaults = {
        'copies': 1,
    }
    _order = 'date_start desc'

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
