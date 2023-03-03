# Code from Robert Cardona!
# Input is a .csv file. Converts the SOAP data into a filtration
# and then runs it through the dionysus function that calculates zigzag
# persistent homology.

import dionysus as d

def soapConverter(spreadsheet):

    # Initializes nodes and edges lists.
    nodes = {};
    edges = {}

    filename = spreadsheet

    # Imports the file you inputted into a string and splits the information into
    # multiple strings via line breaks.
    with open(filename) as f:
        content = f.read().splitlines()

    # Initializes node_counter and current_edge
    node_counter = 0;
    current_edge = None;

    # For each line, it splits up entries by inserting commas
    # If the entry is in the analysis column, it splits it into source and destination
    # For all nodes not yet added to nodes, it adds them. Same for edges.
    analysisCounter = 0
    for line in content:
        if analysisCounter == 2:
            break
        line = line.split(',')

        if "sees" in line[0]:
            source, destination = line[0].split('sees');
            if source not in nodes:
                nodes[source] = node_counter;
                node_counter += 1;
            if destination not in nodes:
                nodes[destination] = node_counter;
                node_counter += 1;

            if line[0] not in edges:
                current_edge = str(line[0])
                edges[current_edge] = []

            riseString = line[1]
            setString = line[2]

            rise = float(riseString)
            edges[current_edge].append(rise)

            set = float(setString)
            edges[current_edge].append(set)
        if line[0].find("Analysis") != -1:
            analysisCounter += 1

    # Initialize nodes.
    simplex = []
    times = []

    # Make the nodes based on the data.
    for node_key, node_number in nodes.items():
      simplex.append([node_number])
      times.append([0]) # all nodes bimport dionysus as d

nodes = {};
edges = {}

filename = "contact_new.csv"

with open(filename) as f:
    content = f.read().splitlines()

node_counter = 0;
current_edge = None;

# old soap data parser
# for line in content:
#     line = line.split(',')
#
#     if line[0] == "Analysis":
#         source, destination = line[1].split('-');
#         if source not in nodes:
#             nodes[source] = node_counter;
#             node_counter += 1;
#         if destination not in nodes:
#             nodes[destination] = node_counter;
#             node_counter += 1;
#
#         if line[1] not in edges:
#             current_edge = str(line[1])
#             edges[current_edge] = []
#         continue;
#
#     if line[0].find("Rise") != -1 or line[0].find("Is_True") != -1:
#         continue;
#
#     riseString, setString, durationString = line
#
#     rise = float(riseString)
#     edges[current_edge].append(rise)
#
#     set = float(setString)
#     edges[current_edge].append(set)

# new soap data parser



for line in content:
    line = line.split(',')

    name = line[0].split(" sees ")

    if len(name) == 2: # means we have " sees " in the first entry
        source = name[0]
        destination = name[1]

        rise = float(line[1])
        set = float(line[2])

        if source not in nodes:
            nodes[source] = node_counter;
            node_counter += 1;
        if destination not in nodes:
            nodes[destination] = node_counter;
            node_counter += 1;

        if line[0] not in edges:
            current_edge = str(line[0])
            edges[current_edge] = []

        edges[current_edge].append(rise)
        edges[current_edge].append(set)

        print("we have a connection", source, destination, "born at", rise, "dies at", set)
        print(nodes)
        print(edges)
    # else skip


# dionysus specific code

simplex = []
times = []

for node_key, node_number in nodes.items():
  simplex.append([node_number])
  times.append([0]) # all nodes born at time zero

for edge_key, edge_times in edges.items():
    edge_source, edge_destination = edge_key.split(" sees ")

    if edge_times == []:
        continue;

    simplex.append([nodes[edge_source], nodes[edge_destination]])
    print(simplex)
    times.append(edge_times)

# problem up here.

f = d.Filtration(simplex)

zz, dgms, cells = d.zigzag_homology_persistence(f, times)

print(zz)

for i,dgm in enumerate(dgms):
    print("Dimension:", i)
    for p in dgm:
        print(p)
#orn at time zero

    # Make the edges, where edge key is the labels and edge times are the birth/death times.
    for edge_key, edge_times in edges.items():
        edge_source, edge_destination = edge_key.split('sees')

        if edge_times == []:
            continue;

    # Makes the appropriate simplex for the given data.
        simplex.append([nodes[edge_source], nodes[edge_destination]])
        times.append(edge_times)

    # Makes the filtration.
    f = d.Filtration(simplex)

    # Computes the zigzag homology.
    zz, dgms, cells = d.zigzag_homology_persistence(f, times)

    print(zz)

    for i,dgm in enumerate(dgms):
        print("Dimension:", i)
        for p in dgm:
            print(p)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        soapConverter(sys.argv[1])
    else:
        raise SystemExit("usage:  python soapConverter.py 'spreadsheet_name.csv' ")
