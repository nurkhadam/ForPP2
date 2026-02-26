import math
import random

# 1-мысал: Математикалық тұрақтылар мен функциялар
print(f"Пи саны: {math.pi}")
print(f"9-дың түбірі: {math.sqrt(9)}")

# 2-мысал: Кездейсоқ сан таңдау
random_num = random.randint(1, 100)
print(f"1 мен 100 арасындағы сан: {random_num}")

# 3-мысал: Тізімнен кездейсоқ элемент алу
fruits = ["алма", "банан", "шие"]
print(f"Таңдалған жеміс: {random.choice(fruits)}")