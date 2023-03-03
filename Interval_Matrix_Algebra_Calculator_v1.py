import portion as P
# Portion used to work with interval arithmetic of subsets of Real numbers

import sys
# Sys used to call for system inputs

import matplotlib.pyplot as plt
import numpy as np
import interval_distance_functions as idf
from mpl_toolkits import mplot3d
#from graph_tool.all import *
import os
import pandas as pd
import contact_analysis as ca
import networkx as nx
# from skimage import metrics

def interval_matrix_mult(X, Y):
    if len(X.columns) == len(Y.columns) and len(X.index) == len(Y.index):
        ret = pd.DataFrame(index=X.index, columns=X.columns, dtype='object')
        v = len(X.columns)
        for i in X.columns:
            for j in X.columns:
                ret[i][j] = P.empty()
                for k in X.columns:
                    ret[i][j] = ret[i][j] | (X[i][k] & Y[k][j])
        return ret
    else:
        print("Your number of columns do not align. Please check your code")

def interval_matrix_sum(X, Y):
    if len(X.columns) == len(Y.columns) and len(X.index) == len(Y.index):
        ret = pd.DataFrame(index=X.index, columns=X.columns, dtype='object')
        v = len(X.columns)
        for i in X.columns:
            for j in X.columns:
                ret[i][j] = X[i][j] | Y[i][j]
        return ret
    else:
        print("Your number of columns do not align. Please check your code")

def soapConverter(contactsheet):
    #Electric Boogaloo
    contact_plan = ca.contact_analysis_parser(contactsheet)
    graph = ca.construct_nx_graph(contact_plan)

    df = nx.to_pandas_adjacency(graph, dtype='object')

    for i in graph.nodes:
        for j in graph.nodes:
            if graph.has_edge(i, j):
                sum_interval = P.empty()
                for interval in graph[i][j]['list']:
                    sum_interval = sum_interval | P.open(interval['rise'],interval['set'])
                df[i][j] = sum_interval
            elif i == j:
                df[i][j] = P.open(-P.inf,P.inf)
            else:
                df[i][j] = P.empty()

    return df

def remove_diagonal(A):
    B = A
    for label in A.index:
        if isinstance(A[label][label], list):
            A[label][label] = [[P.empty(),P.inf]]
        else:
            A[label][label] = P.empty()
    return B

def cb3d(A, title="nil", path="nil", labels=True, upper_triangular=True):
    # Connection Barcode - 3D
    #Take a matrix A and output a 3D contact graph, saved to file "path.png"
    #print(A)
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    M = A.values.tolist()
    max_i = len(M)
    max_j = len(M[0])


    #create empty square matrix
    full_contacts = []
    temp = M
    full_contacts.append(M)

    int_min = 0
    int_max = 10


    #This snippet finds the lower and upper bounds of our plotbox
    for i in range(max_i):
        if upper_triangular == True:
            range_max_j = range(i, max_j)
        else:
            range_max_j = range(max_j)
        for j in range_max_j:
            #print(full_contacts[0][i][j])
            for pt in P.to_data(full_contacts[0][i][j]):
                #pt[0], pt[3] are booleans to represent closed/open interval notation
                #IE: (TRUE, 0, 1, FALSE) = (0,1], or something like that.
                #print(pt[2])

                if int_max < pt[2] and pt[2] != float('inf'):
                    int_max = pt[2]
                if int_min > pt[1] and pt[1] >= 0 and pt[1] != -float('inf'):
                    int_min = pt[1]

    x_vals, y_vals= [],[]
    z_tops = []
    z_bottoms = []
    for i in range(max_i):
        if upper_triangular == True:
            range_max_j = range(i, max_j)
        else:
            range_max_j = range(max_j)
        for j in range_max_j:
            for pt in P.to_data(full_contacts[0][i][j]):
                #DEBUG
                #if(pt[1] == float('inf')):
                #    print(full_contacts[k][i][j])
                if(pt[1] != float('inf')):
                    #x, y endpoints are the same since x and y are the satellites
                    x_vals.append(i)
                    y_vals.append(j)
                    #print(max(pt[1], int_min))
                    z_bottoms.append(max(pt[1], int_min))
                    #z_bottoms.append(0)
                    #This is actually dz, or difference in z, thus the difference
                    z_tops.append(min(pt[2]-pt[1],int_max))
            width = depth = .5
    #fig = plt.figure()
    #ax = fig.axes(projection='3d')
    ax.bar3d(x_vals, y_vals, z_bottoms, width, depth, z_tops)#, shade=True)
    if title != "nil":
        ax.set_title(title)
    else:
        title = ""
        ax.set_title(title)
    ax.tick_params(labelsize=5)
    if labels == True:
        plt.xticks(np.arange(0,max_i, 1.0), A.index)
        plt.yticks(np.arange(0,max_j, 1.0), A.index)

    #plt.legend()
    #ax1.set_xticklabels(tick_labels.astype(int))
    #ax1.set_yticklabels(tick_labels.astype(int))
    if path == "nil":
        plt.show()
    else:
        plt.savefig(str(path) + ".png")

    plt.close()
    return 0

def matrix_k_walk(A, k, prop=0):
    #No delay propagation
    if prop == 0:
        for i in range(1, k+1):
            ret = interval_matrix_mult(ret, ret)
    else:
        ret = propagate_df_matrix_time_delay(A,prop)
        for i in range(1,k+1):
            ret = interval_matrix_mult(ret, propagate_df_matrix_time_delay(A,i*prop))
            #print(propagate_df_matrix_time_delay(A, i*prop))
    return ret

def shift_interval(I, t):
    #return a pyportion interval, shifted forward by t
    return I.apply(lambda x: (x.replace(lower=lambda v: v+t, upper=lambda v: v+t)))

def propagate_interval_time_delay(I, t):
    return shift_interval(I & shift_interval(I, t),-t)

def propagate_df_matrix_time_delay(M, T):
    ret = pd.DataFrame(index=M.index, columns=M.columns)
    for ind in M:
        for col in M:
            ret[col][ind] = propagate_interval_time_delay(M[col][ind],T)
    return ret

def km_to_time_to_travel(km):
    return km/299792.458

def get_average_km_between_nodes(m, n, timesheet):
    total = 0
    count = 0
    if m == n:
        return 0
    for x in timesheet:
        distance_key = m + " - " + n
        if distance_key not in timesheet[x].keys():
            distance_key = n + " - " + m
        total += timesheet[x][distance_key]
        count += 1
    return total/count

def propagate_df_matrix_time_delay_with_timesheet(M, timesheet):
    avg = 0
    count = 0
    #This will function identically to propagate_df_matrix_time_delay, except instead we are grabbing the average delay over the day 
    ret = pd.DataFrame(index=M.index, columns=M.columns)
    for ind in M:
        for col in M:
            avg = get_average_km_between_nodes(ind, col, timesheet)
            ret[col][ind] = propagate_interval_time_delay(M[col][ind],km_to_time_to_travel(avg))



