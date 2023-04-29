import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import interval_distance_functions as idf
from matplotlib import animation

import os
import pandas as pd
import networkx as nx
import numpy as np
import seaborn as sns

from matrix import IntervalMatrix

import portion as P

import logging 
logging.getLogger().setLevel(logging.CRITICAL) # matplotlib has too many


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


def contact_graph(input_matrix):
    # Takes an IntervalMatrix and returns the 3d graph of the contact intervals
    max_i = input_matrix.dim_row
    max_j = input_matrix.dim_col
    fig = plt.figure(figsize=(8,5))
    ax = plt.axes(projection='3d')
    full_contacts = []
    #temp = M.matrix
    full_contacts.append(input_matrix.matrix)

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

def save_heatmap_gif(adjacency_matrices, m, frame_count, filepath):
    print(f"len(data_list) = {len(adjacency_matrices)} | frame_count = {frame_count}")

    my_frame_count = 0
    for data in adjacency_matrices:
        if np.amin(data) < np.amax(data):
            my_frame_count += 1
        else:
            print(f"truncated frame_count={frame_count} to {my_frame_count}")
            frame_count = my_frame_count
            break
    # print(f"frame_count = {frame_count} vs my_frame_count = {my_frame_count}")
    # frame_count = my_frame_count

    def init():
        return sns.heatmap(np.zeros((m, m)), vmax=.8, square=True, cbar=False, xticklabels=False, yticklabels=False)

    def animate(i):
        data = adjacency_matrices[i]
        # print(f"min={np.amin(data)}, max={np.amax(data)}")
        return sns.heatmap(data, vmax=.8, square=True, cbar=False, xticklabels=False, yticklabels=False)

    fig = plt.figure()
    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=frame_count, repeat = False)

    pillowwriter = animation.PillowWriter(fps=5)
    anim.save(filepath, writer=pillowwriter)
    plt.close()

if __name__ == '__main__':
    A = [[P.open(-P.inf,P.inf),P.open(.8,2)|P.open(10,12),P.open(0,1)|P.open(2,5)], [P.open(.8,2)|P.open(10,12),P.open(-P.inf,P.inf),P.open(.5,1)|P.open(3,4)], [P.open(0,1)|P.open(2,4),P.open(0,1)|P.open(3,4),P.open(-P.inf,P.inf)]]
    A = IntervalMatrix(3, 3, A)
    x = contact_graph(A)
    print("Our contact graph is {}".format(x))
    #save_figure(x, "practice")
    display_figure(x)


