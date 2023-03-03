import Interval_Matrix_Algebra_Calculator_v1 as imac
import Interval_Matrix_Algebra_Calculator_v0 as imac0
import imageio.v3 as iio
import imageio.v2 as iio2
from pathlib import Path
import contact_analysis as ca
import networkx as nx
# Portion used to work with interval arithmetic of subsets of Real numbers
import portion as P
# Sys used to call for system inputs
import sys

import matplotlib.pyplot as plt
import numpy as np
import interval_distance_functions as idf
import report_parser as rp
from mpl_toolkits import mplot3d
from graph_tool.all import *
# Used to draw k-walk graphs    
import os
import pandas as pd

import time


# Our data structure is a matrix of arrays of products in L(R) X R+
# Of the form (I, t), where I is the interval in which a communication can be sent, and t is the time it takes to get to the next node


#DATAFRAMES ARE A[COLUMN][ROW] LIKE AWFUL PEOPLE
def multiply_with_propagation(X, Y):
    #print(Y)
    if len(X.columns) == len(Y.index):
        ret = pd.DataFrame(index=X.index, columns=X.columns, dtype='object')
        for i in X.index:
            for j in Y.columns:
                ret[j][i] = []
                for k in X.columns:
                    for a in X[k][i]:
                        for b in Y[j][k]:
                            if a[1] != P.inf and b[1] != P.inf:
                                Q = imac.shift_interval(a[0], a[1])
                                #W is whatever you need to do to interval B
                                W = imac.shift_interval(b[0] & imac.shift_interval(b[0],b[1]),-b[1])
                                check = [imac.shift_interval(Q & W, -a[1]), a[1]+b[1]]
                                if check[0] != P.empty() and check not in ret[j][i]:
                                    #print(check)
                                    ret[j][i].append(check)
        return ret


def mult_prop_with_distance_sheet(X, Y, sheet):
    time = 0
    if len(X.columns) == len(Y.columns) and len(X.index) == len(Y.index):
        ret = pd.DataFrame(index=X.index, columns=X.columns, dtype='object')
        v = len(X.columns)
        for i in X.columns:
            for j in X.columns:
                ret[i][j] = [] 
                for k in X.columns:
                    for a in X[i][k]:
                        for b in Y[k][j]:
                            time = time + 1
                            #if a[1] != P.inf and b[1] != P.inf:
                                #naive approach: shift_interval(I & shift_interval(I, t),-t)
                                #there may be something wrong with the logic here

                                #Q is whatever you need to do to interval A
                            #    Q = imac.shift_interval(a[0], a[1])
                                #W is whatever you need to do to interval B
                            #    W = imac.shift_interval(b[0] & imac.shift_interval(b[0],b[1]),-b[1])
                            #    check = [imac.shift_interval(Q & W, -a[1]), a[1]+b[1]]

                                #check = [imac.shift_interval(imac.shift_interval(a[0], a[1]+b[1]) & b[0],-(a[1]+b[1])), a[1]+b[1]]
                            #    if check[0] != P.empty():
                            #        ret[i][j].append(check)
                                #ret[i][j].append([a[0] & b[0], a[1] + b[1]])
        print(len(X.columns))
        print(len(Y.columns))
        print(time)
        return ret
    else:
        print("Your number of columns do not align. Please check your code")

def build_prop_delay_matrix(A, sheet, ts):
    B = pd.DataFrame.copy(A)

    for i in B:
        for j in B:
            B[i][j] = []
    for i in A.columns:
        for j in A.columns:
            if i != j:
                intervals = P.to_data(A[i][j])
                #Iterate over each interval between i and j
                if not intervals:
                    B[i][j].append([P.empty(), P.inf])
                else:
                    for interval in intervals:
                        #Step over the dictionary
                        for key in sheet:
                            window = P.open(key, key + ts)
                            the_intersection = window & P.from_data([interval])
                            if the_intersection != P.empty():
                                distance_key = i + " - " + j
                                if distance_key not in sheet[key].keys():
                                    distance_key = j + " - " + i
                                new_int = [P.from_data([interval]),sheet[key][distance_key]/299792.458]
                                B[i][j].append(new_int)
            else:
                B[i][j].append([P.open(-P.inf,P.inf), 0])
        #print(a)
        #print(A[a])
    #print(B)
    #print(sheet.keys())
    #print(sheet[0].keys())
    return B

def build_low_fidelity_delay_matrix(A, sheet):
    B = pd.DataFrame.copy(A)
    for i in B:
        for j in B:
            B[i][j] = [[A[i][j],round(imac.km_to_time_to_travel(imac.get_average_km_between_nodes(i,j,sheet)),1)]]
    return B

def forget_times(X):
    #Forgetful functor sending M(L(R) X R+) -> M(L(R))
    ret = pd.DataFrame(index=X.index, columns=X.columns, dtype='object')
    for i in X.index:
        for j in X.columns:
            ret[j][i] = P.empty()
            for k in X[j][i]:
                ret[j][i] = ret[j][i] | k[0]
    return ret

def deep_copy_pd_dataframe(A):
    #Because haters gonna hate
    #Also everything's an object now

    ret = pd.DataFrame(index=A.index, columns=A.columns, dtype='object')
    for row in A.index:
        for col in A.columns:
            ret[col][row] = A[col][row]
    return ret

def rebase_ping(A, ping):
    ret = pd.DataFrame(index = A.index, columns=A.columns, dtype='object')
    #Takes a ping, gets the times that it hits new nodes, then 
    column_sums = {}

    #Gather the things to combine for each entry of the new column
    for col in ping.columns:
        column_sums[col] = []
        for row in ping.index:
            column_sums[col].append(ping[row][col])
    for row in ret.index:
        for col in ret.columns:
            ret[row][col] = []
            for k in column_sums[col]:
                
                for idx, x in enumerate(A[row][col]):
                    if len(k) != 0:
                        for individual_ping in k:
                            interval_to_append = A[row][col][idx][0] & individual_ping[0]
                            delay_to_append = A[row][col][idx][1]
                            combo_to_append = [interval_to_append,delay_to_append]
                            if combo_to_append not in ret[row][col]:
                                ret[row][col].append(combo_to_append)
    return ret

def refactor_rebase_ping(A, ping):
    ret = pd.DataFrame(index = A.index, columns=A.columns, dtype='object')
    #Takes a ping, gets the times that it hits new nodes, then 
    column_sums = {}

    #Gather the things to combine for each entry of the new column
    for col in ping.columns:
        column_sums[col] = []
        for row in ping.index:
            if len(ping[row][col]) != 0:
                for item in ping[row][col]:
                    if item not in column_sums[col]:
                        column_sums[col].append(item)
    for row in ret.index:
        for col in ret.columns:
            ret[row][col] = column_sums[col]
    return ret

def transmission_times(A, size, rate):
    #size is the packet size
    #Rate is the transmission rate; assumed constant for v.0
    ret = pd.DataFrame(index=A.index, columns=A.columns, dtype="object")
    for col in A.columns:
        for ind in A.index:
            ret[col][ind] = []
            for entry in A[col][ind]:
                if entry[0] != P.empty():
                    data = P.to_data(entry[0])
                    # The amount of time actually available will be the size of the interval
                    # But it needs to take place in a sub-interval the size of the propagation delay
                    # So thus this equation for time
                    time = (data[0][2] - data[0][1]) - entry[1]
                    if time * rate >= size:
                        ret[col][ind].append(entry)
                    else:
                        #Then that interval can't work, so empty it out
                        ret[col][ind].append(P.empty())
                else:
                    ret[col][ind].append(P.empty())
    return ret

def push_forward(A):
    ret = deep_copy_pd_dataframe(A)
    for row in A.index:
        for col in A.columns:
            ret[col][row] = []
            for idx, x, in enumerate(A[col][row]):
                dat = P.to_data(A[col][row][idx][0])
                ret_dat = []
                for idy, y in enumerate(dat):
                    time = A[col][row][idx][1]
                    ret_dat.append(P.open(dat[idy][1]+time,dat[idy][2]+time))
                ret[col][row].append(ret_dat)
    return ret

def propagation_test_one():
    oi = [P.open(-P.inf,P.inf), 0]
    ab = [P.open(0,10), 1]
    ac = [P.open(0,10), 3]
    #bc = [P.open(1,4)|P.open(14,16), 2]
    bc = [P.empty(), P.inf]
    ad = [P.empty(), P.inf]
    bd = [P.open(9,15), 3]
    cd = [P.open(9,10), 2]


    C = [[[oi], [ab], [ac], [ad]],
        [[ab], [oi], [bc], [bd]],
        [[ac], [bc], [oi], [cd]],
        [[ad], [bd], [cd], [oi]]]
    C = pd.DataFrame(C, index=["A",'B','C','D'], columns=["A",'B','C','D'])
    B = imac.remove_diagonal(B)


    print("X 'sees' Y, along with delay times")
    print(B)
    C = multiply_with_propagation(B, B)
    D = multiply_with_propagation(C, B)
    E = multiply_with_propagation(D, B)
    v = [P.singleton(1), P.singleton(2), P.singleton(3)]
    vB = vector_matrix_multiplication(v, B)
    vC = vector_matrix_multiplication(v, C)
    vD = vector_matrix_multiplication(v, D)
    vE = vector_matrix_multiplication(v, E)

    print("2-walks")
    print(C)
    print("3-walks")
    print(D)
    print("4-walks")
    print(E)
    #print(forget_times(C))

    B = forget_times(B)
    C = forget_times(C)
    D = forget_times(D)
    E = forget_times(E)



    imac.cb3d(B, title="Initial Matrix", path="1", labels=True, upper_triangular=False)
    imac.cb3d(C, title="2-walk Matrix", path="2", labels=True, upper_triangular=False)
    imac.cb3d(D, title="3-walk Matrix", path="3", labels=True, upper_triangular=False)
    imac.cb3d(E, title="4-walk Matrix", path="4", labels=True, upper_triangular=False)
    

def propagation_test_two():
    time_step = 3600
    file = './outputs/sim-2022-10-07/emm_0 Contact Analysis.csv'
    distance_file = './outputs/sim-2022-10-07/emm_0 Distances.csv'

    A = imac.soapConverter(file)
    distances = rp.distances_report_parser(distance_file)
    #print(A)
    B = build_prop_delay_matrix(A, distances, time_step)


    #def propagate_interval_time_delay(I, t):
    #return shift_interval(I & shift_interval(I, t),-t)

    imac.cb3d(forget_times(B))
    #imac.cb3d(B, title="Initial Matrix", path="1", labels=True, upper_triangular=False)

    #C = multiply_with_propagation(B, B)
    #D = multiply_with_propagation(C, B)
    #E = multiply_with_propagation(D, B)

    #imac.cb3d(C, title="2-walk Matrix", path="2", labels=True, upper_triangular=False)
    #imac.cb3d(D, title="3-walk Matrix", path="3", labels=True, upper_triangular=False)
    #imac.cb3d(E, title="4-walk Matrix", path="4", labels=True, upper_triangular=False)

def propagation_test_three():
    #ERRORS FOUND, NO LONGER WORKS BECAUSE FIXED ELSEWHERE

    time_step = 3600
    file = './outputs/sim-2022-10-07/emm_0 Contact Analysis.csv'
    distance_file = './outputs/sim-2022-10-07/emm_0 Distances.csv'

    init = imac.remove_diagonal(imac.soapConverter(file))

    distances = rp.distances_report_parser(distance_file)
    
    A = build_low_fidelity_delay_matrix(init, distances)
    print("Matrix A: ")
    print(A)
    print("\n\n")
    ping = pd.DataFrame(index=A.index, columns=A.columns, dtype='object')
    for row in A.index:
        for column in A.columns:
            ping[row][column] = []
            if "Sydney" in row:
                print(column)
                for idx, x in enumerate(A[row][column]):
                    ping[row][column].append([A[row][column][idx][0] & P.open(300,350), A[row][column][idx][1]])
            else:
                ping[row][column].append([P.empty(),P.inf])
    ping = ping.T

    B = multiply_with_propagation(ping, A)
    #print("Ping:")
    #print(ping)
    #print("B")
    #print(B)

    B_ping = rebase_ping(A, B)


    C = multiply_with_propagation(B_ping, A)

    C_ping = rebase_ping(A, C)

    D = multiply_with_propagation(C_ping, A)


    B = push_forward(B)
    C = push_forward(C)
    D = push_forward(D)

    B = forget_times(B)
    C = forget_times(C)
    D = forget_times(D)






    imac.cb3d(B, title="1-walk: B", path="1", labels=True, upper_triangular=False)
    imac.cb3d(C, title="2-walk: C", path="2", labels=True, upper_triangular=False)
    imac.cb3d(D, title="3-walk: D", path="3", labels=True, upper_triangular=False)

    cb([B,C,D], "title", "path")

def propagation_test_four():
    time_step = 3600
    file = './outputs/sim-2022-10-07/emm_0 Contact Analysis.csv'
    distance_file = './outputs/sim-2022-10-07/emm_0 Distances.csv'
    init = imac.remove_diagonal(imac.soapConverter(file))
    distances = rp.distances_report_parser(distance_file)
    home_base = "Ground:Sydney"

    A = build_low_fidelity_delay_matrix(init, distances)

    ping = pd.DataFrame(index=[home_base], columns=A.columns, dtype='object')

    for column in ping.columns:
        ping[column][home_base] = []
        if column == home_base:
            ping[column][home_base].append([P.open(300,350), 0])
        else:
            to_append = [P.empty(),P.inf]
            ping[column][home_base].append(to_append)



    k_propagations = []

    for i in range(8):
        time_start = time.time()
        if i == 0:
            to_append = multiply_with_propagation(ping, A)
            k_propagations.append(to_append)
        else:
            to_append = multiply_with_propagation(k_propagations[i-1], A)
            k_propagations.append(to_append)
        time_stop = time.time()
        #print(str(i+1) + "-walk ping calculated in: " + str(time_stop - time_start))
        #print(k_propagations[i])
        print(k_propagations[i])


    for i, entry in enumerate(k_propagations):
        k_propagations[i] = forget_times(push_forward(k_propagations[i]))
        print(k_propagations[i])

    cb(k_propagations, "Ping with Propagation Delay", "output")

def pandas_test():
    B = pd.DataFrame(index=['1','2','3'], columns=['4','5','6'], dtype='object')
    for row in B.index:
        for column in B.columns:
            print(row + " " + column)
            if "1" in row:
                print(column)
    print(B)


def cb(A, title, path):
    fig, ax = plt.subplots()
    #A is a list of walk matrices.
    full_contacts = []
    for M in A:
        full_contacts.append(M.loc["Ground:Sydney",:])
        #full_contacts.append(M.loc["Ground:Sydney",:])

    #This is where the plots go
    p = []
    fig, ax = plt.subplots()

    for i, walk in enumerate(full_contacts):
        print(walk)
        x_vals = []
        height_vals = []
        width = 0.8
        bottom = []
        colors = []

        walk_number = i+1
        color = 'b'
        if i == 0:
            color = 'b'
        if i == 1:
            color = 'g'
        if i == 2:
            color = 'm'
        if i == 3:
            color = 'r'
        if i == 4:
            color = 'blueviolet'
        if i == 5:
            color = 'turquoise'
        if i == 6:
            color = 'crimson'
        if i == 7:
            color = 'bisque'

        for j, thing in walk.items():
            for pt in thing:
                val = P.to_data(pt)[0]
                x_vals.append(j)
                height_vals.append(val[2] - val[1])
                bottom.append(val[1])
                colors.append(color)
        p.append(ax.bar(x_vals,height_vals,width,bottom, label="k = " + str(i+1), zorder=len(A)-i))
            #1-walks
    plt.xticks(rotation = 315)
    #plt.margins(x=500)
    plt.legend(title="Minimum Walk", bbox_to_anchor=(1.1, 1.05))
    plt.title(title)
    plt.show()
    plt.close()
    return 0


def propagation_test_with_file():
    file = './outputs/moongnd-8/moongnd_0 Contact Analysis.csv'
    B = imac.remove_diagonal(imac.soapConverter(file))

    print(B)
    for i in B.index:
        for k in B.columns:
            j = B[i][k]
            print(j)
            print(imac.shift_interval(j,3))
            print(imac.propagate_interval_time_delay(j, 3))

    imac.cb3d(B, title="TVG Matrix", path="default")
    imac.cb3d(imac.propagate_df_matrix_time_delay(B, 3), title="Delay propagation of 3 seconds", path="delay")
    imac.cb3d(imac.propagate_df_matrix_time_delay(B, 500), title="Uniform Delay of 500 seconds, Propagated 1-walk", path="1")

    print(B)
    for i in range(1,10):
        p = 500
        out = imac.matrix_k_walk(imac.remove_diagonal(B), i, prop=p)
        imac.cb3d(out, title="Uniform Delay of " + str(p) + " seconds, Propagated " + str(i+1) + " walk", path=str(i+1))

def test_deep_copy():
    oi = [P.open(-P.inf,P.inf), 0]
    ab = [P.open(0,10), 1]
    ac = [P.open(0,10), 3]
    #bc = [P.open(1,4)|P.open(14,16), 2]
    bc = [P.empty(), P.inf]
    ad = [P.empty(), P.inf]
    bd = [P.open(9,15), 3]
    cd = [P.open(9,10), 2]


    C = [[[oi], [ab], [ac], [ad]],
        [[ab], [oi], [bc], [bd]],
        [[ac], [bc], [oi], [cd]],
        [[ad], [bd], [cd], [oi]]]
    C = pd.DataFrame(C, index=["A",'B','C','D'], columns=["A",'B','C','D'])

    D = deep_copy_pd_dataframe(C)
    C['A']['B'] = 0
    print(C)
    print(D)

def from_csvs():
    B = pd.read_csv('B.csv')
    B_ping = pd.read_csv('B_ping.csv')
    C_ping = pd.read_csv('C_ping.csv')
    D_ping = pd.read_csv('D_ping.csv')
    E_ping = pd.read_csv('E_ping.csv')

    B_ping = forget_times(B_ping)
    C_ping = forget_times(C_ping)
    D_ping = forget_times(D_ping)
    E_ping = forget_times(E_ping)

    imac.cb3d(B_ping, title="Initial Matrix", path="1", labels=True, upper_triangular=False)
    imac.cb3d(C_ping, title="1-walk Ping", path="2", labels=True, upper_triangular=False)
    imac.cb3d(D_ping, title="2-walk Ping", path="3", labels=True, upper_triangular=False)
    imac.cb3d(E_ping, title="3-walk Ping", path="3", labels=True, upper_triangular=False)


if __name__ == "__main__":


    #from_csvs()
    propagation_test_four()
    #pandas_test()



    #test_deep_copy()
    #propagation_test_three()

    #imac.propagate_df_matrix_time_delay_with_timesheet(A, distances)
    #file = './outputs/moongnd-big/moongnd_0 Contact Analysis.csv'
    #distance_file = './outputs/moongnd-big/moongnd_0 Coordinates.csv'

    #propagation_test_one()

    #propagation_test_two()
    #propagation_test_with_file()

