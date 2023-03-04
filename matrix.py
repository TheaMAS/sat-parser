import portion as P
import contact_analysis as ca

class IntervalMatrix():

    def __init__(self, n, m, matrix = None):
        self.dim_row = n
        self.dim_col = m

        if matrix == None:
            self.matrix = self.get_empty_matrix(n, m)
        else:
            # TODO : check it has the right dimensions for every column and row
            self.matrix = matrix

    def get_empty_matrix(self, n, m):
        return [[P.empty() for j in range(m)] for i in range(n)]
    
    def get_element(self, i, j):
        return self.matrix[i][j]

    def set_element(self, i, j, value):
        self.matrix[i][j] = value

    def is_symmetric(self):
        if self.dim_row != self.dim_col:
            return False

        # symmetric = True
        for i in range(self.dim_row):
            for j in range(i + 1, self.dim_col):
                # print("{},{}".format(i, j))
                if self.matrix[i][j] != self.matrix[j][i]:
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
        temp = self.matrix
        for x in range(k-1):
            temp = temp * self.matrix
        return temp

    def get_A_star():
        temp = self.matrix
        prev = []
        curr_walk = self.matrix
        while temp != prev:
            curr_walk = self.matrix * curr_walk
            temp = temp + curr_walk
        return temp

    def __add__(self, im):
        if self.dim_row != im.dim_row or self.dim_col != im.dim_col:
            raise ValueError("Dimension Mismatch Error (in Addition)")
            # print("Throw error : dimensions don't agree.")

        matrix = self.get_empty_matrix(self.dim_row, self.dim_col)
        for i in range(self.dim_row):
            for j in range(self.dim_col):
                matrix[i][j] = self.get_element(i, j) | im.get_element(i, j)

        return IntervalMatrix(self.dim_row, self.dim_col, matrix)

    def __mul__(self, im):

        # TODO : check dimensions agree
        if self.dim_col != im.dim_row:
            raise ValueError("Dimension Mismatch Error (in Multiplication)")
            # print("Throw error : dimensions don't agree.")

        matrix = self.get_empty_matrix(self.dim_row, im.dim_col)
        for i in range(self.dim_row):
            for j in range(im.dim_col):
                matrix[i][j] = P.empty()
                for k in range(self.dim_col):
                    matrix[i][j] = matrix[i][j] | (self.matrix[i][k] & im.matrix[k][j])
        
        return IntervalMatrix(self.dim_row, im.dim_col, matrix)

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
                if self.matrix[i][j] != im.matrix[i][j]:
                    return False
        return True

    def __str__(self):
        strings = []
        for row in self.matrix:
            strings.append(str(row))
        return "\n".join(strings)

    @staticmethod
    def identity(n):
        ret = [[] for x in range(dim)]
        for i, idx in enumerate(ret):
            ret[i] = [P.empty() for x in range(dim)]
            ret[i][i] = P.open(-P.inf, P.inf)
        return IntervalMatrix(dim, dim, ret) 





if __name__ == "__main__":
    matrix = IntervalMatrix(3, 3)
    print(matrix)

    matrix_raw = [
        [P.open(-P.inf,P.inf), P.closed(0, 6), P.closed(6, 10), P.empty()],
        [P.empty(), P.open(-P.inf,P.inf), P.closed(1, 4), P.closed(3, 7)],
        [P.empty(), P.empty(), P.open(-P.inf,P.inf), P.closed(0, 8)],
        [P.empty(), P.empty(), P.empty(), P.open(-P.inf,P.inf)]
    ]
    matrix_raw_sym = [
        [P.open(-P.inf,P.inf), P.closed(0, 6), P.closed(6, 10), P.empty()],
        [P.closed(0, 6), P.open(-P.inf,P.inf), P.closed(1, 4), P.closed(3, 7)],
        [P.closed(6, 10), P.closed(1, 4), P.open(-P.inf,P.inf), P.closed(0, 8)],
        [P.empty(), P.closed(3, 7), P.closed(0, 8), P.open(-P.inf,P.inf)]
    ]
    # matrix = IntervalMatrix(4, 4, matrix_raw)
    matrix = IntervalMatrix(4, 4, matrix_raw_sym)

    print("M")
    print(matrix)
    print("M^2")
    print(matrix + (matrix * matrix))
    print("M^3")
    print(matrix + (matrix * matrix) + matrix * matrix * matrix)
    print("A^3")
    print(matrix )

    print(matrix.is_symmetric())

    print(matrix**1)