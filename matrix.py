import portion as P
import contact_analysis as ca
import interval_distance_functions as idf
<<<<<<< HEAD

class IntervalMatrixIterator():

    def __init__(self, matrix):
        self.matrix = matrix
        self.index = (0, 0)

    def __next__(self):

        m = self.matrix.dim_row
        n = self.matrix.dim_col

        if self.index[0] == m:
            raise StopIteration()

        result = self.matrix[self.index]

        if self.index[1] + 1 == n:
            self.index = (self.index[0] + 1, 0)
        else: 
            self.index = (self.index[0], self.index[1] + 1)

        return result

# TODO : add iterate upper
=======
>>>>>>> cb4f5e2 (Added average contact matrix function)

class IntervalMatrix():

    def __init__(self, n, m, array = None, symmetric=False):
        self.dim_row = n
        self.dim_col = m
        self.max = None
        self.min = None
<<<<<<< HEAD
        self.symmetric = symmetric
=======
>>>>>>> 83b4cb4 (Added max endpoint method to matrix class)

        if array == None:
            self.array = self.get_empty_matrix(n, m)
        else:
            # TODO : check it has the right dimensions for every column and row
            self.array = array

    def __getitem__(self, index):
        return self.array[index[0]][index[1]]

    def __setitem__(self, index, value):
        self.array[index[0]][index[1]] = value

    def __iter__(self):
        return IntervalMatrixIterator(self)

    # TODO : delete; moved below into @staticmethod
    def get_empty_matrix(self, n, m):
        return [[P.empty() for j in range(m)] for i in range(n)]
    
    # TODO : maybe rename to get_entry?
    def get_element(self, i, j):
        return self.array[i][j]

    def set_element(self, i, j, value):
        self.array[i][j] = value

    def get_dimension(self):
        return (self.dim_row, self.dim_col)

    def is_symmetric(self):
        if self.dim_row != self.dim_col:
            return False

        # symmetric = True
        for i in range(self.dim_row):
            for j in range(i + 1, self.dim_col):
                # print("{},{}".format(i, j))
                if self.array[i][j] != self.array[j][i]:
                    return False
        return True

    def remove_diagonal(self):
        '''0's out the matrix diagonal. Used in computation of non-trivial walks'''
        if self.dim_row != self.dim_col:
            return False
        for i in range(0, len(self.dim_row)):
            self.matrix[i][i] = P.empty()
        return True

    def get_k_walk(k):
        #Naive -- can make way more efficient
        temp = self.array
        for x in range(k-1):
            temp = temp * self.array
        return temp

    def get_A_star():
        temp = self.array
        prev = []
        curr_walk = self.array
        while temp != prev:
            curr_walk = self.array * curr_walk
            temp = temp + curr_walk
        return temp

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    def get_max_endpoint(self, include_infinity=True):
=======
    def get_max_endpoint():
>>>>>>> 83b4cb4 (Added max endpoint method to matrix class)
=======
    def get_max_endpoint(self):
>>>>>>> cb4f5e2 (Added average contact matrix function)
=======
    def get_max_endpoint(self, include_infinity=True):
>>>>>>> 27106d4 (Current work on calculating persistence)
        if self.max != None:
            return self.max
        else:
            ret = None
            for x in self.matrix:
                for y in x:
                    temp = None
                    for interval in y:
                        dat = P.to_data(interval)
                        if temp == None:
                            temp = dat[0][2]
                        else:
                            temp = max(temp, dat[0][2])
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 27106d4 (Current work on calculating persistence)
                    if include_infinity == False and temp != float('inf') or include_infinity == True:
                        if ret == None:
                            ret = temp
                        elif temp != None:
                            ret = max(ret, temp)
<<<<<<< HEAD
            return ret

    def get_min_endpoint(self, include_infinity=True):
        if self.min != None:
            return self.min
        else:
            ret = None
            for x in self.matrix:
                for y in x:
                    temp = None
                    for interval in y:
                        dat = P.to_data(interval)
                        if temp == None:
                            temp = dat[0][1]
                        else:
                            temp = min(temp, dat[0][1])
                    if include_infinity == False and temp != float('-inf') or include_infinity == True:
                        if ret == None:
                            ret = temp
                        elif temp != None:
                            ret = min(ret, temp)
            return ret

    def get_slice(self, window_interval):
        pass
=======
                    if ret == None:
                        ret = temp
                    elif temp != None:
                        ret = max(ret, temp)
=======
>>>>>>> 27106d4 (Current work on calculating persistence)
            return ret

    def get_min_endpoint(self, include_infinity=True):
        if self.min != None:
            return self.min
        else:
            ret = None
            for x in self.matrix:
                for y in x:
                    temp = None
                    for interval in y:
                        dat = P.to_data(interval)
                        if temp == None:
                            temp = dat[0][1]
                        else:
                            temp = min(temp, dat[0][1])
                    if include_infinity == False and temp != float('-inf') or include_infinity == True:
                        if ret == None:
                            ret = temp
                        elif temp != None:
                            ret = min(ret, temp)
            return ret

>>>>>>> 83b4cb4 (Added max endpoint method to matrix class)

    def __add__(self, im):
        if self.dim_row != im.dim_row or self.dim_col != im.dim_col:
            raise ValueError("Dimension Mismatch Error (in Addition)")
            # print("Throw error : dimensions don't agree.")

        array = self.get_empty_matrix(self.dim_row, self.dim_col)
        for i in range(self.dim_row):
            for j in range(self.dim_col):
                array[i][j] = self.get_element(i, j) | im.get_element(i, j)

        return IntervalMatrix(self.dim_row, self.dim_col, array)

    def multiply_symmetric(self, im):
        """
        Assumes the matrices are symmetric and commute.
        """

        return IntervalMatrix(self.dim_row, im.dim_col)

    def __mul__(self, im):

        # TODO : check dimensions agree
        if self.dim_col != im.dim_row:
            raise ValueError("Dimension Mismatch Error (in Multiplication)")
            # print("Throw error : dimensions don't agree.")

        array = self.get_empty_matrix(self.dim_row, im.dim_col)
        for i in range(self.dim_row):
            for j in range(im.dim_col):
                array[i][j] = P.empty()
                for k in range(self.dim_col):
                    array[i][j] = array[i][j] | (self.array[i][k] & im.array[k][j])
        
        return IntervalMatrix(self.dim_row, im.dim_col, array)

    def __pow__(self, n):
        # TODO : add persistent memory about what has been calculated.
        # TODO : add specific code for when the matrix is symmetric.
        power = self
        for i in range(2, n + 1):
            print(i)
            power = power * self
        return power

    def __eq__(self, im):

        if self.dim_row != im.dim_row or self.dim_col != im.dim_col:
            # print("Throw error : dimensions don't agree")
            return False

        # equal = True
        for i in range(self.dim_row):
            for j in range(self.dim_col):
                if self.array[i][j] != im.array[i][j]:
                    return False
        return True

    def __str__(self):
        strings = []
        for row in self.array:
            strings.append(str(row))
        return "\n".join(strings)

    @staticmethod
    def matrix_multiply_square(A, B, n):

<<<<<<< HEAD
<<<<<<< HEAD
        return None

    def matrix_multiply_square_sym(A, B, n):

        return None 

    def matrix_multiply(A, B):

        if A.dim_col != B.dim_row:
            raise ValueError("Dimension Mismatch Error (in Multiplication)")

        array = IntervalMatrix.empty_matrix(A.dim_row, B.dim_col)
        for i in range(A.dim_row):
            for j in range(B.dim_col):
                array[i][j] = P.empty()
                for k in range(A.dim_col):
                    array[i][j] = array[i][j] | (A.array[i][k] & B.array[k][j])
        
        return IntervalMatrix(A.dim_row, B.dim_col, array)

        return None

    # TODO : test change
    @staticmethod
    def empty_matrix(m, n):
        array = [[P.empty() for j in range(n)] for i in range(m)]
        return IntervalMatrix(n, n, matarrayrix)

    @staticmethod
    def identity_matrix(n):
        """
        Returns an `n` square matrix with [-infty, infty] along the diagonal,
            and emptyset everywhere else. 
        """
        array = [[P.empty() for j in range(n)] for i in range(n)]
        for i in range(n):
            array[i][i] = P.open(-P.inf, P.inf)
        return IntervalMatrix(n, n, matrix) 

    @staticmethod
    def complete_matrix(n):
        """
        Returns an `n` square matrix with [-infty, infty] in each entry.
        """
        array = [[P.closed(-P.inf, P.inf) for j in range(n)] for i in range(n)]

        return IntervalMatrix(n, n, array)

    def empty_matrix(n):
        matrix = [[P.empty() for j in range(m)] for i in range(n)]
        return IntervalMatrix(n, n, matrix)

=======
def get_average_contact_matrix(mat):
    minimum = mat.get_min_endpoint()
    maximum = mat.get_max_endpoint()

    A = [[None for j in range(mat.dim_col)] for i in range(mat.dim_row)]
    for k in range(len(A)):
        for j in range(len(A[0])):
            A[k][j] = ((maximum - minimum) - idf.xor_distance(mat.get_element(k, j), P.open(minimum, maximum)))/(maximum-minimum)

    return A
>>>>>>> cb4f5e2 (Added average contact matrix function)
=======
>>>>>>> 27106d4 (Current work on calculating persistence)

if __name__ == "__main__":
    matrix = IntervalMatrix(3, 3)
    #print(matrix)

    matrix_raw = [
        [P.open(-P.inf,P.inf), P.closed(0, 6), P.closed(6, 10), P.empty()],
        [P.empty(), P.open(-P.inf,P.inf), P.closed(1, 4), P.closed(3, 7)],
        [P.empty(), P.empty(), P.open(-P.inf,P.inf), P.closed(0, 8)],
        [P.empty(), P.empty(), P.empty(), P.open(-P.inf,P.inf)]
    ]
    matrix_raw_sym = [
        [P.open(0,20), P.closed(0, 6), P.closed(6, 10), P.empty()],
        [P.closed(0, 6), P.open(0, 20), P.closed(1, 4), P.closed(3, 7)],
        [P.closed(6, 10), P.closed(1, 4), P.open(0, 20), P.closed(0, 8)],
        [P.empty(), P.closed(3, 7), P.closed(0, 8), P.open(0, 20)]
    ]
    # matrix = IntervalMatrix(4, 4, matrix_raw)
    matrix = IntervalMatrix(4, 4, matrix_raw_sym)

<<<<<<< HEAD

    print("Row: {}. Col: {}".format(matrix.dim_row, matrix.dim_col))
=======
    #print(matrix)
    #print(matrix.get_max_endpoint())
    #print(matrix.get_min_endpoint())

    #print(get_average_contact_matrix(matrix))

    for k in range(0, 10, 1):
        j = (float)(k/10)
        filt = average_contact_filtration(matrix, j)
        print(imac.A_star(filt.matrix))

    print(average_contact_filtration(matrix, .2))

<<<<<<< HEAD
    print(get_average_contact_matrix(matrix))
>>>>>>> cb4f5e2 (Added average contact matrix function)
=======
>>>>>>> 27106d4 (Current work on calculating persistence)
    #print("M")
    #print(matrix)
    #print("M^2")
    #print(matrix + (matrix * matrix))
    #print("M^3")
    #print(matrix + (matrix * matrix) + matrix * matrix * matrix)
    #print("A^3")
    #print(matrix )
    #print(matrix.is_symmetric())

<<<<<<< HEAD

    print(matrix**1)

    n = matrix.dim_row
    m = matrix.dim_col

    print("Testing Iterator")
    M2 = matrix + (matrix * matrix)
    for index, entry in enumerate(M2):
        print(f"({index // m}, {index % n}) : {entry}")
=======
    #print(matrix**1)
>>>>>>> cb4f5e2 (Added average contact matrix function)
