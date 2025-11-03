# SPDX-FileCopyrightText: 2024 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class EventTrackTheme(models.Model):
    _name = "event.track.theme"

    name = fields.Char()
