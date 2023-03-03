from os_utilities import *
from zz_persistence import *
from sklearn.model_selection import train_test_split
import numpy as np
import contact_analysis as ca


folder_name = "sim-2022-11-10"
folder = "./outputs/" + folder_name

MOON = 0
MARS = 1

# generate x, y
x = []
y = []

# get all contact analysis data from simulation folder.
diagrams = {}
# diagrams_clique = {}

filepaths = get_csv_files(folder)
for filepath in filepaths:

    #print(filepath)
    if not filepath.endswith("Contact_Analysis.csv"):
        continue
        
    contact_plan = ca.contact_analysis_parser(filepath)
    graph = ca.construct_graph(contact_plan)    
    weighted_simplex = ca.construct_weighted_simplex(graph)
    # clique_complex = ca.construct_clique_complex(graph)

    zz, dgms, cells = calculate_zz_persistence(weighted_simplex)
    # zz_clique, dgms_clique, cells_clique = calculate_zz_persistence(clique_complex)

    filename = filepath.split("/")[-1]
    
    diagrams[filename] = {
        "dgms" : dgms,
        "id" : len(x)
    }
    # diagrams_clique[filename] = dgms_clique
    x.append(filename)
    label = -1
    if "moon" in filename:
        label = MOON
    elif "mars" in filename:
        label = MARS

    y.append(label)


def distance_matrix(diagrams, x, y, dim = 0):
    m = len(diagrams)
    matrix = np.zeros((m, m))
    
    for i in range(m):
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
    
dim = 1
distance_matrix_function = distance_matrix(diagrams, x, y, dim = dim)

# print(distance_matrix_function("emm_mars_3 Contact Analysis.csv", "emm_mars_4 Contact Analysis.csv"))


m = len(diagrams)
distance_matrix = []
for i in range(m):
    row = []
    for j in range(m):
        row.append(distance_matrix_function(x[i], x[j]))
    distance_matrix.append(row)
    
distance_matrix = np.array(distance_matrix)
# print(distance_matrix)

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)


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

def old_test():
    accuracies = []
    ks = range(1, 40)
    for k in ks:
        knn = KNeighborsClassifier(distance_matrix_function, k=k)
        knn.fit(x_train, y_train)
        accuracy = knn.evaluate(x_test, y_test)
        accuracies.append(accuracy)
        
    fig, ax = plt.subplots()
    ax.plot(ks, accuracies)
    ax.set(xlabel="k",
           ylabel="Accuracy",
           title="Performance of knn")
    plt.show()
    return 0 

filepath = "./starlink_mars_test.csv"
contact_plan = ca.contact_analysis_parser(filepath)
graph = ca.construct_graph(contact_plan)
weighted_simplex = ca.construct_weighted_simplex(graph)
# clique_complex = ca.construct_clique_complex(graph)
zz, dgms, cells = calculate_zz_persistence(weighted_simplex)

#m = 200
#k = 3
#accuracies = []
#for i in range(m):
#    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)
#    knn = KNeighborsClassifier(distance_matrix_function, k=k)
#    knn.fit(x_train, y_train)
#    accuracy = knn.evaluate(x_test, y_test)
#    accuracies.append(accuracy)
#    
#average = sum(accuracies) / len(accuracies)
#print("Average out of {} train/test splits is {} for k = {} with dim = {}".format(m, average, k, dim))

