# 1-мысал
class A:
    def method_a(self):
        print("Method A")

class B:
    def method_b(self):
        print("Method B")

class C(A, B):
    pass

c = C()
c.method_a()
c.method_b()


# 2-мысал
class Fly:
    def fly(self):
        print("Flying")

class Swim:
    def swim(self):
        print("Swimming")

class Duck(Fly, Swim):
    pass

d = Duck()
d.fly()
d.swim()


# 3-мысал
class Father:
    def skill1(self):
        print("Carpentry")

class Mother:
    def skill2(self):
        print("Cooking")

class Child(Father, Mother):
    pass

child = Child()
child.skill1()
child.skill2()
