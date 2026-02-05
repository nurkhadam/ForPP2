# 1. Skip 3
i = 0
while i < 5:
    i += 1
    if i == 3: continue
    print(i)

# 2. Skip odds (Print evens)
i = 0
while i < 6:
    i += 1
    if i % 2 != 0: continue
    print(i)

# 3. Skip specific value
i = 5
while i < 15:
    i += 5
    if i == 10: continue
    print(i)

# 4. Early loop restart
i = 0
while i < 3:
    i += 1
    if i > 1: continue
    print("Only runs for i=1")

# 5. Skip negative logic
i = -3
while i < 3:
    i += 1
    if i < 0: continue
    print(i)