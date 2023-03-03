import portion as P
import pandas as pd

def matrix_TVG_distance(M, N, d_tvg, d_component):
    #Accepts 4 arguments: two square matrices M & N,
    #a distance function d_component which gets the distance of the individual componentwise pieces
    #and a function d_tvg which consolidates the componentwise distances into a single metric

    #Check if the matrices have the same number of elements. Otherwise this is probable nonsense
    #Take two matrices M and N, which are Matrix TVGs
    #gather the componentwise distance of M and N
    #Then norm this list and return that value
    if isinstance(M, pd.DataFrame):
        M = M.values.tolist()
    if isinstance(N, pd.DataFrame):
        N = N.values.tolist()

    if(len(M) == len(N)):
        temp = []
        for i in range(len(N)):
            for j in range(i, len(N)):
                #Calculate distance of M[i][j] and N[i][j]

                #print(M[i][j])
                #print(N[i][j])
                temp.append(d_component(M[i][j],N[i][j]))
        #Calculate and return the distance with respect to its component distances
        return d_tvg(temp)
    else:
        print("Error: Trying to compare matrices of unequal dimension. Dimensions are " + str(len(M)) + " and " + str(len(N)) + ".")

def xor_distance(A,B):
    #Naively computes the distance of two intervals as the length of their XOR
    #Accepts 2 arguments, python intervals from pyportion (P)
    xor = (A | B) - (A & B)
    ret = 0
    for pt in P.to_data(xor):
        #These two are either invalid or represent an empty interval
        if(pt[2] != -float('inf') and pt[1] != float('inf')):
            ret += pt[2]-pt[1]
    return ret

def val_in_interval(A,x):
    #if x is in A, return true
    #otherwise return false
    if(P.singleton(x) & A != P.empty()):
        return True
    return False

def get_midpoint(A):
    #Accepts a pyportion interval 4-tuple. Returns the value of the midpoint
    return (A[2] + A[1])/2


def close_interval(A):
    ret = P.empty()
    A = P.to_data(A)
    for interval in A:
        ret = ret.union(P.closed(interval[1],interval[2]))
    return ret

def get_endpoints(A):
    ret = []
    for interval in A:
        if(interval[1] != float('inf')):
            ret.append(interval[1])
        if(interval[2] != -float('inf')):
            ret.append(interval[2])
    return ret


def h_loop(Ac, B, B_extreme, max_all):
    distances = []
    for interval in Ac:
        complement = P.from_data([interval])
        #We only want to check values of B in the complement containing our midpoint
        if((complement & B) != P.empty()):
            #If this complement starts with 0, we want to check from 0 instead of a midpoint
            if interval[1] == 0:
                mid = 0
                if val_in_interval(B, mid):
                    distances.append(0)
                else:
                    temp = -1
                    for i in B_extreme:
                        if(interval[1] <= i and i <= interval[2]):
                            if abs(i-interval[2]) < temp or temp == -1:
                                temp = abs(i - interval[2])
                    if temp != -1:
                        distances.append(temp)
            #Check the right boundary
            elif interval[2] == max_all:
                mid = max_all
                if val_in_interval(B, max_all):
                    distances.append(0)
                else:
                    temp = -1
                    for i in B_extreme:
                        if interval[1] <= i and i <= interval[2]:
                            if abs(i - mid) < temp or temp == -1:
                                temp = abs(i - interval[1])
                    if temp != -1:
                        distances.append(temp)
            else:
                mid = get_midpoint(interval)
                if val_in_interval(B, mid):
                    #the midpoint is contained in B, so it will be a furthest distance from A, so append that distance
                    distances.append(interval[2]-mid)
                else:
                    #Grab closest extreme value, since the midpoint isn't in an interval of B, and add that distance into the list
                    #Can't have a negative distance so add that in as default temp to get a first value
                    temp = -1
                    for i in B_extreme:
                        if(interval[1] <= i and i <= interval[2]):
                            check = abs(interval[2] - mid) - abs(mid-i)
                            #print(str(mid) + " is not in B. Checking extreme value " + str(i) + ". It has a distance of " + str(check))
                            if check < temp or temp == -1:
                                #Value should be the distance from the midpoint to the extreme value
                                #Less the value from the midpoint to that element
                                temp = check
                    if(temp != -1):
                        distances.append(temp)
                    #print("We went with: " + str(temp))
    return distances

def h_distance(A,B):
    #Don't use this; I am exhuming pieces of its code form time to time to refactor it (eventually)

    #This is a very large function that has opportunity to be refactored and made substantially more efficient
    #Accepts two components of an interval matrix. These are sets as defined in the python portion library

    #Don't bother doing anything if they're strictly equal.
    if(A == B):
        return 0


    
    A_extreme = get_endpoints(P.to_data(A))
    B_extreme = get_endpoints(P.to_data(B))

    points_all = A_extreme + B_extreme

    if len(points_all) == 0:
        return 0

    #Used for endpoint calculation
    max_all = max(points_all)

    Ac = P.to_data(((~A)-P.open(-P.inf,0))-P.open(max_all,P.inf))
    Bc = P.to_data(((~B)-P.open(-P.inf,0))-P.open(max_all,P.inf))

    A = close_interval(A)
    B = close_interval(B)

    distances = h_loop(Ac, B, B_extreme, max_all) + h_loop(Bc, A, A_extreme, max_all)
    return(max(distances))

def l_infinity(list):
    return max(list)

def l_0(list):
    return len(list)

def l_1(list):
    return sum(list)

def l_2(list):
    for i in list:
        j += i*i
    return sqrt(j)

def l_n(list, n):
    for i in list:
        j += i**n
    return j**(1/n)