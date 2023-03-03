import math

class SemiringBaseclass:
	def zero(self):
		pass
	def one(self):
		pass
	def __str__(self):
		pass
	def __add__(self, other):
		pass
	def __mul__(self, other):
		pass
	def __eq__(self, other):
		pass
	def __pow__(self, i):
		x = self.one()
		for j in range(i):
			x = x * self
		return x
	def __le__(self, other):
		return (self + other) == self
	def __ge__(self, other):
		return (self + other) == other
	def __lt__ (self, other):
		return (self <= other) and not (self == other)
	def __gt__ (self, other):
		return (self >= other) and not (self == other)

class Boolean_S(SemiringBaseclass):
	def __init__(self, n):
		self.x = n;
	def zero(self):
		return Boolean_S(False)
	def one(self):
		return Boolean_S(True)
	def __str__(self):
		return self.x.__str__();
	def __add__(self, other):
		x = self.x or other.x
		return Boolean_S(x)
	def __mul__(self, other):
		x = self.x and other.x
		return Boolean_S(x)
	def __eq__(self, other):
		return self.x == other.x

class Tropical_S(SemiringBaseclass):
	def __init__(self, n):
		self.x = n;
	def zero(self):
		return Tropical_S(math.inf)
	def one(self):
		return Tropical_S(0)
	def __str__(self):
		return self.x.__str__();
	def __add__(self, other):
		x = min(self.x, other.x)
		return Tropical_S(x)
	def __mul__(self, other):
		x = self.x + other.x
		return Tropical_S(x)
	def __eq__(self, other):
		return self.x == other.x

class HopLimited_S(SemiringBaseclass):
	def __init__(self, limit, x):
		self.x = x
		if (x > limit):
			self.x = limit
		if (x < 0):
			self.x = 0
		self.limit = limit
	def zero(self):
		return HopLimited_S(self.limit, self.limit)
	def one(self):
		return HopLimited_S(self.limit, 0)
	def __str__(self):
		if (self.x < self.limit):
			return self.x.__str__()
		else:
			return "inf"
	def __add__(self, other):
		x = min(self.x, other.x)
		return HopLimited_S(self.limit, x)
	def __mul__(self, other):
		x = self.x + other.x
		if (x > self.limit):
			x = self.limit
		return HopLimited_S(self.limit, x)
	def __eq__(self, other):
		return self.x == other.x

class SquareMatrix_S(SemiringBaseclass):
	def __init__(self, size, definingLambda, _prototype):
		self.m = []
		for i in range(size):
			row = []
			for j in range(size):
				x = definingLambda(i,j)
				row.append(x)
			self.m.append(row)
		self.size = size
		self.type = _prototype
	def zero(self):
		return SquareMatrix_S(self.size, lambda i, j : self.type.zero(), self.type)
	def one(self):
		return SquareMatrix_S(self.size, lambda i, j : self.type.one() if i == j else self.type.zero(), self.type)
	def __getitem__(self, key):
		(t,d) = key
		return self.m[t][d]
	def __setitem__(self, key, value):
		(t,d) = key
		self.m[t][d] = value
	def __str__(self):
		x = "{"
		for i in range(self.size):
			if (i != 0):
				x = x + ", "
			x = x + "{"
			for j in range(self.size):
				if (j != 0):
					x = x + ", "
				x = x + (self.m[i][j]).__str__()
			x = x + "}"
		x = x + "}"
		return x
	def __add__(self, other):
		m = []
		for i in range(self.size):
			row = []
			for j in range(self.size):
				x = self.m[i][j] + other.m[i][j]
				row.append(x)
			m.append(row)
		return SquareMatrix_S(self.size, lambda i,j : m[i][j], self.type)
	def __mul__(self, other):
		m = []
		for i in range(self.size):
			row = []
			for j in range(self.size):
				x = self.type.zero()
				for k in range(self.size):
					x = x + self.m[i][k] * other.m[k][j]
				row.append(x)
			m.append(row)
		return SquareMatrix_S(self.size, lambda i,j : m[i][j], self.type)
	def __eq__(self, other):
		for i in range(self.size):
			for j in range(self.size):
				if not (self.m[i][j] == other.m[i][j]):
					return False
		return True

class Contact_S(SemiringBaseclass):
	def __init__(self, size, definingLambda, _prototype):
		self.m = {};
		self.type = _prototype
		self.size = size
		for i in range(self.size):
			for j in range(self.size - i):
				x = definingLambda(i,j)
				if not(x == self.type.zero()):
					if i not in self.m:
						self.m[i] = {}
					self.m[i][j] = x
	def zero(self):
		return Contact_S(self.size, lambda t,d : self.type.zero(), self.type)
	def one(self):
		return Contact_S(self.size, lambda t,d : self.type.one() if d == 0 else self.type.zero(), self.type)
	def __getitem__(self, key):
		(t,d) = key
		if t not in self.m:
			return self.type.zero()
		if d not in self.m[t]:
			return self.type.zero()
		return self.m[t][d]
	def __setitem__(self, key, value):
		(t,d) = key
		if t not in self.m:
			self.m[t] = {}
		if (value == self.type.zero()) and (d in self.m[t]):
			del self.m[t][d]
		else:
			self.m[t][d] = value
	def __str__(self):
		x = "{\n"
		for i in self.m:
			x = x + "[" + i.__str__() + "] "
			for j in self.m[i]:
				x = x + "(" + j.__str__() + ") " + self.m[i][j].__str__() + " "
			x = x + "\n"
		x = x + "}"
		return x
	def __add__(self, other):
		return Contact_S(self.size, lambda t,d : self[t,d] + other[t,d], self.type)
	def __mul__(self,other):
		def add(t,d):
			x = self.type.zero()
			for z in range(d+1):
				x = x + other[t+z,d-z]*self[t,z]
			return x
		return Contact_S(self.size, add, self.type)
	def __eq__(self, other):
		for i in range(self.size):
			for j in range(self.size - i):
				if (self[i,j] != other[i,j]):
					return False
		return True

import random

print("Hello world")
x = Contact_S(5, lambda i,j : HopLimited_S(4, random.randint(0,4)), HopLimited_S(4,0))
print(x)
print(x * x)
print(x**2)
print((x.one() + x)**100)
# print(x.one() * x)
# print(x * x.one())
# print(x.zero())
print(x.one() + x + x**2)
# print(x.one())
print(x != x.one())
print(list(range(0)))