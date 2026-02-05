# 1. Break at specific number
for x in range(10):
    if x == 4: break
    print(x)

# 2. Break list search
for f in ["apple", "cherry"]:
    if f == "cherry": break
    print(f)

# 3. Break on condition
nums = [1, 2, -1, 4]
for n in nums:
    if n < 0: break
    print(n)

# 4. Nested break (inner only)
for i in range(3):
    for j in range(3):
        if j == 1: break

# 5. Early exit
for x in "Hello":
    if x == "l": break
    print(x)