# 1-мысал: Позициялық аргументтер
def greet(name, age):
    print(f"My name is {name}, I am {age} years old.")

greet("Ali", 20)


# 2-мысал: Әдепкі (default) аргумент
def power(base, exponent=2):
    return base ** exponent

print("Power:", power(5))
print("Power:", power(5, 3))


# 3-мысал: Атауымен (keyword) аргумент беру
def student(name, grade):
    print(f"{name} studies in grade {grade}")

student(grade=10, name="Aruzhan")
