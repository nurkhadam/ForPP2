# 1. Comparing numbers
a = 20; b = 33
if b > a:
    print("b is greater")
else:
    print("a is greater")

# 2. Even or Odd
n = 7
if n % 2 == 0:
    print("Even")
else:
    print("Odd")

# 3. User access
user = "admin"
if user == "admin":
    print("Welcome")
else:
    print("Access denied")

# 4. Truthy strings
s = ""
if s:
    print("Not empty")
else:
    print("Empty string")

# 5. List length
l = [1, 2]
if len(l) > 5:
    print("Big list")
else:
    print("Small list")