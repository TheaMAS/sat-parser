import contact_analysis as ca
import portion as P

from matrix import IntervalMatrix

# file_parser.py
# Contains functions which handle data from files




# soap_converter
# Original authors: Robert Cardona and Brittany Story
# Additional contributors: Brian Heller
# @contactsheet: path to file
# @return: IntervalMatrix

def soap_converter(contactsheet):
    contact_plan = ca.contact_analysis_parser(contactsheet)
    graph = ca.construct_graph(contact_plan)
    nodes = graph["nodes"]
    edges = graph["edges"]

    node_counter = len(nodes);

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
            rise = edge_times[i]
            set = edge_times[i + 1]

            # rise = edge_times[0]
            # set = edge_times[1]

            #add interval to both F[i][j] and F[j][i] via union (should create disjoint unions generally)
            Final[nodes[source]][nodes[destination]] = Final[nodes[source]][nodes[destination]] | P.open(rise, set)
            Final[nodes[destination]][nodes[source]] = Final[nodes[destination]][nodes[source]] | P.open(rise, set)

    return IntervalMatrix(node_counter, node_counter, Final)