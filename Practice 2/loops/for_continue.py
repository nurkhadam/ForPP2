# 1. Skip 2
for x in range(5):
    if x == 2: continue
    print(x)

# 2. Skip spaces
for char in "Py thon":
    if char == " ": continue
    print(char)

# 3. Only positive numbers
for n in [1, -2, 3]:
    if n < 0: continue
    print(n)

# 4. Filter list
for f in ["apple", "banana"]:
    if "n" in f: continue
    print(f)

# 5. Skip odd indices
for i in range(6):
    if i % 2 != 0: continue
    print(i)