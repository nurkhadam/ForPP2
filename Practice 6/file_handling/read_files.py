try:
    with open("example.txt", "r", encoding="utf-8") as file:
        content = file.read()
        print("Файл мазмұны:")
        print(content)
except FileNotFoundError:
    print("Файл табылмады!")