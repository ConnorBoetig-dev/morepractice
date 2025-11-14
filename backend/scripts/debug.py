import csv
import os

CSV_DIR = "/home/connor-boetig/Documents/COMPTIA"
FILE = "security.csv"

path = os.path.join(CSV_DIR, FILE)

with open(path, "r", encoding="utf-8-sig") as f:
    reader = csv.reader(f, delimiter="\t")
    headers = next(reader)
    print("HEADERS FOUND:")
    for h in headers:
        print(repr(h))
