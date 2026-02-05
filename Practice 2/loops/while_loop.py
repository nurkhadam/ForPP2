# 1. 1 to 5
i = 1
while i <= 5:
    print(i); i += 1

# 2. Countdown
i = 3
while i > 0:
    print(i); i -= 1

# 3. Multiplication
i = 2
while i < 10:
    print(i); i *= 2

# 4. Iterating list
f = ["a", "b"]; i = 0
while i < len(f):
    print(f[i]); i += 1

# 5. Skip execution
while False:
    print("This will not run")