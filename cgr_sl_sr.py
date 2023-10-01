import portion as P

import warnings

from typing import List, Optional, Tuple, Type

INF = float("inf")

class Contact():
    
    def __init__(self, start: float, end: float, delay: float):

        # TODO : change to raise ValueError()

        # start, end, delay must be int or float
        assert isinstance(start, (int, float)) and \
            isinstance(end, (int, float)) and \
            isinstance(delay, (int, float)), \
                "arguments must be of type `float`"

        # [start, end] must form interval
        assert start <= end, \
            "`start` must be less than `end`"

        # start in [-inf, inf)
        assert -INF <= start and start < INF, \
            "must have `-inf <= start < inf`"

        # end in (-inf, inf]
        assert -INF < end and end <= INF, \
            "must have `-inf < end <= inf`"

        # delay in [0, inf)
        assert delay >= 0 and delay < INF, \
            "must have `0 <= delay < INF"

        self.start = start
        self.end = end
        self.delay = delay

    def __eq__(self, other):
        return self.get_interval() == other.get_interval() and self.delay == other.delay

    def __contains__(self, other):
        contained = False

        if self.delay == other.delay and other.get_interval() in self.get_interval():
            contained = True

        return contained

    def __mul__(self, other):
        start = max(self.start, other.start - self.delay)
        end = min(self.end, other.end - self.delay)
        delay = self.delay + other.delay

        return Contact(start, end, delay)

    def __str__(self):
        return f"([{self.start},{self.end}] : {self.delay})"

    @staticmethod
    def identity() -> Optional["Contact"]:
        return Contact(-INF, INF, 0)

    def get_interval(self) -> Type[P.Interval]:
        return P.closed(self.start, self.end)

    def get_entry(self, i: float, j: float) -> float:
        if self.start <= i and i <= self.end and j == i + self.delay:
            return self.end - i
        else:
            return 0

    def get_boundary(self):
        points = [
            (self.start, self.start + self.delay),
            (self.end, self.end + self.delay)
        ]

        return list(set(points))

# unit tests
if __name__ == "__main__":
    assert Contact(1, 2, 5) in Contact(0, 3, 5)

    points = Contact(4, 6, 0).get_boundary()
    assert (4, 4) in points and (6, 6) in points

class Storage():

    def __init__(self, capacity: float = INF):

        # capacity must be int or float
        assert isinstance(capacity, (int, float)), \
            "`capacity` must be of type `float`"

        # capacity in [0, inf]
        assert capacity >= 0 and capacity <= INF, \
            "must have `0 <= capacity <= INF"

        self.capacity = capacity

    def __contains__(self, other):
        return self.capacity >= other.capacity

    def __eq__(self, other):
        return self.capacity == other.capacity

    def __mul__(self, other): 
        return Storage(self.capacity + other.capacity)

    def __str__(self):
        return f"S_({self.capacity})"

    def get_entry(self, i: float, j: float) -> float:
        if i <= j and j <= self.capacity:
            return INF
        else:
            return 0

    def to_nevada(self):
        return Nevada(Contact.identity(), Contact.identity(), self)

    def contains_contact(self, contact: Type[Contact]) -> bool:
        return contact.delay <= self.capacity

# unit tests
if __name__ == "__main__":
    assert(Storage(5) in Storage(5))
    assert(Storage(5) in Storage())
    assert(Storage(5) not in Storage(3))

class Nevada():

    @staticmethod
    def standard_form(left: Type[Contact], right: Type[Contact], storage: Type[Storage]):
        # TODO : maybe return tuple (left', right', storage')

        # return Nevada(
        #     Contact(
        #         left.start, 
        #         min(left.end, right.end - left.delay), 
        #         0
        #     ),
        #     Contact(
        #         max(left.start, right.start - left.delay), 
        #         right.end - left.delay, 
        #         left.delay + right.delay
        #     ),
        #     Storage(storage.capacity)
        # )

        standard_form = (
            Contact(
                left.start, 
                min(left.end, right.end - left.delay), 
                0
            ),
            Contact(
                max(left.start, right.start - left.delay), 
                right.end - left.delay, 
                left.delay + right.delay
            ),
            Storage(storage.capacity)
        )

        return standard_form

    def __init__(self, left: Type[Contact], right: Type[Contact], storage: Type[Storage] = Storage()):

        # check left and right are Contact type
        assert isinstance(left, Contact) and isinstance(right, Contact), \
            "`left` and `right` must be of type `Contact`"

        # check storage is Storage type
        assert isinstance(storage, Storage), \
            "`storage` must be of type `Storage`"

        (self.left, self.right, self.storage) = Nevada.standard_form(left, right, storage)
        # self.left = left
        # self.right = right
        # self.storage = storage

    def __mul__(self, other):

        # calculate inner contact
        ic = self.right * other.left
        # print(f"inner contact = {ic}")
                
        left = self.left * Contact(ic.start - self.storage.capacity, ic.end, 0)
        right = Contact(ic.start, ic.end + other.storage.capacity, ic.delay) * other.right
        
        storage = Storage(self.storage.capacity + other.storage.capacity)

        return Nevada(left, right, storage)


    def __eq__(self, other):
        return self.left == other.left and self.right == other.right and self.storage == other.storage

    def __contains__(self, other):
        # TODO : move `contains_nevada` code here.

        points = other.get_boundary()
        
        contained = True
        for p in points:
            contained = contained and self.contains_point(*p)
        return contained

    def __str__(self):
        return f"{self.left} {self.storage} {self.right}"

    def get_ascii_diagram(self, size):
        # TODO : rewrte to have start and end range, as well as step size

        diagram = ""
        for i in range(size):
            for j in range(size):
                value = f"{self.get_entry(i, j)} "

                if self.get_entry(i, j) > 0:
                    value = "*"
                else:
                    value = " "

                diagram += value
            diagram += "\n"
        return diagram

    def is_storage(self) -> bool:
        """Returns True if Nevada is of the form : S_alpha, False otherwise."""
        return self.left == Contact.identity() and self.right == Contact.identity()

    def contains_point(self, i: float, j: float) -> bool:

        # assert i > -INF and j < INF
        # Proposition 6.5

        delay_shift_l = lambda x : x - self.left.delay - self.storage.capacity
        delay_shift_u = lambda x : x - self.left.delay 
        interval_a = self.left.get_interval() & \
            self.right.get_interval().replace(
                lower = delay_shift_l, 
                upper = delay_shift_u
            )
        condition_a: bool = i in interval_a

        delay_shift_l = lambda x : x + self.left.delay 
        delay_shift_u = lambda x : x + self.left.delay + self.storage.capacity
        interval_b = self.right.get_interval() & \
            self.left.get_interval().replace(
                lower = delay_shift_l, 
                upper = delay_shift_u
            )
        condition_b: bool = (j - self.right.delay) in interval_b

        delay = self.left.delay + self.right.delay
        interval_c = P.closed(i + delay, i + delay + self.storage.capacity)
        condition_c: bool = j in interval_c

        return condition_a and condition_b and condition_c

    def get_entry(self, i: float, j: float) -> float: 
        value: float = 0

        if self.contains_point(i, j):
            value = min(self.left.end - i, self.right.end - j + self.right.delay)

        return value

    def get_boundary(self) -> List[Tuple[float]]:
        # assumption : self is a non-storage nevada

        left = self.left
        right = self.right
        capacity = self.storage.capacity

        # standard = Nevada.standard_form(self.left, self.right, self.storage)

        # left = standard.left
        # right = standard.right
        # capacity = standard.storage.capacity

        # calculate boundary indices (of matrix entires)

        # A = (left.start, right.start + right.delay)

        # B = (left.start, left.start + left.delay + right.delay + capacity)
        # BC = (left.start, right.end + right.delay)
        # C = (right.end - left.delay - capacity, right.end + right.delay)

        # D = (left.end, right.end + right.delay)
        # E = (left.end, left.end + left.delay + right.delay)
        # F = (right.start - left.delay, right.start + right.delay)

        A = (max(left.start, right.start - left.delay - capacity), right.start + right.delay)

        B = (max(left.start, right.start - left.delay - capacity), max(left.start + left.delay + right.delay + capacity, right.start + right.delay))
        BC = (left.start, right.end + right.delay)
        C = (min(left.end, right.end - left.delay - capacity), min(right.end + right.delay, left.end + left.delay + right.delay + capacity))

        D = (min(left.end, right.end - left.delay), min(right.end + right.delay, left.end + left.delay + right.delay + capacity))
        E = (min(left.end, right.end - left.delay), left.end + left.delay + right.delay)
        F = (right.start - left.delay, right.start + right.delay)

        # print([A, B, BC, C, D, E, F])
        
        boundary = [A, D, E, F]

        # maybe different based on alpha = inf or alpha < inf
        if self.storage.capacity == INF:
            # unlimited storage
            # print("unlimited storage")
            boundary.append(BC)
        else:
            # limited storage
            # print("limited storage")
            boundary.append(B)
            boundary.append(C)

        # points = [
        #     (self.left.start, self.right.start + self.right.delay),
        #     (self.left.start, self.left.start + self.left.delay + self.right.delay + self.storage.capacity),
        #     # (self.left.start + self.left.delay + self.right.delay, self.left.start),
        #     (self.right.end - self.left.delay - self.storage.capacity, self.right.end + self.right.delay),
        #     # (self.right.end + self.right.delay, self.right.end - self.left.delay),
        #     (self.left.end, self.right.end + self.right.delay),
        #     (self.left.end, self.left.end + self.left.delay + self.right.delay),
        #     # (self.left.end - self.left.delay - self.right.delay, self.left.end),
        #     (self.right.start - self.left.delay, self.right.start + self.right.delay)
        # ]

        return list(set(boundary))

    def contains_contact(self, contact: Type[Contact]) -> bool:

        # start = contact.start
        # end = contact.end
        # delay = contact.delay

        # return self.contains_point(start, start + delay) and \
        #     self.contains_point(end, end + delay)

        points = contact.get_boundary()

        contained = True
        for p in points:
            contained = contained and self.contains_point(*p)
        return contained

    def contains_nevada(self, other: Type[Contact]) -> bool:

        # TODO : check case nevada is Storage
        match(self.is_storage(), other.is_storage()):
            case (True, True):
                # print("Both are Storage")
                return other.storage in self.storage
            case (True, False):
                # print("First is Storage. Second is Nevada")
                return other.left.delay + other.right.delay + other.storage.capacity <= self.storage.capacity
            case (False, True):
                # print("First is Nevada. Second is Storage")
                return False
            case (False, False):
                # print("Both are Nevadas")
                pass

        # self and other are non-storage nevada's, so points make sense.
        points = self.get_boundary()

        contained = True
        for p in points:
            contained = contained and self.contains_point(*p)

        return contained

# unit tests
if __name__ == "__main__":

    c = Contact.identity()
    S = Storage()

    assert Nevada(c, c, Storage()).contains_contact(Contact(1, 2, 3))
    assert Nevada(c, c, Storage()).is_storage()
    assert Nevada(c, c, Storage(3)).is_storage()

    assert not Nevada(c, Contact(1,5, 0), Storage()).is_storage()

    assert Nevada(Contact(2, 6, 1), Contact(4, 8, 1), S) == Nevada(Contact(2, 6, 0), Contact(3, 7, 2), S)
    assert Nevada(Contact(2, 6, 1), Contact(4, 8, 1), Storage(2)) == Nevada(Contact(2, 6, 0), Contact(3, 7, 2), Storage(2))

    # boundary c * S_(inf) 
    assert set([(2, 2), (8, 8), (2, INF), (8, INF)]) == set(Nevada(Contact(2, 8, 0), c, Storage()).get_boundary())

    # boundary S_(inf) * c
    assert set([(2, 2), (8, 8), (-INF, 2), (-INF, 8)]) == set(Nevada(c, Contact(2, 8, 0), Storage()).get_boundary())

    # boundary c * S_(inf) * c'
    assert set([(6, 8), (2, 9), (2, 5), (6, 9), (3, 5)]) == set(Nevada(Contact(2, 6, 1), Contact(4, 8, 1), Storage()).get_boundary())

    # boundary S_alpha * c; alpha < inf
    assert set([(8, 9), (0, 3), (2, 3), (6, 9)]) == set(Nevada(c, Contact(2, 8, 1), Storage(2)).get_boundary())

    # boundary c * S_alpha; alpha < inf
    assert set([(2, 3), (8, 9), (2, 5), (8, 11)]) == set(Nevada(Contact(2, 8, 1), c, Storage(2)).get_boundary())

    # boundary c * S_alpha * c'; alpha < inf
    assert set([(6, 8), (2, 6), (5, 9), (2, 5), (6, 9), (3, 5)]) == set(Nevada(Contact(2, 6, 0), Contact(3, 7, 2), Storage(2)).get_boundary())

    size = 12

    # boundary points : S_(inf)
    # c = Contact.identity()
    # S = Storage(2)
    # n = Nevada(Contact(2, 6, 1), Contact(4, 8, 1), S)
    # n = Nevada(Contact(2, 6, 0), Contact(3, 7, 2), S)
    # n = Nevada.standard_form(n.left, n.right, n.storage)
    # print(n)
    # print(n.get_ascii_diagram(size))
    # print(n.get_boundary())
    # print(n.contains_point(-INF, -INF))

    # interval = P.closed(-P.inf, P.inf)
    # print(-INF in interval)

exit()

c = Contact.identity()
cc = Contact(1, 4, 2)
S = Storage()

print(c)
print(cc)

size = 10

n = Nevada(c, cc, S)
# print(n)
print(n.get_ascii_diagram(size))

n = Nevada(cc, c, S)
print(n)
print(n.get_ascii_diagram(size))

# c = Contact(3, 5, 1)
# n = Nevada(c, c, S)
# print(n)
# print(n.get_ascii_diagram(size))

# nn = n.standard_form(n.left, n.right, n.storage)
# print(nn)
# print(nn.get_ascii_diagram(size))
# print(Nevada(c, cc, Storage()).get_ascii_diagram(size))

points = n.get_boundary()
print(points)

exit()

# diagram = ""
# for i in range(size):
#     for j in range(size):
#         if (i, j) in points:
#             diagram += "*"
#         else:
#             diagram += "-"
#     diagram += "\n"
# print(diagram)

# import matplotlib.pyplot as plt
# x, y = zip(*points)
# plt.scatter(x,y)
# plt.show()

# s = Storage()
# n = s.to_nevada()
# print(n.get_entry(0, 0))
# diagram = ""
# for i in range(10):
#     for j in range(10):
#         diagram += f"{n.get_entry(i, j)} "
#     diagram += "\n"
# print(diagram)

generator_types = Type[Contact] | Type[Contact] | Type[Nevada]

class Product():

    def __init__(self, sequence : List[generator_types]):
        
        # sequence must be nonempty
        assert len(sequence) > 0, \
            "`sequence` must have at least one element"

        self.sequence = sequence

    def __str__(self):
        text = ""
        for e in self.sequence:
            text += f"{e} "
        return text

    # TODO : rename to evaluate
    def evaluate(self) -> Type[Contact] | Type[Nevada]:
        if len(self.sequence) < 2:
            return self.sequence[0]

        element = self.sequence[0]
        for e in self.sequence[1:]:
            element = Product.multiply(element, e)
        
        return element


    def get_simplified(self) -> Type[Contact] | Type[Nevada]:
        """Returns `Product` with sequence of the form `[c, S, c, S, ...]`."""
        return sequence

    @staticmethod
    def multiply(x: generator_types, y: generator_types) -> generator_types:

        # print(f"Multiplying {x} and {y}")

        # convert x and y to nevadas if they are storage elements
        if isinstance(x, Storage):
            x = x.to_nevada()

        if isinstance(y, Storage):
            y = y.to_nevada()

        match(isinstance(x, Nevada), isinstance(y, Nevada)):
            case (True, True):
                # print("Both are Nevadas")
                return x * y
            case (True, False):
                # print("First is Nevada. Second is Contact")
                return Nevada(x.left, x.right * y, x.storage)
            case (False, True):
                # print("First is Contact. Second is Nevada")
                return Nevada(x * y.left, y.right, y.storage)
            case (False, False):
                # print("Both are Contacts")
                return x * y

size = 25
sequence = [
    Contact(0, 10, 5),
    Storage(),
    Storage(),
    Contact(3, 6, 2),
    Storage(),
    Contact(1, 8, 1),
    Contact(0, 8, 2)
]
p = Product(sequence)
print(p)
q = p.evaluate()
print(q)
# print(q.get_ascii_diagram(size))
# n = Nevada.standard_form(q.left, q.right, q.storage)
# print(n)
# print(n.get_ascii_diagram(size))