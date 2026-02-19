# 1-мысал
class Math:
    @classmethod
    def add(cls, a, b):
        return a + b

print("Add:", Math.add(5, 6))


# 2-мысал
class Person:
    count = 0

    def __init__(self):
        Person.count += 1

    @classmethod
    def get_count(cls):
        return cls.count

p1 = Person()
p2 = Person()
print("Count:", Person.get_count())


# 3-мысал
class Car:
    brand = "Toyota"

    @classmethod
    def get_brand(cls):
        return cls.brand

print("Brand:", Car.get_brand())
