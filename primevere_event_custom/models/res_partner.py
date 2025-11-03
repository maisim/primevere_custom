# SPDX-FileCopyrightText: 2024 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    nb_poster = fields.Integer(string="Number of posters")
    nb_flyer = fields.Integer(string="Number of flyers")
    journal = fields.Integer()
    ticket_code = fields.Char()
