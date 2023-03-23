import portion as P
import numpy as np
import Interval_Matrix_Algebra_Calculator_v0 as imac
import interval_distance_functions as idf
import matplotlib.pyplot as plt
import contact_analysis as ca
import random
from matrix import IntervalMatrix
import itertools



def get_max_interval_endpoint(input_interval):
    ret = 0
    for interval in input_interval:
        dat = P.to_data(interval)[0][2]
        #if dat != float('inf'):
        ret = max(ret, dat)
    return ret

def get_max_matrix_endpoint(input_matrix):
    #Updated for new class
    #If both are same length, then we generate a resulting matrix.
    ret = 0
    for x in input_matrix.matrix:
        for y in x:
            ret = max(ret, get_max_interval_endpoint(y))
    return ret

def make_interval_periodic_union(input_interval, periodicity):
    dat = P.to_data(input_interval)
    ret = P.empty()
    for k in range(len(dat)):
        # Each interval is going to be one of three cases: 
        # Case 1: given (a, b), b-a >= periodicity. This implies that this interval actually covers the whole period
        if dat[k][2] - dat[k][1] >= periodicity:
            #Endpoints are True because our interval is really closed
            ret0 = True
            ret1 = 0
            ret2 = periodicity
            ret3 = False
            ret = ret.union(P.from_data([(ret0, ret1, ret2, ret3)]))
        else:
            max_mult = (dat[k][1] - (dat[k][1] % periodicity))/periodicity
            if dat[k][2] <= (max_mult + 1)*periodicity:
                # Case 2: k*period <= a < b <= (k+1)*period. This implies that the interval is simply contained in a single period, and you can easily modulate both endpoints
                ret0 = dat[k][0]
                ret1 = dat[k][1]%periodicity
                ret2 = dat[k][2]%periodicity
                if ret2 == 0:
                    ret2 = periodicity
                ret3 = dat[k][3]
                new_tuple = [(ret0, ret1, ret2, ret3)]
                new_interval = P.from_data(new_tuple)
                ret = ret.union(P.from_data(new_tuple))
            else:
                # Case 3: k*period < a < (k+1)*period <= b. This implies that the interval stretches over two periods. This one is a bit tricky
                #We break it up into two intervals and add them both
                ret = ret.union(P.from_data([(True,0, dat[k][2]%periodicity, dat[k][3])]))
                ret = ret.union(P.from_data([(dat[k][0], dat[k][1]%periodicity, periodicity, True)]))

    return ret

def window(t, k, left=False, right=False):
    #t is size of window, k how far shifted it is
    if left == False and right == False:
        return P.closed(0 + k*t, t + k*t)
    elif left == True and right == False:
        return P.openclosed(0 + k*t, t + k*t)
    elif left == False and right == True:
        return P.closedopen(0 + k*t, t + k*t)
    else:
        return P.open(0 + k*t, t + k*t)


def open_cover(I, epsilon):
    #Returns an open cover over a collection of intervals
    ret = P.empty()
    for interval in I:
        dat = P.to_data(interval)
        for k in dat:
            print(k)
            ret = ret.union(P.open(k[1]-epsilon, k[2]+epsilon))
    return ret

    # Sigh; this line breaks other code somehow when you chnage the endpoints to False
    #return I.apply(lambda x: (False , x.lower - epsilon, x.upper + epsilon, False))

def left_shift(interval, t):
    return interval.apply(lambda x: (x.left, x.lower - t, x.upper - t, x.right))

def right_shift(interval, t):
    return interval.apply(lambda x: (x.left, x.lower + t, x.upper + t, x.right))

def make_interval_periodic_intersection(input_interval, periodicity, image_max):

    #parameter max not implemented


    max_endpoint = get_max_interval_endpoint(input_interval)
    ret = P.from_data([(False,-P.inf,P.inf,False)])
    if periodicity > image_max:
        ret = ret.intersection(input_interval)

    #We will be looking at the kth window
    keep_k = 0
    for k in range(0, (int)(max_endpoint/periodicity)):
        w = window(periodicity, k)
        intersected_interval = input_interval.intersection(w)
        ret = ret.intersection(left_shift(intersected_interval,k*periodicity))
        keep_k = k
    
    #There is a right boundary condition we need to meet so we don't bleed too far over. This assumes then that the length of the period defines the upper bound
    # given (a, b), max_endpoint = b, but right_max is going to be whatever 

    right_max = periodicity*(keep_k + 1)

    #The window over the last little bit
    w = right_shift(window(max_endpoint-right_max, 0), right_max)

    #The last intersected bit will be whatever is captured by that smaller window
    #This will be unioned by an interval over whatever remains so its emptiness doesn't destroy the intersection

    last_intersected_bit = w.intersection(input_interval)

    remainder = right_shift(P.openclosed(right_max, right_max + periodicity - (max_endpoint - right_max)), max_endpoint - right_max)
    last_intersected_bit = left_shift(last_intersected_bit.union(remainder), right_max)

    #print("{} has length {}".format(last_intersected_bit, get_interval_length(last_intersected_bit)))

    #print(last_intersected_bit)
    #print(remainder)
    #print("The last intersected bit is {}".format(last_intersected_bit))
    ret = ret.intersection(last_intersected_bit)


    return ret

def make_matrix_periodic(input_matrix, periodicity):
    v = len(input_matrix.n)
    w = len(input_matrix.m)
    result = [[P.empty() for i in range(v) ] for j in range(w)]
    for x in range(v):
        for y in range(w):
            result[x][y] = make_interval_periodic_union(input_matrix[x][y], periodicity)
    return IntervalMatrix(v, w, result)

def make_periodic_extension_of_interval(input_interval, periodicity, to_time):
    ret = input_interval

    if to_time != float('inf'):
        range_max = int(to_time/periodicity) + 1
    else:
        return P.open(-P.inf,P.inf)

    for k in range(1, range_max):
        to_union = input_interval.apply(lambda x: (x.left, x.lower+k*periodicity, x.upper+k*periodicity, x.right)).intersection(P.closed(0,to_time))
        ret = ret.union(to_union)
    return ret

def make_periodic_expansion_of_matrix(input_matrix, periodicity, to_time):
    v = len(input_matrix)
    w = len(input_matrix[0])
    result = [[P.empty() for i in range(v) ] for j in range(w)]
    for x in range(v):
        for y in range(w):
            result[x][y] = make_periodic_extension_of_interval(input_matrix[x][y], periodicity, to_time)
    return result

def generate_boolean_support(number_of_intervals, left, right):
    return 0


def find_period_of_best_fit(interval, minimum, maximum):
    temp_int = interval
    temp_int_length = 0

    for period in range(minimum, maximum):
        maximum_for_length = get_max_interval_endpoint(interval)
        if temp_int_length == 0:
            temp_int = make_interval_periodic_intersection(interval, period, get_max_interval_endpoint(interval))
            temp_int_length = imac.get_length(temp_int, 0, maximum_for_length)
        else:
            temp_2 = make_interval_periodic_intersection(interval, period, get_max_interval_endpoint(interval))
            potential_new_length = imac.get_length(temp_int, 0, maximum_for_length)

def get_interval_length(A):
    ret = 0
    for a in A:
        b = P.to_data(a)
        for c in b:
            ret += c[2]-c[1]
    return ret

def get_periodic_extensions_over_range(I, p_min, p_max, interval_max, p_increment):
    full_range = np.linspace(p_min, p_max, (int)((p_max-p_min)/p_increment))
    ret = []
    #print(full_range)
    for q in full_range:
        p = q/p_increment
        ret.append(make_periodic_extension_of_interval(make_interval_periodic_intersection(I, p*p_increment, get_max_interval_endpoint(I)), p*p_increment, interval_max))
    return ret

def graph_periodic_intersection_over_various_periods(I, p_min, p_max, interval_max, p_increment, display_noise=False):


    # I contains the support of a boolean function
    # max is the end of the domain for I. It is the maximum value for which I records information.
    # p_min is the minimum period
    # p_increment is a float which indicates how to increase the period

    # Suppose so I = 0[------(a---------b)------(c----d)-----]interval_max

    # v2.0 should include phase shift


    fig = plt.figure()
    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2, sharex=ax1)
    ax1.set_title("The periodic support")
    ax2.set_title("The periodic extensions")
    plt.ylabel("Period")
    plt.xlabel("Support")
    #plt.xticks(range(0, interval_max+1))
    #plt.yticks(range(p_min, p_max+1))


    full_range = np.linspace(p_min, p_max, (int)((p_max-p_min)/p_increment))

    scatterx1 = []
    scattery1 = []
    scatterx2 = []
    scattery2 = []

    for q in full_range:
    #for p in range(p_min, (int)((p_max-p_min)/p_increment)):
        p = q/p_increment
        #print("p is {}".format(p))
        #print(p*p_increment)
        #print(p)
        processed_extension = make_interval_periodic_intersection(I, p*p_increment, get_max_interval_endpoint(I))
        #print(processed_extension)
        for k in processed_extension:
            #plt.axhline(y = p*p_increment, xmin=
            dat = P.to_data(k)
            for interval in dat:
                yval = p*p_increment
                xminval = round(interval[1],2)
                xmaxval = round(interval[2],2)
                if xminval == xmaxval:
                    #We're going to be plotting points so scatter!
                    scatterx1.append(xminval)
                    scattery1.append(yval)
                else:
                    ax1.hlines(y = yval, xmin = xminval, xmax = xmaxval)
                #ax1.scatter(scatterx, scattery, marker=',')#, s=(72/fig.dpi)**2)
        for k in make_periodic_extension_of_interval(processed_extension, p*p_increment, interval_max):
            dat = P.to_data(k)
            for interval in dat:
                yval = p*p_increment
                xminval = round(interval[1],2)
                xmaxval = round(interval[2],2)
                if xminval == xmaxval:
                    scatterx2.append(xminval)
                    scattery2.append(yval)
                else:
                    ax2.hlines(y = yval, xmin = xminval, xmax = xmaxval)
    #plt.axhline(y = .9, xmin = 0, xmax = 10)
    if display_noise == True:
        ax1.scatter(scatterx1, scattery1, marker=',', s=(72/fig.dpi)**2)
        ax2.scatter(scatterx2, scattery2, marker=',', s=(72/fig.dpi)**2)
    plt.show()

    return 0

def graph_extensions_with_distinguished_extensions(I, extensions, distinguished_extensions, p_min, p_max, interval_max, p_increment, display_noise=False):
    fig = plt.figure()
    ax1 = fig.add_subplot(2, 1, 1)
    ax1.set_title("periodic extension with distinguished extensions")
    plt.ylabel("Period")
    plt.xlabel("Support")

    return 0

def square_wave(frequency, time):
    #frequency gives the periodicity over (0,1)
    #time is the stopping point of the interval
    # Takes a frequency and builds a collection of intervals that represents a square wave out to a specified time
    ret = P.empty()

    for i in range(0, (int)(time*frequency)):
        ret = ret.union(right_shift(window((float)(1/(frequency*2)), 0), (float)(i/frequency)))
    return ret

def random_one_dimensional_data_cloud(number_of_points, maxval, sigdigs=0):
    ret = P.empty()
    for i in range(0, number_of_points):
        val = (float)(random.random()*maxval)
        if sigdigs != 0:
            val = round(val, sigdigs)
        ret = ret.union(P.singleton(val))
    #print(ret)
    return ret



def unit_test_make_interval_periodic():
    various_intervals = []
    various_intervals.append(P.open(0, 25) | P.open(50, 75))
    for k in range(1,10):
        various_intervals.append(P.open(0, 25) | P.open(50+k*20, 75+k*20))

    for interval in various_intervals:
        periods = []
        distances = []
        max_endpoint = get_max_interval_endpoint(interval)
        for period in range(10, max_endpoint, 1):
            periods.append(period)
            periodic_interval = make_interval_periodic_union(interval, period)
            periodic_expansion = make_periodic_extension_of_interval(periodic_interval, period, max_endpoint)
            distances.append(idf.xor_distance(interval,periodic_expansion))
        plt.bar(periods,distances)
        plt.title("L_1 Distance on the interval {}".format(interval))
        plt.xlabel("Induced Period")
        plt.ylabel("Distance from Original Interval")
        #plt.savefig("imgout/{}.png".format(interval, period), format="png")
        #plt.close()
        plt.show()

def unit_test_make_matrix_periodic():
    file = './outputs/moongnd-8/moongnd_0 Contact Analysis.csv'
    A = imac.soapConverter(file)


    #various_intervals.append(P.open(0,15) | P.open(23,27) | P.open(53,70) | P.open(77,88))
    #for k in range(5,10):
    #    various_intervals.append(P.open(0,15) | P.open(23+k*20,27+k*20) | P.open(53+k*30,70+k*30) | P.open(77+k*40,88+k*40))

    #various_intervals.append(P.open(0,10) | P.open(11,21) | P.open(32,42))
    #various_intervals.append(P.open(0,15) | P.open(23,27) | P.open(53,70) | P.open(77,88))

    # Boring various_intervals.append(P.singleton(3))
    max_endpoint = get_max_matrix_endpoint(A)
    if max_endpoint != float('inf'):
        max_endpoint = round(max_endpoint)

    periods = []
    distances = []
    for period in range(10, max_endpoint, 1):
        periods.append(period)
        periodic_matrix = make_matrix_periodic(A, period)
        periodic_expansion = make_periodic_expansion_of_matrix(periodic_matrix, period, max_endpoint)
        distances.append(idf.matrix_TVG_distance(A, periodic_expansion, idf.xor_distance, idf.l_2))

    plt.bar(periods,distances)
    plt.title("XOR Distance on the matrix")
    plt.xlabel("Induced Period")
    plt.ylabel("Distance from Original Matrix")
    plt.show()

def old_comments():
    #print(A[0][1])
    #print(make_interval_periodic_union(A[0][1], 2))
    #print(N)

    #for k in range(1,50):
    #    print(make_matrix_periodic(N,k))

    #for k in range(1, 5):
    #    B = make_matrix_periodic(A, k)
    #    C = make_periodic_expansion_of_matrix(B, k, 14.5)
    #    print("C = " + str(C))

    #print(A[0][1])
    #print(make_interval_periodic_union(A[0][1], 2))
    #print(N)

    #for k in range(1,50):
    #    print(make_matrix_periodic(N,k))

    #for k in range(1, 5):
    #    B = make_matrix_periodic(A, k)
    #    C = make_periodic_expansion_of_matrix(B, k, 14.5)
    #    print("C = " + str(C))

    return 0

if __name__ == "__main__":
    N = [[P.open(-P.inf,P.inf),P.open(.8,2)|P.open(13.5,14.5),P.open(0,1)|P.open(2,4)], [P.open(.8,2)|P.open(10,12),P.open(-P.inf,P.inf),P.open(0,1)|P.open(3,4)], [P.open(0,1)|P.open(2,4),P.open(0,1)|P.open(3,4),P.open(-P.inf,P.inf)]]
    A = N

    #unit_test_window()


    #X = P.open(3,5) | P.open(7,9)
    #print(len(X))


    #This function generates a bunch of random intervals for you to solve if you want to verify the correctness of the algorithm.
    #It produces a bunch of random, simple problems
    #unit_test_intersection()


    #def graph_periodic_intersection_over_various_periods(I, p_min, p_max, max, p_increment):
    # This produces a nice graph that shows the connected components of this graph nicely


    I = P.open(3,5)|P.open(7,9)|P.open(10,12)|P.open(6, 6.5)|P.open(1,2)
    collection = get_periodic_extensions_over_range(I, 1, 6, 12, .5)
    #print(collection)
    candidate = P.empty()
    candidate_list = []
    candidate_distance = idf.xor_distance(I, candidate)

    for size_of_combination in range(len(collection) + 1):
        for subset in itertools.combinations(collection, size_of_combination):
            union_of_subset = P.empty()
            for k in subset:
                union_of_subset = union_of_subset.union(k)
            new_distance = idf.xor_distance(union_of_subset, I)
            #print("{} has distance {}".format(subset, new_distance))
            if new_distance < candidate_distance:
                candidate_list = subset
                candidate = union_of_subset
                candidate_distance = new_distance
            # If xor distance is lower than previous, make this subset the new collection the periodic span of the interval

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.set_title("The periodic support")
    ax2.set_title("The periodic extensions")
    plt.ylabel("Period")
    plt.xlabel("Support")
    for k in collection:


    print("{} has a distance from the original interval of {}".format(candidate_list, candidate_distance))

    #graph_periodic_intersection_with_distinguished_extensions

    #graph_periodic_intersection_over_various_periods(I, 1, 20, 20, .05)


    #I = random_one_dimensional_data_cloud(50, 10, 2)
    #J = open_cover(I, .01)

    #for i in range(1, 10):
    #    J = open_cover(J, .01)
    #    graph_periodic_intersection_over_various_periods(J, .1, 10, 10, .05, display_noise = True)
    
    #graph_periodic_intersection_over_various_periods(I, .1, 10, 10, .05, display_noise = True)
    #graph_periodic_intersection_over_various_periods(J, .1, 10, 10, .05, display_noise = True)


    #Graphs of Square Waves
    #A = square_wave(3, 10)
    #B = square_wave(2, 10)
    #C = A.intersection(B)
    #graph_periodic_intersection_over_various_periods(A, .1, 10, 10, .1)
    #graph_periodic_intersection_over_various_periods(B, .1, 10, 10, .05)
    #graph_periodic_intersection_over_various_periods(C, .1, 10, 10, .05)

    
    #J = P.empty()
    #for i in range(1, 20):
    #    J = J.union(P.open(0+i*100, 50+i*100))
    #graph_periodic_intersection_over_various_periods(J, p_min = 1, p_max = get_max_interval_endpoint(J) + 20, interval_max = get_max_interval_endpoint(J), p_increment = 5)


    #This produces a nice graph from an actual contact interval

    #file = './outputs/moongnd-8/moongnd_0 Contact Analysis.csv'
    #A = imac.soapConverter(file)
    #print(A[3][5])
    #graph_periodic_intersection_over_various_periods(A[3][5], 1, 86400, 86400, 10)






