from functools import reduce

numbers = [1, 2, 3, 4, 5, 6]

# map(): Сандардың квадратын есептеу
squared = list(map(lambda x: x**2, numbers))
print(f"Квадраттар: {squared}")

# filter(): Жұп сандарды іріктеу
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(f"Жұп сандар: {evens}")

# reduce(): Барлық сандардың қосындысын есептеу
total_sum = reduce(lambda x, y: x + y, numbers)
print(f"Барлық қосынды: {total_sum}")