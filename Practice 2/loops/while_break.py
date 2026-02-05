# 1. Break at 3
i = 1
while i < 10:
    if i == 3: break
    print(i); i += 1

# 2. Search break
i = 0; names = ["Ali", "Asan"]
while i < len(names):
    if names[i] == "Ali": break
    i += 1

# 3. Break infinite loop
while True:
    print("Running once"); break

# 4. Break on threshold
n = 1
while n < 100:
    if n > 5: break
    n += 1

# 5. Break on square root
i = 1
while i < 10:
    if i * i == 16: break
    i += 1