# -*- coding utf-8 -*-

import time
import sys
import string
import datetime
import RPi.GPIO as GPIO
import atexit

try:
	from xml.etree import ElementTree # for Python 2.5 users
except ImportError:
	from elementtree import ElementTree
import gdata.calendar
import gdata.calendar.service

# ======================================================
# !!! MODIFY THE CALENDAR ID AND STATION NAMES BELOW !!!
# ======================================================

# PUBLIC GOOGLE CALENDAR ID
# - the calendar should be set as public
# - calendar id can be found in calendar settings
# - !!!!!!!! PLEASE CHANGE THIS TO YOUR OWN CALENDAR ID !!!!!!
CALENDAR_ID = '5u5kgv3jp9s8s669vd2tubhv8g@group.calendar.google.com'

# STATION NAMES
# - specify the name : index for each station
# - station index starts from 0
# - station names are case sensitive
# - you can define multiple names for each station

STATIONS = {
	"side yard" 		: 0,
	"sideyard"		: 0,
	"Side Yard"		: 0,
	"SideYard"		: 0,

	"front yard"		: 1,  # you can map multiple common names
	"frontyard"		: 1,  # to the same station index
	"Front Yard"		: 1,
	"FrontYard"		: 1,

	"back yard"		: 2,
	"backyard"		: 2,
	"Back Yard"		: 2,
	"BackYard"		: 2,

	"side yard rear"	: 3,
	"sideyardrear"	: 3,
	"Side Yard Rear"	: 3,
	"SideYardRear"	: 3,
}

# ======================================================

# MAXIMUM NUMBER OF STATIONS
MAX_NSTATIONS = 4

# OSPI PIN DEFINES
pin_side_yard =  4
pin_front_yard = 17
pin_back_yard = 27
pin_side_yard_rear = 22

calendar_service = gdata.calendar.service.CalendarService()
query = gdata.calendar.service.CalendarEventQuery(CALENDAR_ID, 'public', 'full')
query.orderby = 'starttime'
query.singleevents = 'true'
query.sortorder = 'a'
station_bits = [0]*MAX_NSTATIONS

def disableAllRelays():
	GPIO.output(pin_side_yard, 0)
	GPIO.output(pin_front_yard, 0)
	GPIO.output(pin_back_yard, 0)
	GPIO.output(pin_side_yard_rear, 0)


def runOSPI():

	global station_bits
	now = datetime.datetime.now();
	print datetime.datetime.now();
	nextminute = now + datetime.timedelta(minutes=1)

	query.start_min = now.isoformat()
	query.start_max = nextminute.isoformat()

	station_bits = [0]*MAX_NSTATIONS;
	try:
		feed = calendar_service.CalendarQuery(query)
		print '(',
		for i, an_event in enumerate(feed.entry):
			if (i!=0):
				print ',',
			try:
				print an_event.title.text,
				station_bits[STATIONS[an_event.title.text]] = 1;
			except:
				print "-> #name not found#",
				#print '%s' % (an_event.title.text)
		print ')'
	except:
		print "#error getting calendar data#"
	try:
		GPIO.output(pin_side_yard, 1 if (station_bits[0]==1) else 0)
		GPIO.output(pin_front_yard, 1 if (station_bits[1]==1) else 0)
		GPIO.output(pin_back_yard, 1 if (station_bits[2]==1) else 0)
		GPIO.output(pin_side_yard_rear, 1 if (station_bits[3]==1) else 0)		
	except:
		print "#shiftOut error#"

def main():
	print('Dosmann Sprinkler System has started...')

	GPIO.cleanup()
	# setup GPIO pins to interface with shift register
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(pin_side_yard, GPIO.OUT)
	GPIO.setup(pin_front_yard, GPIO.OUT)
	GPIO.setup(pin_back_yard, GPIO.OUT)
	GPIO.setup(pin_side_yard_rear, GPIO.OUT)

	disableAllRelays()

	while True:
		try:
			runOSPI()
		except:
			pass
		time.sleep(60)  # check every 60 seconds

def progexit():
	global station_bits
	station_bits = [0]*MAX_NSTATIONS
	disableAllRelays()
	GPIO.cleanup()

if __name__ == "__main__":
	atexit.register(progexit)
	main()
