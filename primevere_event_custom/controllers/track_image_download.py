# SPDX-FileCopyrightText: 2024 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import base64
import io
import zipfile

from odoo import http
from odoo.http import request


class TrackImageDownload(http.Controller):
    @http.route(
        "/primevere_event_custom/event/<model('event.event'):event>"
        "/tracks/website_image/download",
        auth="user",
    )
    def download_track_website_image(self, event, **kw):
        """Create a zip with all the track images and serve it"""
        tracks = request.env["event.track"].search([("event_id", "=", event.id)])
        zipname = f"event-{event.id}-tracks-website_image.zip"
        with io.BytesIO() as buffer:
            with zipfile.ZipFile(
                buffer, mode="w", compression=zipfile.ZIP_DEFLATED
            ) as ziparc:
                for track in tracks:
                    if track.website_image:
                        ziparc.writestr(
                            track.website_image_export_name,
                            base64.b64decode(track.website_image),
                        )
            attach = request.env["ir.attachment"].new(
                {
                    "name": zipname,
                    "db_datas": buffer.getvalue(),
                    "mimetype": "application/zip",
                    "type": "binary",
                }
            )
        stream = http.Stream.from_attachment(attach)
        return stream.get_response(as_attachment=True, immutable=False)
