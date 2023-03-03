from contact_analysis import *
from os_utilities import *
from tle_utilities import *
from orb_parser import *
from os_utilities import *
from coordinates_parser import *

from sgp4.api import Satrec
from sgp4.conveniences import sat_epoch_datetime

import numpy as np

EARTH_RADIUS = 6367 # KM
MOON_RADIUS = 1737 # KM

# using the sat names, get associated tles from .tle files
def extract_satellite_names(graph):

	satellite_names = get_satellite_names(graph)
	return satellite_names

def get_tle(name):
	"""
	Given a satellite name, searches source file tle's and extracts 
	appropriate entry.
	"""

	tle_files = get_ext_files("./sources/", "tle")
	for tle_file in tle_files:
		# print(tle_file)
		file_tles = get_tles_dict(tle_file)
		if name in file_tles:
			return file_tles[name]
	return None

def get_moon_position_tex(jd, fr):
	# https://mail-01.amsat.org/archives/amsat-bb/200307/msg00637.html 
	# using pseudo tle for the moon
	moon = get_tle("MOON")
	e, r, v = moon.sgp4(jd, fr)
	moon_position_normalized = np.asarray(r) / EARTH_RADIUS
	text = "\coordinate (M) at ({}, {}, {});\n".format(
		moon_position_normalized[0],
		moon_position_normalized[1],
		moon_position_normalized[2]
	)
	return text

def get_rotation_matrix(theta, phi):
	"""
	Returns 3d rotation matrix `np.array` associated to 
		`theta` (rotation about x-axis),
		`phi` (rotation about z-axis)
	in degrees, as specified in tikz-3dplot manual.
	"""
	theta = np.deg2rad(theta)
	phi = np.deg2rad(phi)

	c_theta, s_theta = np.cos(theta), np.sin(theta)
	c_phi, s_phi = np.cos(phi), np.sin(phi)
	rotation = np.array([
		[c_phi, s_phi, 0], 
		[-c_theta * s_phi, c_theta * c_phi, -s_theta], 
		[s_theta * s_phi, -s_theta * c_phi, c_theta]
	])
	return rotation

theta = 70
phi = 110
# normal = np.array([0, 0, 1])
# p = np.array([1, 1, 0])
# # print(vector)
# normal_r = np.matmul(normal, get_rotation_matrix(theta, phi))
# normal_p = np.matmul(get_rotation_matrix(theta, phi), p)
# print(normal_r)

def get_plane_normal_vector(theta, phi):
	normal = np.array([0, 0, 1])
	# p = np.array([1, 1, 0])
	# print(vector)
	normal_r = np.matmul(normal, get_rotation_matrix(theta, phi))
	# normal_p = np.matmul(get_rotation_matrix(theta, phi), p)

	return normal_r

normal_r = get_plane_normal_vector(theta, phi)

def get_plane(n, p):
	"""
	Given a normal vector n and a point p, returns the coefficients of 
	the equation for the plane passing through p with normal vector n.

		ax + by + cz + d = 0
	"""

	a = n[0]
	b = n[1]
	c = n[2]

	d = -(a * p[0] + b * p[1] + c * p[2])

	return a, b, c, d

# n = np.array([2, 3, 4])
# p = np.array([1, 1, 1])
# print(get_plane(n, p))

# a, b, c, d = get_plane(normal_r, normal_p)
# print(normal_r)
# print(p)
# print(a)
# print(b)
# print(c)
# print(d)

def is_behind_plane(n, p):
	"""
	Given a plane ax + by + cz + d = 0 and a point p, return true if the 
	point lies behind the plane.

	p is a np array
	"""

	is_behind = False 
	evaluation = np.dot(n, p)
	# print(evaluation)
	if evaluation < 0:
		is_behind = True
	return is_behind


# is_behind = is_behind_plane(0, 0, 1, 0, np.array([0, 0, -1]))
# is_behind = is_behind_plane(normal_r, p)
# print(is_behind)

def get_coordinates(latitude, longitude, altitude):
	r = EARTH_RADIUS + altitude
	x = r * np.cos(longitude) * np.sin(latitude)
	y = r * np.sin(longitude) * np.sin(latitude)
	z = r * np.cos(latitude)
	return x, y, z

# TODO : problems with templating.
def generate_diagram(theta, phi, positions_tex, points_tex, edges_tex):
	text = read_file("./templates/earth_moon_tikz.tex")

	text = text.replace("{theta}", str(theta))
	text = text.replace("{phi}", str(phi))
	text = text.replace("{positions_tex}", positions_tex)
	text = text.replace("{points_tex}", points_tex)
	text = text.replace("{edges_tex}", edges_tex)
	# text = text.format(
	# 	theta = theta,
	# 	phi = phi
	# )
	return text

# diagram = generate_diagram(theta, phi)
# print(diagram)

# exit()


def get_positions(platforms, satellites_dict):
	"""
	Given a dictionary with keys satelite names and values coordinates.
	"""
	positions = {}
	text = ""

	for satellite_name, coordinates in satellites_dict.items():
		body = get_origin_body(platforms, satellite_name)

		r = EARTH_RADIUS
		if body == "Moon" or satellite_name == "Moon":
			r = 5 * EARTH_RADIUS # scaling for readability
		normalized = np.asarray(coordinates) / r

		positions[satellite_name] = [
			normalized[0], 
			normalized[1], 
			normalized[2]
		]

		text += "\\coordinate ({}) at ({}, {}, {});".format(
			satellite_name, 
			normalized[0], 
			normalized[1], 
			normalized[2]
		) + "\n"

	return text, positions

def get_positions_tex(platforms, satellites_dict):
	return get_positions(platforms, satellites_dict)[0]
	
def get_positions_dict(platforms, satellites_dict):
	return get_positions(platforms, satellites_dict)[1]

def get_points_tex(platforms, satellites_dict, plane_normal):
	text = ""
	
	for satellite_name, coordinates in satellites_dict.items():
		body = get_origin_body(platforms, satellite_name)

		r = EARTH_RADIUS
		# if body == "Moon":
		# 	r = MOON_RADIUS
		p = np.asarray(coordinates) / r

		# todo : change color if it lies behind hyperplane
		color = "black"
		if is_behind_plane(plane_normal, p):
			color = "gray"

		text += "\\fill[color={}] ({}) circle (0.5pt);".format(
			color, 
			satellite_name
		) + "\n"

	return text

def is_slice_alive(slice_time, rise_set_list):
	alive = False 

	# check if time lives in edge_times between rise and set
	time_count = len(rise_set_list)
	# assuming soap output always has a set time, even if end of run.
	for i in range(0, time_count, 2):
		rise_time = rise_set_list[i]
		set_time = rise_set_list[i + 1]
		if rise_time <= slice_time and slice_time <= set_time:
			alive = True 
			break
	return alive

def get_edges_tex(positions, graph, plane_normal, slice_time):
	text = ""

	for edge in graph["edges"].keys():
		source, target = edge.strip().split(" - ")[0:2]

		color = "black"
		if is_behind_plane(plane_normal, positions[source]) or is_behind_plane(plane_normal, positions[target]):
			color = "gray"

		rise_set_list = graph["edges"][edge]
		if is_slice_alive(slice_time, rise_set_list):
			text += "\\draw[thick, color={}] ({}) -- ({});".format(
				color,
				source,
				target
			) + "\n"

	return text

# def get_earth_scope_text():
# 	text = ""
# 	return text

# def get_moon_scope_tex():
# 	text = ""
# 	return text
	

simulation_folder = "sim-2022-08-26"
simulation_name = "moongnd_base"
theta = 45
phi = 45

orb_filepath = "./outputs/{}/{}.orb".format(
	simulation_folder, 
	simulation_name
)
platforms = get_platforms(orb_filepath)

coords_filepath = "./outputs/{}/{} Coordinates.csv".format(
	simulation_folder, 
	simulation_name
) 
coordinates = coordinates_view_parser(coords_filepath)

contact_filepath = "./outputs/{}/{} Contact Analysis.csv".format(
	simulation_folder, 
	simulation_name
) 
contact_plan = contact_analysis_parser(contact_filepath)
graph = construct_graph(contact_plan)
satellite_names = extract_satellite_names(graph)

# single slice test
slice_time = 50400.0
satellites_dict = coordinates[slice_time]
# print(coordinates.keys())

positions_tex = get_positions_tex(platforms, satellites_dict)
# print(positions_tex)

plane_normal = get_plane_normal_vector(theta, phi)
points_tex = get_points_tex(platforms, satellites_dict, plane_normal)
# print(points_tex)

positions_dict = get_positions_dict(platforms, satellites_dict)
edges_tex = get_edges_tex(positions_dict, graph, plane_normal, slice_time)
# print(edges_tex)

diagram = generate_diagram(theta, phi, positions_tex, points_tex, edges_tex)
# print(diagram)

# exit()

output_tex = ""
for slice_time in coordinates.keys():
	satellites_dict = coordinates[slice_time]
	# print(coordinates.keys())

	positions_tex = get_positions_tex(platforms, satellites_dict)

	plane_normal = get_plane_normal_vector(theta, phi)
	points_tex = get_points_tex(platforms, satellites_dict, plane_normal)

	positions_dict = get_positions_dict(platforms, satellites_dict)
	edges_tex = get_edges_tex(positions_dict, graph, plane_normal, slice_time)

	diagram = generate_diagram(theta, phi, positions_tex, points_tex, edges_tex)
	output_tex += diagram + "\n"

latex_filepath = "./outputs/{}/{}.tex".format(
	simulation_folder, 
	simulation_name
) 

f = open(latex_filepath, "w")
f.write(output_tex)
f.close()
exit()
# print(len(coordinates[0.0]))
for satellite_name, coords in coordinates[0.0].items():

	body = get_origin_body(platforms, satellite_name)
	distance = np.sqrt(np.sum(np.asarray(coords)**2))

	r = EARTH_RADIUS
	if body == "Moon":
		r = MOON_RADIUS
	xyz = np.asarray(coords) / r

	text = "{} at {} is {} km away from {}".format(
		satellite_name,
		xyz,
		distance,
		body
	)
	print(text)
	
exit()

# platforms = get_platforms("./outputs/sim-2022-08-26/moongnd_base.orb")

# print("Number of Platforms : {}".format(len(platforms)))
# for platform in platforms:
# 	print(platform)
# exit()

albany = platforms[0]
albany_coord = np.asarray(get_coordinates(albany["latitude"], albany["longitude"], albany["altitude"])) / EARTH_RADIUS
# print(albany_coord)


satellite_name = albany["object_name"]
text = "\\coordinate ({}) at ({}, {}, {});\n".format(
		satellite_name, 
		albany_coord[0], 
		albany_coord[1], 
		albany_coord[2]
	)
text += "\\fill[color={}] ({}) circle (0.5pt);".format("red", satellite_name)
print(text)
# tle = get_tle("STARLINK-2186")
# print(tle)
start, stop = parse_contact_analysis_time(contact_filepath)
jd, fr = get_jday(start)

# tex_moon_position = get_moon_position_tex(jd, fr)
# print(tex_moon_position)
# exit()

positions = {}

for satellite_name in satellite_names:
	print(satellite_name)
	satellite = get_tle(satellite_name)
	e, r, v = satellite.sgp4(jd, fr)

	# normalize
	r = np.asarray(r)
	# normalized_r = r / np.sqrt(np.sum(r**2))

	# earth radius = 6367 km
	normalized_r = r / 6367
	# normalized_r = r / 5367

	x.append(normalized_r[0])
	y.append(normalized_r[1])
	z.append(normalized_r[2])

	p = normalized_r
	positions[satellite_name] = [
		normalized_r[0], 
		normalized_r[1], 
		normalized_r[2]
		]

	text = "\\coordinate ({}) at ({}, {}, {});".format(
		satellite_name, 
		normalized_r[0], 
		normalized_r[1], 
		normalized_r[2]
	)
	print(text)
	
	# todo : change color if it lies behind hyperplane
	color = "black"
	if is_behind_plane(normal_r, p):
		color = "gray"
	text = "\\fill[color={}] ({}) circle (0.5pt);".format(color, satellite_name)
	print(text)

	# print(r)
	# print(sat_epoch_datetime(satellite))
	# print(tle)

# print(positions)
slice_time = 0
for edge in graph["edges"].keys():
	source, target = edge.strip().split(" - ")[0:2]
	# TODO : only draw if edge is alive at specified time!
	color = "black"
	if is_behind_plane(normal_r, positions[source]) or is_behind_plane(normal_r, positions[target]):
		color = "gray"
	text = "\\draw[thick, color={}] ({}) -- ({});".format(
		color,
		source,
		target
	)

	# print(graph["edges"][edge])

	# print(text)

	if slice_time in graph["edges"][edge]:
		print(text)

# to handle moon tle, are the heights based on the radius of the moon?