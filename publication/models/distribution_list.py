# -*- coding: utf-8 -*-
# Copyright 2014-2017 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


SQL_CONTRACT_COUNT = """
SELECT COALESCE(SUM(ROUND(l.quantity)::integer), 0) as quantity
 FROM account_analytic_invoice_line l
 JOIN account_analytic_account c
 ON l.contract_id = c.id
 WHERE l.product_id = %s
 AND c.partner_id = %s"""

SQL_ASSIGNED_COUNT = """
SELECT COALESCE(SUM(copies), 0) as copies
 FROM distribution_list
 WHERE product_id = %s
 AND contract_partner_id = %s"""


class DistributionList(models.Model):
    _name = 'distribution.list'
    _order = 'name'

    @api.depends('product_id', 'partner_id')
    def _compute_name_address(self):
        """Create subscription name from publication and partner."""
        for this in self:
            if not this.product_id or not this.partner_id:
                this.name = False
                this.display_address = False
                continue
            this.name = ' - '.join(
                [this.product_id.name, this.partner_id.name])
            if this.product_id.distribution_type == 'email':
                this.display_address = this.partner_id.email
            else:
                this.display_address = this.partner_id.contact_address

    @api.multi
    def _compute_active(self):
        """Apply date logic to determine if version is current"""
        today = fields.Date.today()
        for this in self:
            if ((not this.date_start or this.date_start <= today) and
                    (not this.date_end or this.date_end >= today)):
                this.active = True
            else:
                this.active = False

    @api.multi
    def _compute_counts(self):
        """Used to check how many addresses can still be added."""
        cr = self.env.cr
        for this in self:
            if not self.product_id or not self.contract_partner_id:
                continue
            cr.execute(
                SQL_CONTRACT_COUNT,
                (this.product_id.id, this.contract_partner_id.id))
            contract_count = cr.fetchone()[0]
            cr.execute(
                SQL_ASSIGNED_COUNT,
                (this.product_id.id, this.contract_partner_id.id))
            assigned_count = cr.fetchone()[0]
            available_count = contract_count - assigned_count
            this.contract_count = contract_count
            this.assigned_count = assigned_count
            this.available_count = available_count

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Publication',
        domain=[('publication', '=', True)],
        required=True)
    distribution_type = fields.Boolean(
        string='Type of publication',
        related='product_id.distribution_type',
        store=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Receiving Partner',
        required=True)
    contract_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contract Partner',
        required=True)
    date_start = fields.Date(string='Date start', required=True)
    date_end = fields.Date(
        string='Date end',
        help="End date is exclusive.")
    active = fields.Boolean(string='Active', compute='_compute_active')
    copies = fields.Integer(string='Number of copies', default=1)
    name = fields.Char(
        compute='_compute_name_address',
        string='Name')
    display_address = fields.Char(
        compute='_compute_name_address',
        string='Receiving address')
    contract_count = fields.Integer(
        string="Number to distribute",
        compute='_compute_counts')
    assigned_count = fields.Integer(
        string="Number already assigned",
        compute='_compute_counts')
    available_count = fields.Integer(
        string="Number still available",
        compute='_compute_counts')
