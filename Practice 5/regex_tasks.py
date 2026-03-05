import re

# 1. 'a' әрпінен кейін нөл немесе одан көп 'b' (ab*)
def task1(text):
    return re.fullmatch(r'ab*', text) is not None

# 2. 'a' әрпінен кейін 2-3 'b' (ab{2,3})
def task2(text):
    return re.fullmatch(r'ab{2,3}', text) is not None

# 3. Кіші әріптер мен астын сызу арқылы қосылған тізбек (a_b)
def task3(text):
    return re.findall(r'[a-z]+_[a-z]+', text)

# 4. Бас әріппен басталып, кіші әріппен жалғасатын тізбек (Aa)
def task4(text):
    return re.findall(r'[A-Z][a-z]+', text)

# 5. 'a' әрпінен басталып, кез келген символға жалғасып, 'b'-мен аяқталуы (a...b)
def task5(text):
    return re.fullmatch(r'a.*b', text) is not None

# 6. Бос орын, үтір немесе нүктені қос нүктеге ауыстыру
def task6(text):
    return re.sub(r'[ ,.]', ':', text)

# 7. snake_case-ті camelCase-ке айналдыру
def task7(text):
    return re.sub(r'_([a-z])', lambda x: x.group(1).upper(), text)

# 8. Жолды бас әріптер бойынша бөлу
def task8(text):
    return re.findall(r'[A-Z][^A-Z]*', text)

# 9. Бас әріппен басталатын сөздердің арасына бос орын қосу
def task9(text):
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

# 10. camelCase-ті snake_case-ке айналдыру
def task10(text):
    return re.sub(r'([a-z])([A-Z])', r'\1_\2', text).lower()