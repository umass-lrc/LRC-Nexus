content = ""

with open("data_dump.json", "r", encoding="utf-8") as f:
    content = f.read()

cleaned = content.replace("\\u0000", "")

with open("data_dump.json", "w", encoding="utf-8") as f:
    f.write(cleaned)

print("Data cleaning complete. Null characters removed from data_dump.json.")