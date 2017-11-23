# -*- coding: utf-8 -*-
# Copyright 2014-2017 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PublicationSubscriptionAddress(models.Model):
    _name = 'publication.subscription.address'
    _order = 'publication_id, partner_id'
    _name_field = 'publication_id'

    @api.model
    def name_search(
            self, name, args=None, operator='ilike', limit=100):
        """We have no real name. Search on name of publication."""
        newargs = args and args[:] or []  # copy or empty
        if name:
            publication_model = self.env['publication.publication']
            publication_ids = publication_model.search(
                [('name', operator, name)])
            if not publication_ids:
                return self.browse([])
            newargs.append(('publication_id', 'in', publication_ids.ids))
        subscriptions = super(PublicationSubscriptionAddress, self).search(
            args=newargs, limit=limit)
        return subscriptions.name_get()

    @api.depends('publication_id', 'partner_id')
    def _compute_name_address(self):
        """Create subscription name from publication and partner."""
        for this in self:
            this.name = ' - '.join(
                [this.publication_id.name, this.partner_id.name])
            if this.publication_id.distribution_type == 'email':
                this.display_address = this.partner_id.email
            else:
                this.display_address = this.partner_id.contract_address

    publication_id = fields.Many2one(
        comodel_name='publication.publication',
        string='Publication',
        required=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Receiving Partner',
        required=True)
    contract_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contract Partner',
        required=True)
    copies = fields.Integer(string='Number of copies', default=1)
    name = fields.Char(
        compute='_compute_name_address',
        string='Name')
    display_address = fields.Char(
        compute='_compute_name_address',
        string='Receiving address')
