# -*- coding: utf-8 -*-
# Copyright 2014-2017 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


# Define constants for SQL statements. Makes it easier to copy from
# editor to psql console.
SQL_ANALYTIC = """
SELECT aaa.partner_id
 FROM account_analytic_invoice_line aail
 JOIN account_analytic_account aaa
     ON aail.analytic_account_id = aaa.id
 WHERE aail.id = %s
"""


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    @api.multi
    def _compute_partner_id(self):
        """We need this, because reference to contract is broken."""
        partner_model = self.env['res.partner']
        for this in self:
            # Hack based on fact that database field not corrupted:
            self.env.cr.execute(SQL_ANALYTIC, (this.id, ))
            record = self.env.cr.fetchone()
            partner = partner_model.browse([record[0]])
            this.partner_id = partner

    publication = fields.Boolean(
        string='Subscription product line',
        related='product_id.publication',
        store=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        compute='_compute_partner_id',
        string='Partner')
