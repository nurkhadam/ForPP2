# 1-мысал
class Animal:
    def speak(self):
        print("Animal sound")

class Dog(Animal):
    def speak(self):
        print("Woof!")

Dog().speak()


# 2-мысал
class Vehicle:
    def move(self):
        print("Vehicle moving")

class Car(Vehicle):
    def move(self):
        print("Car driving")

Car().move()


# 3-мысал
class Person:
    def introduce(self):
        print("I am a person")

class Student(Person):
    def introduce(self):
        print("I am a student")

Student().introduce()
