names = ["Alice", "Bob", "Charlie"]
scores = [85, 90, 95]

# zip() және enumerate() қолдану
print("Студенттер тізімі:")
for index, (name, score) in enumerate(zip(names, scores), 1):
    print(f"{index}. {name}: {score} ұпай")

# Типтерді тексеру және түрлендіру
value = "100"
if isinstance(value, str):
    num_value = int(value) # str -> int түрлендіру
    print(f"Түрлендірілген мән: {num_value}, Типі: {type(num_value)}")