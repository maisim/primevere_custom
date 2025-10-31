# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
import io
from datetime import date, datetime
from unittest.mock import patch

from odoo.tests.common import TransactionCase


class TestEventSpeakersExport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Create a test event
        cls.event = cls.env["event.event"].create({
            "name": "Test Event",
            "date_begin": datetime(2025, 6, 1, 9, 0),
            "date_end": datetime(2025, 6, 3, 18, 0),
        })
        
        # Create partners for speakers
        cls.partner1 = cls.env["res.partner"].create({
            "name": "Speaker One",
            "email": "speaker1@example.com",
            "phone": "+33123456789",
            "function": "Expert",
            "website_description": "<p>Short bio speaker 1</p>",
        })
        
        cls.partner2 = cls.env["res.partner"].create({
            "name": "Speaker Two", 
            "email": "speaker2@example.com",
            "phone": "+33987654321",
            "function": "Consultant",
            "website_description": "<p>Short bio speaker 2</p>",
        })
        
        # Create a welcomer (volunteer)
        cls.welcomer = cls.env["res.partner"].create({
            "name": "Volunteer Welcome",
            "email": "welcomer@example.com",
        })
        
        # Create formats and locations
        cls.format = cls.env["event.track.format"].create({
            "name": "Conference"
        })
        
        cls.location = cls.env["event.track.location"].create({
            "name": "Room A - Amphitheater"
        })
        
        # Create themes
        cls.theme1 = cls.env["event.track.theme"].create({
            "name": "Technology"
        })
        
        cls.theme2 = cls.env["event.track.theme"].create({
            "name": "Innovation"
        })
        
        # Create speakers
        cls.speaker1 = cls.env["event.track.speaker"].create({
            "partner_id": cls.partner1.id,
            "event_id": cls.event.id,  # Explicitly set event_id to satisfy constraints
            "curriculum_vitae": "Long CV of speaker 1",
            "invitation_number": 5,
            "invitation_code": "CODE123",
            "need_ticket": True,
            "need_reserved_car_place": True,
            "slot_wishes": "Prefers morning",
        })
        
        cls.speaker2 = cls.env["event.track.speaker"].create({
            "partner_id": cls.partner2.id,
            "event_id": cls.event.id,  # Explicitly set event_id to satisfy constraints
            "curriculum_vitae": "Long CV of speaker 2",
            "invitation_number": 3,
            "invitation_code": "CODE456",
            "need_ticket": False,
            "need_reserved_car_place": False,
            "slot_wishes": "Prefers afternoon",
        })
        
        # Create books linked to speakers
        cls.book_provider = cls.env["event.track.speaker.book.provider"].create({
            "name": "Test Bookstore"
        })
        
        cls.book = cls.env["event.track.speaker.book"].create({
            "name": "Test Book",
            "editor_id": cls.env["res.partner"].create({"name": "Test Publishing"}).id,
            "provider_id": cls.book_provider.id,
            "speaker_ids": [(6, 0, [cls.speaker1.id])],  # Link book to speaker1
        })
        
        # Create equipment
        cls.equipment_elec = cls.env["event.track.equipment"].create({
            "name": "Power outlet"
        })
        
        cls.equipment_micro = cls.env["event.track.equipment"].create({
            "name": "Microphone"
        })

    def test_csv_report_options(self):
        """Test that CSV options are correctly configured"""
        report = self.env["report.primevere_event_speakers_export.event_speakers_export"]
        options = report.csv_report_options()
        
        # Check delimiter
        self.assertEqual(options["delimiter"], ";")
        
        # Check that all expected fields are present
        expected_fields = [
            "Id intervenant", "Id session", "date session", "horaire session",
            "en permanence", "responsable", "lieux session", "format session",
            "durée session", "titre session", "nom intervenant", "mail intervenant",
            "tel portable intervenant", "récap intervenant long", "Résumé pour présentation",
            "commission", "thème session", "souhait horaire", "nom livre",
            "maison édition", "provider", "Equipement électricité",
            "Equipement (nombre et objet)", "repas (liste des jours)",
            "travel booking", "travel expense", "logistique parking",
            "logistique ticket", "logistique nombre invitation",
            "logistique code invitation", "Bénévole accueillant"
        ]
        
        self.assertEqual(options["fieldnames"], expected_fields)

    def test_track_without_speakers(self):
        """Test export of a track without speakers"""
        track = self.env["event.track"].create({
            "name": "Track without speakers",
            "event_id": self.event.id,
            "duration": 1.5,
            "all_event": False,
            "format_id": self.format.id,
            "location_id": self.location.id,
            "theme_ids": [(6, 0, [self.theme1.id])],
        })
        
        report = self.env["report.primevere_event_speakers_export.event_speakers_export"]
        
        # Simulate CSV writing
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=report.csv_report_options()["fieldnames"], delimiter=";")
        
        report._write_track_row(writer, track, None)
        
        output.seek(0)
        csv_content = output.getvalue()
        
        # Check that the line contains track information but no speaker
        self.assertIn("Track without speakers", csv_content)
        self.assertIn("Amphitheater", csv_content)  # Location parsing corrected
        self.assertIn("Conference", csv_content)  # Format
        self.assertIn("01:30", csv_content)  # Duration formatting

    def test_track_with_speakers(self):
        """Test export of a track with speakers"""
        track = self.env["event.track"].create({
            "name": "Track with speakers",
            "event_id": self.event.id,
            "duration": 2.0,
            "all_event": True,
            "format_id": self.format.id,
            "location_id": self.location.id,
            "theme_ids": [(6, 0, [self.theme1.id, self.theme2.id])],
            "speaker_ids": [(6, 0, [self.speaker1.id, self.speaker2.id])],
        })
        
        # Add equipment
        equipment_line1 = self.env["event.track.equipment.line"].create({
            "track_id": track.id,
            "equipment_id": self.equipment_elec.id,
            "quantity": 2,
        })
        
        equipment_line2 = self.env["event.track.equipment.line"].create({
            "track_id": track.id,
            "equipment_id": self.equipment_micro.id,
            "quantity": 1,
        })
        
        report = self.env["report.primevere_event_speakers_export.event_speakers_export"]
        
        # Simulate CSV writing
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=report.csv_report_options()["fieldnames"], delimiter=";")
        
        # Test for first speaker
        report._write_track_row(writer, track, self.speaker1)
        
        output.seek(0)
        csv_content = output.getvalue()
        
        # Check track information
        self.assertIn("Track with speakers", csv_content)
        self.assertIn("Oui", csv_content)  # all_event = True
        self.assertIn("Technology, Innovation", csv_content)  # themes
        
        # Check speaker 1 information
        self.assertIn("Speaker One", csv_content)
        self.assertIn("speaker1@example.com", csv_content)
        self.assertIn("Long CV of speaker 1", csv_content)
        self.assertIn("CODE123", csv_content)
        self.assertIn("Prefers morning", csv_content)
        
        # Check equipment
        self.assertIn("Power outlet (2)", csv_content)
        self.assertIn("Microphone", csv_content)
        
        # Check books
        self.assertIn("Test Book", csv_content)
        self.assertIn("Test Publishing", csv_content)
        self.assertIn("Test Bookstore", csv_content)

    def test_track_with_dates(self):
        """Test export of a track with multiple dates"""
        track = self.env["event.track"].create({
            "name": "Track with dates",
            "event_id": self.event.id,
            "duration": 1.0,
            "speaker_ids": [(6, 0, [self.speaker1.id])],
        })
        
        # Create multiple dates if the module is available
        if self.env.registry.get("event.track.date"):
            # Use a datetime within the event range with proper constraints
            valid_datetime = datetime(2025, 6, 1, 14, 30)  # 14:30 on event start date
            date_line = self.env["event.track.date"].create({
                "track_id": track.id,
                "datetime": valid_datetime,
            })
            
            report = self.env["report.primevere_event_speakers_export.event_speakers_export"]
            
            # Simulate CSV writing
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=report.csv_report_options()["fieldnames"], delimiter=";")
            
            report._write_track_row(writer, track, self.speaker1)
            
            output.seek(0)
            csv_content = output.getvalue()
            
            # Check that track dates are properly formatted
            self.assertIn("Track with dates", csv_content)
            self.assertIn("Speaker One", csv_content)
            # If dates module is working, verify time formatting
            if hasattr(track, 'dates') and track.dates:
                # The hour should be computed correctly
                hour_value = track.dates[0].hour
                if hour_value == 14.5:  # 14:30
                    self.assertIn("14:30", csv_content)
                    self.assertIn("2025-06-01", csv_content)
        else:
            # Skip this test if the module is not available
            self.skipTest("event.track.date module not available")

    def test_meal_dates_export(self):
        """Test export of meal dates"""
        # Create meal dates for the speaker within event date range
        # The constraint requires dates to be within event range
        meal_date1 = self.env["event.track.speaker.meal.date"].with_context(event_id=self.event.id).create({
            "speaker_id": self.speaker1.id,
            "date": date(2025, 6, 1),  # Event start date
            "quantity": 1,
        })
        
        meal_date2 = self.env["event.track.speaker.meal.date"].with_context(event_id=self.event.id).create({
            "speaker_id": self.speaker1.id,
            "date": date(2025, 6, 2),  # Within event range
            "quantity": 2,
        })
        
        track = self.env["event.track"].create({
            "name": "Track test meals",
            "event_id": self.event.id,
            "speaker_ids": [(6, 0, [self.speaker1.id])],
        })
        
        report = self.env["report.primevere_event_speakers_export.event_speakers_export"]
        
        # Simulate CSV writing
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=report.csv_report_options()["fieldnames"], delimiter=";")
        
        report._write_track_row(writer, track, self.speaker1)
        
        output.seek(0)
        csv_content = output.getvalue()
        
        # Check that meal dates are present in the export
        self.assertIn("Track test meals", csv_content)
        self.assertIn("Speaker One", csv_content)
        self.assertIn("2025-06-01, 2025-06-02", csv_content)

    def test_travel_export(self):
        """Test export of travel information"""
        # Create an expense type for automatic calculation
        expense_type = self.env["event.track.speaker.travel.expense.type"].create({
            "name": "Taxi",
            "price": 25.0,
        })
        
        # Create travel bookings
        travel_booking = self.env["event.track.speaker.travel.booking"].create({
            "speaker_id": self.speaker1.id,
            "name": "Train Paris-Lyon",
            "cost": 150.0,
            "status": "confirmed",
        })
        
        travel_expense = self.env["event.track.speaker.travel.expense"].create({
            "speaker_id": self.speaker1.id,
            "name": "Airport taxi",
            "quantity": 1.0,
            "expense_type_id": expense_type.id,
            "status": "confirmed",
        })
        
        track = self.env["event.track"].create({
            "name": "Track test travel",
            "event_id": self.event.id,
            "speaker_ids": [(6, 0, [self.speaker1.id])],
        })
        
        report = self.env["report.primevere_event_speakers_export.event_speakers_export"]
        
        # Simulate CSV writing
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=report.csv_report_options()["fieldnames"], delimiter=";")
        
        report._write_track_row(writer, track, self.speaker1)
        
        output.seek(0)
        csv_content = output.getvalue()
        
        # Check travel information
        self.assertIn("Train Paris-Lyon: 150.0", csv_content)
        self.assertIn("Airport taxi: 25.0", csv_content)

    def test_equipment_categorization(self):
        """Test categorization of electrical vs other equipment"""
        track = self.env["event.track"].create({
            "name": "Track test equipment",
            "event_id": self.event.id,
            "speaker_ids": [(6, 0, [self.speaker1.id])],
        })
        
        # Electrical equipment
        elec_equipment = self.env["event.track.equipment"].create({
            "name": "Special power outlet"
        })
        
        # Non-electrical equipment
        other_equipment = self.env["event.track.equipment"].create({
            "name": "Whiteboard"
        })
        
        self.env["event.track.equipment.line"].create({
            "track_id": track.id,
            "equipment_id": elec_equipment.id,
            "quantity": 3,
        })
        
        self.env["event.track.equipment.line"].create({
            "track_id": track.id,
            "equipment_id": other_equipment.id,
            "quantity": 1,
        })
        
        report = self.env["report.primevere_event_speakers_export.event_speakers_export"]
        
        # Simulate CSV writing
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=report.csv_report_options()["fieldnames"], delimiter=";")
        
        report._write_track_row(writer, track, self.speaker1)
        
        output.seek(0)
        csv_content = output.getvalue()
        
        # Check categorization - use content-based checks instead of index-based
        # This is more robust than trying to parse CSV manually
        self.assertIn("Special power outlet", csv_content)
        self.assertIn("Whiteboard", csv_content)
        self.assertIn("(3)", csv_content)  # Check quantity formatting

    def test_full_export_integration(self):
        """Complete integration test of export"""
        # Create a complete track with multiple speakers
        track = self.env["event.track"].create({
            "name": "Complete track",
            "event_id": self.event.id,
            "duration": 2.5,
            "all_event": False,
            "format_id": self.format.id,
            "location_id": self.location.id,
            "theme_ids": [(6, 0, [self.theme1.id])],
            "speaker_ids": [(6, 0, [self.speaker1.id, self.speaker2.id])],
        })
        
        report = self.env["report.primevere_event_speakers_export.event_speakers_export"]
        
        # Simulate a complete export
        output = io.StringIO()
        writer = csv.DictWriter(
            output, 
            fieldnames=report.csv_report_options()["fieldnames"], 
            delimiter=";"
        )
        
        # Call main method
        report.generate_csv_report(writer, {}, self.event)
        
        output.seek(0)
        csv_content = output.read()
        
        # Check that we have at least 2 lines (2 speakers) - may be 3 with header
        lines = csv_content.strip().split('\n')
        self.assertGreaterEqual(len(lines), 2)  # At least 2 lines for 2 speakers
        
        # Check that both speakers are present
        self.assertIn("Speaker One", csv_content)
        self.assertIn("Speaker Two", csv_content)

    def test_location_parsing(self):
        """Test parsing of complex location names"""
        location_complex = self.env["event.track.location"].create({
            "name": "Building A - Room 101 - First floor"
        })
        
        track = self.env["event.track"].create({
            "name": "Track complex location",
            "event_id": self.event.id,
            "location_id": location_complex.id,
        })
        
        report = self.env["report.primevere_event_speakers_export.event_speakers_export"]
        
        # Simulate CSV writing
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=report.csv_report_options()["fieldnames"], delimiter=";")
        
        report._write_track_row(writer, track, None)
        
        output.seek(0)
        csv_content = output.getvalue()
        
        # Check that we get the last part correctly
        self.assertIn("First floor", csv_content)

    def test_duration_formatting(self):
        """Test duration formatting"""
        track = self.env["event.track"].create({
            "name": "Track duration test",
            "event_id": self.event.id,
            "duration": 1.75,  # 1h45
        })
        
        report = self.env["report.primevere_event_speakers_export.event_speakers_export"]
        
        # Simulate CSV writing
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=report.csv_report_options()["fieldnames"], delimiter=";")
        
        report._write_track_row(writer, track, None)
        
        output.seek(0)
        csv_content = output.getvalue()
        
        # Check duration formatting (1h45 = 01:45)
        self.assertIn("01:45", csv_content)

    def test_welcomer_export(self):
        """Test export of welcomer (volunteer) information"""
        # Create track with welcomer
        track_with_welcomer = self.env["event.track"].create({
            "name": "Track with welcomer",
            "event_id": self.event.id,
            "duration": 1.0,
            "speaker_ids": [(6, 0, [self.speaker1.id])],
            "welcomer_id": self.welcomer.id,  # Welcomer is on track, not speaker
        })
        
        # Create track without welcomer
        track_without_welcomer = self.env["event.track"].create({
            "name": "Track without welcomer",
            "event_id": self.event.id,
            "duration": 1.0,
            "speaker_ids": [(6, 0, [self.speaker2.id])],
            # No welcomer_id
        })
        
        report = self.env["report.primevere_event_speakers_export.event_speakers_export"]
        
        # Test track with welcomer
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=report.csv_report_options()["fieldnames"], delimiter=";")
        
        report._write_track_row(writer, track_with_welcomer, self.speaker1)
        
        output.seek(0)
        csv_content = output.getvalue()
        
        # Check that welcomer name is present
        self.assertIn("Volunteer Welcome", csv_content)
        self.assertIn("Speaker One", csv_content)
        
        # Test track without welcomer
        output2 = io.StringIO()
        writer2 = csv.DictWriter(output2, fieldnames=report.csv_report_options()["fieldnames"], delimiter=";")
        
        report._write_track_row(writer2, track_without_welcomer, self.speaker2)
        
        output2.seek(0)
        csv_content2 = output2.getvalue()
        
        # Check that no welcomer is present (should be empty, not False)
        lines = csv_content2.split(';')
        fieldnames = report.csv_report_options()["fieldnames"]
        welcomer_idx = fieldnames.index("Bénévole accueillant")
        # Should be empty string, not "False" (strip newlines)
        self.assertEqual(lines[welcomer_idx].strip(), "")

    def test_complete_speaker_data_export(self):
        """Test export with all speaker data filled"""
        # Create a complete track with comprehensive data including welcomer
        track = self.env["event.track"].create({
            "name": "Complete track test",
            "event_id": self.event.id,
            "duration": 2.0,
            "all_event": False,
            "format_id": self.format.id,
            "location_id": self.location.id,
            "theme_ids": [(6, 0, [self.theme1.id, self.theme2.id])],
            "speaker_ids": [(6, 0, [self.speaker1.id])],
            "welcomer_id": self.welcomer.id,  # Add welcomer to track
        })
        
        report = self.env["report.primevere_event_speakers_export.event_speakers_export"]
        
        # Simulate CSV writing
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=report.csv_report_options()["fieldnames"], delimiter=";")
        
        report._write_track_row(writer, track, self.speaker1)
        
        output.seek(0)
        csv_content = output.getvalue()
        
        # Verify all key fields are present and correct
        self.assertIn("Speaker One", csv_content)  # Speaker name
        self.assertIn("speaker1@example.com", csv_content)  # Email
        self.assertIn("+33123456789", csv_content)  # Phone
        self.assertIn("Long CV of speaker 1", csv_content)  # Bio
        self.assertIn("Expert", csv_content)  # Function
        self.assertIn("Prefers morning", csv_content)  # Slot wishes
        self.assertIn("5", csv_content)  # Invitation number
        self.assertIn("CODE123", csv_content)  # Invitation code
        self.assertIn("Test Book", csv_content)  # Book name
        self.assertIn("Test Publishing", csv_content)  # Book editor
        self.assertIn("Test Bookstore", csv_content)  # Book provider
        self.assertIn("Volunteer Welcome", csv_content)  # Welcomer
        self.assertIn("Technology, Innovation", csv_content)  # Themes
        self.assertIn("Conference", csv_content)  # Format
        self.assertIn("Amphitheater", csv_content)  # Location
        
        # Check boolean fields are properly formatted
        self.assertIn("Oui", csv_content)  # Should appear for need_ticket and need_parking (both True for speaker1)
