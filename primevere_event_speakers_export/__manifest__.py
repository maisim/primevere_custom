# Copyright 2025 Association Primevère
# License: AGPL-3.0-or-later

{
    "name": "Primevere Event Speakers Export",
    "summary": "Export CSV des intervenants pour les événements Primevere",
    "version": "16.0.1.0.0",
    "category": "Event",
    "website": "https://github.com/coopiteasy/cie-custom",
    "author": "Coop IT Easy SC",
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
