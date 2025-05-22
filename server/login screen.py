# login_screen.py
import tkinter as tk
from tkinter import messagebox
import database # Import the database module

# Import screen modules, but don't run them directly yet
import admin_screen
import user_screen

# Global variables for the main window and currently logged-in user
main_app_window = None
logged_in_username = None
logged_in_user_id = None

def start_app():
    """Initializes the database and sets up the main login window."""
    global main_app_window

    # Inicializuje databázi POUZE JEDNOU při spuštění aplikace.
    # To je klíčové pro zabránění zámkům databáze.
    database.initialize_db()

    main_app_window = tk.Tk()
    main_app_window.title("Přihlašovací obrazovka")
    main_app_window.geometry("300x200")
    main_app_window.resizable(False, False)

    # Center the window on the screen
    main_app_window.update_idletasks()
    x = main_app_window.winfo_screenwidth() // 2 - main_app_window.winfo_width() // 2
    y = main_app_window.winfo_screenheight() // 2 - main_app_window.winfo_height() // 2
    main_app_window.geometry(f"+{x}+{y}")

    # Call function to create login UI initially
    create_login_widgets(main_app_window)

    main_app_window.mainloop()

def create_login_widgets(parent_window):
    """Creates the login screen widgets."""
    global username_entry, password_entry, main_app_window # Ensure access to these globals

    # Clear any existing widgets from previous screens
    for widget in parent_window.winfo_children():
        widget.destroy()

    login_frame = tk.Frame(parent_window, padx=10, pady=10)
    login_frame.pack(expand=True)

    username_label = tk.Label(login_frame, text="Uživatelské jméno:")
    username_label.pack(pady=5)
    username_entry = tk.Entry(login_frame)
    username_entry.pack(pady=5)

    password_label = tk.Label(login_frame, text="Heslo:")
    password_label.pack(pady=5)
    password_entry = tk.Entry(login_frame, show="*")
    password_entry.pack(pady=5)

    login_button = tk.Button(login_frame, text="Přihlásit se", command=login_button_click)
    login_button.pack(pady=10)

    register_button = tk.Button(login_frame, text="Registrovat", command=register_button_click)
    register_button.pack(pady=5)

def login_button_click():
    """Handles the login button click event."""
    global logged_in_username, logged_in_user_id

    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showwarning("Upozornění", "Vyplňte prosím uživatelské jméno i heslo.")
        return

    # Změna z verify_login na verify_user
    user_id_from_db, is_valid_login, is_admin_user = database.verify_user(username, password)

    if is_valid_login:
        logged_in_username = username
        logged_in_user_id = user_id_from_db

        if user_id_from_db: # Check if user_id was actually found
            if is_admin_user:
                # Hide login window and show admin panel
                main_app_window.withdraw()
                admin_screen.show_admin_page(main_app_window, username, user_id_from_db, lambda: create_login_widgets(main_app_window))
            else:
                # Hide login window and show user panel
                main_app_window.withdraw()
                user_screen.show_user_page(main_app_window, username, user_id_from_db, lambda: create_login_widgets(main_app_window))
        else:
            messagebox.showerror("Chyba", "Uživatelské ID nebylo nalezeno.")
    else:
        messagebox.showerror("Chyba přihlášení", "Neplatné uživatelské jméno nebo heslo.")

def register_button_click():
    """Handles the registration button click event."""
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showwarning("Upozornění", "Uživatelské jméno a heslo nemohou být prázdné.")
        return

    # Register the user as non-admin by default
    # is_admin je boolean, ne číslo
    if database.register_user(username, password, is_admin=False):
        messagebox.showinfo("Úspěch", "Registrace úspěšná! Nyní se můžete přihlásit.")
        # Optionally clear the input fields after successful registration
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Chyba", "Registrace se nezdařila. Uživatelské jméno možná již existuje.")

if __name__ == "__main__":
    start_app()