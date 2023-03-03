import contact_analysis as ca
from os_utilities import *

from graph_tool.all import *
import matplotlib.pyplot as plt

import scipy
import numpy as np

# import os # for run_sims; TODO : remove when we move that

if __name__ == "__main__":
    DEBUG = True
else:
    DEBUG = False

#TODO: define and write a function that Grabs graph at a time t

def get_graph_slice_at(graph, time):
    """
    Given a temporal graph and a fixed time during its lifetime, return a
    static (graph_tool) graph `g` that exists at that point in time.
    """
    g = Graph(directed=False)

    label = g.new_vertex_property("object");
    g.vertex_properties["label"] = label;

    # add all nodes; independent of time
    nodes = {}
    for node_key, node_number in graph["nodes"].items():
        vertex = g.add_vertex()

        nodes[node_key] = vertex;
        g.vp.label[vertex] = node_key

    edges = {}
    for edge_key, edge_times in graph["edges"].items():

        # check if time lives in edge_times between rise and set
        time_count = len(edge_times)
        # assuming soap output always has a set time, even if end of run.
        for i in range(0, time_count, 2):
            rise_time = edge_times[i]
            set_time = edge_times[i + 1]

            if rise_time <= time and time <= set_time:
                # add edge
                edge_source, edge_destination = edge_key.split(" - ")
                edges[edge_key] = g.add_edge(nodes[edge_source], nodes[edge_destination])

            if time > set_time:
                # get out of loop since this edge will not be added
                break;

    return g

# graph = get_graph_slice_at(None)
# print(graph)

def get_diameter(g):
    """
    Given a static (graph_tool) graph `g`, we return the pseudo_diameter of
    that graph together with a representative source and target that
    realizes the diameter.

    We assume the graph is unweighted, so the diameter consists of
    the number of hops.
    """
    diameter = 0

    dist, ends = pseudo_diameter(g)
    #print(dist)
    #print(int(ends[0]), int(ends[1]))

    source_index = int(ends[0])
    target_index = int(ends[1])

    source = g.vp.label[source_index]
    target =  g.vp.label[target_index]

    representative = {
        "source_index" : source_index,
        "target_index" : target_index,
        "source" : source,
        "target" : target
    }

    return dist
    # return dist, representative

def get_vertex_count(g):
    """
    Returns the number of vertices in a (graph_tool) graph object.
    """
    return g.num_vertices()

def get_edge_count(g):
    """
    Returns the number of edges in a (graph_tool) graph object.
    """
    return g.num_edges()

def get_degree_distribution(g):
    v_hist, v_hist_bins = vertex_hist(g, "total")
    v_hist_count = len(v_hist)

    n = get_vertex_count(g)


    x = list(range(0, n))
    y = list(range(0, n))
    for i in range(0, n):
        y[i] = 0
        if i < v_hist_count:
            y[i] = v_hist[i] / n

    # print(sum(y))
    assert(abs(1 - sum(y)) < 0.001)

    # if DEBUG :
    #     plt.plot(x, y)
    #     plt.show()

    return x, y

def iterate_slices(graph, sample_times, functions):
    """
    This function takes in a temporal graph together with a list of
    sample times that live within the lifetime of the temporal graph,
    and a list of functions to be run on slices of static graphs taken at
    the specified times.
    """

    output = {}
    for f in functions:
        output[f.__name__] = []
    # if DEBUG : print(output)

    for time in sample_times:
        # if DEBUG : print(time)

        g = get_graph_slice_at(graph, time);

        for f in functions:
            f_output = f(g)
            output[f.__name__].append(f_output)

    return output

def get_slices(graph, critical_times):
    # critical_times = ca.extract_critical_times(graph)

    # samples[i] = midpoint between c_times[i+ 1] and c_times[i]
    critical_samples = ca.sample_critical_times(critical_times)

    # for i in range(len(critical_times) - 1):
    #     difference = (critical_times[i + 1] - critical_times[i] )
    #     middle = critical_times[i] + (difference / 2)
    #
    #     critical_samples.append(middle)

    diameters = []

    for time in critical_samples:
        break
        g = get_graph_slice_at(graph, time)
        # print(g)

        dist, ends = pseudo_diameter(g)
        #print(dist)
        #print(int(ends[0]), int(ends[1]))

        source_index = int(ends[0])
        target_index = int(ends[1])
        source = g.vp.label[source_index]
        target =  g.vp.label[target_index]

        diameters.append(dist)
        # print("The diameter is {}.".format(dist))
        # print("Largest path is between {} and {}".format(source, target))

    # plt.hist(diameters)
    # plt.show()
    # test code
    time = critical_samples[1713]
    # time = critical_samples[2]
    g = get_graph_slice_at(graph, time)
    #print(g)
    filename = "test.pdf";
    # graph_tool.draw.graph_draw(g, vertex_text=g.vp.label, output=filename);
    pos = sfdp_layout(g)
    deg = g.degree_property_map("in")
    graph_draw(g, pos=pos, vertex_size=5, output=filename)

    dist, ends = pseudo_diameter(g)

    source_index = int(ends[0])
    target_index = int(ends[1])

    #print("The diameter is {}.".format(dist))
    source = g.vp.label[source_index]
    target =  g.vp.label[target_index]
    #print("Largest path is between {} and {}".format(source, target))

    vlist, elist = shortest_path(g, g.vertex(source_index), g.vertex(target_index))
    # print([str(v) for v in vlist])
    # print([str(e) for e in elist])

    ecolor = g.new_edge_property("string")
    ewidth = g.new_edge_property("double")
    ewidth.a = 1
    for e in g.edges():
        ecolor[e] = "#d3d7cf"
        # print(elist)
        if e in elist:
            # ecolor[e] = "#a40000"  # "#3465a4"
            ecolor[e] = "#3465a4"
            ewidth[e] = 2

    graph_draw(g, pos=pos, vertex_size=5, edge_color=ecolor, edge_pen_width=ewidth, output=filename)


    # adjacency matrix
    # A = adjacency(g, operator=True)
    # L = laplacian(g, operator=True)
    # N = g.num_vertices()
    # ew1 = scipy.sparse.linalg.eigs(L, k=N//2, which="LR", return_eigenvectors=False)
    # ew2 = scipy.sparse.linalg.eigs(L, k=N-N//2, which="SR", return_eigenvectors=False)
    # ew = np.concatenate((ew1, ew2))
    #
    # plt.figure(figsize=(8, 2))
    # plt.scatter(np.real(ew), np.imag(ew), c=np.sqrt(abs(ew)), linewidths=0, alpha=0.6)
    # plt.xlabel(r"$\operatorname{Re}(\lambda)$")
    # plt.ylabel(r"$\operatorname{Im}(\lambda)$")
    # plt.tight_layout()
    # plt.savefig("adjacency-spectrum.svg")

    # centrality
    # g = GraphView(g, vfilt=label_largest_component(g))
    # ee, x, y = hits(g)
    # graph_draw(g, vertex_fill_color=x,
    #       vertex_size=prop_to_size(x, mi=5, ma=15),
    #       vcmap=plt.cm.gist_heat,
    #       vorder=x, output="polblogs_hits_auths.pdf")
    #
    # graph_draw(g, vertex_fill_color=y,
    #         vertex_size=prop_to_size(y, mi=5, ma=15),
    #         vcmap=plt.cm.gist_heat,
    #         vorder=y, output="polblogs_hits_hubs.pdf")

    # eigenvector
    g = GraphView(g, vfilt=label_largest_component(g))
    w = g.new_edge_property("double")
    w.a = np.random.random(len(w.a)) * 42
    ee, x = eigenvector(g, w)
    graph_draw(g, vertex_fill_color=x,
                  vertex_size=prop_to_size(x, mi=5, ma=15),
                  vcmap=plt.cm.gist_heat,
                  vorder=x, output="polblogs_eigenvector.pdf")

    # todo histogram relative centrality scores : eigenvector centrality
    #       R : Track specific ones, or changing high to low.
    #       which centrality measures more stable over time?
    return None

def example_usage():

    filename = "contact_simple.csv"
    filename = "./outputs/starlink-80/starlink_3 Contact Analysis.csv"
    contact_plan = ca.contact_analysis_parser(filename)
    graph = ca.construct_graph(contact_plan)
    critical_times = ca.extract_critical_times(graph)

    g = get_graph_slice_at(graph, 0)
    g = get_graph_slice_at(graph, 1713)

    def draw_graph(g, filename):
        pos = sfdp_layout(g)
        deg = g.degree_property_map("in")
        graph_draw(g, pos=pos, vertex_size=5, output=filename)

    filename = "test.pdf";
    # graph_tool.draw.graph_draw(g, vertex_text=g.vp.label, output=filename);
    # pos = sfdp_layout(g)
    # deg = g.degree_property_map("in")
    # graph_draw(g, pos=pos, vertex_size=5, output=filename)
    draw_graph(g, filename)

    # print(get_vertex_count(g))
    get_degree_distribution(g)
    v_hist = vertex_hist(g, "total")
    # print(get_diameter(g))
    # print(get_edge_count(g))
    # print(sum(v_hist[0]))
    # print(v_hist)
    # print(diameter_list)
    # Creating histogram
    fig, ax = plt.subplots(figsize =(10, 7))
    ax.hist(v_hist[0], bins=v_hist[1])

    # Show plot
    # plt.show()

    # expect sum(vertex_hist(g, "total")[0]) == get_vertex_count(g)

    # sample_times = ca.sample_critical_times(critical_times)
    sample_times = range(0, 86400, 3600)
    outputs = iterate_slices(
        graph,
        sample_times,
        [get_diameter, get_edge_count])

def run_simulations(folder):
    # diagrams = {}
    outputs = []

    filepaths = get_csv_files(folder)

    for filepath in filepaths:
        filename = filepath.split("/")[-1]
        # print(filename)

        contact_plan = ca.contact_analysis_parser(filepath)
        graph = ca.construct_graph(contact_plan)

        sample_times = range(0, 86400, 3600)
        output = iterate_slices(
            graph,
            sample_times,
            [get_diameter, get_edge_count, get_degree_distribution])
        # print(dgms)

        outputs.append(output)

    # return outputs
    # testing
    plt.figure()
    for output in outputs:
        for dist in output["get_degree_distribution"]:
            # print(dist)
            x = output["get_degree_distribution"][0]
            y = output["get_degree_distribution"][1]
        # print(x)
        # print(y)
            plt.plot(x, y)
    plt.show()
    return outputs

if __name__ == "__main__":

    folder = "./tests/csv/"
    run_simulations(folder)

    # diameter_list = outputs[get_diameter.__name__]
    # edge_list = outputs[get_edge_count.__name__]

    # # print(diameter_list)
    # # Creating histogram
    # fig, ax = plt.subplots(figsize =(10, 7))
    # ax.hist(edge_list)
    #
    # # Show plot
    # plt.show()


    # get_slices(graph, critical_times)
