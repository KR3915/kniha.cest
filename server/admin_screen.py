# admin_screen.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import database 

# --- Styling Constants (Minimalist Theme) ---
BG_COLOR = "#f0f0f0"  # Light gray background
FG_COLOR = "#333333"  # Dark gray foreground (text)
BUTTON_BG = "#e0e0e0"  # Light gray button background
BUTTON_FG = FG_COLOR
BUTTON_ACTIVE_BG = "#d0f0d0" 
FONT = ("Segoe UI", 12)  
TITLE_FONT = ("Segoe UI", 16, "bold")
PADDING = 10
BUTTON_PADDING_X = 20
BUTTON_PADDING_Y = 10

# Global variables specific to the admin screen (will be set when opened)
admin_root = None # This will be the main_app_window passed from login_screen
admin_username = "Unknown Admin"
admin_user_id = None
user_tree = None 
current_users_data = [] 

# Nová globální proměnná pro uložení funkce pro návrat na login
_create_login_widgets_callback = None 

def show_admin_page(parent_window, username, user_id, create_login_widgets_callback_func):
    """
    Zobrazí administrátorský panel.
    :param parent_window: Kořenové okno Tkinteru.
    :param username: Uživatelské jméno přihlášeného administrátora.
    :param user_id: ID přihlášeného administrátora.
    :param create_login_widgets_callback_func: Callback funkce z login_screen pro návrat zpět na login.
    """
    global admin_root, admin_username, admin_user_id, user_tree, _create_login_widgets_callback

    admin_root = parent_window
    admin_username = username
    admin_user_id = user_id
    _create_login_widgets_callback = create_login_widgets_callback_func # Uložení callbacku

    admin_root.title(f"Administrátorský panel pro {admin_username}")
    admin_root.geometry("800x600")
    admin_root.deiconify() # Ensure the window is visible

    for widget in admin_root.winfo_children():
        widget.destroy()

    create_admin_page_layout()

def create_admin_page_layout():
    """Vytvoří rozložení prvků administrátorského panelu."""
    global user_tree, current_users_data

    style = ttk.Style(admin_root)
    style.theme_use("clam")
    style.configure("TFrame", background=BG_COLOR)
    style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR, font=FONT)
    style.configure("TEntry", font=FONT)
    style.configure("TButton", font=FONT, padding=(BUTTON_PADDING_X, BUTTON_PADDING_Y), background=BUTTON_BG, foreground=BUTTON_FG)
    style.map("TButton", background=[("active", BUTTON_ACTIVE_BG)])
    style.configure("Treeview", font=FONT, rowheight=25)
    style.configure("Treeview.Heading", font=(FONT[0], FONT[1], "bold"))
    style.map("Treeview", background=[("selected", "#347083")])
    style.configure("Red.TButton", background="red", foreground="white") # Speciální styl pro mazací tlačítko
    style.map("Red.TButton", background=[("active", "#cc0000")])


    admin_frame = ttk.Frame(admin_root, padding=PADDING)
    admin_frame.pack(fill="both", expand=True)

    title_label = ttk.Label(admin_frame, text=f"Administrace uživatelů - {admin_username}", font=TITLE_FONT)
    title_label.pack(pady=(0, PADDING * 2))

    # Treeview pro zobrazení uživatelů
    user_tree_frame = ttk.Frame(admin_frame)
    user_tree_frame.pack(fill="both", expand=True, pady=PADDING)

    columns = ("id", "username", "is_admin")
    user_tree = ttk.Treeview(user_tree_frame, columns=columns, show="headings")
    user_tree.pack(side="left", fill="both", expand=True)

    user_tree.heading("id", text="ID")
    user_tree.heading("username", text="Uživatelské jméno")
    user_tree.heading("is_admin", text="Admin")

    user_tree.column("id", width=50, anchor="center")
    user_tree.column("username", width=200, stretch=tk.YES)
    user_tree.column("is_admin", width=100, anchor="center")

    scrollbar = ttk.Scrollbar(user_tree_frame, orient="vertical", command=user_tree.yview)
    user_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Tlačítka pro správu uživatelů
    button_frame = ttk.Frame(admin_frame, padding=(0, PADDING))
    button_frame.pack(fill="x", pady=PADDING)

    ttk.Button(button_frame, text="Přidat uživatele", command=add_user_dialog).pack(side="left", padx=5, expand=True)
    ttk.Button(button_frame, text="Upravit uživatele", command=edit_user_dialog).pack(side="left", padx=5, expand=True)
    ttk.Button(button_frame, text="Smazat uživatele", command=delete_user_confirm, style="Red.TButton").pack(side="left", padx=5, expand=True)
    ttk.Button(button_frame, text="Aktualizovat seznam", command=refresh_user_list).pack(side="left", padx=5, expand=True)

    refresh_user_list() # Načte seznam uživatelů při spuštění

    # Back to Login button
    back_button = ttk.Button(admin_frame, text="Zpět na přihlášení", command=go_back_to_login)
    back_button.pack(side="bottom", pady=PADDING)


def refresh_user_list():
    """Načte všechny uživatele z databáze a aktualizuje Treeview."""
    global user_tree, current_users_data

    for item in user_tree.get_children():
        user_tree.delete(item)

    current_users_data = database.get_all_users()

    for user in current_users_data:
        admin_status = "Ano" if user.get('is_admin') else "Ne"
        user_tree.insert("", "end", values=(user.get('id'), user.get('username'), admin_status))


def add_user_dialog():
    """Zobrazí dialog pro přidání nového uživatele."""
    dialog = tk.Toplevel(admin_root)
    dialog.title("Přidat nového uživatele")
    dialog.transient(admin_root)
    dialog.grab_set()
    dialog.geometry("300x200")
    dialog.resizable(False, False)
    dialog.configure(bg=BG_COLOR)

    dialog_frame = ttk.Frame(dialog, padding=PADDING)
    dialog_frame.pack(fill="both", expand=True)

    ttk.Label(dialog_frame, text="Uživatelské jméno:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    username_entry = ttk.Entry(dialog_frame)
    username_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    ttk.Label(dialog_frame, text="Heslo:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    password_entry = ttk.Entry(dialog_frame, show="*")
    password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    is_admin_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(dialog_frame, text="Administrátor", variable=is_admin_var).grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    dialog_frame.grid_columnconfigure(1, weight=1)

    def save_user():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        is_admin = is_admin_var.get()

        if not username or not password:
            messagebox.showwarning("Upozornění", "Uživatelské jméno a heslo nemohou být prázdné.", parent=dialog)
            return

        if is_admin and database.count_admins() >= 3:
            messagebox.showwarning("Upozornění", "Maximální počet administrátorů (3) byl dosažen.", parent=dialog)
            # Dovolíme přidat uživatele, ale s is_admin=False, pokud je limit dosažen
            is_admin = False
            messagebox.showinfo("Informace", "Uživatel bude přidán jako běžný uživatel, protože byl dosažen limit administrátorů.", parent=dialog)


        if database.register_user(username, password, is_admin):
            messagebox.showinfo("Úspěch", "Uživatel úspěšně přidán.", parent=dialog)
            dialog.destroy()
            refresh_user_list()
        else:
            messagebox.showerror("Chyba", "Nepodařilo se přidat uživatele. Uživatelské jméno již může existovat.", parent=dialog)

    ttk.Button(dialog_frame, text="Uložit", command=save_user).grid(row=3, column=0, columnspan=2, pady=10)

    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
    dialog.wait_window()


def edit_user_dialog():
    """Zobrazí dialog pro úpravu vybraného uživatele."""
    selected_item = user_tree.selection()
    if not selected_item:
        messagebox.showwarning("Upozornění", "Vyberte prosím uživatele k úpravě.", parent=admin_root)
        return

    # Get the ID of the selected user from the treeview
    selected_user_id = user_tree.item(selected_item, "values")[0]

    # Find the full user data from the cached list
    selected_user_data = next((user for user in current_users_data if user['id'] == selected_user_id), None)

    if not selected_user_data:
        messagebox.showerror("Chyba", "Nepodařilo se najít data pro vybraného uživatele.", parent=admin_root)
        return

    dialog = tk.Toplevel(admin_root)
    dialog.title(f"Upravit uživatele: {selected_user_data['username']}")
    dialog.transient(admin_root)
    dialog.grab_set()
    dialog.geometry("300x250")
    dialog.resizable(False, False)
    dialog.configure(bg=BG_COLOR)

    dialog_frame = ttk.Frame(dialog, padding=PADDING)
    dialog_frame.pack(fill="both", expand=True)

    ttk.Label(dialog_frame, text="Uživatelské jméno:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    username_entry = ttk.Entry(dialog_frame)
    username_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    username_entry.insert(0, selected_user_data['username'])

    ttk.Label(dialog_frame, text="Nové heslo (ponechte prázdné pro zachování):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    password_entry = ttk.Entry(dialog_frame, show="*")
    password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    is_admin_var = tk.BooleanVar(value=selected_user_data['is_admin'])
    ttk.Checkbutton(dialog_frame, text="Administrátor", variable=is_admin_var).grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    dialog_frame.grid_columnconfigure(1, weight=1)

    def save_changes():
        new_username = username_entry.get().strip()
        new_password = password_entry.get().strip()
        new_is_admin = is_admin_var.get()

        if not new_username:
            messagebox.showwarning("Upozornění", "Uživatelské jméno nemůže být prázdné.", parent=dialog)
            return

        # Check admin count if trying to change admin status
        if new_is_admin and not selected_user_data['is_admin']: # Trying to make non-admin into admin
            if database.count_admins() >= 3:
                messagebox.showwarning("Upozornění", "Maximální počet administrátorů (3) byl dosažen. Uživatel nemůže být nastaven jako administrátor.", parent=dialog)
                new_is_admin = False # Prevent setting as admin if limit reached

        # If user is admin and trying to become non-admin, ensure there's at least one other admin
        if not new_is_admin and selected_user_data['is_admin']:
            if database.count_admins() <= 1:
                messagebox.showwarning("Upozornění", "Nemůžete odebrat administrátorská práva poslednímu administrátorovi.", parent=dialog)
                return # Stop the process if it's the last admin


        # Pass None if no change for username/password
        username_to_update = new_username if new_username != selected_user_data['username'] else None
        password_to_update = new_password if new_password else None # Only update if new_password is not empty

        if database.update_user(selected_user_id, username_to_update, password_to_update, new_is_admin):
            messagebox.showinfo("Úspěch", "Uživatel úspěšně aktualizován.", parent=dialog)
            dialog.destroy()
            refresh_user_list()
        else:
            messagebox.showerror("Chyba", "Nepodařilo se aktualizovat uživatele. Uživatelské jméno již může existovat.", parent=dialog)


    ttk.Button(dialog_frame, text="Uložit změny", command=save_changes).grid(row=3, column=0, columnspan=2, pady=10)

    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
    dialog.wait_window()

def delete_user_confirm():
    """Potvrdí a smaže vybraného uživatele."""
    selected_item = user_tree.selection()
    if not selected_item:
        messagebox.showwarning("Upozornění", "Vyberte prosím uživatele ke smazání.", parent=admin_root)
        return

    selected_user_id = user_tree.item(selected_item, "values")[0]
    selected_username = user_tree.item(selected_item, "values")[1]
    is_admin_to_delete = user_tree.item(selected_item, "values")[2] == "Ano" # Convert 'Ano'/'Ne' to boolean

    # Prevent deleting the currently logged-in admin
    if selected_user_id == admin_user_id:
        messagebox.showwarning("Upozornění", "Nemůžete smazat sám sebe jako přihlášeného administrátora.", parent=admin_root)
        return

    # Prevent deleting the last admin if it's an admin
    if is_admin_to_delete and database.count_admins() <= 1:
        messagebox.showwarning("Upozornění", "Nemůžete smazat posledního administrátora v systému.", parent=admin_root)
        return

    response = messagebox.askyesno("Potvrdit smazání", f"Opravdu chcete smazat uživatele '{selected_username}'? Všechny jeho trasy budou také smazány.", parent=admin_root)
    if response:
        if database.delete_user(selected_user_id):
            messagebox.showinfo("Úspěch", "Uživatel a jeho trasy byly úspěšně smazány.", parent=admin_root)
            refresh_user_list()
        else:
            messagebox.showerror("Chyba", "Nepodařilo se smazat uživatele.", parent=admin_root)

def go_back_to_login():
    """Destroys current screen content and returns to login using the stored callback."""
    global admin_root, _create_login_widgets_callback

    for widget in admin_root.winfo_children():
        widget.destroy()
    admin_root.geometry("300x200") # Reset size for login screen
    admin_root.title("Přihlašovací obrazovka")
    
    # Zde voláme uloženou callback funkci, místo importu login_screen
    if _create_login_widgets_callback:
        _create_login_widgets_callback() # Call the callback without arguments, as it's lambda: create_login_ui(main_app_window)
    else:
        # Fallback, pokud by z nějakého důvodu callback nebyl nastaven
        messagebox.showerror("Chyba", "Nelze se vrátit na přihlašovací obrazovku. Chybí callback.")
    
    admin_root.deiconify() # Show the window again if it was hidden# admin_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
import database

# Global variables for the admin screen
admin_root = None
current_admin_username = "Unknown Admin"
current_admin_user_id = None
admin_users_tree = None
_create_login_widgets_callback = None # New global variable for the callback

# Styling (can be shared with other screens or defined globally)
BG_COLOR = "#f0f0f0"
FG_COLOR = "#333333"
BUTTON_BG = "#e0e0e0"
BUTTON_FG = FG_COLOR
BUTTON_ACTIVE_BG = "#d0d0d0"
FONT = ("Segoe UI", 12)
TITLE_FONT = ("Segoe UI", 16, "bold")
PADDING = 10
BUTTON_PADDING_X = 20
BUTTON_PADDING_Y = 10


def show_admin_page(parent_window, username, user_id, create_login_widgets_callback_func):
    """
    Zobrazí administrátorský panel.
    :param parent_window: Kořenové okno Tkinteru.
    :param username: Uživatelské jméno přihlášeného administrátora.
    :param user_id: ID přihlášeného administrátora.
    :param create_login_widgets_callback_func: Callback funkce z login_screen pro návrat zpět na login.
    """
    global admin_root, current_admin_username, current_admin_user_id, _create_login_widgets_callback

    admin_root = parent_window
    current_admin_username = username
    current_admin_user_id = user_id
    _create_login_widgets_callback = create_login_widgets_callback_func # Store the callback

    admin_root.title(f"Administrátorský panel pro {current_admin_username}")
    admin_root.geometry("700x500")
    admin_root.deiconify() # Ensure the window is visible

    for widget in admin_root.winfo_children():
        widget.destroy()

    create_admin_page_layout()

def create_admin_page_layout():
    """Vytvoří rozložení prvků administrátorského panelu."""
    global admin_users_tree

    # Style configuration
    style = ttk.Style(admin_root)
    style.theme_use("clam")
    style.configure("TFrame", background=BG_COLOR)
    style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR, font=FONT)
    style.configure("TButton", font=FONT, background=BUTTON_BG, foreground=BUTTON_FG, padding=(BUTTON_PADDING_X, BUTTON_PADDING_Y))
    style.map("TButton", background=[("active", BUTTON_ACTIVE_BG)])
    style.configure("Treeview", font=FONT, rowheight=25)
    style.configure("Treeview.Heading", font=(FONT[0], FONT[1], "bold"))
    style.map("Treeview", background=[("selected", "#347083")])

    main_frame = ttk.Frame(admin_root, padding=PADDING)
    main_frame.pack(fill="both", expand=True)

    # Title
    title_label = ttk.Label(main_frame, text=f"Administrátorská sekce ({current_admin_username})", font=TITLE_FONT)
    title_label.pack(pady=(0, PADDING * 2))

    # Treeview for Users
    users_frame = ttk.Frame(main_frame)
    users_frame.pack(fill="both", expand=True, pady=PADDING)

    columns = ("id", "username", "is_admin")
    admin_users_tree = ttk.Treeview(users_frame, columns=columns, show="headings")
    admin_users_tree.pack(side="left", fill="both", expand=True)

    # Define headings
    admin_users_tree.heading("id", text="ID")
    admin_users_tree.heading("username", text="Uživatelské jméno")
    admin_users_tree.heading("is_admin", text="Admin")

    # Column widths
    admin_users_tree.column("id", width=50, stretch=tk.NO, anchor="center")
    admin_users_tree.column("username", width=200, stretch=tk.YES)
    admin_users_tree.column("is_admin", width=100, stretch=tk.NO, anchor="center")

    # Scrollbar
    scrollbar = ttk.Scrollbar(users_frame, orient="vertical", command=admin_users_tree.yview)
    admin_users_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Buttons for User Management
    button_frame = ttk.Frame(main_frame, padding=(0, PADDING))
    button_frame.pack(fill="x", pady=PADDING)

    ttk.Button(button_frame, text="Aktualizovat uživatele", command=load_users).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Přidat uživatele", command=add_user_dialog).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Smazat uživatele", command=delete_user_confirm).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Zpět na přihlášení", command=go_back_to_login).pack(side="right", padx=5)

    load_users() # Initial load of users

def load_users():
    """Načte všechny uživatele z databáze a zobrazí je v Treeview."""
    global admin_users_tree
    for item in admin_users_tree.get_children():
        admin_users_tree.delete(item)

    users = database.get_all_users()
    for user in users:
        admin_users_tree.insert("", "end", values=(user['id'], user['username'], "Ano" if user['is_admin'] else "Ne"))

def add_user_dialog():
    """Zobrazí dialog pro přidání nového uživatele."""
    dialog = tk.Toplevel(admin_root)
    dialog.title("Přidat nového uživatele")
    dialog.transient(admin_root)
    dialog.grab_set()
    dialog.geometry("300x200")
    dialog.resizable(False, False)
    dialog.configure(bg=BG_COLOR)

    dialog_frame = ttk.Frame(dialog, padding=PADDING)
    dialog_frame.pack(fill="both", expand=True)

    ttk.Label(dialog_frame, text="Uživatelské jméno:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    username_entry = ttk.Entry(dialog_frame)
    username_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    ttk.Label(dialog_frame, text="Heslo:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    password_entry = ttk.Entry(dialog_frame, show="*")
    password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    is_admin_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(dialog_frame, text="Administrátor", variable=is_admin_var).grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    dialog_frame.grid_columnconfigure(1, weight=1)

    def save_user():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        is_admin = is_admin_var.get()

        if not username or not password:
            messagebox.showwarning("Upozornění", "Uživatelské jméno a heslo jsou povinné.", parent=dialog)
            return

        if database.register_user(username, password, is_admin):
            messagebox.showinfo("Úspěch", "Uživatel úspěšně přidán.", parent=dialog)
            dialog.destroy()
            load_users() # Refresh user list
        else:
            messagebox.showerror("Chyba", "Nepodařilo se přidat uživatele. Uživatelské jméno už možná existuje.", parent=dialog)

    ttk.Button(dialog_frame, text="Uložit", command=save_user).grid(row=3, column=0, columnspan=2, pady=10)

    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
    dialog.wait_window()

def delete_user_confirm():
    """Potvrdí a smaže vybraného uživatele."""
    selected_item = admin_users_tree.selection()
    if not selected_item:
        messagebox.showwarning("Upozornění", "Vyberte prosím uživatele ke smazání.", parent=admin_root)
        return

    user_id_to_delete = admin_users_tree.item(selected_item, "values")[0]
    username_to_delete = admin_users_tree.item(selected_item, "values")[1]

    if user_id_to_delete == current_admin_user_id:
        messagebox.showerror("Chyba", "Nemůžete smazat svůj vlastní účet!", parent=admin_root)
        return

    response = messagebox.askyesno("Potvrdit smazání", f"Opravdu chcete smazat uživatele '{username_to_delete}' (ID: {user_id_to_delete})?\n\nTímto budou smazány VŠECHNY jeho trasy!", parent=admin_root)
    if response:
        if database.delete_user(user_id_to_delete):
            messagebox.showinfo("Úspěch", "Uživatel byl úspěšně smazán.", parent=admin_root)
            load_users() # Refresh user list
        else:
            messagebox.showerror("Chyba", "Nepodařilo se smazat uživatele.", parent=admin_root)

def go_back_to_login():
    """Destroys current screen content and returns to login using the stored callback."""
    global admin_root, _create_login_widgets_callback

    # Clear current screen widgets
    for widget in admin_root.winfo_children():
        widget.destroy()

    # Reset window size and title
    admin_root.geometry("300x200")
    admin_root.title("Přihlašovací obrazovka")

    # Call the stored callback function to recreate the login UI
    if _create_login_widgets_callback:
        _create_login_widgets_callback()
    else:
        messagebox.showerror("Chyba", "Nelze se vrátit na přihlašovací obrazovku. Chybí callback.")

    admin_root.deiconify() # Ensure window is visible