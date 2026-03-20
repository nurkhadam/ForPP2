import shutil
import os

# Тест үшін файл жасау
with open("move_me.txt", "w") as f:
    f.write("Жылжытылатын файл")

# Файлды басқа папкаға көшіру/жылжыту
os.makedirs("destination", exist_ok=True)
shutil.move("move_me.txt", "destination/moved_me.txt")
print("Файл 'destination' папкасына жылжытылды.")