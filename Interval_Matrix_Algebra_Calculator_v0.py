# The functions in this library are mostly deprecated -- use the IntervalMatrix class.

# Self-contained program for the multiplication of interval matrices using unions and intersections.
# Created by Bob Short, initial version 3/30/2022
# Last updated 4/7/2022
# 5/19/22: Added k_walks, interval matrix sum, and A* refinement  ~Brian Addendum: And a bunch of other stuff

import portion as P
# Portion used to work with interval arithmetic of subsets of Real numbers

import sys
# Sys used to call for system inputs

import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import interval_distance_functions as idf
from mpl_toolkits import mplot3d
#from graph_tool.all import *
import os
import pandas as pd
import contact_analysis as ca
import networkx as nx
import numpy as np
import file_parser as fp
from matrix import IntervalMatrix
# from skimage import metrics
import warnings

# matrix multiplication function


## Deprecated: added to matrix class
def interval_matrix_mult(X,Y):
    warnings.warn("Warning: imac0.interval_matrix_mult deprecated. Use class IntervalMatrix multiplication instead.", DeprecationWarning)

    #First check that rows are same length, else error
    if len(X)==len(Y):
        #Then check that columns are same length, else error
        if len(X[0])==len(Y[0]):
            #If both are same length, then we generate a resulting matrix.
            v=len(X)
            #initialize resulting matrix as empty
            result=[[ P.empty() for i in range(v) ] for j in range(v)]
            #Then perform the corresponding "multiplication" for each entry
            for i in range(v): #index of row
                for j in range(v): #index of column
                    for k in range(v): #index of "sum"
                        result[i][j] = result[i][j]|(X[i][k] & Y[k][j])
                        #this unions current [i][j] entry with intersection of X[i][k] and Y[k][j], as in matrix multiplication
            return result
        else:
            print("Your number of columns do not align.  Please check your code.")
    else:
        print("Your number of rows do not align.  Please check your code.")

## Deprecated: added to matrix class
def interval_matrix_sum(X,Y):
    warnings.warn("Warning: imac0.interval_matrix_sum deprecated. Use class IntervalMatrix sum instead.", DeprecationWarning)

    #First check that rows are same length, else error
    if len(X)==len(Y):
        #Then check that columns are same length, else error
        if len(X[0])==len(Y[0]):
            #If both are same length, then we generate a resulting matrix.
            v=len(X)
            #initialize resulting matrix as empty
            result=[[ P.empty() for i in range(v) ] for j in range(v)]
            #Then perform the corresponding "multiplication" for each entry
            for i in range(v): #index of row
                for j in range(v): #index of column
                    result[i][j] = X[i][j] | Y[i][j]
            return result
        else:
            print("Your number of columns do not align.  Please check your code.")
    else:
        print("Your number of rows do not align.  Please check your code.")

## deprecated: Added to class IntervalMatrix
#This de-trivializes the matrix, so walks like a -> a don't exist
def remove_diagonal(A):
    temp = A
    for i in range(0, len(A)):
        temp[i][i] = P.open(P.inf,-P.inf)
    return temp

#soapConverter Deprecated -- Use soap_converter in file_parser.py
#soapConverter function originally created by Robert Cardona and Brittany Story
#edited to convert to matrix TVG data
def soapConverter(contactsheet):
    warnings.warn("Warning: imac0.soapConverter deprecated. Use file_parser.soap_converter", DeprecationWarning)
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

    #print final matrix
    #for i in range(node_counter):
    #    print(Final[i])

    #return the matrix so we can do stuff with it
    return Final

# Deprecated, use in class
def matrix_k_walk(A, k):
    warnings.warn("Warning: imac0.matrix_k_walk deprecated. Use class IntervalMatrix multiplication instead.", DeprecationWarning)

    temp = A
    for x in range(k-1):
        temp = interval_matrix_mult(temp,A)
    return temp

#   Deprecated, use in class
def matrix_nontrivial_k_walk(A, k):
    warnings.warn("Warning: imac0.matrix_nontrivial_k_walk deprecated. Use class IntervalMatrix multiplication instead.", DeprecationWarning)

    temp = remove_diagonal(A)
    return matrix_k_walk(temp,k)

#   Deprecated
def nontrivial_A_star_r(A, r):
    warnings.warn("Warning: imac0.nontrivial_A_star_r deprecated.", DeprecationWarning)
    return A_star_r(remove_diagonal(A), r)

#   Deprecated; use in class
def nontrivial_A_star(A):
    warnings.warn("Warning: imac0.nontrivial_A_star deprecated.", DeprecationWarning)
    return A_star(remove_diagonal(A))

## Deprecated; use in class
#Compute A* to a specific refinement r
def A_star_r(A, r):
    warnings.warn("Warning: imac0.A_star_r deprecated.", DeprecationWarning)

    temp = A
    curr_walk = A
    for x in range(2, r+1):
        curr_walk = interval_matrix_mult(A,curr_walk)
        temp = interval_matrix_sum(temp, curr_walk)
        #Add matrix_k_walk(A,x) to temp
    return temp

## Deprecated; use in class
def A_star(A):
    warnings.warn("Warning: imac0.A_star deprecated.", DeprecationWarning)
    k = 1
    temp = A
    prev = []
    curr_walk = A
    while(temp != prev):
        k += 1
        curr_walk = interval_matrix_mult(A, curr_walk)
        prev = temp
        temp = interval_matrix_sum(temp,curr_walk)
    return temp

##Unnecessary: This is get element on A^n
#Returns the intervals of possible k-walks from i to j
def interval_sequence(A,i,j,n):
    temp = A
    ret = []
    ret.append(A[i][j])
    for x in range(n-1):
        temp = interval_matrix_mult(temp,A)
        ret.append(temp[i][j])
    return ret

# This was written to capture some visualizations on individual connections between two nodes. It needs a minor update to work with the IntervalMatrix class
def connection_barcode(M,i,j,n):
    # M is matrix
    # i, j are the nodes you are analyzing
    # n is how far you want to compute k-walks... 1-walk, 2-walk ... n-walk.

    #First grab the k-walks
    interval = interval_sequence(M,i,j,n)
    int_min = 0
    int_max = 10

    #Grab Max and Min so infinity doesn't cause ruin
    for k in range(0,n-1):
        data = P.to_data(interval[k])
        for pt in data:
            if(pt[1] < int_min and pt[1] != -float('inf')):
                int_min = pt[1]
            if(pt[2] > int_max and pt[2] != float('inf')):
                int_max = pt[2]

    for k in range(0,n-1):
        data = P.to_data(interval[k])
        for pt in data:
            x_vals, y_vals = [], []
            #We want to graph the interval between these two points
            #pt[0] and pt[3] are False or True, to denote closed and open intervals
            x_vals.append(max(pt[1],int_min))
            x_vals.append(min(pt[2],int_max))
            #y is just whatever k-walk we're on, so we just keep going with that
            y_vals.append(k)
            y_vals.append(k)
            plt.plot(x_vals,y_vals,"b-", linewidth=3)
    plt.ylabel("k")
    plt.axis([0, int_max, -.5, n])
    plt.show()

#Using a matrix as a linear transformation on a vector
def transformation(A, v):
    #Linear Transformation
    if len(A) == len(v):
        ret = []
        for i, entry in enumerate(A):
            temp = P.empty()
            for j, jentry in enumerate(A[i]):
                temp = temp | (jentry & v[j])
            ret.append(temp)
        return ret
    else:
        print("Error! Matrix and vector have different dimensions")

def snapshot(A, t):
    #Grabs a snapshot of A, effectively a thick slice of A x R along the t-axis
    #Grab yourself a time sandwich
    return interval_matrix_mult(A, create_tI(len(A),t))

    return 0

# Obsolete
def create_tI(dim, t):
    ret = [[] for x in range(dim)]
    for i, idx in enumerate(ret):
        ret[i] = [P.empty() for x in range(dim)]
        ret[i][i] = t
    return IntervalMatrix(dim, dim, ret) 

    #Use this to refactor remove_diagonal, and for snapshot

#Graphics function -- can rewrite if we need it
def connection_barcode_3d_at_slice(A, t):
    connection_barcode_3d(snapshot(A, t), 1)

#Updated to work with interval class
def connection_barcode_3d_inline(M):
    #Demo version
    #Take a matrix M and output a 3D contact graph
    max_i = len(M.matrix)
    max_j = len(M.matrix[0])
    fig = plt.figure()
    ax = plt.axes(projection='3d')

    #create empty square matrix
    full_contacts = []
    temp = M.matrix
    full_contacts.append(M.matrix)

    int_min = 0
    int_max = 10


    #This snippet finds the lower and upper bounds of our plotbox
    for i in range(max_i):
        for j in range(i, max_j):
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
        for j in range(i, max_j):
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
    ax.set_title('TVG Matrix')
    plt.xticks(np.arange(0,max_i, 1.0))
    plt.yticks(np.arange(0,max_j, 1.0))
    #ax1.set_xticklabels(tick_labels.astype(int))
    #ax1.set_yticklabels(tick_labels.astype(int))

    plt.show()
    plt.close()
    return 0

#Graphics function -- updated
def connection_barcode_3d(M,n):
    #Take a matrix M and output a 3D contact graph for each k-walk, k <= n
    max_i = len(M.matrix)
    max_j = len(M.matrix[0])
    fig = plt.figure()
    ax = plt.axes(projection='3d')

    #create empty square matrix
    full_contacts = [[0] for x in range(n)]
    for i in range(n):
        full_contacts[i] = np.zeros((max_i,max_j))
    #refactor this as full_contacts[k][i][j]

    temp = M.matrix
    full_contacts[0] = M.matrix
    for i in range(1, n):
        temp = interval_matrix_mult(temp, M.matrix)
        full_contacts[i] = temp
    #Expecting: full_contacts[k] = the interval matrix for k-walks

    foo_count = 0
    for k in range(0, n):
        int_min = 0
        int_max = 10

        #This snippet finds the lower and upper bounds of our plotbox
        for i in range(max_i):
            for j in range(i, max_j):
                for pt in P.to_data(full_contacts[k][i][j]):
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
            for j in range(i, max_j):
                for pt in P.to_data(full_contacts[k][i][j]):
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
                    else:
                        foo_count += 1
                width = depth = .5
        fig = plt.figure(figsize=(8,8))
        ax1 = fig.add_subplot(111, projection='3d')
        ax1.bar3d(x_vals, y_vals, z_bottoms, width, depth, z_tops)#, shade=True)
        ax1.set_title('K = ' + str(k+1))
        plt.xticks(np.arange(0,max_i, 1.0))
        plt.yticks(np.arange(0,max_j, 1.0))
        #ax1.set_xticklabels(tick_labels.astype(int))
        #ax1.set_yticklabels(tick_labels.astype(int))

        #plt.show()
        #plt.savefig(str(k+1) + " Walks.png")
        plt.savefig("Changing Time Slice")
        plt.close()
        foo_count = 0
    return 0

#Graphics function -- updated
def connection_barcode_3d_with_paths(M,n, path):
    #Take a matrix M and output a 3D contact graph for each k-walk, k <= n
    max_i = len(M.matrix)
    max_j = len(M.matrix[0])
    fig = plt.figure()
    ax = plt.axes(projection='3d')

    #create empty square matrix
    full_contacts = [[0] for x in range(n)]
    for i in range(n):
        full_contacts[i] = np.zeros((max_i,max_j))
    #refactor this as full_contacts[k][i][j]

    temp = M.matrix
    full_contacts[0] = M.matrix
    for i in range(1, n):
        temp = interval_matrix_mult(temp, M.matrix)
        full_contacts[i] = temp
    #Expecting: full_contacts[k] = the interval matrix for k-walks

    foo_count = 0
    for k in range(0, n):
        int_min = 0
        int_max = 10

        #This snippet finds the lower and upper bounds of our plotbox
        for i in range(max_i):
            for j in range(i, max_j):
                for pt in P.to_data(full_contacts[k][i][j]):
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
            for j in range(i, max_j):
                for pt in P.to_data(full_contacts[k][i][j]):
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
                    else:
                        foo_count += 1
                width = depth = .5
        fig = plt.figure(figsize=(8,8))
        ax1 = fig.add_subplot(111, projection='3d')
        ax1.bar3d(x_vals, y_vals, z_bottoms, width, depth, z_tops)#, shade=True)
        ax1.set_title('K = ' + str(k+1))
        plt.xticks(np.arange(0,max_i, 1.0))
        plt.yticks(np.arange(0,max_j, 1.0))
        #ax1.set_xticklabels(tick_labels.astype(int))
        #ax1.set_yticklabels(tick_labels.astype(int))

        #plt.show()
        plt.savefig(str(path) + str(k+1) + " Walks.png")
        plt.close()
        foo_count = 0
    return 0

def get_length(intervals, min, max):
    length = 0

    intervals = list(intervals)
    for interval in intervals:
        upper = np.minimum(interval.upper, max)
        lower = np.maximum(min, interval.lower)
        length += upper - lower
    return length


def test_matrix_of_k_walk_distances():
    A = remove_diagonal(soapConverter(sys.argv[1]))
    scope = 5
    all_k_walks = []
    all_k_walks.append(A)
    for i in range(scope):
        all_k_walks.append(matrix_k_walk(A, i+2))
    distance_matrix = [[0]*len(all_k_walks) for i in range(len(all_k_walks))]
    labels = range(1, scope+2)

    for idi, i in enumerate(distance_matrix):
        for idj, j in enumerate(distance_matrix[idi]):
            distance_matrix[idi][idj] = round(matrix_TVG_distance(all_k_walks[idi],all_k_walks[idj],l_1,h_distance),3)
    print(pd.DataFrame(distance_matrix,index=labels,columns=labels))

def compare_all_7_walks(folder):
    #Compare all TVG's in a simulation folder parameter
    fs = []
    for root, dirs, files in os.walk(folder):
        for file in sorted(files):
            if file.endswith(".csv"):
                f = os.path.join(root,file)
                fs.append(remove_diagonal(soapConverter(os.path.join(root,file))))

    distance_matrix = [[0]*len(fs) for i in range(len(fs))]
    for idi, i in enumerate(fs):
        for idj, j in enumerate(fs):
            #print(fs[idi])
            distance_matrix[idi][idj] = matrix_TVG_distance(fs[idi],fs[idj],l_infinity,h_distance)
    print(DataFrame(distance_matrix))


    #print(files)

def csvs_in_folder(folder):
    #return list of .csv files, relative to top path of code (eg: ./outputs/moongnd-8)
    ret = []
    for root, dirs, files in os.walk(folder):
        for file in sorted(files):
            if file.endswith(".csv"):
                ret.append(str(root) + str(file))
    return ret


#This has been updated to work with the new class
def cb3d(M, title, path):

    #Demo version
    #Take a matrix M and output a 3D contact graph, saved to file "text.png"
    max_i = len(M.matrix)
    max_j = len(M.matrix[0])
    fig = plt.figure(figsize=(8,5))
    ax = plt.axes(projection='3d')

    #create empty square matrix
    full_contacts = []
    temp = M.matrix
    full_contacts.append(M.matrix)

    int_min = 0
    int_max = 10

    #This snippet finds the lower and upper bounds of our plotbox
    for i in range(max_i):
        for j in range(i, max_j):
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
        for j in range(i, max_j):
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
    ax.set_title(title)
    plt.xticks(np.arange(0,max_i, 1.0))
    plt.yticks(np.arange(0,max_j, 1.0))
    #ax1.set_xticklabels(tick_labels.astype(int))
    #ax1.set_yticklabels(tick_labels.astype(int))
    plt.savefig(str(path) + ".png")

    plt.close()
    return 0



if __name__ == "__main__":


    A = fp.soap_converter('./outputs/moongnd-8/starlink_15_sats_0 Contact Analysis.csv')
    #print(len(A))

    B = soapConverter('./outputs/moongnd-8/starlink_15_sats_0 Contact Analysis.csv')
    print(len(B))
    #cb3d(A, "Demo", "hm")
    #So we don't have an empty if block for testing
    #asdf = 1
    #file = './outputs/moongnd-8/moongnd_0 Contact Analysis.csv'
    #print(A)
    #print(matrix_k_walk(A,0))
    #connection_barcode_3d_inline()

    #h_distance_unit_test()
    #B = matrix_k_walk(A,2)
    #x = 3
    #y = 6
    # B = P.open(1,5)|P.open(7,10)|P.open(12,15)|P.open(17,20)
    #C = P.open(3,6)|P.open(8,10)|P.open(100,140)
    #get_length(B, 0, 100)
    #get_length(P.open(-P.inf,P.inf),5, 100)
    #print("B: " + str(C))
    #print("A: " + str(B))

    #exit()

    #print(P.to_data(B))
    #print(get_midpoint(P.to_data(B)[0]))

    # The matrix N
    #  R              (.8,2)          (0,1)U(2,4)
    #  (.8,2)         R               (0,1)U(3,4)
    #  (0,1)U(2,4)    (0,1)U(3,4)     R
    #
    # getting the interval sequence for N should result in (.8,2), then (0,2) repeating
    #N = [[P.open(-P.inf,P.inf),P.open(.8,2)|P.open(10,12),P.open(0,1)|P.open(2,4)], [P.open(.8,2)|P.open(10,12),P.open(-P.inf,P.inf),P.open(0,1)|P.open(3,4)], [P.open(0,1)|P.open(2,4),P.open(0,1)|P.open(3,4),P.open(-P.inf,P.inf)]]
    #A = N


    #print(A[0][1])
    #make_interval_periodic(A[0][1], 2)
    #print(get_max_matrix_endpoint(A))
    #print(make_matrix_periodic(A))

    #M = [[P.open(-P.inf,P.inf),P.open(.8,2)|P.open(10,12),P.open(0,1)|P.open(2,5)], [P.open(.8,2)|P.open(10,12),P.open(-P.inf,P.inf),P.open(.5,1)|P.open(3,4)], [P.open(0,1)|P.open(2,4),P.open(0,1)|P.open(3,4),P.open(-P.inf,P.inf)]]
    #print(interval_matrix_mult(M, M))

    #N_2 = [[P.open(-P.inf,P.inf),P.open(.8,6)|P.open(10,12),P.open(0,1)|P.open(2,4)], [P.open(.8,2)|P.open(10,12),P.open(-P.inf,P.inf),P.open(0,1)|P.open(3,4)], [P.open(0,1)|P.open(2,4),P.open(0,1)|P.open(3,4),P.open(-P.inf,P.inf)]]


