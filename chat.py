import tkinter as tk
from tkinter import ttk, messagebox
import threading
import socket

def start_chat(username, user_id, server_ip):
    last_sender = None

    # сервер
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, 5001))
    client_socket.send(f"{username}|{user_id}".encode())  

    root = tk.Tk()
    root.title("Chat")
    root.geometry("800x600")
    root.configure(bg="#2e2e2e")

    # список чатов
    sidebar = tk.Frame(root, bg="#3a3a3a", width=220)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(sidebar, text="Chats", bg="#3a3a3a", fg="white", font=("Arial", 14, "bold")).pack(pady=(10,5))
    tk.Button(sidebar, text="Chat", bg="#5a5a5a", fg="white", font=("Arial", 12), relief="flat").pack(fill="x", padx=10, pady=5)
    tk.Button(sidebar, text="Settings", bg="#5a5a5a", fg="white", font=("Arial", 14), relief="flat",
              command=lambda: messagebox.showinfo("Settings", "no settings yet")).pack(side="bottom", fill="x", padx=10, pady=20)

    # чат
    right_panel = tk.Frame(root, bg="#2e2e2e")
    right_panel.pack(side="left", fill="both", expand=True)

    group_frame = tk.Frame(right_panel, bg="#3a3a3a", bd=2, relief="groove")
    group_frame.pack(fill="x", padx=10, pady=10)
    tk.Label(group_frame, text="group chat", bg="#3a3a3a", fg="white", font=("Arial", 14, "bold")).pack(anchor="w", padx=10)

    # сообщения
    canvas_frame = tk.Frame(right_panel, bg="#2e2e2e")
    canvas_frame.pack(fill="both", expand=True, padx=10, pady=(0,10))

    canvas = tk.Canvas(canvas_frame, bg="#2e2e2e", highlightthickness=0)
    scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#2e2e2e")

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # ввод сообщений
    input_frame = tk.Frame(right_panel, bg="#3a3a3a")
    input_frame.pack(fill="x", padx=10, pady=10)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("RoundedEntry.TEntry",
                    padding=8,
                    relief="flat",
                    borderwidth=0,
                    foreground="white",
                    fieldbackground="#4a4a4a",
                    background="#4a4a4a")

    message_entry = ttk.Entry(input_frame, style="RoundedEntry.TEntry", font=("Arial", 12))
    message_entry.pack(side="left", fill="x", expand=True, padx=(0,5))
    send_button = tk.Button(input_frame, text="Send", bg="#5a5a5a", fg="white", font=("Arial", 12))
    send_button.pack(side="right")

    # сообщения
    def add_message(msg, sender="Other", name="friend"):
        nonlocal last_sender
        is_me = sender == "You"
        bg_color = "#6a6a6a" if is_me else "#505050"

        canvas_width = canvas.winfo_width()  
        max_bubble_width = int(canvas_width * 0.7)  
        # как далеко сообщения от левой стороны
        if is_me:
            padx = max(10, canvas_width - max_bubble_width - 10) - 20
        else:
            padx = 10

        msg_container = tk.Frame(scrollable_frame, bg="#2e2e2e")
        msg_container.pack(fill="x", pady=5)
        bubble_frame = tk.Frame(msg_container, bg="#2e2e2e")
        bubble_frame.pack(fill="x")

        if not is_me and sender != last_sender:
            tk.Label(bubble_frame, text=name, bg="#2e2e2e", fg="#c0c0c0", font=("Arial", 8, "bold")).pack(anchor="w", padx=padx)

        tk.Label(
            bubble_frame,
            text=msg,
            bg=bg_color,
            fg="white",
            font=("Arial", 12),
            wraplength=max_bubble_width,
            justify="left",
            padx=10,
            pady=5
        ).pack(side="right" if is_me else "left", padx=padx)

        last_sender = sender
        canvas.update_idletasks()
        canvas.yview_moveto(1)

    def send_message(event=None):
        msg = message_entry.get().strip()
        if msg:
            add_message(msg, sender="You")  
            message_entry.delete(0, "end")
            try:
                client_socket.send(msg.encode())  
            except:
                messagebox.showerror("Error", "connection lost.")

    message_entry.bind("<Return>", send_message)
    send_button.config(command=send_message)

    def handle_message(msg):
        msg = msg.strip()
        if not msg:
            return

        if ": " in msg:
            sender_name, message_text = msg.split(": ", 1)
            sender_name = sender_name.strip()
            message_text = message_text.strip()

            if sender_name == username:
                add_message(message_text, sender="You")
            else:
                add_message(message_text, sender="Other", name=sender_name)
        else:
            add_message(msg, sender="Other", name="")

    def receive_messages():
        buffer = ""
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                buffer += data.decode()
                while "\n" in buffer:
                    msg, buffer = buffer.split("\n", 1)
                    handle_message(msg)
            except:
                break

    threading.Thread(target=receive_messages, daemon=True).start()
    root.mainloop()
