#-*- coding: utf-8 -*-
"""Define publication.subscription model."""
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


class Subscription(orm.Model):
    """Link partners to publications."""
    _name = 'publication.subscription'

    def on_change_publication_id(
            self, cr, uid, dummy_ids, publication_id, distribution_preference,
            context=None):
        """Selecting a publication will determine whether print of email
        distribution is valid. If a publication is changed  fields for
        distribution will be set to sensible defaults for the publication."""
        if not publication_id:
            return {}  # do nothing
        publication_model = self.pool['publication.publication']
        # if only print or email allowed, deselect the not allowed
        # distribution methods, and select the one allowed.
        publication_records = publication_model.read(
            cr, uid, [publication_id],
            ['email_distribution', 'print_distribution'], context=context
        )
        assert publication_records, (
            _('No record for publication_id %d') % publication_id)
        result = {
            'value': {
                'email_distribution':
                    publication_records[0]['email_distribution'],
                'print_distribution':
                    publication_records[0]['print_distribution'],
            },
        }
        # if multiple modes of distribution are allowed, fill method according
        # to partner preferences.
        if (result['value']['email_distribution']
                and result['value']['email_distribution']):
            # If we get here the values for print and email will both be
            # True. A distribution-preference False or 'both' will not
            # have any effect.
            if distribution_preference == 'print':
                result['value']['email_distribution'] = False
            if distribution_preference == 'email':
                result['value']['print_distribution'] = False
                result['value']['copies'] = 1
        return result

    def on_change_partner_publication_id(
            self, cr, uid, dummy_ids, partner_id, publication_id,
            context=None):
        """Onchange publication for stand-alone subscription form."""
        distribution_preference = False
        if partner_id:
            partner_model = self.pool['res.partner']
            partner_objs = partner_model.browse(
                cr, uid, [partner_id], context=context)
            if partner_objs:
                distribution_preference = (
                    partner_objs[0].distribution_preference)
        return self.on_change_publication_id(
            cr, uid, dummy_ids, publication_id, distribution_preference,
            context=context
        )

    def get_root_analytic_account_id(self, cr, uid):
        """Return id of standard analytic account to use as parent in
        subscription contract."""
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
        """We need unit product uom for contract line."""
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
        """Unlink contract that exists only to support subscription."""
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
        """Make sure subscriptions remain synchronized with contracts.
        Contracts themselves should not be modified directly, because
        synchronization is one way only."""
        analytic_model = self.pool['account.analytic.account']
        # analytic account invoice line is NOT !!!! an invoice line, but
        # a specification of the products and amounts in the contract!!
        line_model = self.pool['account.analytic.invoice.line']
        for this_obj in self.browse(cr, uid, ids, context=context):
            contract_id = (
                this_obj.contract_id and this_obj.contract_id.id or False)
            product_id = (
                this_obj.product_id and this_obj.product_id.id or False)
            if not contract_id and not product_id:
                # If no contract and no product, no need to do anything:
                pass
            elif contract_id and not product_id:
                # If there is a contract, but no product, delete contract:
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
        """Update contracts when subscriptions are updated."""
        if 'copies' in vals and vals['copies'] < 1:
            vals['copies'] = 1
        res = super(Subscription, self).write(
            cr, uid, ids, vals, context=context)
        self._synchronize_contract(cr, uid, ids, context=context)
        return res

    def create(self, cr, uid, vals, context=None):
        """Create contract if publication is linked to a product."""
        if 'copies' in vals and vals['copies'] < 1:
            vals['copies'] = 1
        new_id = super(Subscription, self).create(
            cr, uid, vals, context=context)
        if 'product_id' in vals and vals['product_id']:
            self._synchronize_contract(cr, uid, [new_id], context=context)
        return new_id

    def _get_name(self, cr, uid, ids, field_name, args, context=None):
        """Create subscription name from publication and partner."""
        res = {}
        for this_obj in self.browse(cr, uid, ids, context=context):
            res[this_obj.id] = ' - '.join([
                this_obj.partner_id.name, this_obj.publication_id.name])
        return res

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
        'name': fields.function(
            _get_name,
            type='char',
            size=64,
            string='Active'
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

    def _check_dates(self, cr, uid, ids, context=None):
        for this_obj in self.browse(cr, uid, ids, context=context):
            date_start = this_obj.date_start
            date_end = this_obj.date_end
            publication_start = this_obj.publication_id.date_start
            publication_end = this_obj.publication_id.date_end
            if date_end and date_start and (date_end < date_start):
                raise orm.except_orm(
                    _('End date before start date'),
                    _("The subscriptions's end date needs to be after the "
                      "subscriptions's start date"))
            if (date_start and publication_start
                    and date_start < publication_start):
                raise orm.except_orm(
                    _('Subscription can not start before publication'),
                    _("The subscriptions start date needs to be equal or"
                      " after the publication's start date"))
            if (date_end and publication_end
                    and date_end > publication_end):
                raise orm.except_orm(
                    _('Subscription can not end after publication'),
                    _("The subscriptions end date needs to be equal or"
                      " before the publication's end date"))
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
            if (this_obj.email_distribution
                 and not this_obj.publication_id.email_distribution):
                raise orm.except_orm(
                    _('No email distribution for this publication'),
                    _('Email distribution for this publication not allowed')
                )
            if (this_obj.print_distribution
                 and not this_obj.publication_id.print_distribution):
                raise orm.except_orm(
                    _('No print distribution for this publication'),
                    _('Print distribution for this publication not allowed')
                )
        return True

    _constraints = [
        (_check_dates, '', ['date_start', 'date_end']),
        (_check_distributions, '',
            ['email_distribution', 'print_distribution']),
    ]

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
