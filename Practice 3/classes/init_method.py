# 1-мысал
class Person:
    def __init__(self, name):
        self.name = name

p = Person("Ali")
print("Name:", p.name)


# 2-мысал
class Car:
    def __init__(self, brand, year):
        self.brand = brand
        self.year = year

c = Car("Toyota", 2022)
print(c.brand, c.year)


# 3-мысал
class Student:
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade

s = Student("Aruzhan", 10)
print(s.name, s.grade)
