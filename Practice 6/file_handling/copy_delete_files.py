import shutil
import os

# Көшіру (Backup жасау)
shutil.copy("example.txt", "example_backup.txt")
print("Файл көшірмесі (backup) жасалды.")

# Қауіпсіз жою (файл бар болса ғана жою)
if os.path.exists("example_backup.txt"):
    os.remove("example_backup.txt")
    print("Көшірме файл жойылды.")