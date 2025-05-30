# login_screen.py
import customtkinter as ctk
from tkinter import messagebox
import database
import logo_utils

# Import ostatních obrazovek pro navigaci po přihlášení
import admin_screen 
import user_screen

# Globální proměnné pro vstupní pole, aby k nim měly přístup funkce
username_entry = None
password_entry = None

# Globální proměnné pro uchování informací o přihlášeném uživateli
# (tyto by se v reálnější aplikaci spravovaly bezpečněji, např. v instanci třídy aplikace)
logged_in_username = None
logged_in_user_id = None

# Nastavení vzhledu (může být i v main.py, pokud by bylo globálnější)
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Definice fontů
FONT_FAMILY = "Roboto"
FONT_LARGE = ("Roboto", 24, "bold")
FONT_MEDIUM = ("Roboto", 14, "bold")
FONT_SMALL = ("Roboto", 12, "bold")

# Konfigurace výchozího fontu pro widgety CustomTkinter
ctk.ThemeManager.theme["CTkFont"]["family"] = FONT_FAMILY

def create_login_widgets(parent_window):
    """Vytvoří a zobrazí widgety přihlašovací obrazovky v daném parent_window."""
    global username_entry, password_entry
    
    # Smazání existujících widgetů z parent_window (pro případ návratu na login)
    for widget in parent_window.winfo_children():
        widget.destroy()

    parent_window.title("Kniha.cest - Přihlášení")
    parent_window.geometry("400x500")
    parent_window.resizable(False, False)

    # Centrování okna
    parent_window.update_idletasks()
    screen_width = parent_window.winfo_screenwidth()
    screen_height = parent_window.winfo_screenheight()
    x_coord = int((screen_width / 2) - (parent_window.winfo_width() / 2))
    y_coord = int((screen_height / 2) - (parent_window.winfo_height() / 2))
    parent_window.geometry(f"+{x_coord}+{y_coord}")
    
    frame = ctk.CTkFrame(parent_window)
    frame.pack(expand=True, fill="both", padx=40, pady=40)

    logo_label = logo_utils.setup_logo(frame)
    if logo_label:
        logo_label.pack(pady=(20, 10))

    title_label = ctk.CTkLabel(frame, text="Kniha.cest", font=FONT_LARGE)
    title_label.pack(pady=(20, 30))

    subtitle_label = ctk.CTkLabel(frame, text="Přihlaste se do svého účtu", font=FONT_MEDIUM)
    subtitle_label.pack(pady=(0, 20))

    username_label = ctk.CTkLabel(frame, text="Uživatelské jméno", font=FONT_SMALL)
    username_label.pack(pady=(0, 5), anchor="w", padx=20)
    username_entry = ctk.CTkEntry(frame, width=300, placeholder_text="Zadejte uživatelské jméno", font=FONT_SMALL)
    username_entry.pack(pady=(0, 15))

    password_label = ctk.CTkLabel(frame, text="Heslo", font=FONT_SMALL)
    password_label.pack(pady=(0, 5), anchor="w", padx=20)
    password_entry = ctk.CTkEntry(frame, width=300, placeholder_text="Zadejte heslo", show="•", font=FONT_SMALL)
    password_entry.pack(pady=(0, 30))

    button_frame = ctk.CTkFrame(frame, fg_color="transparent")
    button_frame.pack(pady=(0, 20), fill="x", padx=20)

    login_button = ctk.CTkButton(button_frame, text="Přihlásit se", width=140, command=lambda: attempt_login(parent_window), font=FONT_SMALL)
    login_button.pack(side="left", padx=5)

    register_button = ctk.CTkButton(button_frame, text="Registrovat se", width=140, command=lambda: register_user_click(parent_window), fg_color="transparent", border_width=2, text_color=("gray10", "gray90"), font=FONT_SMALL)
    register_button.pack(side="right", padx=5)

    theme_switch = ctk.CTkSwitch(frame, text="Tmavý režim", command=toggle_theme, onvalue="dark", offvalue="light", font=FONT_SMALL)
    theme_switch.pack(pady=(20, 0))

def toggle_theme():
    """Přepne mezi světlým a tmavým režimem."""
    if ctk.get_appearance_mode() == "dark":
        ctk.set_appearance_mode("light")
    else:
        ctk.set_appearance_mode("dark")

def attempt_login(app_window_ref):
    """Pokusí se přihlásit uživatele s zadanými údaji."""
    global logged_in_username, logged_in_user_id

    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showwarning("Upozornění", "Uživatelské jméno a heslo nemohou být prázdné.", parent=app_window_ref)
        return

    user_id_from_db, is_valid, is_admin = database.verify_user(username, password)

    if is_valid:
        logged_in_username = username
        logged_in_user_id = user_id_from_db
        
        # Smazat widgety přihlašovací obrazovky před zobrazením nové
        for widget in app_window_ref.winfo_children():
            widget.destroy()
        app_window_ref.update_idletasks()

        if is_admin:
            admin_screen.show_admin_page(app_window_ref, username, logged_in_user_id, lambda: create_login_widgets(app_window_ref))
        else:
            user_screen.show_user_page(app_window_ref, username, logged_in_user_id, lambda: create_login_widgets(app_window_ref))
    else:
        messagebox.showerror("Chyba přihlášení", "Neplatné uživatelské jméno nebo heslo.", parent=app_window_ref)

def register_user_click(app_window_ref):
    """Zpracuje kliknutí na tlačítko registrace."""
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showwarning("Upozornění", "Uživatelské jméno a heslo nemohou být prázdné.", parent=app_window_ref)
        return

    if database.register_user(username, password, is_admin=False):
        messagebox.showinfo("Úspěch", "Registrace úspěšná! Nyní se můžete přihlásit.", parent=app_window_ref)
        username_entry.delete(0, ctk.END)
        password_entry.delete(0, ctk.END)
    else:
        messagebox.showerror("Chyba registrace", "Registrace se nezdařila. Možná uživatelské jméno již existuje.", parent=app_window_ref) 