import portion as P
import dionysus as d
from itertools import permutations
from matrix import *

import Interval_Matrix_Algebra_Calculator_v0 as imac
import numpy as np 
from scipy import stats
import math

# TODO : rewrite all of this to use the IntervalMatrix class

def tvg_to_diagram_matrix(A, start_time, end_time):
    """
    Takes in an interval matrix associated to a TVG and returns a matrix
        of dionysus diagrams. Each entry is a diagram consisting of the 
        intervals in the interval object.
    """
    m = len(A)
    diagram = []
    for i in range(m):
        diagram.append([])
        for j in range(m):
            # print("A({}, {}) =".format(i, j))
            intervals = list(A[i][j])
            diagram_ij = d.Diagram()
            for interval in intervals:
                lower = interval.lower
                upper = interval.upper

                # check if emptyset?
                if lower == P.inf and upper == -P.inf:
                    continue

                # check if interval is R
                if lower == -P.inf:
                    lower = start_time
                if upper == P.inf:
                    upper = end_time

                # print("\t[{}, {}]".format(lower, upper))
                diagram_ij.append(d.DiagramPoint(lower, upper))
            diagram[i].append(diagram_ij)
    return diagram

def tvg_to_complement_diagram_matrix(A, start_time, end_time, delta = 0.1):
    """
    Takes in an interval matrix associated to a TVG and returns a matrix
        of dionysus diagrams. Each entry is a diagram consisting of the 
        complement of the intervals in the interval object.
    """
    m = A.dim_row
    diagram = []
    for i in range(m):
        diagram.append([])
        for j in range(m):
            intervals = list(A.get_element(i, j))
            diagram_ij = d.Diagram()
            # print(intervals)
            intervals_c = []
            
            lower = start_time           
            for interval in intervals:
                
                # check if emptyset?
                if interval.lower == P.inf and interval.upper == -P.inf:
                    continue
                
                upper = interval.lower
                
                # check if interval is R
                if interval.lower == -P.inf:
                    upper = start_time
                
                # print(interval)
                intervals_c.append([lower, upper])
                # print("({}, {})".format(lower, upper))
        
                # manually remove singletons to avoid dionysus2 bug
                # if lower != upper:
                if upper - lower >= delta:
                    diagram_ij.append(d.DiagramPoint(lower, upper))

                    # if upper - lower < 0.5:
                    #     print(f"maybe bug still here : {upper - lower}")
                
                # if upper - lower >= 0.5:
                #     diagram_ij.append(d.DiagramPoint(lower, upper))
                
                lower = interval.upper
                if interval.upper == P.inf:
                    lower = end_time
                    
            intervals_c.append([lower, end_time])
            # print("complement : {}".format(intervals_c))
            
            # manually remove singletons to avoid dionysus2 bug
            # if lower != end_time:
            if end_time - lower >= delta:
                diagram_ij.append(d.DiagramPoint(lower, end_time))

                # if end_time - lower < 0.5:
                #     print(f"maybe bug still here : ({lower}, {end_time}) : {end_time - lower}")

            diagram[i].append(diagram_ij)
    return diagram

def tvg_interval_wasserstein_distance_matrix(diagram_a, diagram_b, m, q = 2):
    """
    Given two diagram matrices, return the matrix of wasserstein distances 
        computed entrywise.
    """
    wdist = []
    for i in range(m):
        wdist.append([])
        for j in range(m):
            diagram_aij = diagram_a[i][j]
            diagram_bij = diagram_b[i][j]
            # print(diagram_aij)
            # print(diagram_bij)
            
            wdist[i].append(d.wasserstein_distance(diagram_aij, diagram_bij, q=q))
            # print("2-Wasserstein distance between ({}, {})-intervals: {}".format(i, j, wdist[i][j]))

    return wdist

def tvg_interval_bottleneck_distance_matrix(diagram_a, diagram_b, m):
    """
    Given two diagram matrices, return the matrix of bottleneck distances
        computed entrywise.
    """
    bdist = []
    for i in range(m):
        bdist.append([])
        for j in range(m):
            diagram_aij = diagram_a[i][j]
            diagram_bij = diagram_b[i][j]
            # print(diagram_aij)
            # print(diagram_bij)
            
            bdist[i].append(d.bottleneck_distance(diagram_aij, diagram_bij))
            # print("Bottleneck distance between ({}, {})-intervals: {}".format(i, j, bdist[i][j]))
            
    return bdist

def sup_norm(distance_matrix):
    """
    Given a square matrix `distance_matrix` as a list of lists, return the 
        $\ell^\infty$-norm.
    """
    m = len(distance_matrix)
    
    supremum = float("-inf")
    for i in range(m):
        for j in range(m):
            entry = distance_matrix[i][j]
            supremum = max(supremum, entry)
    return supremum

def q_norm(distance_matrix, q):
    """
    Given a square matrix `distance matrix` as a list of lists, 
        return the $\ell^q$-norm, with `q` a float in [1, float("inf"))
    """
    
    m = len(distance_matrix)
    
    summation = 0
    for i in range(m):
        for j in range(m):
            entry = distance_matrix[i][j]
            summation += pow(entry, q)
    return pow(summation, 1/q)

def tvg_interval_wasserstein_distance_sym_matrix_permutation(diagram_a, diagram_b, permutation, m, q = 2):
    """
    Calculates wasserstein distance over a given permutations of labels.
    """
    wdist = []
    for i in range(m):
        wdist.append([])
        for j in range(m):
            diagram_aij = diagram_a[i][j]
            diagram_bij = diagram_b[permutation[i]][permutation[j]]
            # print(diagram_aij)
            # print(diagram_bij)

            wdist[i].append(d.wasserstein_distance(diagram_aij, diagram_bij, q=q))
            # print("Bottleneck distance between ({}, {})-intervals: {}".format(i, j, bdist[i][j]))
            
    return wdist

def tvg_interval_wasserstein_distance_sym_matrix(diagram_a, diagram_b, m, q = 2):
    wdist_sym_inf = float('inf')
    permutations_list = list(permutations(range(m)))[1:]
    for permutation in permutations_list:
        wdist_sym = tvg_interval_wasserstein_distance_sym_matrix_permutation(diagram_a, diagram_b, permutation, m, q=q)

        wdist_sym_sup = 0.0
        for i in range(m):
            for j in range(m):
                wdist_sym_sup = max(wdist_sym_sup, wdist_sym[i][j])
        wdist_sym_inf = min(wdist_sym_inf, wdist_sym_sup)
    return wdist_sym_inf


def tvg_interval_bottleneck_distance_sym_matrix_permutation(diagram_a, diagram_b, permutation, m):
    """
    Calculate bottleneck distance over a given permutations of labels.
    """
    bdist = []
    for i in range(m):
        bdist.append([])
        for j in range(m):
            diagram_aij = diagram_a[i][j]
            diagram_bij = diagram_b[permutation[i]][permutation[j]]
            # print(diagram_aij)
            # print(diagram_bij)

            bdist[i].append(d.bottleneck_distance(diagram_aij, diagram_bij))
            # print("Bottleneck distance between ({}, {})-intervals: {}".format(i, j, bdist[i][j]))
            
    return bdist 

def tvg_interval_bottleneck_distance_sym_matrix(diagram_a, diagram_b, m):
    bdist_sym_inf = float('inf')
    permutations_list = list(permutations(range(m)))[1:]
    for permutation in permutations_list:
        bdist_sym = tvg_interval_bottleneck_distance_sym_matrix_permutation(diagram_a, diagram_b, permutation, m)

        bdist_sym_sup = 0.0
        for i in range(m):
            for j in range(m):
                bdist_sym_sup = max(bdist_sym_sup, bdist_sym[i][j])

        bdist_sym_inf = min(bdist_sym_inf, bdist_sym_sup)
    return bdist_sym_inf


# TODO : Move this to the interval_distance_functions file
def get_length(intervals, min, max):
    length = 0

    intervals = list(intervals)
    for interval in intervals:
        if interval == P.empty():
            continue
        upper = np.minimum(interval.upper, max)
        lower = np.maximum(min, interval.lower)
        length += upper - lower
    return length

# def tvg_lifetime_matrix(A_walks, start_time, end_time, r):
#     A = A_walks[1]
#     n = len(A)
#     L = {}

#     # check r < len(A_walks)

#     for k in range(0, r):
#         # print("Calculating {}-star".format(k))

#         A_star = A_walks[0] # starting with identity matrix A^0
#         for i in range(1, k):
#             A_star = imac.interval_matrix_sum(A_star, A_walks[i])

#         for i in range(0, n):        
#             for j in range(i + 1, n):
#                 # print("\ti = {}, j = {}".format(i, j))
#                 entry = A_star[i][j]
#                 # print(entry)
#                 entry_length = get_length(entry, start_time, end_time)
#                 L[(k, i, j)] = entry_length
#                 # print(get_length(entry, start_time, end_time))
#     return L

def tvg_lifetime_matrix(walks, start_time, end_time, walk_length):

    n = walks[0].dim_row
    L = {}

    for k in range(0, walk_length):
        star_sum = walks[0] # starting with identity matrix A^0
        for i in range(1, k):
            star_sum = star_sum + walks[i]
        
        for i in range(n):
            for j in range(i + 1, n):
                L[(k, i, j)] = get_length(star_sum.get_element(i, j), start_time, end_time)
                
    return L

def generate_y_list(L, m, walk_length):
    y_list = []

    for i in range(0, m):
        for j in range(i + 1, m):
            y = []
            for k in range(0, walk_length):
                interval_sum = L[(k, i, j)]
                y.append(interval_sum)
            y_list.append(y)
    return y_list

def calculate_y_list_average(y_list, walk_length):
    y_list_average = []
    
    for k in range(0, walk_length):
        average_sum = 0
        for y in y_list:
            average_sum += y[k]
        average = average_sum / len(y_list)
        y_list_average.append(average)

    return y_list_average

# source : https://pythonguides.com/scipy-confidence-interval/
def confidence_interval(data, confidence=0.95):
    data = np.array(data)
    length = len(data)
    mean, std_error = np.mean(data), stats.sem(data)
    h = std_error * stats.t.ppf((1 + confidence) / 2.0, length - 1)
    return mean, mean - h, mean + h

def error_bars(data):
    data = np.array(data)
    length = len(data)
    mean, std = np.mean(data), np.std(data)
    error = 2 * std / math.sqrt(length)
    return mean, mean - error, mean + error