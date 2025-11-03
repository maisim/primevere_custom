# Copyright 2025 Association Primevère
# License: AGPL-3.0-or-later

import csv
import io
from datetime import datetime

from odoo.tests.common import TransactionCase


class TestTrackWebsiteExport(TransactionCase):
    def setUp(self):
        super().setUp()

        # Create test event
        self.event = self.env["event.event"].create(
            {
                "name": "Test Event",
                "date_begin": "2025-06-01 08:00:00",
                "date_end": "2025-06-03 18:00:00",
            }
        )

        # Create test format
        self.format = self.env["event.track.format"].create({"name": "Conference"})

        # Create test location
        self.location = self.env["event.track.location"].create(
            {"name": "Building A - Amphitheater"}
        )

    def test_permanent_track_without_dates_export(self):
        """Test that permanent tracks without dates are exported with special format"""
        # Create a permanent track without dates
        track = self.env["event.track"].create(
            {
                "name": "Permanent Session",
                "event_id": self.event.id,
                "duration": 2.0,
                "all_event": True,  # Permanent session
                "format_id": self.format.id,
                "location_id": self.location.id,
                "com_info_speaker_short": "Test Speaker",
                "com_info_event": "Test event description",
            }
        )

        # Ensure no dates are set
        self.assertEqual(len(track.dates), 0)

        # Test the export
        report = self.env["report.primevere_event_custom.track_export_website"]

        output = io.StringIO()
        writer = csv.DictWriter(
            output, fieldnames=report.csv_report_options()["fieldnames"], delimiter=";"
        )

        # Generate CSV
        report.generate_csv_report(writer, {}, self.event)

        output.seek(0)
        csv_content = output.getvalue()

        # Parse the CSV to verify column values
        output.seek(0)
        reader = csv.DictReader(output, delimiter=";")
        rows = list(reader)

        # Should have exactly one row for the permanent track
        self.assertEqual(len(rows), 1)
        row = rows[0]

        # Verify each column has the correct value
        self.assertEqual(row["id"], str(track.id))  # Track ID (not date_line ID)
        self.assertEqual(row["id_horaire"], f"{track.id}1")  # Track ID + sequence
        self.assertEqual(row["titre session"], "Permanent Session")
        self.assertEqual(row["date"], "00-00-0000")  # Special date format
        self.assertEqual(row["heure"], "00:00:00")  # Special time format
        self.assertEqual(row["permanent"], "1")  # permanent = 1 (True)
        self.assertEqual(row["intervenant court"], "Test Speaker")
        self.assertEqual(row["lieux"], "Amphitheater")  # Location parsing
        self.assertEqual(row["forme"], "Conference")
        self.assertEqual(row["duree"], "02:00")  # 2.0 hours formatted
        self.assertEqual(row["texte de présentation"], "Test event description")

    def test_normal_track_with_dates_export(self):
        """Test that normal tracks with dates work as before"""
        # Create a normal track with dates
        track = self.env["event.track"].create(
            {
                "name": "Normal Session",
                "event_id": self.event.id,
                "duration": 1.5,
                "all_event": False,
                "format_id": self.format.id,
                "location_id": self.location.id,
            }
        )

        # Add a date to the track
        test_datetime = datetime(2025, 6, 1, 14, 30)  # 14:30 on June 1st
        self.env["event.track.date"].create(
            {
                "track_id": track.id,
                "datetime": test_datetime,
            }
        )

        # Test the export
        report = self.env["report.primevere_event_custom.track_export_website"]

        output = io.StringIO()
        writer = csv.DictWriter(
            output, fieldnames=report.csv_report_options()["fieldnames"], delimiter=";"
        )

        # Generate CSV
        report.generate_csv_report(writer, {}, self.event)

        output.seek(0)
        csv_content = output.getvalue()

        # Parse the CSV to verify column values
        output.seek(0)
        reader = csv.DictReader(output, delimiter=";")
        rows = list(reader)

        # Should have exactly one row for the normal track
        self.assertEqual(len(rows), 1)
        row = rows[0]

        # Verify each column has the correct value
        self.assertEqual(row["id"], str(track.id))  # Track ID (not date_line ID)
        self.assertEqual(row["id_horaire"], f"{track.id}1")  # Track ID + sequence
        self.assertEqual(row["titre session"], "Normal Session")
        self.assertEqual(row["date"], "2025-06-01")  # Real date
        self.assertEqual(row["heure"], "16:30")  # Time with timezone conversion (UTC+2)
        self.assertEqual(row["permanent"], "0")  # permanent = 0 (False)
        self.assertEqual(row["lieux"], "Amphitheater")  # Location parsing
        self.assertEqual(row["forme"], "Conference")
        self.assertEqual(row["duree"], "01:30")  # 1.5 hours formatted

    def test_track_with_multiple_dates(self):
        """Test that a track with multiple dates generates multiple rows with correct id_horaire"""
        # Create a track with multiple dates
        track = self.env["event.track"].create(
            {
                "name": "Multi-date Session",
                "event_id": self.event.id,
                "duration": 1.0,
                "all_event": False,
                "format_id": self.format.id,
                "location_id": self.location.id,
            }
        )

        # Add multiple dates to the track
        date1 = datetime(2025, 6, 1, 10, 0)
        date2 = datetime(2025, 6, 2, 14, 0)
        self.env["event.track.date"].create(
            {
                "track_id": track.id,
                "datetime": date1,
            }
        )
        self.env["event.track.date"].create(
            {
                "track_id": track.id,
                "datetime": date2,
            }
        )

        # Test the export
        report = self.env["report.primevere_event_custom.track_export_website"]

        output = io.StringIO()
        writer = csv.DictWriter(
            output, fieldnames=report.csv_report_options()["fieldnames"], delimiter=";"
        )

        # Generate CSV
        report.generate_csv_report(writer, {}, self.event)

        output.seek(0)
        reader = csv.DictReader(output, delimiter=";")
        rows = list(reader)

        # Should have exactly two rows for the two dates
        self.assertEqual(len(rows), 2)

        # First row
        row1 = rows[0]
        self.assertEqual(row1["id"], str(track.id))  # Same track ID
        self.assertEqual(row1["id_horaire"], f"{track.id}1")  # First sequence
        self.assertEqual(row1["titre session"], "Multi-date Session")

        # Second row
        row2 = rows[1]
        self.assertEqual(row2["id"], str(track.id))  # Same track ID
        self.assertEqual(row2["id_horaire"], f"{track.id}2")  # Second sequence
        self.assertEqual(row2["titre session"], "Multi-date Session")
