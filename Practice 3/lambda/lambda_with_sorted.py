# 1-мысал
numbers = [5, 2, 9, 1]
sorted_nums = sorted(numbers, key=lambda x: x)
print("Sorted numbers:", sorted_nums)


# 2-мысал
students = [("Ali", 85), ("Aruzhan", 92), ("Dias", 78)]
sorted_students = sorted(students, key=lambda x: x[1])
print("Sorted by grade:", sorted_students)


# 3-мысал
words = ["banana", "apple", "cherry"]
sorted_words = sorted(words, key=lambda x: len(x))
print("Sorted by length:", sorted_words)
