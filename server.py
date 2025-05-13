import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/get-contract", methods=["POST"])
def get_contract():
    data = request.json
    number = data.get("number")

    conn = sqlite3.connect("contracts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT text, file_url FROM contracts WHERE number = ?", (number,))
    result = cursor.fetchone()


    # Логирование запроса
    log_conn = sqlite3.connect("contracts.db")
    log_cursor = log_conn.cursor()
    log_cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    log_cursor.execute('''
        INSERT INTO logs (number, status) VALUES (?, ?)
    ''', (number, "успех" if result else "не найден"))
    log_conn.commit()
    log_conn.close()

    conn.close()

    if result:
        text, file = result
        return jsonify({"text": text, "file": file})
    else:
        return jsonify({"text": "❌ Договор не найден. Проверьте правильность введённого номера."}), 404


@app.route("/logs", methods=["GET"])
def view_logs():
    conn = sqlite3.connect("contracts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT number, status, timestamp FROM logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    conn.close()

    html = "<h2>Логи запросов</h2><table border='1'><tr><th>Номер договора</th><th>Статус</th><th>Дата и время</th></tr>"
    for log in logs:
        html += f"<tr><td>{log[0]}</td><td>{log[1]}</td><td>{log[2]}</td></tr>"
    html += "</table>"
    return html


if __name__ == "__main__":
    app.run(port=5005)