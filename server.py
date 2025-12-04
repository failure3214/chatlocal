import socket
import threading
import sqlite3
from time import sleep

conn = sqlite3.connect("chat.db", check_same_thread=False)
cursor = conn.cursor()


def start_db():
    cursor.execute("""CREATE TABLE IF NOT EXISTS messages (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            user_id INTEGER,
                            username TEXT,   
                            message TEXT,
                            FOREIGN KEY(user_id) REFERENCES users(id)
                )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT, 
                            password TEXT)""")
    conn.commit()


def register_user(username, password):
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        return False
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    return True


def login_user(username, password):
    cursor.execute("SELECT id, password FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    if not row:
        return "user_not_found"
    user_id, stored_password = row
    if stored_password != password:
        return "wrong_password"
    return user_id


clients = []  # список людей


# авторизация
def handle_auth(client):
    try:
        data = client.recv(1024).decode()
        cmd, username, password = data.split("|")
        if cmd == "LOG":
            result = login_user(username, password)
            if result == "user_not_found":
                client.send("NO_USER".encode())
            elif result == "wrong_password":
                client.send("BAD_PASS".encode())
            else:
                client.send(f"OK|{result}".encode())
        elif cmd == "REG":
            success = register_user(username, password)
            if success:
                client.send("OK".encode())
            else:
                client.send("Username already exists.".encode())
    except:
        pass
    finally:
        client.close()


# чат
def handle_chat(client):
    try:
        # ник и айди сразу после подключения
        data = client.recv(1024).decode()
        username, user_id = data.split("|")
        user_id = int(user_id)

        clients.append((client, username, user_id))
        print(f"[INFO] {username} подключился к чату")

        # отправляем последние 20 сообщений
        cursor.execute("""
            SELECT users.username, messages.message 
            FROM messages 
            JOIN users ON messages.user_id = users.id 
            ORDER BY messages.id DESC LIMIT 20
        """)
        history = cursor.fetchall()
        for sender_name, message_text in reversed(history):
            client.send(f"{sender_name}: {message_text}\n".encode())

        while True:
            data = client.recv(1024)
            if not data:
                break
            message = data.decode().strip()
            if not message:
                continue

            print(f"[MSG] {username}: {message}")

            # сохраняем сообщение
            cursor.execute("INSERT INTO messages (user_id, message) VALUES (?, ?)", (user_id, message))
            conn.commit()

            # рассылаем всем остальным
            for c, uname, uid in clients:
                if c != client:
                    try:
                        c.send(f"{username}: {message}\n".encode())
                    except:
                        pass
    except Exception as e:
        print(f"[EXCEPTION] Ошибка с клиентом {username}: {e}")
    finally:
        try:
            clients.remove((client, username, user_id))
        except:
            pass
        client.close()
        for c, uname, uid in clients:
            try:
                c.send(f"[INFO] {username} вышел из чата".encode())
            except:
                pass


start_db()


auth_server = socket.socket()
auth_server.bind(("0.0.0.0", 5000))
auth_server.listen()


chat_server = socket.socket()
chat_server.bind(("0.0.0.0", 5001))
chat_server.listen()


def accept_auth():
    while True:
        client, addr = auth_server.accept()
        threading.Thread(target=handle_auth, args=(client,), daemon=True).start()


def accept_chat():
    while True:
        client, addr = chat_server.accept()
        threading.Thread(target=handle_chat, args=(client,), daemon=True).start()


threading.Thread(target=accept_auth, daemon=True).start()
threading.Thread(target=accept_chat, daemon=True).start()


while True:
    pass