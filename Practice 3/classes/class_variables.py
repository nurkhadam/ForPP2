# 1-мысал
class Person:
    species = "Human"

print(Person.species)


# 2-мысал
class Car:
    wheels = 4

c1 = Car()
c2 = Car()
print(c1.wheels, c2.wheels)


# 3-мысал
class Student:
    school = "High School"

    def __init__(self, name):
        self.name = name

s = Student("Ali")
print(s.name, s.school)
