<<<<<<< HEAD
Practice 4

generators.py
dates.py
math.py
json.py
=======
# Receipt Analyzer and RegEx Practice

This repository contains Python-based solutions for parsing retail receipts and performing common text manipulations using Regular Expressions.

## Project Structure

* **raw.txt** – Contains the raw text extracted from a retail receipt.
* **receipt_parser.py** – A script that extracts structured data from `raw.txt` using RegEx.
* **regex_tasks.py** – A collection of 10 solved RegEx exercises for text processing.
* **result.json** – The final structured output of the receipt analysis in JSON format.

## Features

### 1. Receipt Parser
The `receipt_parser.py` script identifies and extracts the following information:
* List of all products and their names.
* Unit prices and quantities for each item.
* Total transaction amount.
* Date and timestamp of the purchase.
* Payment method identification (Card/Cash).

### 2. RegEx Tasks
The `regex_tasks.py` file includes functions to:
* Validate string patterns.
* Convert between `snake_case` and `camelCase`.
* Insert spaces between words starting with capital letters.
* Split strings based on uppercase characters.
* Replace specific characters (spaces, commas, dots) with colons.

## Usage

1. Ensure `raw.txt` is in the same directory as the scripts.
2. Run the parser:
   ```bash
   python receipt_parser.py
>>>>>>> 19bbefe6236785c0b31561126068b44e319be403
