from zz_persistence import *

import numpy as np
from tqdm import tqdm
from sklearn.model_selection import train_test_split

def most_common(lst):
    '''Returns the most common element in a list'''
    return max(set(lst), key=lst.count)

class KNeighborsClassifier():
    
    def __init__(self, dist_matrix_function, k=5):
        self.k = k
        self.dist_metric = dist_matrix_function   
        
    def fit(self, x_train, y_train):
        self.x_train = x_train
        self.y_train = y_train
        
    def predict(self, x_test):
        neighbors = []
        for x in x_test:
            distances = [self.dist_metric(x, i) for i in self.x_train]
            y_sorted = [y for _, y in sorted(zip(distances, self.y_train))]
            neighbors.append(y_sorted[:self.k])        
        return list(map(most_common, neighbors))
    
    def evaluate(self, x_test, y_test):
        y_pred = self.predict(x_test)
        sum_equals = 0
        for i in range(len(x_test)):
            if y_pred[i] == y_test[i]:
                sum_equals += 1
        accuracy = sum_equals / len(y_test)
        return accuracy

# TODO : This can be multithreaded 
def distance_matrix_lambda_function(diagrams, x, y, dim = 0):
    m = len(diagrams)
    matrix = np.zeros((m, m))
    
    for i in tqdm(range(m)):
        diagram_i = diagrams[x[i]]["dgms"]
        for j in range(i + 1, m):
            diagram_j = diagrams[x[j]]["dgms"]
            # distance_ij = d.bottleneck_distance(diagram_i[dim], diagram_j[dim])
            distance_ij = d.wasserstein_distance(diagram_i[dim], diagram_j[dim], q = 2)
            matrix[i, j] = distance_ij
            matrix[j, i] = distance_ij
            # print("{}, {}".format(i, j))
    # print(matrix)
    return lambda a, b : matrix[diagrams[a]["id"]][diagrams[b]["id"]]
    
# dim = 1
# distance_matrix_function = distance_matrix(diagrams, x, y, dim = dim)

def distance_matrix(distance_matrix_function, diagrams, x):
    m = len(diagrams)
    matrix = []
    for i in range(m):
        row = []
        for j in range(m):
            row.append(distance_matrix_function(x[i], x[j]))
        matrix.append(row)

    return np.array(matrix)
