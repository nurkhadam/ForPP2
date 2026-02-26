import json

# 1-мысал: Python сөздігін JSON мәтініне айналдыру (Dumps)
user_data = {"name": "Askar", "age": 25, "city": "Almaty"}
json_string = json.dumps(user_data)
print("JSON түрі:", json_string)

# 2-мысал: JSON мәтінін Python нысанына айналдыру (Loads)
json_input = '{"course": "Python", "price": 0}'
parsed_data = json.loads(json_input)
print("Курс атауы:", parsed_data["course"])

# 3-мысал: JSON файлын әдемі форматта шығару (indent)
pretty_json = json.dumps(user_data, indent=4)
print("Әдемі JSON:\n", pretty_json)