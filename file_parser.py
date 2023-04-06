# import contact_analysis as ca
import report_parser as rp
import portion as P

from matrix import IntervalMatrix

# file_parser.py
# Contains functions which handle data from files

# TODO : RC thinks this should be moved into report_parser since it deals
#	with the contact analysis reports


# soap_converter
# Original authors: Robert Cardona and Brittany Story
# Additional contributors: Brian Heller
# @contactsheet: path to file
# @return: IntervalMatrix

def soap_converter(contactsheet):
    contact_plan = rp.contact_analysis_parser(contactsheet)
    graph = rp.construct_graph(contact_plan)

    nodes = graph["nodes"]
    edges = graph["edges"]

    node_counter = len(nodes)
    print(node_counter)

    #generate blank matrix for overall
    Final=[[ P.empty() for i in range(node_counter) ] for j in range(node_counter)]
    #diagonal is all R (for now, should be adjusted to min/max time in future rev)
    for i in range(node_counter):
        Final[i][i]=P.open(-P.inf,P.inf)

    #generate interval for each edge and append it to matrix via union
    for edge_key, edge_times in edges.items():
        source, destination = edge_key.split(' - ')

        # print(len(edge_times))

        for i in range(0, len(edge_times), 2):
            rise_time = edge_times[i]
            set_time = edge_times[i + 1]

            # rise = edge_times[0]
            # set = edge_times[1]

            #add interval to both F[i][j] and F[j][i] via union (should create disjoint unions generally)
            Final[nodes[source]][nodes[destination]] = Final[nodes[source]][nodes[destination]] | P.open(rise_time, set_time)
            Final[nodes[destination]][nodes[source]] = Final[nodes[destination]][nodes[source]] | P.open(rise_time, set_time)

    return IntervalMatrix(node_counter, node_counter, Final)

if __name__ == "__main__":

	A = soap_converter("./outputs/starlink-15-sat-single/starlink_15_sats_0 Contact Analysis.csv")

	test = """
		"STARLINK-1199 - STARLINK-2419"
		"STARLINK-1199 - STARLINK-2451"
		"STARLINK-1199 - STARLINK-3633"
		"STARLINK-1199 - STARLINK-3740"
		"STARLINK-1199 - STARLINK-2228"
		"STARLINK-1199 - STARLINK-3606"
		"STARLINK-1199 - STARLINK-2151"
		"STARLINK-1199 - STARLINK-3516"
		"STARLINK-1199 - STARLINK-3818"
		"STARLINK-1199 - STARLINK-2082"
		"STARLINK-1199 - STARLINK-1849"
		"STARLINK-1199 - STARLINK-1054"
		"STARLINK-1199 - STARLINK-1882"
		"STARLINK-1199 - STARLINK-1680"
		"STARLINK-2419 - STARLINK-2451"
		"STARLINK-2419 - STARLINK-3633"
		"STARLINK-2419 - STARLINK-3740"
		"STARLINK-2419 - STARLINK-2228"
		"STARLINK-2419 - STARLINK-3606"
		"STARLINK-2419 - STARLINK-2151"
		"STARLINK-2419 - STARLINK-3516"
		"STARLINK-2419 - STARLINK-3818"
		"STARLINK-2419 - STARLINK-2082"
		"STARLINK-2419 - STARLINK-1849"
		"STARLINK-2419 - STARLINK-1054"
		"STARLINK-2419 - STARLINK-1882"
		"STARLINK-2419 - STARLINK-1680"
		"STARLINK-2451 - STARLINK-3633"
		"STARLINK-2451 - STARLINK-3740"
		"STARLINK-2451 - STARLINK-2228"
		"STARLINK-2451 - STARLINK-3606"
		"STARLINK-2451 - STARLINK-2151"
		"STARLINK-2451 - STARLINK-3516"
		"STARLINK-2451 - STARLINK-3818"
		"STARLINK-2451 - STARLINK-2082"
		"STARLINK-2451 - STARLINK-1849"
		"STARLINK-2451 - STARLINK-1054"
		"STARLINK-2451 - STARLINK-1882"
		"STARLINK-2451 - STARLINK-1680"
		"STARLINK-3633 - STARLINK-3740"
		"STARLINK-3633 - STARLINK-2228"
		"STARLINK-3633 - STARLINK-3606"
		"STARLINK-3633 - STARLINK-2151"
		"STARLINK-3633 - STARLINK-3516"
		"STARLINK-3633 - STARLINK-3818"
		"STARLINK-3633 - STARLINK-2082"
		"STARLINK-3633 - STARLINK-1849"
		"STARLINK-3633 - STARLINK-1054"
		"STARLINK-3633 - STARLINK-1882"
		"STARLINK-3633 - STARLINK-1680"
		"STARLINK-3740 - STARLINK-2228"
		"STARLINK-3740 - STARLINK-3606"
		"STARLINK-3740 - STARLINK-2151"
		"STARLINK-3740 - STARLINK-3516"
		"STARLINK-3740 - STARLINK-3818"
		"STARLINK-3740 - STARLINK-2082"
		"STARLINK-3740 - STARLINK-1849"
		"STARLINK-3740 - STARLINK-1054"
		"STARLINK-3740 - STARLINK-1882"
		"STARLINK-3740 - STARLINK-1680"
		"STARLINK-2228 - STARLINK-3606"
		"STARLINK-2228 - STARLINK-2151"
		"STARLINK-2228 - STARLINK-3516"
		"STARLINK-2228 - STARLINK-3818"
		"STARLINK-2228 - STARLINK-2082"
		"STARLINK-2228 - STARLINK-1849"
		"STARLINK-2228 - STARLINK-1054"
		"STARLINK-2228 - STARLINK-1882"
		"STARLINK-2228 - STARLINK-1680"
		"STARLINK-3606 - STARLINK-2151"
		"STARLINK-3606 - STARLINK-3516"
		"STARLINK-3606 - STARLINK-3818"
		"STARLINK-3606 - STARLINK-2082"
		"STARLINK-3606 - STARLINK-1849"
		"STARLINK-3606 - STARLINK-1054"
		"STARLINK-3606 - STARLINK-1882"
		"STARLINK-3606 - STARLINK-1680"
		"STARLINK-2151 - STARLINK-3516"
		"STARLINK-2151 - STARLINK-3818"
		"STARLINK-2151 - STARLINK-2082"
		"STARLINK-2151 - STARLINK-1849"
		"STARLINK-2151 - STARLINK-1054"
		"STARLINK-2151 - STARLINK-1882"
		"STARLINK-2151 - STARLINK-1680"
		"STARLINK-3516 - STARLINK-3818"
		"STARLINK-3516 - STARLINK-2082"
		"STARLINK-3516 - STARLINK-1849"
		"STARLINK-3516 - STARLINK-1054"
		"STARLINK-3516 - STARLINK-1882"
		"STARLINK-3516 - STARLINK-1680"
		"STARLINK-3818 - STARLINK-2082"
		"STARLINK-3818 - STARLINK-1849"
		"STARLINK-3818 - STARLINK-1054"
		"STARLINK-3818 - STARLINK-1882"
		"STARLINK-3818 - STARLINK-1680"
		"STARLINK-2082 - STARLINK-1849"
		"STARLINK-2082 - STARLINK-1054"
		"STARLINK-2082 - STARLINK-1882"
		"STARLINK-2082 - STARLINK-1680"
		"STARLINK-1849 - STARLINK-1054"
		"STARLINK-1849 - STARLINK-1882"
		"STARLINK-1849 - STARLINK-1680"
		"STARLINK-1054 - STARLINK-1882"
		"STARLINK-1054 - STARLINK-1680"
		"STARLINK-1882 - STARLINK-1680"
	"""


	sats = set()
	test = test.replace("\t ", "").replace("\"", "").split("\n")
	for pair in test[1:-1]:
		source, destination = pair.split(" - ")
			
		sats.add(source)
		sats.add(destination)
	print(sats)