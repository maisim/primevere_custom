# Primevere Event Speakers Export

This module adds a CSV export report for event speakers in Primevere events.

## Features

- CSV export of all speakers for an event
- One line per speaker per session (if a session has 3 speakers, there will be 3 lines)
- Available in the "Print" menu of events, next to the "Website Export CSV"

## Exported Fields

The report contains the following fields:

### Session Information

- Session ID
- Session date
- Session time
- All event
- Responsible
- Session location
- Session format
- Session duration
- Session title
- Session theme

### Speaker Information

- Speaker ID
- Speaker name
- Speaker email
- Speaker mobile phone
- Long speaker summary
- Summary for presentation
- Commission
- Time preferences

### Books

- Book name
- Publishing house
- Provider

### Equipment

- Electrical equipment
- Equipment (number and object)

### Logistics

- Meals (list of days)
- Travel booking
- Travel expense
- Parking logistics
- Ticket logistics
- Invitation number logistics
- Invitation code logistics
- Welcomer volunteer

## Installation

This module depends on:

- `primevere_event_custom`
- `report_csv`

It is installed automatically with the Primevere system.

## Usage

1. Go to Events menu
2. Open an event
3. Click "Print"
4. Select "Speakers Export CSV"

The generated CSV file will use `;` delimiter and UTF-8 encoding.
