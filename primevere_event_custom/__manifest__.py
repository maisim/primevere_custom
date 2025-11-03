# SPDX-FileCopyrightText: 2024 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Primevere Event Custom",
    "summary": """Primevere Customisation For Event Management""",
    "version": "16.0.1.0.0",
    "category": "Event",
    "website": "https://github.com/maisim/primevere_custom",
    "author": "Coop IT Easy SC",
    "maintainers": ["victor-champonnois"],
    "license": "AGPL-3",
    "application": False,
    "depends": [
        "event_track_multi_speaker",
        "event_track_multi_date",
        "event_track_speaker_travel",
        "event_track_speaker_catering",
        "event_track_equipment",
        "report_csv",
    ],
    "excludes": [],
    "data": [
        "security/ir.model.access.csv",
        "views/event_track_speaker.xml",
        "views/event_event.xml",
        "views/event_track.xml",
        "views/event_track_speaker_booking.xml",
        "views/res_partner.xml",
        "reports/track_export_website.xml",
        "views/menuitems.xml",
    ],
    "demo": [],
    "qweb": [],
}
