# -*- coding: utf-8 -*-
# Copyright 2014-2017 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    subscription_ids = fields.One2many(
        comodel_name='account.analytic.invoice.line',
        inverse_name='partner_id',
        domain=[('subscription_product_line', '=', True)],
        string='Subscription contracts')

    subscription_address_ids = fields.One2many(
        comodel_name='publication.subscription.address',
        inverse_name='partner_id',
        string='Publications received')
