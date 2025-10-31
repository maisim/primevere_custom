# Copyright 2025 Association Primevère
# License: AGPL-3.0-or-later

{
    "name": "Primevere event speakers export",
    "summary": "Export CSV of speakers for Primevere events",
    "version": "16.0.1.0.0",
    "category": "Event",
    "website": "https://github.com/maisim/primevere_custom",
    "author": "Simon Maillard",
    "license": "AGPL-3",
    "depends": [
        "primevere_event_custom",
        "report_csv",
    ],
    "data": [
        "reports/event_speakers_export.xml",
    ],
    "installable": True,
    "auto_install": False,
}
