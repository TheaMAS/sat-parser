import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def distances_report_parser(filename):
	"""
	Returns a dictionary whose keys are time slices and whose 
		values are dictionaries whose keys are `satA-satB` and with 
		value the distance between satA and satB in km.
	distances[time_slice]["satA-satB"] = distance (in km)
	"""
	logging.info('Running `distances_report_parser` on `{}`'.format(filename))

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
		# a_name, b_name = name.split(" - ")
		# print("{} : {}".format(a_name, b_name))
		# logger.debug("{} : {}".format(a_name, b_name))
		indices_names.append(name)
	# print(indices_names)

	distances = {}

	table = content.split("km,\n")
	lines = table[-1].split("\n")
	for line in lines:

		time_step = None
		entries = line.split(",")[:-1]
		for i, entry in enumerate(entries):
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

	print(timesteps)

