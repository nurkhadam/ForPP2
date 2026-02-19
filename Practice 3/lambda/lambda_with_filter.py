# 1-мысал
numbers = [1, 2, 3, 4, 5, 6]
evens = list(filter(lambda x: x % 2 == 0, numbers))
print("Evens:", evens)


# 2-мысал
nums = [10, 15, 20, 25]
greater_than_15 = list(filter(lambda x: x > 15, nums))
print("Greater than 15:", greater_than_15)


# 3-мысал
words = ["apple", "hi", "banana", "cat"]
long_words = list(filter(lambda x: len(x) > 3, words))
print("Long words:", long_words)
