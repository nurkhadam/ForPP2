# 1-мысал: Қарапайым генератор (yield қолдану)
def simple_generator():
    yield "Бірінші"
    yield "Екінші"
    yield "Үшінші"

gen = simple_generator()
for item in gen:
    print(item)

# 2-мысал: Сандардың квадратын шығаратын генератор
def square_numbers(n):
    for i in range(1, n + 1):
        yield i * i

squares = square_numbers(3)
print(next(squares)) # 1
print(next(squares)) # 4

# 3-мысал: Генераторлық өрнек (Generator Expression)
nums = (x for x in range(10) if x % 2 == 0)
print(list(nums)) # [0, 2, 4, 6, 8]