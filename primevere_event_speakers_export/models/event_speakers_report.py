# Copyright 2025 Association Primevère
# License: AGPL-3.0-or-later

import csv
import datetime

from odoo import models


class EventSpeakersExportCSV(models.AbstractModel):
    _name = "report.primevere_event_speakers_export.event_speakers_export"
    _description = "Event Speakers Export CSV Report"
    _inherit = "report.report_csv.abstract"

    def generate_csv_report(self, writer, data, event):
        tracks = event.track_ids
        writer.writeheader()

        for track in tracks:
            # If the track has no speakers, we still generate an empty line
            if not track.speaker_ids:
                self._write_track_row(writer, track, None)
            else:
                # One line per speaker
                for speaker in track.speaker_ids:
                    self._write_track_row(writer, track, speaker)

    def _write_track_row(self, writer, track, speaker):
        """Write a single row for a given track and speaker."""
        # Session date and time - uses multi-date track dates if available
        session_date = ""
        session_time = ""

        # Special formatting for "all event" sessions (en permanence)
        if track.all_event:
            session_date = "00-00-0000"
            session_time = "00:00:00"
        elif hasattr(track, "dates") and track.dates:
            # Use first date if multiple dates
            first_date = track.dates[0]
            session_date = first_date.date
            # Convert float hour to HH:MM format
            hour = int(first_date.hour)
            minute = round(60 * (first_date.hour - hour))
            session_time = datetime.time(hour=hour, minute=minute).isoformat(
                timespec="minutes"
            )
        elif track.date:
            session_date = track.date
            hour = (
                int(track.date_begin_located_hour)
                if hasattr(track, "date_begin_located_hour")
                else 0
            )
            minute = (
                round(60 * (track.date_begin_located_hour - hour))
                if hasattr(track, "date_begin_located_hour")
                else 0
            )
            session_time = datetime.time(hour=hour, minute=minute).isoformat(
                timespec="minutes"
            )

        # Session duration
        duration_str = ""
        if track.duration:
            hour = int(track.duration)
            minute = round(60 * (track.duration - hour))
            duration_str = datetime.time(hour=hour, minute=minute).isoformat(
                timespec="minutes"
            )

        # Session location (parsing location name)
        location_name = ""
        if track.location_id:
            locations = tuple(map(str.strip, track.location_id.name.split("-")))
            location_name = locations[-1] if locations else ""

        # Speaker information
        speaker_id = speaker.id if speaker else ""
        speaker_name = speaker.name if speaker else ""
        speaker_email = speaker.email if speaker else ""
        speaker_phone = speaker.phone if speaker else ""
        speaker_bio_long = (
            speaker.curriculum_vitae
            if speaker
            and hasattr(speaker, "curriculum_vitae")
            and speaker.curriculum_vitae
            else ""
        )
        speaker_bio_short = speaker.biography if speaker and speaker.biography else ""
        speaker_function = speaker.function if speaker and speaker.function else ""
        slot_wishes = (
            speaker.slot_wishes
            if speaker and hasattr(speaker, "slot_wishes") and speaker.slot_wishes
            else ""
        )
        invitation_number = (
            speaker.invitation_number
            if speaker
            and hasattr(speaker, "invitation_number")
            and speaker.invitation_number
            else ""
        )
        invitation_code = (
            speaker.invitation_code
            if speaker
            and hasattr(speaker, "invitation_code")
            and speaker.invitation_code
            else ""
        )
        need_ticket = (
            "Oui"
            if speaker and hasattr(speaker, "need_ticket") and speaker.need_ticket
            else "Non"
        )
        need_parking = (
            "Oui"
            if speaker
            and hasattr(speaker, "need_reserved_car_place")
            and speaker.need_reserved_car_place
            else "Non"
        )

        # Bénévole accueillant (welcomer) - on track, not speaker
        welcomer_name = ""
        if track and hasattr(track, "welcomer_id") and track.welcomer_id:
            welcomer_name = track.welcomer_id.name

        # Books
        book_names = ""
        book_editors = ""
        book_providers = ""
        if speaker:
            # Look for books where this speaker is mentioned
            books = self.env["event.track.speaker.book"].search(
                [("speaker_ids", "in", speaker.id)]
            )
            if books:
                book_names = ", ".join([book.name for book in books if book.name])
                book_editors = ", ".join(
                    [
                        book.editor_id.name
                        for book in books
                        if book.editor_id and book.editor_id.name
                    ]
                )
                book_providers = ", ".join(
                    [
                        book.provider_id.name
                        for book in books
                        if book.provider_id and book.provider_id.name
                    ]
                )

        # Meals
        meal_dates = ""
        if speaker and hasattr(speaker, "meal_date_ids") and speaker.meal_date_ids:
            dates = [
                meal.date.strftime("%Y-%m-%d")
                for meal in speaker.meal_date_ids
                if meal.date
            ]
            meal_dates = ", ".join(dates)

        # Travel booking et expenses
        travel_booking = ""
        travel_expense = ""
        if (
            speaker
            and hasattr(speaker, "travel_booking_ids")
            and speaker.travel_booking_ids
        ):
            travel_booking = ", ".join(
                [
                    f"{booking.name}: {booking.cost}"
                    for booking in speaker.travel_booking_ids
                ]
            )
        if (
            speaker
            and hasattr(speaker, "travel_expense_ids")
            and speaker.travel_expense_ids
        ):
            travel_expense = ", ".join(
                [
                    f"{expense.name}: {expense.cost}"
                    for expense in speaker.travel_expense_ids
                ]
            )

        # Equipment
        equipment_electricity = ""
        equipment_list = ""
        if hasattr(track, "equipment_line_ids") and track.equipment_line_ids:
            electricity_equip = []
            other_equip = []
            for line in track.equipment_line_ids:
                equip_name = line.equipment_id.name if line.equipment_id else ""
                equip_qty = line.quantity
                equip_text = (
                    f"{equip_name} ({equip_qty})" if equip_qty > 1 else equip_name
                )

                # Determine if it's electrical equipment (based on name)
                if any(
                    keyword in equip_name.lower()
                    for keyword in ["électr", "electric", "prise", "courant", "alim"]
                ):
                    electricity_equip.append(equip_text)
                else:
                    other_equip.append(equip_text)

            equipment_electricity = ", ".join(electricity_equip)
            equipment_list = ", ".join(other_equip)

        # Themes
        themes = ""
        if hasattr(track, "theme_ids") and track.theme_ids:
            themes = ", ".join([theme.name for theme in track.theme_ids if theme.name])

        writer.writerow(
            {
                "Id intervenant": speaker_id,
                "Id session": track.id,
                "date session": session_date,
                "horaire session": session_time,
                "en permanence": "Oui" if track.all_event else "Non",
                "responsable": track.user_id.name if track.user_id else "",
                "lieux session": location_name,
                "format session": track.format_id.name if track.format_id else "",
                "durée session": duration_str,
                "titre session": track.name or "",
                "nom intervenant": speaker_name,
                "mail intervenant": speaker_email,
                "tel portable intervenant": speaker_phone,
                "récap intervenant long": speaker_bio_long,
                "Résumé pour présentation": speaker_bio_short,
                "commission": speaker_function,
                "thème session": themes,
                "souhait horaire": slot_wishes,
                "nom livre": book_names,
                "maison édition": book_editors,
                "provider": book_providers,
                "Equipement électricité": equipment_electricity,
                "Equipement (nombre et objet)": equipment_list,
                "repas (liste des jours)": meal_dates,
                "travel booking": travel_booking,
                "travel expense": travel_expense,
                "logistique parking": need_parking,
                "logistique ticket": need_ticket,
                "logistique nombre invitation": invitation_number,
                "logistique code invitation": invitation_code,
                "Bénévole accueillant": welcomer_name,
            }
        )

    def csv_report_options(self):
        res = super().csv_report_options()
        res["fieldnames"] = [
            "Id intervenant",
            "Id session",
            "date session",
            "horaire session",
            "en permanence",
            "responsable",
            "lieux session",
            "format session",
            "durée session",
            "titre session",
            "nom intervenant",
            "mail intervenant",
            "tel portable intervenant",
            "récap intervenant long",
            "Résumé pour présentation",
            "commission",
            "thème session",
            "souhait horaire",
            "nom livre",
            "maison édition",
            "provider",
            "Equipement électricité",
            "Equipement (nombre et objet)",
            "repas (liste des jours)",
            "travel booking",
            "travel expense",
            "logistique parking",
            "logistique ticket",
            "logistique nombre invitation",
            "logistique code invitation",
            "Bénévole accueillant",
        ]
        res["delimiter"] = ";"
        res["quoting"] = csv.QUOTE_MINIMAL
        return res
