import re
import json

def parse_receipt(text):
    item_pattern = r'(\d+)\.\n(.*?)\n([\d, ]+) x ([\d, ]+)\n([\d, ]+)\n.*?\n([\d, ]+)'
    items_matches = re.findall(item_pattern, text, re.DOTALL)
    
    items = []
    total_calc = 0
    for m in items_matches:
        name = m[1].replace('\n', ' ').strip()
        price = float(m[3].replace(' ', '').replace(',', '.'))
        qty = float(m[2].replace(' ', '').replace(',', '.'))
        cost = float(m[5].replace(' ', '').replace(',', '.'))
        
        items.append({
            "item_no": m[0],
            "name": name,
            "quantity": qty,
            "price_per_unit": price,
            "total_cost": cost
        })
        total_calc += cost

    dt_match = re.search(r'Время:\s+(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2})', text)
    date_time = dt_match.group(1) if dt_match else "Н/Д"

    payment_method = "Банковская карта" if "Банковская карта" in text else "Наличные"

    total_match = re.search(r'ИТОГО:\n([\d, ]+)', text)
    total_sum = float(total_match.group(1).replace(' ', '').replace(',', '.')) if total_match else total_calc

    result = {
        "metadata": {
            "date_time": date_time,
            "payment_method": payment_method,
            "total_sum": total_sum
        },
        "items": items
    }
    return result

if __name__ == "__main__":
    try:
        with open('raw.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            
        final_data = parse_receipt(content)

        print(json.dumps(final_data, ensure_ascii=False, indent=4))

        with open('result.json', 'w', encoding='utf-8') as f_out:
            json.dump(final_data, f_out, ensure_ascii=False, indent=4)
            
    except FileNotFoundError:
        print("Қате: 'raw.txt' файлын таба алмадым. Чек мәтінін осы файлға сал.")