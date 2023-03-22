import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import interval_distance_functions as idf

import os
import pandas as pd
import networkx as nx
import numpy as np

from matrix import IntervalMatrix

import portion as P



<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
def save_figure(plot_context, filename):
    fig = plot_context[0]
    ax = plot_context[1]
    plt.savefig(str(filename))
    return plot_context

def display_figure(plot_context):
    fig = plot_context[0]
    ax = plot_context[1]
    plt.show()
    return plot_context

=======
def save_figure(plt, ax, filename):
=======
def save_figure(fig, ax, filename):
>>>>>>> b90d999 (Added passes to unimplemented functions)
=======
def save_figure(plot_context, filename):
    fig = plot_context[0]
    ax = plot_context[1]
>>>>>>> a2b9ac1 (0004 Continued refactoring of visualization code)
    plt.savefig(str(filename))
    return plot_context

<<<<<<< HEAD
def display_figure(fig, ax):
    pass
>>>>>>> 38ae1c9 (0004: Initial stage of refactoring; adding warnings)
=======
def display_figure(plot_context):
    fig = plot_context[0]
    ax = plot_context[1]
    plt.show()
    return plot_context
>>>>>>> a2b9ac1 (0004 Continued refactoring of visualization code)

def contact_graph(input_matrix):
    # Takes an IntervalMatrix and returns the 3d graph of the contact intervals

<<<<<<< HEAD
<<<<<<< HEAD
    max_i = input_matrix.dim_row
    max_j = input_matrix.dim_col
    fig = plt.figure(figsize=(8,5))
    ax = plt.axes(projection='3d')
    full_contacts = []
    #temp = M.matrix
    full_contacts.append(input_matrix.matrix)
=======
    max_i = len(M.matrix)
    max_j = len(M.matrix[0])
    fig = plt.figure(figsize=(8,5))
    ax = plt.axes(projection='3d')
    full_contacts = []
    temp = M.matrix
    full_contacts.append(M.matrix)
>>>>>>> 38ae1c9 (0004: Initial stage of refactoring; adding warnings)
=======
    max_i = input_matrix.dim_row
    max_j = input_matrix.dim_col
    fig = plt.figure(figsize=(8,5))
    ax = plt.axes(projection='3d')
    full_contacts = []
    #temp = M.matrix
    full_contacts.append(input_matrix.matrix)
>>>>>>> a2b9ac1 (0004 Continued refactoring of visualization code)

    int_min = 0
    int_max = 10

    for i in range(max_i):
        for j in range(i, max_j):
            for pt in P.to_data(full_contacts[0][i][j]):

                if int_max < pt[2] and pt[2] != float('inf'):
                    int_max = pt[2]
                if int_min > pt[1] and pt[1] >= 0 and pt[1] != -float('inf'):
                    int_min = pt[1]

<<<<<<< HEAD
<<<<<<< HEAD
    x_vals, y_vals= [], []

=======
    x_vals, y_vals= [],[]
>>>>>>> 38ae1c9 (0004: Initial stage of refactoring; adding warnings)
=======
    x_vals, y_vals= [], []
>>>>>>> b90d999 (Added passes to unimplemented functions)
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
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> a2b9ac1 (0004 Continued refactoring of visualization code)

    A = [[P.open(-P.inf,P.inf),P.open(.8,2)|P.open(10,12),P.open(0,1)|P.open(2,5)], [P.open(.8,2)|P.open(10,12),P.open(-P.inf,P.inf),P.open(.5,1)|P.open(3,4)], [P.open(0,1)|P.open(2,4),P.open(0,1)|P.open(3,4),P.open(-P.inf,P.inf)]]
    A = IntervalMatrix(3, 3, A)
    x = contact_graph(A)
    print("Our contact graph is {}".format(x))
    #save_figure(x, "practice")
    display_figure(x)
<<<<<<< HEAD
=======
    
>>>>>>> 38ae1c9 (0004: Initial stage of refactoring; adding warnings)

=======
    pass
>>>>>>> b90d999 (Added passes to unimplemented functions)
=======










>>>>>>> a2b9ac1 (0004 Continued refactoring of visualization code)
