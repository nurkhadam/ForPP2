from datetime import datetime, timedelta

# 1-мысал: Қазіргі уақытты алу
now = datetime.now()
print("Қазіргі уақыт:", now)

# 2-мысал: Уақытты форматтау (Күн.Ай.Жыл)
formatted_date = now.strftime("%d.%m.%Y")
print("Форматталған күн:", formatted_date)

# 3-мысал: Уақытқа күн қосу (Ертеңгі күнді есептеу)
tomorrow = now + timedelta(days=1)
print("Ертеңгі күн:", tomorrow.strftime("%d-%B"))