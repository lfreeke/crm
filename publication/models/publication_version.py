# -*- coding: utf-8 -*-
# Copyright 2014-2017 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PublicationVersion(models.Model):
    _name = 'publication.version'
    _order = 'name, date_start desc'

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

    publication_id = fields.Many2one(
        comodel_name='publication.publication',
        string='Publication',
        required=True)
    name = fields.Char(string='Current Name', required=True)
    date_start = fields.Date(string='Date start', required=True)
    date_end = fields.Date(
        string='Date end',
        help="End date is exclusive, so end date of one version is"
             " beginning date of new version, if any.")
    active = fields.Boolean(string='Active', compute='_compute_active')
    publishing_frequency_type = fields.Selection(
        selection=[
            ('irregular', 'Irregular'),
            ('daily', 'Day(s)'),
            ('weekly', 'Week(s)'),
            ('monthly', 'Month(s)'),
            ('quarterly', 'Quarterly'),
            ('yearly', 'Year(s)')],
        default='monthly',
        string='Publishing frequency',
        help="At what intervals publication is published")
    publishing_frequency_interval = fields.Integer(
        string='Publish Every',
        default=1,
        help="Publish every (Days/Week/Month/Quarter/Year)")

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for this in self:
            if this.date_end and this.date_start and \
                    this.date_end < this.date_start:
                raise ValidationError(
                    _("The publication version's end date needs to be after "
                      "the version's start date"))

    @api.multi
    def _end_previous(self):
        """If a new version start, a previous version should be ended."""
        self.ensure_one()
        previous_version = self.search(
            [('date_start', '<', self.date_start)],
            order='date_start desc',
            limit=1)
        if previous_version:
            super(PublicationVersion, previous_version).write({
                'date_end': self.date_start})

    @api.model
    def create(self, vals):
        """Create products if needed."""
        new_version = super(PublicationVersion, self).create(vals)
        new_version._end_previous()
        return new_version

    @api.multi
    def write(self, vals):
        """Create products if needed."""
        result = super(PublicationVersion, self).write(vals)
        if 'email_distribution' in vals or 'print_distribution' in vals:
            for this in self:
                this._end_previous()
        return result
