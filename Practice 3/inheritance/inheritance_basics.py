# 1-мысал
class Animal:
    def speak(self):
        print("Animal sound")

class Dog(Animal):
    pass

d = Dog()
d.speak()


# 2-мысал
class Vehicle:
    def move(self):
        print("Moving")

class Car(Vehicle):
    pass

c = Car()
c.move()


# 3-мысал
class Person:
    def walk(self):
        print("Walking")

class Student(Person):
    pass

s = Student()
s.walk()
