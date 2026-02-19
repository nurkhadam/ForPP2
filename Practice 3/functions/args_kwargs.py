# 1-мысал: *args қолдану
def add_numbers(*args):
    return sum(args)

print("Sum:", add_numbers(1, 2, 3, 4))


# 2-мысал: **kwargs қолдану
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Ali", age=22)


# 3-мысал: *args және **kwargs бірге
def example(a, *args, **kwargs):
    print("a:", a)
    print("args:", args)
    print("kwargs:", kwargs)

example(10, 20, 30, name="Aruzhan", city="Almaty")
