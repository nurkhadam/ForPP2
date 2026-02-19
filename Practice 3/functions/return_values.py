# 1-мысал: Бір мән қайтару
def get_pi():
    return 3.14

print("Pi:", get_pi())


# 2-мысал: Бірнеше мән қайтару
def arithmetic(a, b):
    return a + b, a - b

sum_, diff = arithmetic(10, 5)
print("Sum:", sum_, "Difference:", diff)


# 3-мысал: Логикалық мән қайтару
def is_even(n):
    return n % 2 == 0

print("Is 4 even?", is_even(4))
