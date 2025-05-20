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

def refresh_user_list():
    """Fetches all users from the database and updates the Treeview."""
    global user_tree, current_users_data
    
    # Clear existing items
    for item in user_tree.get_children():
        user_tree.delete(item)

    current_users_data = database.get_all_users()

    for user in current_users_data:
        admin_status = "Ano" if user['is_admin'] else "Ne"
        user_tree.insert("", "end", iid=user['id'], 
                         values=(user['username'], admin_status))

def add_user_dialog():
    """Opens a dialog to add a new user."""
    dialog = tk.Toplevel(admin_root)
    dialog.title("Přidat uživatele")
    dialog.transient(admin_root) # Make dialog transient for the main window
    dialog.grab_set() # Make dialog modal
    dialog.geometry("300x200")
    dialog.configure(bg=BG_COLOR)

    # Center the dialog relative to the main window
    dialog.update_idletasks()
    x = admin_root.winfo_x() + (admin_root.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = admin_root.winfo_y() + (admin_root.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")

    tk.Label(dialog, text="Uživatelské jméno:", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
    username_entry = tk.Entry(dialog, font=FONT, bg="white", fg=FG_COLOR)
    username_entry.pack(pady=2, padx=10, fill="x")

    tk.Label(dialog, text="Heslo:", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
    password_entry = tk.Entry(dialog, show="*", font=FONT, bg="white", fg=FG_COLOR)
    password_entry.pack(pady=2, padx=10, fill="x")

    is_admin_var = tk.BooleanVar(dialog, value=False)
    tk.Checkbutton(dialog, text="Administrátor?", variable=is_admin_var, bg=BG_COLOR, fg=FG_COLOR, font=FONT, selectcolor="white").pack(pady=5)

    def save_new_user():
        username = username_entry.get()
        password = password_entry.get()
        is_admin = 1 if is_admin_var.get() else 0

        if not username or not password:
            messagebox.showwarning("Upozornění", "Vyplňte uživatelské jméno a heslo.", parent=dialog)
            return

        if database.register_user(username, password, is_admin):
            messagebox.showinfo("Úspěch", "Uživatel úspěšně přidán!", parent=dialog)
            dialog.destroy()
            refresh_user_list()
        else:
            messagebox.showerror("Chyba", "Nepodařilo se přidat uživatele. Uživatelské jméno už možná existuje.", parent=dialog)

    ttk.Button(dialog, text="Přidat uživatele", command=save_new_user).pack(pady=10)
    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy) # Handle window close button
    admin_root.wait_window(dialog) # Wait for dialog to close

def edit_user_dialog():
    """Opens a dialog to edit an existing user."""
    selected_item = user_tree.focus()
    if not selected_item:
        messagebox.showwarning("Upozornění", "Vyberte uživatele k úpravě.", parent=admin_root)
        return

    user_id_to_edit = int(selected_item) # Treeview iid is the user_id

    # Find the user data from the cached list
    user_data = next((user for user in current_users_data if user['id'] == user_id_to_edit), None)
    if not user_data:
        messagebox.showerror("Chyba", "Uživatel nenalezen.", parent=admin_root)
        return

    dialog = tk.Toplevel(admin_root)
    dialog.title(f"Upravit uživatele: {user_data['username']}")
    dialog.transient(admin_root)
    dialog.grab_set()
    dialog.geometry("300x200")
    dialog.configure(bg=BG_COLOR)

    dialog.update_idletasks()
    x = admin_root.winfo_x() + (admin_root.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = admin_root.winfo_y() + (admin_root.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")

    tk.Label(dialog, text="Uživatelské jméno:", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
    username_entry = tk.Entry(dialog, font=FONT, bg="white", fg=FG_COLOR)
    username_entry.insert(0, user_data['username'])
    username_entry.pack(pady=2, padx=10, fill="x")

    tk.Label(dialog, text="Nové heslo (volitelné):", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
    password_entry = tk.Entry(dialog, show="*", font=FONT, bg="white", fg=FG_COLOR)
    password_entry.pack(pady=2, padx=10, fill="x")

    is_admin_var = tk.BooleanVar(dialog, value=user_data['is_admin'])
    tk.Checkbutton(dialog, text="Administrátor?", variable=is_admin_var, bg=BG_COLOR, fg=FG_COLOR, font=FONT, selectcolor="white").pack(pady=5)

    def save_edited_user():
        new_username = username_entry.get()
        new_password = password_entry.get() # Could be empty if not changed
        new_is_admin = 1 if is_admin_var.get() else 0

        if not new_username:
            messagebox.showwarning("Upozornění", "Uživatelské jméno nemůže být prázdné.", parent=dialog)
            return
        
        # Prevent admin from de-admining themselves if they are the only admin
        if user_id_to_edit == admin_user_id and not new_is_admin:
            if database.count_admins() == 1:
                messagebox.showwarning("Upozornění", "Jste jediný administrátor. Nemůžete si odebrat administrátorská práva.", parent=dialog)
                return

        if database.update_user(user_id_to_edit, new_username, new_password if new_password else None, new_is_admin):
            messagebox.showinfo("Úspěch", "Uživatel úspěšně aktualizován!", parent=dialog)
            dialog.destroy()
            refresh_user_list()
        else:
            messagebox.showerror("Chyba", "Nepodařilo se aktualizovat uživatele. Nové uživatelské jméno už možná existuje.", parent=dialog)

    ttk.Button(dialog, text="Uložit změny", command=save_edited_user).pack(pady=10)
    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
    admin_root.wait_window(dialog)

def delete_user_dialog():
    """Confirms and deletes a user."""
    selected_item = user_tree.focus()
    if not selected_item:
        messagebox.showwarning("Upozornění", "Vyberte uživatele ke smazání.", parent=admin_root)
        return

    user_id_to_delete = int(selected_item)
    
    # Prevent admin from deleting themselves
    if user_id_to_delete == admin_user_id:
        messagebox.showwarning("Upozornění", "Nemůžete smazat svůj vlastní účet.", parent=admin_root)
        return

    # Prevent deleting the last admin
    user_data = next((user for user in current_users_data if user['id'] == user_id_to_delete), None)
    if user_data and user_data['is_admin'] and database.count_admins() == 1:
        messagebox.showwarning("Upozornění", "Nemůžete smazat posledního administrátora v systému.", parent=admin_root)
        return

    if messagebox.askyesno("Potvrdit smazání", f"Opravdu chcete smazat uživatele s ID {user_id_to_delete} a VŠECHNY jeho trasy?", parent=admin_root):
        if database.delete_user(user_id_to_delete):
            messagebox.showinfo("Úspěch", "Uživatel byl smazán.", parent=admin_root)
            refresh_user_list()
        else:
            messagebox.showerror("Chyba", "Nepodařilo se smazat uživatele.", parent=admin_root)

def show_admin_page(parent_window, username, user_id):
    """
    Sets up the admin page within the given parent_window.
    This function is called from login_screen.py.
    """
    global admin_root, admin_username, admin_user_id, user_tree

    admin_root = parent_window # Use the main_app_window as the admin_root
    admin_username = username
    admin_user_id = user_id

    admin_root.title(f"Administrátorský panel pro {admin_username}")
    admin_root.geometry("800x600") # Resize for admin panel
    admin_root.deiconify() # Show the window again

    # Clear existing widgets from the parent_window (login screen)
    for widget in admin_root.winfo_children():
        widget.destroy()

    # Create the main frame for the admin page content
    admin_frame = tk.Frame(admin_root, bg=BG_COLOR)
    admin_frame.pack(expand=True, fill="both", padx=PADDING, pady=PADDING)

    tk.Label(admin_frame, text=f"Vítejte v administrátorském panelu, {admin_username}!", font=TITLE_FONT, bg=BG_COLOR, fg=FG_COLOR).pack(pady=PADDING)

    # --- User Management Section ---
    user_management_frame = tk.LabelFrame(admin_frame, text="Správa uživatelů", bg=BG_COLOR, fg=FG_COLOR, font=TITLE_FONT)
    user_management_frame.pack(pady=PADDING, padx=PADDING, fill="both", expand=True)

    # Treeview for displaying users
    user_tree = ttk.Treeview(user_management_frame, columns=("username", "is_admin"), show="headings")
    user_tree.heading("username", text="Uživatelské jméno")
    user_tree.heading("is_admin", text="Admin")
    
    user_tree.column("username", width=200, anchor="center")
    user_tree.column("is_admin", width=100, anchor="center")
    
    user_tree.pack(pady=PADDING, padx=PADDING, fill="both", expand=True)

    # Scrollbar for Treeview
    scrollbar = ttk.Scrollbar(user_tree, orient="vertical", command=user_tree.yview)
    user_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Buttons for user actions
    button_frame = tk.Frame(user_management_frame, bg=BG_COLOR)
    button_frame.pack(pady=PADDING)

    ttk.Button(button_frame, text="Přidat uživatele", command=add_user_dialog).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Upravit uživatele", command=edit_user_dialog).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Smazat uživatele", command=delete_user_dialog).pack(side="left", padx=5)
    
    # Configure Treeview style
    style = ttk.Style()
    style.configure("Treeview.Heading", font=FONT, background=BUTTON_BG, foreground=BUTTON_FG)
    style.configure("Treeview", 
                    font=FONT, 
                    rowheight=25, 
                    background="white", 
                    foreground=FG_COLOR, 
                    fieldbackground="white", 
                    bordercolor="#cccccc", 
                    borderwidth=1, 
                    relief="solid")
    style.map("Treeview", 
              background=[("selected", "#347083")]) # Darker blue on select
    
    # Styles for buttons (optional, can be moved to a common config if desired)
    style.configure("TButton", 
                    font=FONT, 
                    padding=BUTTON_PADDING_Y, 
                    background=BUTTON_BG, 
                    foreground=BUTTON_FG)
    style.map("TButton", 
              background=[("active", BUTTON_ACTIVE_BG)])

    refresh_user_list() # Populate the list on startup

    # Back to Login button
    back_button = ttk.Button(admin_frame, text="Zpět na přihlášení", command=lambda: go_back_to_login(admin_root))
    back_button.pack(side="bottom", pady=PADDING)

    # This part was `root.mainloop()` before, now it's managed by login_screen.py
    # Don't call admin_root.mainloop() here. The mainloop is in login_screen.py

def go_back_to_login(current_window):
    """Destroys current screen content and returns to login."""
    # Importing login_screen inside the function to avoid circular imports at top level
    import login_screen 

    for widget in current_window.winfo_children():
        widget.destroy()
    current_window.geometry("300x200") # Reset size for login screen
    current_window.title("Přihlašovací obrazovka")
    login_screen.create_login_widgets(current_window) # Recreate login widgets
    current_window.deiconify() # Show the window again if it was hidden

# The __main__ block is removed as this module is now imported and its functions called.
# if __name__ == "__main__":
#     pass