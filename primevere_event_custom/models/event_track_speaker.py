# SPDX-FileCopyrightText: 2024 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class EventTrackSpeaker(models.Model):
    _inherit = "event.track.speaker"

    curriculum_vitae = fields.Text()
    invitation_number = fields.Integer()
    invitation_code = fields.Char()
    need_ticket = fields.Boolean()
    need_reserved_car_place = fields.Boolean()
    slot_wishes = fields.Text()
