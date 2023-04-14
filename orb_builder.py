from sgp4 import exporter
from sgp4.api import Satrec

from os_utilities import *
from orb_parser import *

import time_utilities as tu
from datetime import date
from itertools import combinations

import random

if __name__ == "__main__":
	DEBUG = True;
else:
	DEBUG = False

def check_dupliate_sources(csv_data):
	"""
	This method checks for duplicate satellite names.
	If duplicates exist, there could be errors in the the soap output and
		analysis files.

		`csv_data` is assumed to be a pandas object returned from
		`get_csv_data` on the associated TLE .csv file.
	"""
	duplicates = False

	names = []
	for i in range(len(csv_data)):
		object_raw = csv_data.loc[i].to_dict();
		object_name = object_raw["OBJECT_NAME"]
		if object_name in names:
			duplicates = True
			break
		else:
			names.append(object_name)

	return duplicates

# def get_csv_data(csv_location):
# 	return pd.read_csv(csv_location)

if __name__ == "__main__":

	# Test that `check_dupliate_sources` actually catches errors
	csv_data = get_csv_data("./tests/sources_dupes.csv")
	assert(check_dupliate_sources(csv_data) == True)

	# Checks all csv in `/sources/` don't have duplicates.
	filepaths = get_csv_files("./sources/")
	for filepath in filepaths:
		csv_data = get_csv_data(filepath)
		assert(check_dupliate_sources(csv_data) == False)

	# for rest of the unit tests
	csv_data = get_csv_data("./sources/norad.csv")


def add_base(date):
	# if random_date:
	# 	year, month, day = tu.get_random_date()
	# else:
	# 	year, month, day = 2022, 4, 30

	text = read_file("./templates/base.orb")
	text = text.format(
		batchmode = "ON",
		warnings = "ON",
		year = date.year,
		month = date.month,
		day = date.day,
		hour = "0.0",
		minute = "0.0",
		second = "0.0"
		)
	return text

def create_object_dictionary(
		object_name,
		norad_cat_id,
		epoch_year,
		epoch_fraction,
		mean_motion_dot,
		mean_motion_ddot,
		bstar,
		ephemeris_type,
		element_set_no,
		inclination,
		ra_of_asc_node,
		eccentricity,
		arg_of_pericenter,
		mean_anomaly,
		mean_motion,
		rev_at_epoch
		):

	object = {}
	object["object_name"] = object_name # ex : TDRS 3
	object["norad_cat_id"] = norad_cat_id # ex : 19548
	object["epoch_year"] = epoch_year
	object["epoch_fraction"] = epoch_fraction
	object["mean_motion_dot"] = mean_motion_dot
	object["mean_motion_ddot"] = mean_motion_ddot
	object["bstar"] = bstar
	object["ephemeris_type"] = ephemeris_type
	object["element_set_no"] = element_set_no
	object["inclination"] = inclination
	object["ra_of_asc_node"] = ra_of_asc_node
	object["eccentricity"] = eccentricity
	object["arg_of_pericenter"] = arg_of_pericenter
	object["mean_anomaly"] = mean_anomaly
	object["mean_motion"] = mean_motion
	object["rev_at_epoch"] = rev_at_epoch

	return object;

# TODO : modify, more complicated than this
def create_custom_object_dictionary(
		system,
		platform_id,
		body,
		ic_type,
		orbit_type,
		semi_major_axis,
		eccentricity,
		inclination,
		ra_of_asc_node,
		arg_of_pericenter,
		mean_anomaly,
		year,
		month,
		day,
		hour,
		minute,
		second,
		):

	object = {}
	object["system"] = system # ex : NORAD, KEPLER, ECR_FIXED, ECI_FIXED
	object["object_name"] = platform_id
	object["body"] = body # ex : Earth, Moon, Mars, Sun
	object["ic_type"] = ic_type
	object["orbit_type"] = orbit_type # ex : CUSTOM, GEOSYNCHRONOUS
	object["semi_major_axis"] = semi_major_axis
	object["eccentricity"] = eccentricity
	object["inclination"] = inclination
	object["ra_of_asc_node"] = ra_of_asc_node
	object["arg_of_pericenter"] = arg_of_pericenter
	object["mean_anomaly"] = mean_anomaly
	object["year"] = year
	object["month"] = month
	object["day"] = day
	object["hour"] = hour
	object["minute"] = minute
	object["second"] = second

	return object;

def create_ground_object_dictionary(name, latitude, longitude, altitude):
	object = {}

	object["object_name"] = name
	object["latitude"] = latitude
	object["longitude"] = longitude
	object["altitude"] = altitude

	return object

def add_object(object):

	if "system" in object:
		text = read_file("./templates/platform_custom.orb")
	elif "latitude" in object:
		text = read_file("./templates/platform_ground.orb")
	else:
		text = read_file("./templates/platform.orb") # default : norad platform

	text = text.format(
		**object
		# object_name = object["object_name"],
		# norad_cat_id = object["norad_cat_id"],
		# mean_motion_dot = object["mean_motion_dot"],
		# mean_motion_ddot = object["mean_motion_ddot"],
		# bstar = object["bstar"],
		# ephemeris_type = object["ephemeris_type"],
		# element_set_no = object["element_set_no"],
		# inclination = object["inclination"],
		# ra_of_asc_node = object["ra_of_asc_node"],
		# eccentricity = object["eccentricity"],
		# arg_of_pericenter = object["arg_of_pericenter"],
		# mean_anomaly = object["mean_anomaly"],
		# mean_motion = object["mean_motion"],
		# rev_at_epoch = object["rev_at_epoch"]
	)
	return text

if __name__ == "__main__":

	object_raw = csv_data.loc[0].to_dict();
	object = {}
	object = create_object_dictionary(
		object_raw["OBJECT_NAME"],
		object_raw["NORAD_CAT_ID"],
		tu.epoch_year(object_raw["EPOCH"]),
		tu.epoch_fraction(object_raw["EPOCH"]),
		object_raw["MEAN_MOTION_DOT"],
		object_raw["MEAN_MOTION_DDOT"],
		object_raw["BSTAR"],
		object_raw["EPHEMERIS_TYPE"],
		object_raw["ELEMENT_SET_NO"],
		object_raw["INCLINATION"],
		object_raw["RA_OF_ASC_NODE"],
		object_raw["ECCENTRICITY"],
		object_raw["ARG_OF_PERICENTER"],
		object_raw["MEAN_ANOMALY"],
		object_raw["MEAN_MOTION"],
		object_raw["REV_AT_EPOCH"]
	)

	# Test default norad platform builder
	assert(add_object(object) == read_file("./tests/orb/platform_norad.orb"))

	# object_text = add_object(object)
	# print(len(object_text))
	# print(object_text)
	# norad_platform = read_file("./tests/orb/platform_norad.orb")
	# print(len(norad_platform))
	# print(norad_platform)
	# for i in range(len(object_text)):
		# o_char = object_text[i]
		# n_char = norad_platform[i]
		# print("{} -- {}".format(o_char, n_char))
		# print(o_char == n_char)

	# Test Moon custom platform builder
	object = get_platforms("./tests/orb/platforms_moon.orb")[0]
	#assert(add_object(object) == read_file("./tests/orb/platform_moon.orb"))

	# object_text = add_object(object)
	# print(len(object_text))
	# print(object_text)
	# moon_platform = read_file("./tests/orb/platform_moon.orb")
	# print(len(moon_platform))
	# print(moon_platform)
	# for i in range(len(object_text)):
	# 	o_char = object_text[i]
	# 	n_char = moon_platform[i]
	# 	print("{} -- {}".format(o_char, n_char))
	# 	print(o_char == n_char)

	# Test Ground station platform builder
	object = get_platforms("./tests/orb/platform_ground.orb")[0]

	# object_text = add_object(object)
	# print(len(object_text))
	# print(object_text)
	# ground_platform = read_file("./tests/orb/platform_ground.orb")
	# print(len(ground_platform))
	# print(ground_platform)
	# for i in range(len(object_text)):
	# 	o_char = object_text[i]
	# 	n_char = ground_platform[i]
	# 	print("{} -- {}".format(o_char, n_char))
	# 	print(o_char == n_char)

	assert(add_object(object) == read_file("./tests/orb/platform_ground.orb"))

def add_tx(object_name):
	text = read_file("./templates/tx.orb")
	text = text.format(object_name = object_name)
	return text
# print(add_tx("sl-1234"));


def add_rx(a_name, b_name):
	text = read_file("./templates/rx.orb")
	text = text.format(a = a_name, b = b_name)
	return text
# print(add_rx("SL-1234", "SL-5678"));


def add_analysis_distance(a_name, b_name):
	# return add_analysis("Distance", a_name, b_name, "RANGE_MAGNITUDE", 0, 63781.37)
	text = read_file("./templates/analysis.orb")
	text = text.format(
		label = "Distance",
		a = a_name,
		b = b_name,
		variable = "RANGE_MAGNITUDE",
		lower = 0,
		upper = 63781.37
		)
	return text
# print(add_analysis_distance("SL-1234", "SL-5678"))

def add_analysis_rx_power(a_name, b_name):
	# return add_analysis("Rx Power", a_name, b_name, "RX_TPOWER", -998, 30)
	text = read_file("./templates/analysis_power.orb")
	text = text.format(
		label = "", #"Rx Power",
		a = a_name,
		b = b_name,
		variable = "RX_TPOWER",
		lower = -998,
		upper = 30
		)
	return text
# print(add_analysis_rx_power("SL-1234", "SL-5678"))

def add_analysis_coordinate(reference, origin, target, axis):

	text = read_file("./templates/analysis_coordinate.orb")
	text = text.format(
		target = target,
		axis = axis,
		reference = reference,
		origin = origin,
		lower = 0,
		upper = 63781.37
	)
	return text

# print(add_analysis_coordinate(".Moon Cartesian", "Moon", "IOAG:Equatorial", "X"))

def add_distances_graph(source, targets_text):
	text = read_file("./templates/distances_graph.orb")
	text = text.format(
		source = source,
		variables = targets_text
		)
	return text

def add_contact_analysis(pairs_text, step_size, name, duration):
	text = read_file("./templates/contact_analysis.orb")
	text = text.format(
		variables = pairs_text,
		step_size = step_size,
		name = name,
		duration = duration
		)
	return text

def add_visibility_sensors(satellites_text):
	text = read_file("./templates/visibility.orb")
	text = text.format(
		variables = satellites_text
	)
	return text

def add_coordinate_view(targets_text, step_size, name, duration):
	"""
	Returns the entry text for a view of (x, y, z) coordinates for a given 
		list of objects.

		`duration` is length of the simulation in seconds.
	"""
	text = read_file("./templates/coordinates_view.orb")
	text = text.format(
		variables = targets_text,
		step_size = step_size,
		name = name,
		duration = duration
	)
	return text

# TODO : maybe rename these to `report`

def add_distances_view(targets_text, step_size, name, duration):
	"""
	Returns the entry text for a view of distances between 
		a list of objects.

		`duration` is length of the simulation in seconds.
	"""
	text = read_file("./templates/distances_view.orb")
	text = text.format(
		variables = targets_text,
		step_size = step_size,
		name = name,
		duration = duration
	)
	return text

TODAY = date.today()

def generate_orb(satellites, name, date=TODAY):
	text = ""

	step_size = 3600 # every hour for now
	duration = 86400 # duration of the simulation in seconds.

	generate_coordinates = False

	# get base
	# TODO : add date.
	text += add_base(date) + "\n\n"

	# add satellites
	for sat in satellites:
		# build satellite object
		text += add_object(sat) + "\n"

	# add visibility
	# variables_text = "\n".join([f"\"{sat['object_name']}\"" for sat in satellites])
	# text += add_visibility_sensors(variables_text)
	text += read_file("./templates/visibility_inv.orb")

	# add transmitters
	for sat in satellites:
		text += add_tx(sat["object_name"]) + "\n"

	# add receivers
	for pair in combinations(satellites, 2):
		a_name = pair[0]["object_name"]
		b_name = pair[1]["object_name"]
		text += add_rx(a_name, b_name) + "\n"

	# coordinates only needed for latex related code 
	if generate_coordinates:

		# add coordinates
		axes = ["X", "Y", "Z"]

		for sat in satellites:
			origin = "Earth"
			object_name = sat["object_name"]
			# if "body" in sat:
			# 	origin = sat["body"]

			for axis in axes:
				text += add_analysis_coordinate(
					"." + origin + " Cartesian", 
					origin, 
					object_name, 
					axis
				) + "\n"
		
		# add moon coordinates 
		for axis in axes:
			text += add_analysis_coordinate(
				".Earth Cartesian", 
				"Earth", 
				"Moon", 
				axis
			) + "\n"

	
		# add coordinates view 
		targets_text = "\n"
		for sat in satellites:
			target_name = sat["object_name"]
			for axis in axes:
				targets_text += "\t \"" + target_name + " " + axis + "-Coordinate\"\n"

		# add coordinates view for moon
		for axis in axes:
			targets_text += "\t \"Moon " + axis + "-Coordinate\"\n"

		text += add_coordinate_view(targets_text, step_size, name, duration)


	# add analysis
	for pair in combinations(satellites, 2):
		a_name = pair[0]["object_name"]
		b_name = pair[1]["object_name"]
		text += add_analysis_rx_power(a_name, b_name) +  "\n"
		text += add_analysis_distance(a_name, b_name) + "\n"

	# test graphing
	source_name = satellites[0]["object_name"]
	targets = "\n"
	for sat in satellites:
		target_name = sat["object_name"]
		if target_name != source_name:
			targets += "\t \"Distance " + source_name + " - " + target_name + "\"\n"
	text += add_distances_graph(source_name, targets)

	# add distances report
	targets_text = "\n"
	for pair in combinations(satellites, 2):
		a_name = pair[0]["object_name"]
		b_name = pair[1]["object_name"]
		targets_text += "\t \"Distance " + a_name + " - " + b_name + "\"\n"

	text += add_distances_view(targets_text, step_size, name, duration)

	# add contact analysis
	pairs_text = "\n"
	for pair in combinations(satellites, 2):
		a_name = pair[0]["object_name"]
		b_name = pair[1]["object_name"]
		pairs_text += "\t \"" + a_name + " - " + b_name + "\"\n"

	text += add_contact_analysis(pairs_text, step_size, name, duration)
	
	return text

# TODO : rename to `build_satellites_from_csv`
def build_satellites_csv(source):
	csv_data = get_csv_data("./sources/" + source + ".csv")

	satellites = []
	for i in range(len(csv_data)):
		object_raw = csv_data.loc[i].to_dict();
		object = {}
		object = create_object_dictionary(
			object_raw["OBJECT_NAME"],
			object_raw["NORAD_CAT_ID"],
			tu.epoch_year(object_raw["EPOCH"]),
			tu.epoch_fraction(object_raw["EPOCH"]),
			object_raw["MEAN_MOTION_DOT"],
			object_raw["MEAN_MOTION_DDOT"],
			object_raw["BSTAR"],
			object_raw["EPHEMERIS_TYPE"],
			object_raw["ELEMENT_SET_NO"],
			object_raw["INCLINATION"],
			object_raw["RA_OF_ASC_NODE"],
			object_raw["ECCENTRICITY"],
			object_raw["ARG_OF_PERICENTER"],
			object_raw["MEAN_ANOMALY"],
			object_raw["MEAN_MOTION"],
			object_raw["REV_AT_EPOCH"]
		)
		satellites.append(object)

	return satellites
# print(build_satellites_csv("norad"))


# See : https://pypi.org/project/sgp4/
def build_satellite_tle(tle):
	"""
	This method takes in a single TLE and creates a satellite dictionary.
	"""
	lines = tle.split("\n")
	lines = [i for i in lines if i]
	assert(len(lines) == 3)
	# print(find())
	satellite = Satrec.twoline2rv(lines[1], lines[2])
	name = lines[0].rstrip()
	object_raw = exporter.export_omm(satellite, name)

	object = create_object_dictionary(
		object_raw["OBJECT_NAME"],
		object_raw["NORAD_CAT_ID"],
		tu.epoch_year(object_raw["EPOCH"]),
		tu.epoch_fraction(object_raw["EPOCH"]),
		object_raw["MEAN_MOTION_DOT"],
		object_raw["MEAN_MOTION_DDOT"],
		object_raw["BSTAR"],
		object_raw["EPHEMERIS_TYPE"],
		object_raw["ELEMENT_SET_NO"],
		object_raw["INCLINATION"],
		object_raw["RA_OF_ASC_NODE"],
		object_raw["ECCENTRICITY"],
		object_raw["ARG_OF_PERICENTER"],
		object_raw["MEAN_ANOMALY"],
		object_raw["MEAN_MOTION"],
		object_raw["REV_AT_EPOCH"]
	)

	# object = create_object_dictionary(
	# 	lines[0], # object_raw["OBJECT_NAME"],
	# 	satellite.satnum, # object_raw["NORAD_CAT_ID"],
	# 	satellite.epochyr, # tu.epoch_year(object_raw["EPOCH"]),
	# 	satellite.epochdays, # tu.epoch_fraction(object_raw["EPOCH"]),
	# 	satellite.ndot, # object_raw["MEAN_MOTION_DOT"],
	# 	satellite.nddot, # object_raw["MEAN_MOTION_DDOT"],
	# 	satellite.bstar, # object_raw["BSTAR"],
	# 	satellite.ephtype, # object_raw["EPHEMERIS_TYPE"],
	# 	satellite.elnum, # object_raw["ELEMENT_SET_NO"],
	# 	satellite.inclo, # object_raw["INCLINATION"],
	# 	satellite.nodeo, # object_raw["RA_OF_ASC_NODE"],
	# 	satellite.ecco, # object_raw["ECCENTRICITY"],
	# 	satellite.argpo, # object_raw["ARG_OF_PERICENTER"],
	# 	satellite.mo, # object_raw["MEAN_ANOMALY"],
	# 	satellite.no_kozai, # object_raw["MEAN_MOTION"],
	# 	satellite.revnum # object_raw["REV_AT_EPOCH"]
	# )

	return object

if __name__ == "__main__":

	tle = """
TDRS 3
1 19548U 88091B   22144.45796491 -.00000313  00000+0  00000+0 0  9997
2 19548  13.7334 351.5139 0036255 336.8078  29.6172  1.00266005110484
"""
	object = build_satellite_tle(tle)
	# print(object)

def build_satellites_from_tle(filepath):
	"""
	Takes in the filepath of a .tle file containing tle entries and returns
	a list of satellite objects as dictionaries.
	"""
	content = read_file(filepath)

	lines = content.split("\n")
	lines = [i for i in lines if i]

	assert(len(lines) % 3 == 0)

	satellites = []
	for i in range(int(len(lines) / 3)):
		j = 3 * i
		name = lines[j]
		line_one = lines[j + 1]
		line_two = lines[j + 2]
		tle = "\n".join([name, line_one, line_two])
		object = build_satellite_tle(tle)
		satellites.append(object)
		# satellite = Satrec.twoline2rv(line_one, line_two)
	# print(len(lines))

	return satellites

if __name__ == "__main__":

	tles = build_satellites_from_tle("./sources/tdrss.tle")
	assert(len(tles) == 31)
	# print(len(tles))


def sample_sats(sat_array, k):
	random.shuffle(sat_array)
	return sat_array[:k]
# print sample_sats([1, 2, 3, 4, 5], 2)

# satellites = build_satellites_csv("norad")
# save_to_file(generate_orb(satellites), "norad")

# working code
# satellites = build_satellites_csv("starlink")
# satellites = sample_sats(satellites, 15)
# save_to_file(generate_orb(satellites), "starlink")

# exit()

def get_tdrs_platforms():
    satellites = build_satellites_csv("norad")
    tdrs = []
    for satellite in satellites:
        if satellite["object_name"].startswith("TDRS"):
            tdrs.append(satellite);
            # print(satellite)
    # print(len(tdrs))
    return tdrs

if __name__ == "__main__":

	assert(len(get_tdrs_platforms()) == 10)

def get_moon_platforms():
    platforms = get_platforms("./tests/orb/platforms_moon.orb")
    return platforms

def get_mars_platforms():
	platforms = get_platforms("./tests/orb/platforms_mars.orb")
	return platforms

# print(get_mars_platforms())
