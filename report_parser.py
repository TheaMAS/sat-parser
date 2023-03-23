from orb_parser import *

import numpy as np

import portion as P
from itertools import combinations
from datetime import datetime # for getting time period of contact output

import logging

logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)


def contact_analysis_parser_v14(content):
	"""
	This function takes in the content of a contact analysis csv output
	from soap version 14 and returns a list of contacts, each of which
	is a dictionary : `connection`, `source`, `destination`, and `list` of
	contact times.
	"""
	logging.info("Running `contact_analysis_parser_v14`")

	content = content.split("Analysis,")
	contact_plan = []

	# each block corresponds to the connection times between a pair of sats
	for block in content[1:]:
		block_lines = block.split("\n")

		contacts = []

		connection = block_lines[0].split(",")[0]
		source, destination = connection.split(" - ")

		for line in block_lines[2:-2]:
			entries = line.split(",")

			rise = float(entries[0])
			set = float(entries[1])
			duration = float(entries[2])

			contacts.append({"rise" : rise, "set" : set, "duration" : duration})

		contact = {
			"connection" : connection,
			"source" : source,
			"destination" : destination,
			"list" : contacts
		}

		contact_plan.append(contact)
	# print(contact_plan)
	return contact_plan

def contact_analysis_parser_v15(content):
	"""
	This function takes in the content of a contact analysis csv output
	from soap version 15 and returns a list of contacts, each of which
	is a dictionary : `connection`, `source`, `destination`, and `list` of
	contact times.
	"""
	logging.info("Running `contact_analysis_parser_v15`")

	content = content.split("Analysis,")[1]
	lines = content.split("\n")

	current_connection = ""
	blocks = {}

	# first pass; prepare blocks
	for line in lines[2:-1]:
		entries = line.split(",")
		connection = entries[0]

		if current_connection != connection:
			current_connection = connection
			blocks[current_connection] = []

		rise = float(entries[1])
		set = float(entries[2])
		duration = float(entries[3])

		blocks[current_connection].append({"rise" : rise, "set" : set, "duration" : duration})

	# print(blocks)

	contact_plan = []

	for key, value in blocks.items():
		# print(key)
		# print(value)
		source, destination = key.split(" - ")
		contact = {
			"connection" : key,
			"source" : source,
			"destination" : destination,
			"list" : value
		}
		contact_plan.append(contact)
	# print(content)

	# print(contact_plan)

	return contact_plan

def contact_analysis_parser(filename):
	"""
	Main function used to parse a contact analysis csv output from soap.
	It takes in a csv from soap v14 or v15 and parses it appropriately.
	"""
	logging.info(f"Running `contact_analysis_parser` on `{filename}`")

	content = ""
	with open(filename) as f:
		content = f.read()

	# check which version it is
	contact_plan = []
	if content[0] == "\n":
		# if DEBUG : print("Version 14")
		contact_plan = contact_analysis_parser_v14(content)
	else:
		contact_plan = contact_analysis_parser_v15(content)
		# if DEBUG : print("Version 15")
	#
	return contact_plan

if __name__ == "__main__":
	filename = "./tests/csv/moongnd_base Contact Analysis.csv"
	
	contact_plan = contact_analysis_parser(filename)
	# print(f"len(contact_plan) = {len(contact_plan)}")

def parse_contact_analysis_time(filepath):
	"""
		Parses the start and stop times of a given contact analysis report,
			returned as a tuple `(start, stop)`

		"Start: 2022/04/30 01:43:00.00, Stop: 2022/05/01 01:43:00.00,"
	"""
	logging.info(f"Running `parse_contact_analysis_time` on `{filename}`")

	content = ""
	with open(filename) as f:
		content = f.read()
	
	lines = content.split("\n")

	start, stop = None, None

	for line in lines:
		if line.startswith("Start:"):
			start, stop = line.split(",")[0:2]

			start = start.split("Start:")[-1].strip().split(".")[0]
			stop = stop.split("Stop:")[-1].strip().split(".")[0]

			# print(start)

			start = datetime.strptime(start, "%Y/%m/%d %H:%M:%S")
			# print(start)

			stop = datetime.strptime(stop, "%Y/%m/%d %H:%M:%S")
			# print(stop)
	return start, stop

if __name__ == "__main__":

	start, stop = parse_contact_analysis_time(filename)
	# print(start)
	# print(stop)

# `construct_graph` is internal function to this module.
#	Not to be confused with user accessible graph objects.
def construct_graph(contact_plan):
	"""
	This function takes the contact plan output from `contact_analysis_parser`
	and creates a "graph" dictionary consisting of a dictionary of nodes
	with key `nodes` and a dictionary of edges with key `edges`.

	Each node has key the name of the source, and value a generated id.
	Each edge has key the name of the source and the name of the target,
		and value the list of rise and set times.
	"""
	logging.info("Running `construct_graph`")

	nodes = {};
	edges = {}

	node_counter = 0;
	# current_edge = None;

	for contact in contact_plan:

		connection = contact["connection"]
		source = contact["source"]
		destination = contact["destination"]

		set_prev = -1
		for entry in contact["list"]:

			rise = entry["rise"]
			set = entry["set"]

			if source not in nodes:
				nodes[source] = node_counter;
				node_counter += 1;
			if destination not in nodes:
				nodes[destination] = node_counter;
				node_counter += 1;

			if connection not in edges:
				edges[connection] = []

			if set_prev == rise or (rise - set_prev < 1):
				# This shouldn't happen : soap bug
				edges[connection].pop()
				# print("internal : ERROR")
			else:
				edges[connection].append(rise)
			edges[connection].append(set)
			
			set_prev = set
			# print("we have a connection", source, destination, "born at", rise, "dies at", set)

	# print(nodes)
		# print(contact["connection"])
	return {"nodes" : nodes, "edges" : edges}

def get_satellite_names(graph):
	"""
	Given a `graph` as in `construct_graph`, we get the names of the satellites
		in the simulation.
	"""
	logging.info("Running `distances_report_parser`")

	satellite_names = list(graph["nodes"].keys())

	return satellite_names

if __name__ == "__main__":

	graph = construct_graph(contact_plan)

def extract_critical_times(graph):
	"""
	This function takes a "graph" object as given by `construct_graph`
	and extracts a list of "critical times," that is, times when the
	underlying graph changes in the temporal graph. The list is sorted
	from smallest to largest.
	"""
	logging.info("Running `extract_critical_times`")

	times = []

	edges = graph["edges"]

	for edge_key, edge_times in edges.items():
		# edge_source, edge_destination = edge_key.split(" - ")
		for time in edge_times:
			times.append(time)

	# remove duplicates
	times = list( dict.fromkeys(times) )

	# print(len(times))

	# sort
	times.sort()

	return times

def sample_critical_times(critical_times):
	"""
	Given a set of critical times of a temporal graph, this returns a list
	of time strictly between the critical times.
	"""
	logging.info("Running `sample_critical_times`")

	# samples[i] = midpoint between c_times[i+ 1] and c_times[i]
	critical_samples = []

	for i in range(len(critical_times) - 1):
		difference = (critical_times[i + 1] - critical_times[i] )
		middle = critical_times[i] + (difference / 2)

		critical_samples.append(middle)

	return critical_samples

def get_graph_length(graph):
	"""
	This function takes a "graph" object as given by `construct_graph` and
	returns the length of the temporal graph, defined to be the largest
	critical time minus the smallest critical time.
	"""
	logging.info("Running `get_graph_length`")

	critical_times = extract_critical_times(graph)

	length = critical_times[-1] - critical_times[0]

	return length

def construct_weighted_simplex(graph):
	"""
	This function takes a "graph" object as given by `construct_graph`
	and returns a weighted simplex as needed by dionysus for zig-zag
	persistence computations.

	The output is a dictionary with two keys `simplex` and `times`.
	"""
	logging.info("Running `construct_weighted_simplex`")

	nodes = graph["nodes"]
	edges = graph["edges"]

	simplex = []
	times = []

	for node_key, node_number in nodes.items():
	  simplex.append([node_number])
	  times.append([0]) # all nodes born at time zero

	for edge_key, edge_times in edges.items():
		edge_source, edge_destination = edge_key.split(" - ")

		# if edge_times == []:
		#     continue;

		# Makes the appropriate simplex for the given data.
		simplex.append([nodes[edge_source], nodes[edge_destination]])
		# print(simplex)
		times.append(edge_times)
	return {"simplex" : simplex, "times" : times}

if __name__ == "__main__":

	weighted_simplex = construct_weighted_simplex(graph)
	# print(weighted_simplex)

def distances_report_parser(filename):
	"""
	Returns a dictionary whose keys are time slices and whose 
		values are dictionaries whose keys are `satA-satB` and with 
		value the distance between satA and satB in km.

	distances[time_slice]["satA-satB"] = distance (in km)
	"""
	logging.info(f"Running `distances_report_parser` on `{filename}`")

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
	for title in indices[1:-1]:
		name = title.split("Distance ")[1]
		a_name, b_name = name.split(" - ")
		# print("{} : {}".format(a_name, b_name))
		logger.debug(f"{a_name} : {b_name}")
		indices_names.append(name)
	# logger.debug(f"{indices_names}")
	# print(indices_names)

	distances = {}

	table = content.split("km,\n")
	lines = table[-1].split("\n")
	for line in lines:

		time_step = None
		entries = line.split(",")[:-1]
		for i, entry in enumerate(entries):
			# logger.debug(f"{i} : {entry.strip()} : {indices_names[i]}")
			# print("{} : {} : {}".format(i, entry.strip(), indices_names[i]))

			entry_float = float(entry.strip())
			if i == 0:
				time_step = entry_float
				distances[time_step] = {}
			else:
				distances[time_step][indices_names[i]] = entry_float

	return distances

if __name__ == "__main__":

	# filename = "./outputs/moongnd-5/moongnd_0 Distances.csv"
	filename = "./tests/csv/starlink_10 Distances.csv"
	distances = distances_report_parser(filename)

	timesteps = []
	for key, value in distances.items():
		timesteps.append(key)

	# print(timesteps)


def coordinates_report_parser(filename):
	"""
	Returns a dictionary `coordinates` whose keys consist of time slices
		and whose objects constist of dictionaries of 
		satellite name : [x, y, z] coordinates.

	coordinates[time_slice][target] = [x, y, z]
	"""

	logging.info(f'Running `coordinates_report_parser` on `{filename}`')

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

	logging.info(f'Running `get_origin_body` for `{target_name}`')

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
	coordinates = coordinates_report_parser(filename)

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