#!/usr/bin/python3
import urllib.request
from lxml import html
import sys
import itertools
import re
from time import strftime
import multiprocessing


def printnl(s):
	print(s, end="")
	sys.stdout.flush()


def flatten(listOfLists):
    "Flatten one level of nesting"
    return itertools.chain.from_iterable(listOfLists)


def get_iop_cal_xml(year, month):
	calendar_print_url = "http://www.iop.harvard.edu/print/calendar/month/%04d-%02d" % (year, month)
	with urllib.request.urlopen(calendar_print_url) as response:
		html = response.read()
		return html


def extract_ics_urls(iop_xml):
	tree = html.fromstring(iop_xml)
	ics_urls = tree.xpath('//*[@class="add-to-calendar-button"]/@href')
	return ics_urls


def get_ics(ics_url):
	with urllib.request.urlopen(ics_url) as response:
		return response.read().decode('UTF-8')


def combine_ics(icss):
	has_set_calendar_meta = False
	past_vcal_meta = False
	ics_lines = []
	for line in flatten([ics.split("\r\n") for ics in icss]):
		if "END:VCALENDAR" not in line:
			if not has_set_calendar_meta:
				ics_lines.append(line)
			if past_vcal_meta:
				ics_lines.append(line)
			if "BEGIN:VEVENT" in line:
				has_set_calendar_meta = True
				past_vcal_meta = True
		else:
			past_vcal_meta = False
	ics_lines.append("END:VCALENDAR")
	return ics_lines


def __cli_download_event(event_url):
	ics_data = get_ics(event_url)
	print("%s ----> %d bytes" % (event_url, len(ics_data)))
	return ics_data


if __name__ == '__main__':
	try:
		cli_output = True

		print("\n#==   Extracting Events   ==#")
		event_urls = []
		for year in [2015]:
			for month_less_one in range(12):
				month = month_less_one + 1
				printnl("Calendar %04d-%02d" % (year, month))
				ics_urls = extract_ics_urls(get_iop_cal_xml(year, month))
				event_urls.extend(ics_urls)
				print(" ----> %d events" % len(ics_urls))
		print("Extracted %d events" % len(event_urls))

		print("\n#==  Downloading Events   ==#")
		with multiprocessing.Pool(processes = 5) as pool:
			event_icss = pool.map(__cli_download_event, event_urls)

		print("\n#==   Processing Events   ==#")
		print("Combining ICS events")
		events_ics = '\n'.join(combine_ics(event_icss))

		if len(sys.argv) == 2:
			file_name = sys.argv[1]
		else:
			file_name = "iop_events_%s.ics" % strftime("%Y-%m-%dT%H-%M-%S")

		with open(file_name, "w") as file:
		    file.write(events_ics)
		print('\n%d events written to %s (%d kb)' % (len(event_urls), file_name, len(events_ics) / 1000))

	except KeyboardInterrupt:
		printnl("\nexiting")
		sys.exit(1)


