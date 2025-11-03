# SPDX-FileCopyrightText: 2024 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
import datetime

from odoo import models


class TrackWebsiteExportCSV(models.AbstractModel):
    _name = "report.primevere_event_custom.track_export_website"
    _inherit = "report.report_csv.abstract"

    def generate_csv_report(self, writer, data, event):
        tracks = event.track_ids
        writer.writeheader()
        for track in tracks:
            # Special handling for permanent sessions without dates
            if track.all_event and not track.dates:
                self._write_permanent_track_row(writer, track, sequence=1)
            else:
                # Normal processing for sessions with dates
                for sequence, date_line in enumerate(track.dates, start=1):
                    self._write_normal_track_row(writer, track, date_line, sequence)

    def _write_permanent_track_row(self, writer, track, sequence):
        """Write a row for a permanent session without dates."""
        # Use special formatting for permanent sessions
        track_time = "00:00:00"
        track_date = "00-00-0000"
        track_id = track.id  # Always use track ID
        id_horaire = f"{track_id}{sequence}"  # Concatenate track ID with sequence

        # Format duration
        track_duration = self._format_duration(track.duration)

        # Parse location
        locations = self._parse_location(track)

        # Write the row
        self._write_csv_row(
            writer,
            {
                "id": track_id,
                "id_horaire": id_horaire,
                "date": track_date,
                "heure": track_time,
                "permanent": int(track.all_event),
                "lieux_parent": locations[0] if len(locations) > 1 else "",
                "lieux": locations[-1] if locations else "",
                "forme": track.format_id.name if track.format_id else "",
                "duree": track_duration.isoformat(timespec="minutes"),
            },
            track,
        )

    def _write_normal_track_row(self, writer, track, date_line, sequence):
        """Write a row for a normal session with dates."""
        # Format time from date_line
        hour = int(date_line.hour)
        minute = round(60 * (date_line.hour - hour))
        track_time = datetime.time(hour=hour, minute=minute)

        # Format duration
        track_duration = self._format_duration(track.duration)

        # Parse location
        locations = self._parse_location(track)

        # Use track ID (not date_line ID) and create id_horaire
        track_id = track.id
        id_horaire = f"{track_id}{sequence}"

        # Write the row
        self._write_csv_row(
            writer,
            {
                "id": track_id,
                "id_horaire": id_horaire,
                "date": date_line.date,
                "heure": track_time.isoformat(timespec="minutes"),
                "permanent": int(track.all_event),
                "lieux_parent": locations[0] if len(locations) > 1 else "",
                "lieux": locations[-1] if locations else "",
                "forme": track.format_id.name if track.format_id else "",
                "duree": track_duration.isoformat(timespec="minutes"),
            },
            track,
        )

    def _format_duration(self, duration):
        """Format track duration as time object."""
        hour = int(duration)
        minute = round(60 * (duration - hour))
        return datetime.time(hour=hour, minute=minute)

    def _parse_location(self, track):
        """Parse location name into parent and child parts."""
        if track.location_id:
            return tuple(map(str.strip, track.location_id.name.split("-")))
        return ("", "")

    def _write_csv_row(self, writer, base_data, track):
        """Write a CSV row with common track information."""
        row_data = base_data.copy()
        row_data.update(
            {
                "intervenant court": track.com_info_speaker_short or "",
                "titre session": track.name or "",
                "presentation intervenant longue": track.com_info_speaker_long or "",
                "texte de présentation": track.com_info_event or "",
                "contact des intervenants": track.com_info_contacts or "",
                "theme": ",".join(track.theme_ids.mapped("name")),
                "photo": track.website_image_export_name or "",
                "age spécifique": track.com_info_age or "",
                "info dernière minute": track.com_info_note or "",
            }
        )
        writer.writerow(row_data)

    def csv_report_options(self):
        res = super().csv_report_options()
        res["fieldnames"].append("id")
        res["fieldnames"].append("id_horaire")
        res["fieldnames"].append("date")
        res["fieldnames"].append("heure")
        res["fieldnames"].append("permanent")
        res["fieldnames"].append("lieux_parent")
        res["fieldnames"].append("lieux")
        res["fieldnames"].append("forme")
        res["fieldnames"].append("duree")
        res["fieldnames"].append("intervenant court")
        res["fieldnames"].append("titre session")
        res["fieldnames"].append("presentation intervenant longue")
        res["fieldnames"].append("texte de présentation")
        res["fieldnames"].append("contact des intervenants")
        res["fieldnames"].append("theme")
        res["fieldnames"].append("photo")
        res["fieldnames"].append("age spécifique")
        res["fieldnames"].append("info dernière minute")
        res["delimiter"] = ";"
        res["quoting"] = csv.QUOTE_MINIMAL
        return res
