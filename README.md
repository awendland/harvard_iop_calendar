# Harvard IOP Events

Extracts all the IOP events in a given date range and converts them into a single ICS file for import

The daily output of this script can be found at <http://alexwendland.com/harvard/iop_events.ics>. Adding this URL to a calendar (such as Google Calendar) will keep you updated with all the latest IOP events.

## Requirements

* Python 3
* lxml

## Usage

`python3 iop_calendar.py` will download all the calendar events from IOP for the 2015 year and will combine them into a single file called `iop_events_YYYY-MM-DDTHH-MM-SS.ics`.

`python3 iop_calendar.py file_name` will combine them into a single file called `file_name`.