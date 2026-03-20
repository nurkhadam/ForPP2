import os

# 1. Создание вложенных каталогов
folder_path = "parent_folder/child_folder"
os.makedirs(folder_path, exist_ok=True)
print(f"Каталог '{folder_path}' создан.")

# 2. Список файлов и папок в текущей директории
print("\nСодержимое текущей директории:")
for item in os.listdir('.'):
    print(item)

# 3. Найти файлы по расширению (например, .py)
extension = ".py"
py_files = [f for f in os.listdir('.') if f.endswith(extension)]
print(f"\nФайлы с расширением {extension}:")
for f in py_files:
    print(f)