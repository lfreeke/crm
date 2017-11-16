# -*- coding: utf-8 -*-
# Copyright 2014-2017 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Publication(models.Model):
    _name = 'publication.publication'
    _order = 'code'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', required=True)
    distribution_type = fields.Selection(
        selection=[('email', 'Electronic'), ('print', 'Print')],
        string='Distribution',
        required=True)
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        readonly=True,
        help="Product for this publication")
    version_ids = fields.One2many(
        comodel_name='publication.version',
        inverse_name='publication_id',
        string='Versions')
