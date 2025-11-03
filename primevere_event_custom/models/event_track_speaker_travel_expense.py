# SPDX-FileCopyrightText: 2024 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class EventTrackSpeakerTravelExpense(models.Model):
    _inherit = "event.track.speaker.travel.expense"

    status = fields.Selection(selection_add=[("to_pay_in_hand", "To Pay In Hand")])
