import tkinter as tk
from tkinter import messagebox
import socket
import threading
from chat import start_chat


global root, login_username, login_password, reg_username, reg_password

def on_close():
    root.destroy()

def rounded_entry(parent, width=250, height=35, radius=15, bg="#555", fg="white", show=None):
    frame = tk.Frame(parent, bg=parent["bg"])
    c = tk.Canvas(frame, width=width, height=height, bg=parent["bg"], highlightthickness=0, bd=0)
    c.pack()
    c.create_arc(0, 0, radius*2, radius*2, start=90, extent=90, fill=bg, outline="")
    c.create_arc(width-radius*2, 0, width, radius*2, start=0, extent=90, fill=bg, outline="")
    c.create_arc(width-radius*2, height-radius*2, width, height, start=270, extent=90, fill=bg, outline="")
    c.create_arc(0, height-radius*2, radius*2, height, start=180, extent=90, fill=bg, outline="")
    c.create_rectangle(radius, 0, width-radius, height, fill=bg, outline="")
    c.create_rectangle(0, radius, width, height-radius, fill=bg, outline="")
    entry = tk.Entry(frame, bg=bg, fg=fg, relief="flat", font=("Arial", 12), insertbackground="white", show=show)
    entry.place(x=radius, y=height//4, width=width-2*radius)
    return frame, entry

def login_thread():
    username = login_username.get()
    password = login_password.get()
    try:
        auth_socket = socket.socket()
        print("trying to connect")
        auth_socket.connect(("209.25.141.30", 19158))
        auth_socket.send(f"LOG|{username}|{password}".encode())
        response = auth_socket.recv(1024).decode()
        auth_socket.close()
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", f"Cannot connect to server: {e}"))
        return

    if response.startswith("OK|"):
        parts = response.split("|")
        if len(parts) == 2:
            user_id = int(parts[1])
            root.after(0, lambda: start_chat(username, user_id))
            root.destroy()
        else:
            root.after(0, lambda: messagebox.showerror("Login Failed", "Invalid server response"))
    else:
        root.after(0, lambda: messagebox.showerror("Login Failed", response))

def login():
    threading.Thread(target=login_thread, daemon=True).start()

def register_thread():
    username = reg_username.get()
    password = reg_password.get()
    try:
        auth_socket = socket.socket()
        print("trying to connect")
        auth_socket.connect(("209.25.141.30", 19158))
        auth_socket.send(f"REG|{username}|{password}".encode())
        response = auth_socket.recv(1024).decode()
        auth_socket.close()
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", f"Cannot connect to server: {e}"))
        return

    if response == "OK":
        messagebox.showinfo("Success", f"Registered as {username}")
    else:
        messagebox.showerror("Register Failed", response)

def register():
    threading.Thread(target=register_thread, daemon=True).start()

root = tk.Tk()
root.title("Auth Window")
root.geometry("380x330")
root.configure(bg="#2f2f2f")

# логин
login_window = tk.Frame(root, bg="#2f2f2f")
login_window.pack(fill="both", expand=True)
tk.Label(login_window, text="Username", bg="#2f2f2f", fg="white", font=("Arial", 12)).pack(pady=(25,5))
login_user_frame, login_username = rounded_entry(login_window)
login_user_frame.pack()
tk.Label(login_window, text="Password", bg="#2f2f2f", fg="white", font=("Arial", 12)).pack(pady=5)
login_pass_frame, login_password = rounded_entry(login_window, show="*")
login_pass_frame.pack()
tk.Button(login_window, text="Login", command=login, bg="#4a4a4a", fg="white", font=("Arial", 12), width=12, height=1).pack(pady=20)
tk.Label(login_window, text="Not registered?", bg="#2f2f2f", fg="white", font=("Arial", 11)).pack(pady=(5,0))
reg_label = tk.Label(login_window, text="Register", bg="#2f2f2f", fg="#62b0ff", cursor="hand2", font=("Arial", 11))
reg_label.pack()

# регистрация
register_window = tk.Frame(root, bg="#2f2f2f")
def show_register():
    login_window.pack_forget()
    register_window.pack(fill="both", expand=True)
def show_login():
    register_window.pack_forget()
    login_window.pack(fill="both", expand=True)
reg_label.bind("<Button-1>", lambda e: show_register())

tk.Label(register_window, text="Register Account", bg="#2f2f2f", fg="white", font=("Arial", 16)).pack(pady=(40,10))
tk.Label(register_window, text="Username", bg="#2f2f2f", fg="white", font=("Arial", 12)).pack(pady=5)
reg_user_frame, reg_username = rounded_entry(register_window)
reg_user_frame.pack()
tk.Label(register_window, text="Password", bg="#2f2f2f", fg="white", font=("Arial", 12)).pack(pady=5)
reg_pass_frame, reg_password = rounded_entry(register_window, show="*")
reg_pass_frame.pack()
tk.Button(register_window, text="Register", command=register, bg="#4a4a4a", fg="white", font=("Arial", 12), width=12, height=1).pack(pady=25)
back_label = tk.Label(register_window, text="Back to Login", bg="#2f2f2f", fg="#62b0ff", cursor="hand2", font=("Arial", 11))
back_label.pack()
back_label.bind("<Button-1>", lambda e: show_login())

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()


