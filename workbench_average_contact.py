from matrix import IntervalMatrix
import Interval_Matrix_Algebra_Calculator_v0 as imac
import portion as P
import interval_distance_functions as idf
import file_parser as fp
import zz_persistence as z
import dionysus as d
import matplotlib.pyplot as plt



def get_average_contact_matrix(mat):
    minimum = mat.get_min_endpoint(False)
    #print(minimum)
    maximum = mat.get_max_endpoint(False)
    #print(maximum)

    A = [[None for j in range(mat.dim_col)] for i in range(mat.dim_row)]
    for k in range(len(A)):
        for j in range(len(A[0])):
            A[k][j] = ((maximum - minimum) - idf.xor_distance(mat.get_element(k, j), P.open(minimum, maximum)))/(maximum-minimum)
    return A


def construct_weighted_simplex_from_matrix(matrix):
    """
    Given an (square) IntervalMatrix object, we construct the filtered 
        simplicial complex that Dionysus uses.
    """
    #logger.info("Running interval_matrix_to_graph")

    m = matrix.dim_row
    simplex = []
    times = []

    for i in range(m):
        simplex.append([i])
        times.append([0]) # all nodes born at time zero and exist througout

    for i in range(m):
        for j in range(i + 1, m):
            simplex.append([i, j])
            
            edge_times = []
            for interval in list(matrix.get_element(i, j)):
                edge_times.append(interval.lower) # max(start_time, interval.lower)
                edge_times.append(interval.upper) # min(end_time, interval.upper)
            times.append(edge_times)

    return {"simplex" : simplex, "times" : times}


def average_contact_filtration(A, t):
    # Takes a contact matrix A, and a constant t \in [0, 1]
    # Returns a sub-matrix A_t with nonzero entries at points where the average contact is >= t

    acm = get_average_contact_matrix(A)
    ret = IntervalMatrix(A.dim_row, A.dim_col)

    for i in range(A.dim_row):
        for j in range(A.dim_col):
            if acm[i][j] >= t:
                ret.set_element(i, j, A.get_element(i, j))
            else:
                ret.set_element(i, j, P.empty())
    return ret


def test_1():
    print("Test 1")
    M = IntervalMatrix(4, 4)
    for i in range(0,4):
        M.set_element(i, i, P.open(0, 25))
    filt = average_contact_filtration(M, .3)
    simp = construct_weighted_simplex_from_matrix(filt)
    zz, dgms, cells = z.calculate_zz_persistence(simp)
    print(M)
    print(zz)
    for i, k in enumerate(dgms):
        print("{}: {}".format(i, k))
    for i, k in enumerate(dgms):
        d.plot.plot_diagram(k, show=False)
    print("")


def test_2():
    print("Test 2")
    M = IntervalMatrix(4, 4)
    for i in range(0,4):
        M.set_element(i, i, P.open(0, 25))
    M.set_element(0,1, P.open(10, 15))
    filt = average_contact_filtration(M, .3)
    simp = construct_weighted_simplex_from_matrix(filt)
    zz, dgms, cells = z.calculate_zz_persistence(simp)
    print(M)
    print(zz)
    for i, k in enumerate(dgms):
        print("{}: {}".format(i, k))
    for i, k in enumerate(dgms):
        d.plot.plot_diagram(k, show=False)
    print("")

def test_3():
    print("Test 3")
    M = IntervalMatrix(4, 4)
    for i in range(0,4):
        M.set_element(i, i, P.open(0, 25))
    M.set_element(0, 1, P.open(0, 10))
    M.set_element(1, 0, P.open(0, 10))
    M.set_element(1, 2, P.open(0, 10))
    M.set_element(2, 1, P.open(0, 10))
    M.set_element(2, 3, P.open(0, 10))
    M.set_element(3, 2, P.open(0, 10))
    M.set_element(3, 0, P.open(0, 10))
    M.set_element(0, 3, P.open(0, 10))
    filt = average_contact_filtration(M, .3)
    simp = construct_weighted_simplex_from_matrix(filt)
    zz, dgms, cells = z.calculate_zz_persistence(simp)
    print(M)
    print(zz)
    for i, k in enumerate(dgms):
        print("{}: {}".format(i, k))
    for i, k in enumerate(dgms):
        d.plot.plot_diagram(k, show=False)
    print("")

def test_4():
    print("Test 4")
    M = IntervalMatrix(4, 4)
    for i in range(0,4):
        M.set_element(i, i, P.open(0, 25))
    M.set_element(0, 1, P.open(0, 10))
    M.set_element(1, 2, P.open(0, 10))
    M.set_element(2, 3, P.open(0, 10))
    M.set_element(0, 3, P.open(0, 10))
    filt = average_contact_filtration(M, .3)
    simp = construct_weighted_simplex_from_matrix(filt)
    zz, dgms, cells = z.calculate_zz_persistence(simp)
    print(M)
    print(zz)
    for i, k in enumerate(dgms):
        print("{}: {}".format(i, k))
    for i, k in enumerate(dgms):
        d.plot.plot_diagram(k, show=True)
    print("")


if __name__ == "__main__":

    M = IntervalMatrix(4, 4)
    for i in range(0,4):
        M.set_element(i, i, P.open(0, 25))
    '''M.set_element(0, 1, P.open(0,10))
    M.set_element(1, 0, P.open(0,10))
    M.set_element(1, 2, P.open(5, 15))
    M.set_element(2, 1, P.open(5, 15))
    M.set_element(2, 3, P.open(10, 20))
    M.set_element(3, 2, P.open(10, 20))
    M.set_element(3, 0, P.open(15, 25))
    M.set_element(0, 3, P.open(15, 25))
    print(M)'''

    test_1()
    test_2()
    test_3()
    test_4()

    '''
    matrix = IntervalMatrix(3, 3)
    #print(matrix)
