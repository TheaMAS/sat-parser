import sys
import csv
import os
# from datetime import date
import random
from itertools import combinations

import pandas as pd

import time_utilities as tu
from os_utilities import *
from orb_parser import *


DEBUG = True;

# #Is this thing a file?
# def file_check(fn):
# 	try:
# 		open(fn, "r")
# 		return 1
# 	except IOError:
# 		print("Error: Needs a file")
# 		return 0
#
# def read_file(fn):
# 	data = ""
# 	with open(fn) as f:
#    		data = f.read()
# 	return data;

# def add_analysis(label, a_name, b_name, variable_type, lower_bound, upper_bound):
# 	text = read_file("./templates/analysis.orb")
# 	text = text.format(
# 		label = label,
# 		a = a_name,
# 		b = b_name,
# 		variable = variable_type,
# 		lower = lower_bound,
# 		upper = upper_bound
# 		)
# 	return text
# print(add_analysis("Distance", "SL-1234", "SL-5678", "RANGE_MAGNITUDE", 0, 63781))


exit()


#I wanted to write something that parsed individual TLE blobs in case we wind up needing it...
#I also wrote this before realizing we were inputting CSV so oops
#parse_tle takes a single TLE and returns its formatted text
sample = """TDRS 9
1 27389U 02011A   22135.33389021 -.00000278  00000+0  00000+0 0  9991
2 27389   8.9517  61.1184 0026249 303.3709 286.5593  1.00273101 75465"""

def parse_tle(tle):
	#Separate lines of TLE and strip whitespace
	s = [item.strip() for item in tle.split('\n')]
	#Line 2 and 3 also need to be split
	s[1] = [item.strip() for item in s[1].split(" ")]
	s[2] = [item.strip() for item in s[2].split(" ")]
	while("" in s[1]):
		s[1].remove("")
	while("" in s[2]):
		s[2].remove("")
	print(s[1])
	print(s[2])
	#Instantiate String
	retstr = ""
	retstr = retstr + "DEFINE PLATFORM NORAD \"" + s[0] + "\"\n"
	retstr = retstr + "        " + "STATE " + s[1][1].replace("U","") + "  " + s[1][3][0:2] + " " +  s[1][3][2:] + " "
	retstr = retstr + s[1][4] + " " + s[1][5] + " " + s[1][6] + " " + s[1][7] + " " + s[1][8]
	retstr = retstr + s[2][2] + " " + s[2][3] + " " + s[2][4] + " " + s[2][5] + " " + s[2][6] + " " + s[2][7] + " " + s[2][8]
	retstr += "\n SHAPE SATELLITE\nCOLOR Magenta\nICON ON\nERROR_ELLIPSOID OFF\nLABEL ON\nGROUND_TRACE OFF\nSUBPOINT OFF\nORBIT OFF\nDEADB4EPOCH OFF"
	return retstr

# print (parse_tle(sample))

#TODO: Could be useful functionality but is unnecessary right now
def tle_to_csv(tle):
	return 0

#Also generates transmitters
def parse_csv_satellites(file=""):
	# SHAPE VIEW_ONLY

	#Did we pass a file?
	if(len(sys.argv) > 1):
		if(file_check(sys.argv[1])):
			retstr = ""
			with open(sys.argv[1]) as f:
				reader = csv.DictReader(f)
				for row in reader:
					#All Whitespace in this concatenation is to preserve the structure identified in the .orb
					retstr += "DEFINE PLATFORM NORAD \"" + row['OBJECT_NAME'] + "\"\n"
					retstr += "\t" + "STATE " + row['NORAD_CAT_ID'] + "  " + epoch_year(row['EPOCH']) + " " +  orb_epoch(row['EPOCH']) + " "
					retstr += row['MEAN_MOTION_DOT'] + " " + row['MEAN_MOTION_DDOT'] + " " + row['BSTAR'] + " " + row['EPHEMERIS_TYPE'] + " " + row['ELEMENT_SET_NO'] + " "
					retstr += row['INCLINATION'] + " " + row['RA_OF_ASC_NODE'] + " " + row['ECCENTRICITY'] + " " + row['ARG_OF_PERICENTER'] + " "
					retstr += row['MEAN_ANOMALY'] + " " + row['MEAN_MOTION'] + " " + row['REV_AT_EPOCH'] +"\n"
					retstr += "  SHAPE VIEW_ONLY\n    COLOR Magenta\n  ICON OFF\n  ERROR_ELLIPSOID OFF\n  LABEL OFF\n  GROUND_TRACE OFF\n  SUBPOINT OFF\n  ORBIT OFF\n  DEADB4EPOCH OFF" + "\n\n"
					retstr += "DEFINE JX  \"" + row['OBJECT_NAME'] + " Tx\"\n  TXPT TXCS  \".Earth Cartesian\"\n  PLAT  \"" + row['OBJECT_NAME'] + "\"\n	OPERFREQ 1000.000000000000000 \n"
					retstr += "\tTXPOWER 1.000000000000000 \n\tTXLINELOSS 0.000000000000000 \n  WAVEFORM CONTINUOUS \n  TGAINPATTERN PARABOLIC\n	CONEANGLE 180.000000000000000 \n	ANTDIAM 10.000000000000000 \n	ANTEFFIC 0.550000000000000 \n\n"
			if(file != ""):
				print(file)
			return retstr
		else:
			return 0
	else:
		return 0



exit()


#Also generates receivers
def parse_csv_links(file=""):
	#Did we pass a file?
	if(file_check(sys.argv[1])):
		retstr = ""
		sat_array = []
		with open(sys.argv[1]) as f:
			reader = csv.DictReader(f)
			for row in reader:
				sat_array.append(row['OBJECT_NAME'])
	else:
		return 0

	if DEBUG : print("There are {} satellites.".format(len(sat_array)))

	sample_size = 10
	if len(sat_array) > sample_size:
		sat_array = sample_sats(sat_array, sample_size)

	retstr = ""
	for pair in combinations(sat_array, 2):
		retstr += "DEFINE RF  \"" + pair[0] + " - " + pair[1] + "\"\n"
		retstr += "\tPRIMARY_TX \"" + pair[0] + " Tx\"\n"
		retstr += "  PLAT \"" + pair[1] + "\"\n"
		retstr += "  RXPT RXCS  \".Earth Cartesian\"\n\tBANDWIDTH 4.000000000000000 \n\tRXLINELOSS 0.000000000000000 \n\tRXTEMP 100.000000000000000 \n  RGAINPATTERN PARABOLIC\n"
		retstr += "\tCONEANGLE 180.000000000000000 \n\tANTDIAM 10.000000000000000 \n\tANTEFFIC 0.550000000000000 \n\tATMA_MODEL CCIR_719_2\n\tRAIN_MODEL CRANE_1980\n\t"
		retstr += "AVAIL 99.000000000000000 \n\tGRNDTEMP 273.000000000000000 \n\tRELHUMID 0.250000000000000 \n\tPLZTN_TILT 0.000000000000000 \n\tTSNR 0.000000000000000 \n\t"
		retstr += "IRAIN OFF\n\tIATMOSPHERE OFF\n\tPRAIN ON\n\tPATMOSPHERE ON\n\tDOPPLER OFF\n\tLINK ON\n\tCUE OFF\n\tUSE_BODY ON\n\tUSE_TERRAIN ON\n\tUSE_3DMODELS OFF\n\t"
		retstr += "CONTOURS OFF\n  NCONTOURS 10\n\tCONTOURI 1.000000000000000 \n  JCONTOURS OFF\n\tTEIRP 0.000000000000000 \n  TERMINAL ALONG_BORESIGHT 0.000000\n\t"
		retstr += "JCPOWER\n\t 0.000000\n\t 0.000000\n\t 0.000000\n\t0.000000\n\t 0.000000\n\tJSR\n\t 0.000000\n\t 0.000000\n\t 0.000000\n\t 0.000000\n\t 0.000000\n\t"
		retstr += "JCOLOR\n\t 134\n\t 134\n\t 134\n\t 134\n\t 134\n\n"

		# TODO : separate all defines into own functions
		retstr += "DEFINE ANALYSIS  \"" + pair[0] + " - " + pair[1] + "\"\n" + \
			"  VARIABLE RX_TPOWER  \"" + pair[0] + " - " + pair[1] + \
			"\"\n" + "  BOUNDS                  -998                    30\n"
		retstr += "  COLOR Red\n  MARKER  \"*\"\n  LINK OFF\n  CUE OFF\n\n"

		retstr += "DEFINE ANALYSIS  \"Dist " + pair[0] + "-" + pair[1]  + \
			"\"\n  VARIABLE RANGE_MAGNITUDE  \"" + pair[0] + "\" \"" + \
			pair[1] + "\"\n  BOUNDS 0 63781.37\n\tCOLOR Red\n  " + \
			"MARKER  \"*\"\n  LINK OFF\n  CUE OFF\n  PLOT_ANALYSIS  \"" + \
			pair[0] + "-" + pair[1] + "\"\n\n"

	return retstr

definitions = parse_csv_satellites()
links = parse_csv_links()

def append_new_satellite_data(datastring, file):
	#Open file as append
	f = open(file,"a")
	f.write("\n\n" + datastring)
	f.close()
	return 0

append_new_satellite_data(parse_csv_satellites(),"test.orb")
print("Appended new satellites")
append_new_satellite_data(parse_csv_links(),"test.orb")
print("Appended new links")
