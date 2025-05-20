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

    # Start the Tkinter event loop
    main_app_window.mainloop()

def create_login_widgets(parent_window):
    """Creates and places login widgets onto the given parent window."""
    global username_entry, password_entry # Make entries accessible

    # Clear any existing widgets from the parent_window before drawing new ones
    for widget in parent_window.winfo_children():
        widget.destroy()

    # Create a frame to better organize widgets within the window
    login_frame = tk.Frame(parent_window)
    login_frame.pack(expand=True, fill="both", padx=20, pady=20)

    # Username Label and Entry
    username_label = tk.Label(login_frame, text="Uživatelské jméno:")
    username_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    username_entry = tk.Entry(login_frame)
    username_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    # Password Label and Entry
    password_label = tk.Label(login_frame, text="Heslo:")
    password_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    password_entry = tk.Entry(login_frame, show="*") # Show asterisks for password
    password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    # Login Button
    login_button = tk.Button(login_frame, text="Přihlásit se", command=login_button_click)
    login_button.grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

    # Register Button
    register_button = tk.Button(login_frame, text="Registrovat se", command=register_button_click)
    register_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    # Configure the second column of the grid to expand horizontally
    login_frame.grid_columnconfigure(1, weight=1)

def login_button_click():
    """Handles the login button click event."""
    global logged_in_username, logged_in_user_id

    username = username_entry.get()
    password = password_entry.get()

    # Verify credentials using the database module
    if database.verify_login(username, password):
        logged_in_username = username
        logged_in_user_id = database.get_user_id(username) # Get the user ID from the database
        messagebox.showinfo("Úspěch", "Přihlášení úspěšné!")
        
        # Determine if the user is an admin and show the appropriate screen
        if database.is_admin(username):
            main_app_window.withdraw() # Hide the main window temporarily
            admin_screen.show_admin_page(main_app_window, logged_in_username, logged_in_user_id)
        else:
            main_app_window.withdraw() # Hide the main window temporarily
            user_screen.show_user_page(main_app_window, logged_in_username, logged_in_user_id)
    else:
        messagebox.showerror("Chyba", "Neplatné uživatelské jméno nebo heslo.")

def register_button_click():
    """Handles the registration button click event."""
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showwarning("Upozornění", "Uživatelské jméno a heslo nemohou být prázdné.")
        return

    # Register the user as non-admin by default
    if database.register_user(username, password, is_admin=0):
        messagebox.showinfo("Úspěch", "Registrace úspěšná! Nyní se můžete přihlásit.")
        # Optionally clear the input fields after successful registration
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Chyba", "Registrace se nezdařila. Uživatelské jméno už možná existuje.")

# This block ensures that the start_app() function is called only when
# the script is executed directly (not when imported as a module).
if __name__ == "__main__":
    start_app()