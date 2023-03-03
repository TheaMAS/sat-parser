import numpy as np
from orb_parser import *

def coordinates_view_parser(filename):
	"""

	coordinates[time_slice][target] = [x, y, z]
	"""

	content = ""
	with open(filename) as f:
		content = f.read()

	
	indices = None
	lines = content.split("\n")
	for line in lines:
		if line.startswith("TIME_UNITS"):
			indices = line.split(",")
	# print(indices)

	indices_names = [None]
	indices_axes = [None]
	for coordinate in indices[1:-1]:
		name = coordinate.split("-Coordinate")[0]
		if name.endswith("X"):
			indices_names.append(name.split("X")[0].strip())
			indices_axes.append("X")
		elif name.endswith("Y"):
			indices_names.append(name.split("Y")[0].strip())
			indices_axes.append("Y")
		elif name.endswith("Z"):
			indices_names.append(name.split("Z")[0].strip())
			indices_axes.append("Z")
	# print(indices_names)

	coordinates = {}

	table = content.split("km,\n")
	lines = table[-1].split("\n")
	for line in lines:

		time_step = None
		entries = line.split(",")[:-1]
		for i, entry in enumerate(entries):
			# print("{} : {}".format(i, entry))
			entry_float = float(entry.strip())
			if i == 0:
				time_step = entry_float
				coordinates[time_step] = {}
			else:
				if indices_axes[i] == "X":
					coordinates[time_step][indices_names[i]] = [entry_float]
				else:
					coordinates[time_step][indices_names[i]].append(entry_float)
				# print("\t{}".format(indices[i]))

	# print(coordinates)
	return coordinates


def get_origin_body(platforms, target_name):
	"""
	Given a list of platforms from the orb file and a target satellite name,
		return the origin body.
	"""
	origin = "Earth"
	for platform in platforms:
		if platform["object_name"] == target_name and "body" in platform:
			origin = platform["body"]
	return origin

if __name__ == "__main__":
	EARTH_RADIUS = 6367 # KM
	MOON_RADIUS = 1737 # KM
	platforms = get_platforms("./tests/orb/moongnd_base.orb")

	filename = "./tests/csv/moongnd_base Coordinates.csv"
	coordinates = coordinates_view_parser(filename)

	# for time_slice, satellite in coordinates.items():
	# 	print(satellite)
	# exit()

	for time_slice, value in coordinates.items():
		# print("{} : \n\t{}".format(time_slice, value))
		coords = value["Moon"]
		coords = np.asarray(coords) 
		# print(np.sqrt(np.sum(coords**2)))
	# exit()

	# print(len(coordinates[0.0]))
	for satellite, coords in coordinates[0.0].items():
		# print(satellite)
		body = get_origin_body(platforms, satellite)
		# print("\t{}".format(body))
		r = EARTH_RADIUS
		if body == "Moon":
			r = MOON_RADIUS
		# print(np.sqrt(np.sum(np.asarray(coords)**2)))
		xyz = np.asarray(coords) / r
		# print(xyz)