import sqlite3

# Создаем или открываем БД
conn = sqlite3.connect("contracts.db")
cursor = conn.cursor()

# Создаем таблицу договоров
cursor.execute('''
CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT UNIQUE,
    text TEXT,
    file_url TEXT
)
''')

# Добавим один тестовый договор
cursor.execute('''
INSERT OR IGNORE INTO contracts (number, text, file_url)
VALUES (?, ?, ?)
''', (
    "6153514376",
    "Ваш договор №6153514376 от 24.03.2025",
    "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
))

conn.commit()
conn.close()

print("✅ База и таблица созданы. Данные добавлены.")