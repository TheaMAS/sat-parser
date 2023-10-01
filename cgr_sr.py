import portion as P

import warnings

INFINITY = float("inf")

if __name__ == "__main__":
    DEBUG = True;
else:
    DEBUG = False

def endpoint_add(x, y):
    # assumption : at least one is not +/- P.inf
    if x == P.inf or y == P.inf:
        return P.inf

    if x == -P.inf or y == -P.inf:
        return -P.inf

    return x + y

class Contact():
    
    def __init__(self, interval, delay):
        self.interval = interval
        self.delay = delay

    def __eq__(self, val):
        return self.interval == val.interval and self.delay == val.delay

    def __contains__(self, other):
        contained = False

        if self.delay == other.delay and other.interval in self.interval:
            contained = True
        
        return contained

    @staticmethod
    def identity():
        return Contact(P.closed(-P.inf, P.inf), 0)

    # def __add__(self, val):
    #     return None

    def __mul__(self, val):
        delay_shift = lambda x : x - self.delay
        interval = self.interval & val.interval.replace(lower = delay_shift, upper = delay_shift)

        return Contact(interval, self.delay + val.delay)

    def __str__(self):
        return f"([{self.interval.lower}, {self.interval.upper}] : {self.delay})"

c = Contact(P.closed(0, 10), 5)
cc = Contact(P.closed(-P.inf, 6), 0)

print(c)
print(cc)
print(c * cc)

print(c == cc)
print(Contact.identity() == Contact(P.closed(-P.inf, P.inf), 0))

c = Contact(P.closed(3, P.inf), 2)
cc = Contact(P.closed(1, 7), 3)

print(c)
print(cc)
print(c * cc)

class Storage():

    def __init__(self, capacity = P.inf):
        self.capacity = capacity

class Nevada():

    def __init__(self, left, right, storage = Storage()):
        # Nevada contains left and right Contacts
        #   c S c'
        self.left = left
        self.right = right
        self.storage = storage

        # todo : maybe on init precalculate standard forms to use for comparison
        # self.std = Nevada.standard_form(left, right)

    def get_boundary_vertices(self):
        # todo : rewrite for generalized storage

        # vertices = [
        #     (self.right.lower + self.right.delay, self.left.lower), # top left
        #     (self.right.upper + self.right.delay, self.left.lower), # top right
        #     (self.right.upper + self.right.delay, self.left.upper), # bottom right
        #     (self.right.lower + self.right.delay, self.right.lower - self.left.delay),
        #     (self.left.upper + self.left.delay + self.right.delay, self.left.upper)
        # ]

        interval_l = self.left.interval
        interval_r = self.right.interval

        # top left
        vertex_tl = (endpoint_add(interval_r.lower, self.right.delay), interval_l.lower)

        # top right 
        vertex_tr = (endpoint_add(interval_r.upper, self.right.delay), interval_l.lower)

        # bottom right 
        vertex_br = (endpoint_add(interval_r.upper, self.right.delay), interval_l.upper)

        # diagonal upper 
        vertex_du = (endpoint_add(interval_r.lower, self.right.delay), endpoint_add(interval_r.lower, -self.left.delay))

        # diagonal lower 
        vertex_dl = (endpoint_add(interval_l.upper, self.left.delay + self.right.delay), interval_l.upper)

        return [vertex_tl, vertex_tr, vertex_br, vertex_du, vertex_dl]
    
    def __mul__(self, val):
        
        # calculate inner contact
        ic = self.right * val.left

        left = self.left * Contact(P.closed(-P.inf, ic.interval.upper), 0)
        right = Contact(P.closed(ic.interval.lower, P.inf), ic.delay) * val.right
        
        return Nevada(left, right) # todo: return in standard form?

    def __eq__(self, other):
        pass

    def __contains__(self, other):
        # maybe have case when other is a point and where other is a nevada
        #   and where other is a contact
        if isinstance(other, tuple):
            pass
        pass

    # TODO : rename to get_point(i, j)
    def contains_point(self, point):
        (x, y) = point
        if y not in self.left.interval:
            return False

        delay_shift = lambda x : x + self.right.delay
        if x not in self.right.interval.replace(lower = delay_shift, upper = delay_shift):
            return False

        # check if below diagonal
        if (x - (y + self.left.delay + self.right.delay)) < 0:
            return False

        return True

    def contains_nevada(self, nevada):
        pass

    def contains_contact(self, contact):
        pass

    @staticmethod
    def identity():
        left = Contact(P.closed(-P.inf, P.inf), 0)
        right = Contact(P.closed(-P.inf, P.inf), 0)
        return Nevada(left, right)

    @staticmethod
    def standard_form(left, right):

        print(f"left=[{left.interval.lower},{left.interval.upper}]; right=[{right.interval.lower},{right.interval.upper}]")
        # print(f"{portion_interval_add(right.interval.upper, -left.delay)} -- {min(0, P.inf)}")
        # print(f"{right.interval.upper - left.delay}")

        left_std_lower = left.interval.lower
        left_std_upper = min(left.interval.upper, portion_interval_add(right.interval.upper, -left.delay))
        left_std_interval = P.closed(left_std_lower, left_std_upper)

        left_std_delay = 0

        left_std = Contact(left_std_interval, left_std_delay)

        right_std_lower = max(left.interval.lower, portion_interval_add(right.interval.lower, -left.delay))
        right_std_upper = portion_interval_add(right.interval.upper, -left.delay)
        right_std_interval = P.closed(right_std_lower, right_std_upper)

        right_std_delay = left.delay - right.delay

        right_std = Contact(right_std_interval, right_std_delay)
        return Nevada(left_std, right_std)

    def __str__(self):
        # todo : modify this method so that if left or right is the identity
        #   matrix, then don't print
        left_str = ""
        if self.left != Contact.identity():
            left_str = str(self.left) + " "

        right_str = ""
        if self.right != Contact.identity():
            right_str = " " + str(self.right)
        return f"{left_str}S{right_str}"

n = Nevada(cc, c)
vertices = n.get_boundary_vertices()
print(vertices)

print(Nevada(cc, c))

n1 = Nevada(Contact(P.closed(0, 10), 5), Contact(P.closed(3, 6), 2))
c = Contact(P.closed(1, 8), 1) * Contact(P.closed(0, 8), 2)
n2 = Nevada(Contact(P.closed(-P.inf, P.inf), 0), c)
print(n1 * n2)
print(n2)
# exit()

# TODO : rename to product
class Word():
    # c * cSc * S * S * c * cSc * cSc
    # cSc
    # c

    # self.word = []

    def __init__(self, word):
        self.word = word

    def is_nevada(self):
        for e in self.word:
            if isinstance(e, Nevada):
                return True
        
        return False

    def get_simplified(self):
        if len(self.word) < 2:
            return self
        
        element = self.word[0]
        for e in self.word[1:]:
            element = Word.multiply_elements(element, e)
        
        return Word([element])

    @staticmethod
    def multiply_elements(x, y):
        # assume x and y are either contacts or nevadas
        match (isinstance(x, Nevada), isinstance(y, Nevada)):
            case (True, True):
                # print("Both are Nevadas")
                return x * y
            case (True, False):
                # print("First is Nevada. Second is Contact")
                return Nevada(x.left, x.right * y)
            case (False, True):
                # print("First is Contact. Second is Nevada")
                return Nevada(x * y.left, y.right)
            case (False, False):
                # print("Both are Contacts")
                return x * y

word = [c, Nevada(cc, c), cc]
element = Word(word)
print(element.is_nevada())

word = [c, cc]
element = Word(word)
print(element.is_nevada())

Word.multiply_elements(c, cc)
Word.multiply_elements(Nevada(cc, c), cc)
Word.multiply_elements(c, Nevada(cc, c))
Word.multiply_elements(Nevada(cc, c), Nevada(c, cc))

# TODO : rename to sum
class Element():

    # self.element = []

    def __init__(self, element):
        self.element = element

    def __add__(self, other):
        return Element(self.element + other.element)
    
    def __mul__(self, other):
        element = []
        for x in self.element:
            for y in self.element:
                element.append(Word.multiply_elements(x, y))
        # todo : maybe make element a set; or remove duplicates at the end.
        return Element(element)