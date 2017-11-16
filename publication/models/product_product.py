# -*- coding: utf-8 -*-
# Copyright 2014-2017 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class Product(models.Model):
    _inherit = 'product.product'

    @api.multi
    def unlink(self):
        """Product can not be removed if used in publication."""
        publication_model = self.env['publication.publication']
        for this in self:
            publication = publication_model.search(
                [('product_id', '=', this.id)], limit=1)
            if publication:
                raise ValidationError(_(
                    "Product is linked to publication %s, and can"
                    " therefore not be removed." % publication.name))
