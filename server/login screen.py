# login_screen.py
import tkinter as tk
from tkinter import messagebox
import database # Import the database module

# Import screen modules, but don't run them directly yet
import admin_screen
import user_screen

# Global variables for the main window and currently logged-in user
main_app_window = None
username_entry = None # Explicitly declare
password_entry = None # Explicitly declare
logged_in_username = None
logged_in_user_id = None

# Callback pro návrat na login screen
_create_login_ui_callback = None # Bude nastaveno v start_app

def create_login_ui(root):
    """
    Creates the login screen user interface elements.
    This function is also used as a callback to return to the login screen.
    """
    global main_app_window, username_entry, password_entry, _create_login_ui_callback

    main_app_window = root 

    # Store the reference to this function itself for callbacks from other screens
    # This is crucial for breaking circular import dependencies
    _create_login_ui_callback = lambda: create_login_ui(main_app_window)


    # Clear any existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Reset window size and title for login screen
    root.title("Přihlašovací obrazovka")
    root.geometry("300x200")
    root.resizable(False, False)

    # Center the window on the screen
    root.update_idletasks()
    x = root.winfo_screenwidth() // 2 - root.winfo_width() // 2
    y = root.winfo_screenheight() // 2 - root.winfo_height() // 2
    root.geometry(f"+{x}+{y}")

    # Create a frame for better organization and padding
    login_frame = tk.Frame(root, padx=20, pady=20)
    login_frame.pack(expand=True)

    # Username label and entry
    username_label = tk.Label(login_frame, text="Uživatelské jméno:")
    username_label.pack(pady=5)
    username_entry = tk.Entry(login_frame)
    username_entry.pack(pady=5)

    # Password label and entry
    password_label = tk.Label(login_frame, text="Heslo:")
    password_label.pack(pady=5)
    password_entry = tk.Entry(login_frame, show="*") # Hide password
    password_entry.pack(pady=5)

    # Login button
    login_button = tk.Button(login_frame, text="Přihlásit se", command=login_button_click)
    login_button.pack(pady=10)

    # Register button
    register_button = tk.Button(login_frame, text="Registrovat", command=register_button_click)
    register_button.pack(pady=5)


def login_button_click():
    """Handles the login button click event."""
    global logged_in_username, logged_in_user_id, main_app_window

    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showwarning("Upozornění", "Uživatelské jméno a heslo nemohou být prázdné.", parent=main_app_window)
        return

    # Ověří uživatele a získá jeho informace (ID a admin status)
    user_info = database.verify_login(username, password) # Tato funkce v database.py musí vracet slovník nebo None

    if user_info:
        logged_in_user_id = user_info['id']
        logged_in_username = user_info['username']
        is_admin_user = user_info['is_admin']

        messagebox.showinfo("Přihlášení úspěšné", f"Vítejte, {logged_in_username}!", parent=main_app_window)

        main_app_window.withdraw() # Skryje přihlašovací okno

        if is_admin_user:
            admin_screen.show_admin_page(main_app_window, logged_in_username, logged_in_user_id, _create_login_ui_callback)
        else:
            # PŘEDÁVÁME CALLBACK PRO NÁVRAT NA LOGIN SCREEN
            user_screen.show_user_page(main_app_window, logged_in_username, logged_in_user_id, _create_login_ui_callback)
    else:
        messagebox.showerror("Chyba", "Neplatné uživatelské jméno nebo heslo.", parent=main_app_window)


def register_button_click():
    """Handles the registration button click event."""
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showwarning("Upozornění", "Uživatelské jméno a heslo nemohou být prázdné.", parent=main_app_window)
        return

    # Register the user as non-admin by default
    if database.register_user(username, password, is_admin=0):
        messagebox.showinfo("Úspěch", "Registrace úspěšná! Nyní se můžete přihlásit.", parent=main_app_window)
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Chyba", "Registrace se nezdařila. Uživatelské jméno již může existovat.", parent=main_app_window)

def start_app():
    """Initializes the database and sets up the main login window."""
    global main_app_window

    database.initialize_db()

    main_app_window = tk.Tk()
    create_login_ui(main_app_window) # Původní volání, které nyní nastaví i callback

    main_app_window.mainloop()

if __name__ == "__main__":
    start_app()