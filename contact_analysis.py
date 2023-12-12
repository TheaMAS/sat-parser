import networkx as nx

# Portion used to work with interval arithmetic of subsets of Real numbers
import portion as P
from itertools import combinations

from datetime import datetime # for getting time period of contact output

import warnings

if __name__ == "__main__":
	DEBUG = True;
else:
	DEBUG = False

def contact_analysis_parser_v14(content):
	"""
	This function takes in the content of a contact analysis csv output
	from soap version 14 and returns a list of contacts, each of which
	is a dictionary : `connection`, `source`, `destination`, and `list` of
	contact times.
	"""
	warnings.warn(
		"Warning: contact_analysis.contact_analysis_parser_v14 deprecated. " + \
			"Use function in reports_parser instead.", DeprecationWarning)
			
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
	warnings.warn(
		"Warning: contact_analysis.contact_analysis_parser_v15 deprecated. " + \
			"Use function in reports_parser instead.", DeprecationWarning)

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
	warnings.warn(
		"Warning: contact_analysis.contact_analysis_parser deprecated. " + \
			"Use function in reports_parser instead.", DeprecationWarning)

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

	# contact_plan = []
	#
	# content = ""
	# with open(filename) as f:
	#     content = f.read().split("Analysis,")
	#
	# # each block corresponds to the connection times between a pair of sats
	# for block in content[1:]:
	#     block_lines = block.split("\n")
	#
	#     contacts = []
	#
	#     connection = block_lines[0].split(",")[0]
	#     source, destination = connection.split(" - ")
	#
	#     for line in block_lines[2:-2]:
	#         entries = line.split(",")
	#
	#         rise = float(entries[0])
	#         set = float(entries[1])
	#         duration = float(entries[2])
	#
	#         contacts.append({"rise" : rise, "set" : set, "duration" : duration})
	#
	#     contact = {
	#         "connection" : connection,
	#         "source" : source,
	#         "destination" : destination,
	#         "list" : contacts
	#     }
	#
	#     contact_plan.append(contact)
	#
	# return contact_plan

if __name__ == "__main__":

	# filename = "contact_simple.csv"
	filename = "./outputs/starlink-7/starlink_6 Contact Analysis.csv"
	filename= "./tests/csv/moongnd_base Contact Analysis.csv"
	# filename = "./outputs/starlink-7/starlink_0 Contact Analysis.csv"
	#
	contact_plan = contact_analysis_parser(filename)
	# print(contact_plan)

def parse_contact_analysis_time(filepath):
	"""

		"Start: 2022/04/30 01:43:00.00, Stop: 2022/05/01 01:43:00.00,"
	"""
	warnings.warn(
		"Warning: contact_analysis.parse_contact_analysis_time deprecated. " + \
			"Use function in reports_parser instead.", DeprecationWarning)

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

def construct_graph(contact_plan):
	"""
	This function takes the contact plan output from `contact_analysis_parser`
	and creates a "graph" dictionary consisting of a dictionary of nodes
	with key `nodes` and a dictionary of edges with key `edges`.

	Each node has key the name of the source, and value a generated id.
	Each edge has key the name of the source and the name of the target,
		and value the list of rise and set times.
	"""
	warnings.warn(
		"Warning: contact_analysis.construct_graph deprecated. " + \
			"Use function in reports_parser instead.", DeprecationWarning)

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
	warnings.warn(
		"Warning: contact_analysis.get_satellite_names deprecated. " + \
			"Use function in reports_parser instead.", DeprecationWarning)

	satellite_names = list(graph["nodes"].keys())

	return satellite_names


# TODO : move this to the appropriate slice analysis module
def construct_nx_graph(contact_plan):
	G = nx.Graph()
	node_counter = 0;
	for contact in contact_plan:
		G.add_edge(contact['source'], contact['destination'])
		G[contact['source']][contact['destination']]['list'] = contact['list']
	return G

if __name__ == "__main__":

	graph = construct_graph(contact_plan)
	# print(graph)

def extract_critical_times(graph):
	"""
	This function takes a "graph" object as given by `construct_graph`
	and extracts a list of "critical times," that is, times when the
	underlying graph changes in the temporal graph. The list is sorted
	from smallest to largest.
	"""
	warnings.warn(
		"Warning: contact_analysis.extract_critical_times deprecated. " + \
			"Use function in reports_parser instead.", DeprecationWarning)

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
	warnings.warn(
		"Warning: contact_analysis.sample_critical_times deprecated. " + \
			"Use function in reports_parser instead.", DeprecationWarning)

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
	warnings.warn(
		"Warning: contact_analysis.get_graph_length deprecated. " + \
			"Use function in reports_parser instead.", DeprecationWarning)

	critical_times = extract_critical_times(graph)

	length = critical_times[-1] - critical_times[0]

	return length

# if __name__ == "__main__":

	# critical_times = extract_critical_times(graph)
	# print(critical_times)

def construct_weighted_simplex(graph):
	"""
	This function takes a "graph" object as given by `construct_graph`
	and returns a weighted simplex as needed by dionysus for zig-zag
	persistence computations.

	The output is a dictionary with two keys `simplex` and `times`.
	"""
	warnings.warn(
		"Warning: contact_analysis.construct_weighted_simplex deprecated. " + \
			"Use function in reports_parser instead.", DeprecationWarning)

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

# TODO : fully deprecate since not using anymore, or move to slice_analysis_nx
def construct_clique_complex(graph):
	# 1. extract the underlying summary graph of the temporal graph as nx 
	#       object. 
	# 2. call `enumerate_all_cliques`
	g = nx.Graph()

	# add all nodes; independent of time
	nodes = {}
	for node_key, node_number in graph["nodes"].items():
		g.add_node(node_number, label=node_key)
		nodes[node_key] = node_number;

	# edges = {}
	for edge_key, edge_times in graph["edges"].items():

		# add edge
		edge_source, edge_destination = edge_key.split(" - ")
		g.add_edge(nodes[edge_source], nodes[edge_destination])

		interval = P.empty()

		for i in range(0, len(edge_times), 2):
			rise_time = edge_times[i]
			set_time = edge_times[i + 1]

			interval = interval | P.closed(rise_time, set_time)

		g.edges[nodes[edge_source], nodes[edge_destination]]["times"] = interval
		
		# print("{} - {}".format(nodes[edge_source], nodes[edge_destination]))
		# print(" --- {}".format(interval))

	simplex = []
	times = []

	cliques = list(nx.enumerate_all_cliques(g))
	for clique in cliques:
		# print(clique)

		interval = P.closed(-P.inf, P.inf) 
		for pair in combinations(clique, 2):
			# print(" --- {}".format(pair))
			# print(" ------ {}".format(g.edges[pair[0], pair[1]]["times"]))
			interval = interval & g.edges[pair[0], pair[1]]["times"]

		simplex_times = []
		for time in P.to_data(interval):
			# print(time)
			rise_time = time[1] 
			set_time = time[2]

			# check if emptyset
			if rise_time == float("inf") and set_time == float("-inf"):
				continue

			# check if starts at -infty
			if rise_time == float("-inf"):
				rise_time = 0
			simplex_times.append(rise_time)

			# check if ends at infty
			if set_time == float("inf"):
				continue
			simplex_times.append(set_time)

			# print("(rise = {}, set = {})".format(rise_time, set_time))
		# print(list(interval))
		
		if simplex_times != []:
			simplex.append(clique)
			times.append(simplex_times)

	return {"simplex" : simplex, "times" : times}


if __name__ == "__main__":
	
	clique_complex = construct_clique_complex(graph)
	# print(clique_complex)

def create_json_contact(index, source, dest, start, end, rate, owlt):

	contact = {
		"contact" : index,
		"source" : source,
		"dest" : dest,
		"startTime" : start,
		"endTime" : end,
		"rateBitsPerSec" : rate,
		"owlt" : owlt
	}

	contact_list = [f'\t\t\t"{key}": {value}' for key, value in contact.items()]
	content = ",\n".join(contact_list)

	return "\t\t{\n" + content + "\n\t\t}"

if __name__ == "__main__":
	entry = create_json_contact(0, 102, 10, 0, 2000, 1000000000, 1)

def tvg_to_json(graph):

	nodes = graph["nodes"]
	edges = graph["edges"]

	contact_counter = 0
	
	entries = []
	for edge_key, edge_times in edges.items():
		edge_source, edge_destination = edge_key.split(" - ")

		for i in range(0, len(edge_times), 2):
			rise_time = edge_times[i]
			set_time = edge_times[i + 1]

			entry = create_json_contact(
				contact_counter, 
				nodes[edge_source], 
				nodes[edge_destination], 
				rise_time, 
				set_time, 
				1000000000, 
				1
			)
			entries.append(entry)

			entry = create_json_contact(
				contact_counter + 1, 
				nodes[edge_destination],
				nodes[edge_source],  
				rise_time, 
				set_time, 
				1000000000, 
				1
			)
			entries.append(entry)

			contact_counter += 2
	content = ",\n".join(entries)
	return '\t"contacts": [\n' + content + '\n\t]\n}\n'


if __name__ == "__main__":
	
	content = tvg_to_json(graph)
	print(content)