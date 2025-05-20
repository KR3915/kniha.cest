import tkinter as tk
import json
from tkinter import messagebox
import subprocess # Pro spuštění user_screen.py v novém procesu
import sys # Pro ukončení procesu login_screen po spuštění user_screen

# Import admin_screen modul
# Ujistěte se, že 'admin_screen.py' je ve stejném adresáři
import admin_screen

# --- Styling Constants (můžete si je přizpůsobit) ---
BG_COLOR = "#f0f0f0"
FG_COLOR = "#333333"
BUTTON_BG = "#e0e0e0"
BUTTON_FG = FG_COLOR
FONT = ("Segoe UI", 10)
TITLE_FONT = ("Segoe UI", 16, "bold")
PADDING = 10
BUTTON_PADDING_X = 15
BUTTON_PADDING_Y = 8

LOGIN_FILE = "login.json" # Centralizovaný název souboru pro snadnou úpravu

def load_login_data(file):
    """Načte celý JSON soubor s přihlašovacími údaji."""
    try:
        # Používáme encoding='utf-8' pro správnou manipulaci s českými znaky
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        messagebox.showerror("Chyba načítání", f"Soubor '{file}' nebyl nalezen!", parent=window)
        return None
    except json.JSONDecodeError:
        messagebox.showerror("Chyba formátu", f"Neplatný formát JSON v souboru '{file}'!", parent=window)
        return None

def verify_is_admin(username):
    """
    Ověří, zda má dané uživatelské jméno administrátorská oprávnění.
    Tato funkce POUZE KONTROLUJE status a nic nespouští.
    """
    data = load_login_data(LOGIN_FILE)
    if data is None or "users" not in data:
        return False

    for user_data in data.get("users", []):
        if user_data.get("username") == username:
            # Zkontrolujeme, zda 'admin' klíč existuje a má hodnotu "1"
            if user_data.get("admin") == "1":
                return True
    return False # Uživatel nalezen, ale není admin, nebo uživatel nenalezen

def verify_login(username, password):
    """Ověří uživatelské jméno a heslo."""
    data = load_login_data(LOGIN_FILE)
    if data is None or "users" not in data:
        return False

    for user_data in data.get("users", []):
        if user_data.get("username") == username:
            if user_data.get("password") == password:
                return True # Správné uživatelské jméno a heslo
            else:
                messagebox.showerror("Chyba přihlášení", "Nesprávné heslo!")
                return False # Nesprávné heslo
    messagebox.showerror("Chyba přihlášení", "Uživatelské jméno nebylo nalezeno!")
    return False # Uživatelské jméno nebylo nalezeno

def login_button_click():
    """Obsluhuje stisk tlačítka Přihlásit se."""
    username = username_entry.get()
    password = password_entry.get()

    if verify_login(username, password):
        messagebox.showinfo("Úspěch", "Přihlášení úspěšné!")
        window.withdraw()  # Skryjeme přihlašovací okno

        if verify_is_admin(username):
            # Pokud je uživatel administrátor, zobrazíme administrační obrazovku
            admin_screen.show_main_admin_page()
            # Pro okna Toplevel (což admin_screen používá) není potřeba ukončovat hlavní proces.
            # admin_screen se otevře jako nové okno v rámci stejného programu.
        else:
            # Pokud není administrátor, spustíme uživatelskou obrazovku v novém procesu
            # a ukončíme tento přihlašovací proces.
            subprocess.Popen(["python", "user_screen.py", username])
            sys.exit() # Ukončí aktuální proces přihlašovací obrazovky

# --- Vytvoření hlavního okna Tkinter ---
window = tk.Tk()
window.title("Přihlašovací obrazovka")
window.geometry("300x200")
window.configure(bg=BG_COLOR)

# Konfigurace sloupce pro roztažení vstupních polí
window.grid_columnconfigure(1, weight=1)

# Uživatelské jméno
username_label = tk.Label(window, text="Uživatelské jméno:", font=FONT, bg=BG_COLOR, fg=FG_COLOR)
username_label.grid(row=0, column=0, padx=PADDING, pady=PADDING, sticky="w")
username_entry = tk.Entry(window, font=FONT, bg="white", fg=FG_COLOR, relief="solid", bd=1)
username_entry.grid(row=0, column=1, padx=PADDING, pady=PADDING, sticky="ew")

# Heslo
password_label = tk.Label(window, text="Heslo:", font=FONT, bg=BG_COLOR, fg=FG_COLOR)
password_label.grid(row=1, column=0, padx=PADDING, pady=PADDING, sticky="w")
password_entry = tk.Entry(window, show="*", font=FONT, bg="white", fg=FG_COLOR, relief="solid", bd=1)
password_entry.grid(row=1, column=1, padx=PADDING, pady=PADDING, sticky="ew")

# Tlačítko Přihlásit se
login_button = tk.Button(window, text="Přihlásit se", command=login_button_click,
                         bg=BUTTON_BG, fg=BUTTON_FG, font=FONT, padx=BUTTON_PADDING_X, pady=BUTTON_PADDING_Y)
login_button.grid(row=2, column=0, columnspan=2, padx=PADDING, pady=PADDING, sticky="ew")

# Spuštění hlavní smyčky Tkinter
window.mainloop()