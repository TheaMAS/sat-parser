import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import interval_distance_functions as idf

import os
import pandas as pd
import networkx as nx
import numpy as np

from matrix import IntervalMatrix

import portion as P



def save_figure(plt, ax, filename):
    plt.savefig(str(filename))
    return 0

def display_figure(plt, ax):
    pass

def contact_graph(input_matrix):
    # Takes an IntervalMatrix and returns the 3d graph of the contact intervals

    max_i = len(M.matrix)
    max_j = len(M.matrix[0])
    fig = plt.figure(figsize=(8,5))
    ax = plt.axes(projection='3d')
    full_contacts = []
    temp = M.matrix
    full_contacts.append(M.matrix)

    int_min = 0
    int_max = 10

    for i in range(max_i):
        for j in range(i, max_j):
            for pt in P.to_data(full_contacts[0][i][j]):

                if int_max < pt[2] and pt[2] != float('inf'):
                    int_max = pt[2]
                if int_min > pt[1] and pt[1] >= 0 and pt[1] != -float('inf'):
                    int_min = pt[1]

    x_vals, y_vals= [],[]
    z_tops = []
    z_bottoms = []
    for i in range(max_i):
        for j in range(i, max_j):
            for pt in P.to_data(full_contacts[0][i][j]):
                if(pt[1] != float('inf')):
                    x_vals.append(i)
                    y_vals.append(j)
                    z_bottoms.append(max(pt[1], int_min))
                    z_tops.append(min(pt[2]-pt[1],int_max))
            width = depth = .5
    ax.bar3d(x_vals, y_vals, z_bottoms, width, depth, z_tops)#, shade=True)
    #ax.set_title(title)
    plt.xticks(np.arange(0,max_i, 1.0))
    plt.yticks(np.arange(0,max_j, 1.0))
    return fig, ax

if __name__ == '__main__':
    

