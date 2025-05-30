# login screen.py
import customtkinter as ctk
from tkinter import messagebox
import database  # Import the database module
import logo_utils
import os
from export_utils import APP_DIR, EXPORTS_DIR, ensure_exports_dir

# Import screen modules, but don't run them directly yet
import admin_screen
import user_screen

# Global variables for the main window and currently logged-in user
main_app_window = None
logged_in_username = None
logged_in_user_id = None

# Global variables for entries (to be accessed by functions)
username_entry = None
password_entry = None

# Set the appearance mode and default color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Define font settings
FONT_FAMILY = "Roboto"
FONT_LARGE = ("Roboto", 24, "bold")
FONT_MEDIUM = ("Roboto", 14, "bold")
FONT_SMALL = ("Roboto", 12, "bold")

# Configure default font for all widgets
ctk.set_default_color_theme("blue")
ctk.ThemeManager.theme["CTkFont"]["family"] = FONT_FAMILY

def start_app():
    """Initializes the database and sets up the main login window."""
    global main_app_window

    # Initialize database ONLY ONCE when starting the application
    database.initialize_db()
    
    # Ensure exports directory exists
    ensure_exports_dir()

    main_app_window = ctk.CTk()
    main_app_window.title("Kniha.cest - Přihlášení")
    main_app_window.geometry("400x500")
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
    """Creates and displays the login widgets."""
    global username_entry, password_entry
    
    # Clear any existing widgets from the parent window
    for widget in parent_window.winfo_children():
        widget.destroy()

    parent_window.title("Kniha.cest - Přihlášení")
    parent_window.geometry("400x500")  # Larger window for better spacing
    
    # Main frame with padding
    frame = ctk.CTkFrame(parent_window)
    frame.pack(expand=True, fill="both", padx=40, pady=40)

    # Add logo at the top
    logo_label = logo_utils.setup_logo(frame)
    if logo_label:
        logo_label.pack(pady=(20, 10))

    # Title label
    title_label = ctk.CTkLabel(
        frame, 
        text="Kniha.cest",
        font=FONT_LARGE
    )
    title_label.pack(pady=(20, 30))

    # Subtitle
    subtitle_label = ctk.CTkLabel(
        frame,
        text="Přihlaste se do svého účtu",
        font=FONT_MEDIUM
    )
    subtitle_label.pack(pady=(0, 20))

    # Username entry with label
    username_label = ctk.CTkLabel(frame, text="Uživatelské jméno", font=FONT_SMALL)
    username_label.pack(pady=(0, 5), anchor="w", padx=20)
    
    username_entry = ctk.CTkEntry(
        frame,
        width=300,
        placeholder_text="Zadejte uživatelské jméno",
        font=FONT_SMALL
    )
    username_entry.pack(pady=(0, 15))

    # Password entry with label
    password_label = ctk.CTkLabel(frame, text="Heslo", font=FONT_SMALL)
    password_label.pack(pady=(0, 5), anchor="w", padx=20)
    
    password_entry = ctk.CTkEntry(
        frame,
        width=300,
        placeholder_text="Zadejte heslo",
        show="•",
        font=FONT_SMALL
    )
    password_entry.pack(pady=(0, 30))

    # Buttons frame
    button_frame = ctk.CTkFrame(frame, fg_color="transparent")
    button_frame.pack(pady=(0, 20), fill="x", padx=20)

    # Login button
    login_button = ctk.CTkButton(
        button_frame,
        text="Přihlásit se",
        width=140,
        command=lambda: attempt_login(parent_window),
        font=FONT_SMALL
    )
    login_button.pack(side="left", padx=5)

    # Register button
    register_button = ctk.CTkButton(
        button_frame,
        text="Registrovat se",
        width=140,
        command=register_user_click,
        fg_color="transparent",
        border_width=2,
        text_color=("gray10", "gray90"),
        font=FONT_SMALL
    )
    register_button.pack(side="right", padx=5)

    # Theme switch
    theme_switch = ctk.CTkSwitch(
        frame,
        text="Tmavý režim",
        command=toggle_theme,
        onvalue="dark",
        offvalue="light",
        font=FONT_SMALL
    )
    theme_switch.pack(pady=(20, 0))

def toggle_theme():
    """Toggle between light and dark theme"""
    if ctk.get_appearance_mode() == "dark":
        ctk.set_appearance_mode("light")
    else:
        ctk.set_appearance_mode("dark")

def attempt_login(main_app_window):
    """Attempts to log in the user with the provided credentials."""
    global logged_in_username, logged_in_user_id

    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showwarning("Upozornění", "Uživatelské jméno a heslo nemohou být prázdné.", parent=main_app_window)
        return

    # Use verify_user which returns user_id, is_valid, is_admin
    user_id, is_valid, is_admin = database.verify_user(username, password)

    if is_valid:
        logged_in_username = username
        logged_in_user_id = user_id

        messagebox.showinfo("Přihlášení úspěšné", f"Vítejte, {username}!", parent=main_app_window)
        
        if is_admin:
            # Hide login window and show admin panel
            main_app_window.withdraw()
            admin_screen.show_admin_page(main_app_window, username, logged_in_user_id, lambda: create_login_widgets(main_app_window))
        else:
            # Hide login window and show user panel
            main_app_window.withdraw()
            user_screen.show_user_page(main_app_window, username, logged_in_user_id, lambda: create_login_widgets(main_app_window))
    else:
        messagebox.showerror("Chyba přihlášení", "Neplatné uživatelské jméno nebo heslo.", parent=main_app_window)

def register_user_click():
    """Handles the registration button click event."""
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showwarning("Upozornění", "Uživatelské jméno a heslo nemohou být prázdné.")
        return

    # Register the user as non-admin by default
    if database.register_user(username, password, is_admin=False):
        messagebox.showinfo("Úspěch", "Registrace úspěšná! Nyní se můžete přihlásit.")
        # Clear the input fields after successful registration
        username_entry.delete(0, ctk.END)
        password_entry.delete(0, ctk.END)
    else:
        messagebox.showerror("Chyba registrace", "Registrace se nezdařila. Možná uživatelské jméno již existuje.")

if __name__ == "__main__":
    start_app()