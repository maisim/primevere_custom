# SPDX-FileCopyrightText: 2024 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import mimetypes

from odoo import api, fields, models


class EventTrack(models.Model):
    _inherit = "event.track"

    theme_ids = fields.Many2many("event.track.theme", string="Themes")
    format_id = fields.Many2one("event.track.format", string="Format")
    commission_summary = fields.Text()
    information = fields.Text()
    contacts = fields.Text()
    all_event = fields.Boolean()
    welcomer_id = fields.Many2one("res.partner", string="Welcomer")
    electricity_watt = fields.Integer()
    com_info_speaker_short = fields.Char(size=50)
    com_info_speaker_long = fields.Text()
    com_info_event = fields.Text()
    com_info_contacts = fields.Text()
    com_info_age = fields.Text()
    com_info_note = fields.Text()
    website_image_export_name = fields.Char(
        compute="_compute_website_image_export_name"
    )

    @api.depends("image")
    def _compute_website_image_export_name(self):
        for track in self:
            attachment = self.env["ir.attachment"].search(
                [
                    ("res_id", "=", track.id),
                    ("res_model", "=", track._name),
                    ("res_field", "=", "website_image"),
                ],
                limit=1,
            )
            if attachment:
                extension = mimetypes.guess_extension(attachment.mimetype)
                track.website_image_export_name = f"{track.id}{extension}"
            else:
                track.website_image_export_name = False
