# Файл жасау және мәлімет жазу
with open("example.txt", "w", encoding="utf-8") as file:
    file.write("Бұл бірінші жол.\n")
    file.write("Бұл екінші жол.\n")

# Жаңа жолдар қосу
with open("example.txt", "a", encoding="utf-8") as file:
    file.write("Қосымша үшінші жол қосылды.\n")

print("Файл сәтті жасалып, мәліметтер жазылды.")