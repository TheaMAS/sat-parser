import dionysus as d

import contact_analysis as ca

import os # for run_sims; TODO : remove when we move that
# testing purposes visualizing
import numpy as np
import matplotlib.pyplot as plt

def calculate_zz_persistence(weighted_simplex):
    """
    This function takes in a `weighted_simplex` from the function
    `construct_weighted_simplex` and calculates its zig-zag persistence,
    as output from dionysus2.
    """

    simplex = weighted_simplex["simplex"]
    times = weighted_simplex["times"]

    # Makes the filtration.
    f = d.Filtration(simplex)

    # print(d.is_simplicial(f, report = True))

    zz, dgms, cells = d.zigzag_homology_persistence(f, times)
    # output = d.zigzag_homology_persistence(f, times)
    # print(output)

    # for i,dgm in enumerate(dgms):
    #     print("Dimension:", i)
    #     for p in dgm:
    #         print(p)

    return zz, dgms, cells

def get_csv_files(folder):
    """
    This function gets the full filepaths of all the csv files in a given
    folder as a list.
    """
    filepaths = []

    for filename in os.listdir(folder):
        f = os.path.join(folder, filename)
        if os.path.isfile(f) and f.endswith(".csv"):
            filepaths.append(f)
    return filepaths

def run_simulations(folder):
    """
    This is an example function of how to run simulations on a collection of
    contact analysis csvs. The input is the filepath of a folder containing
    a collection of contact analysis csv outputs from soap.

    Here we calculate the zig-zag persistence on each contact plan and
    calculate the pairwise barcode distances (2-wasserstein and bottleneck)
    on them.
    """
    # diagrams = {}
    diagrams = []

    filepaths = get_csv_files(folder)

    for filepath in filepaths:
        filename = filepath.split("/")[-1]
        # print(filename)

        contact_plan = ca.contact_analysis_parser(filepath)
        graph = ca.construct_graph(contact_plan)
        weighted_simplex = ca.construct_weighted_simplex(graph)
        zz, dgms, cells = calculate_zz_persistence(weighted_simplex)
        # print(dgms)

        # diagrams[filename] = dgms
        diagrams.append(dgms)


    # Creating a numpy array
    x = []
    y = []
    zw = []
    zb = []

    for i in range(len(diagrams)):
        for j in range(i + 1, len(diagrams)):
            dgms1 = diagrams[i]
            dgms2 = diagrams[j]
            # print(dgms1)
            # print(dgms2)

            # for i,dgm in enumerate(dgms1):
            #     print("Dimension:", i)
            #     for p in dgm:
            #         print(p)
            #
            # for i,dgm in enumerate(dgms2):
            #     print("Dimension:", i)
            #     for p in dgm:
            #         print(p)
            dim = 1

            wdist = d.wasserstein_distance(dgms1[dim], dgms2[dim], q=2)
            print("2-Wasserstein distance between {}-dimensional persistence diagrams: {}".format(dim, wdist))

            bdist = d.bottleneck_distance(dgms1[dim], dgms2[dim])
            print("Bottleneck distance between {}-dimensional persistence diagrams: {}".format(dim, bdist))

            x.append(i)
            y.append(j)
            zw.append(wdist)
            zb.append(bdist)
            # print("{} - {}".format(i, j))


    # Creating dataset
    x = np.array(x)
    y = np.array(y)
    zw = np.array(zw)
    zb = np.array(zb)

    # Creating figure
    fig = plt.figure(figsize = (10, 7))
    ax = plt.axes(projection ="3d")

    # Creating plot
    ax.scatter3D(x, y, zw, color = "green", label="Wasserstein")
    ax.scatter3D(x, y, zb, color = "red", label = "Bottleneck")
    plt.title("Zig-Zag Distances")
    plt.legend(loc='upper left');
    # show plot
    # plt.show()

    # for key, value in diagrams.items():
    #     # print("{}", key)
    #     wdist = d.wasserstein_distance(dgms1[1], dgms2[1], q=2)

    # print(diagrams)
    return None

# folder = "./outputs/starlink-7/"
# run_simulations(folder)

# exit()
#
# #filename = "contact_simple.csv"
# # filename = "./outputs/starlink-80/starlink_3 Contact Analysis.csve"
# filename = "./outputs/starlink-80/starlink_0 Contact Analysis.csv"
#
# contact_plan = ca.contact_analysis_parser(filename)
#
# # for contact in contact_plan:
#     # print("".format(contact["connection"], contact["source"], contact[]))
#     # print(contact["connection"], "=", contact["source"], "-", contact["destination"])
#
# graph = ca.construct_graph(contact_plan)
# weighted_simplex = ca.construct_weighted_simplex(graph)
# zz, dgms, cells = calculate_zz_persistence(weighted_simplex)

# print(dgms[0][1])
# exit()

# d.plot.plot_diagram(dgms[1], show = True)

# d.plot.plot_diagram_density(dgms[1], show = True)
# d.plot.plot_bars(dgms[1], show = True)

# TODO : for each contact plan csv in experiment folder,
#   calculate zz persistence
#def calculate_zz_persistence(folder):

#    return ""
