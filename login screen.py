import tkinter as tk
import json
from tkinter import messagebox

def load_login(file):
    try:
        with open(file, 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        messagebox.showerror("Error", "login.json file not found!")
        return None
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Invalid JSON format in login.json!")
        return None

def verify_login(username, password):
    data = load_login("login.json")
    if not data or "users" not in data:
        return False 

    for user_data in data.get("users", []):
        if user_data.get("username") == username:
            if user_data.get("password") == password:
                return True
            else:
                return False  # Incorrect password
    return False  # Username not found

def login_button_click():
    username = username_entry.get()
    password = password_entry.get()

    if verify_login(username, password):
        messagebox.showinfo("Success", "Login successful!")
        # You can add code here to open the main application window
    else:
        messagebox.showerror("Error", "Invalid username or password.")

# Create the main window
window = tk.Tk()
window.title("Login Screen")

# Username Label and Entry
username_label = tk.Label(window, text="Username:")
username_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
username_entry = tk.Entry(window)
username_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

password_label = tk.Label(window, text="Password:")
password_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
password_entry = tk.Entry(window, show="*")  
password_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

# Login Button
login_button = tk.Button(window, text="Login", command=login_button_click)
login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

# grid
window.grid_columnconfigure(1, weight=1)

window.mainloop()