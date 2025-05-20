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
        admin_status = "Ano" if user["is_admin"] else "Ne"
        user_tree.insert("", "end", iid=str(user["id"]), 
                         values=(user["username"], admin_status))

def toggle_admin_status():
    """Toggles admin status for the selected user."""
    selected_item = user_tree.selection()
    if not selected_item:
        messagebox.showwarning("Upozornění", "Vyberte uživatele k úpravě.", parent=admin_root)
        return

    user_id_to_toggle = int(selected_item[0]) 

    selected_user = next((user for user in current_users_data if user["id"] == user_id_to_toggle), None)

    if not selected_user:
        messagebox.showerror("Chyba", "Uživatel nenalezen v datech.", parent=admin_root)
        return

    if user_id_to_toggle == admin_user_id:
        messagebox.showwarning("Upozornění", "Nemůžete si odebrat vlastní administrátorská práva.", parent=admin_root)
        return

    new_admin_status = not selected_user["is_admin"] 

    if database.update_user_admin_status(user_id_to_toggle, new_admin_status):
        messagebox.showinfo("Úspěch", f"Admin status pro uživatele '{selected_user['username']}' byl změněn na {'Admin' if new_admin_status else 'Uživatel'}.", parent=admin_root)
        refresh_user_list() 
    else:
        messagebox.showerror("Chyba", "Nepodařilo se změnit admin status.", parent=admin_root)

def delete_selected_user():
    """Deletes the selected user from the database."""
    selected_item = user_tree.selection()
    if not selected_item:
        messagebox.showwarning("Upozornění", "Vyberte uživatele ke smazání.", parent=admin_root)
        return

    user_id_to_delete = int(selected_item[0]) 

    selected_user = next((user for user in current_users_data if user["id"] == user_id_to_delete), None)
    if not selected_user:
        messagebox.showerror("Chyba", "Uživatel nenalezen v datech.", parent=admin_root)
        return

    if user_id_to_delete == admin_user_id:
        messagebox.showwarning("Upozornění", "Nemůžete smazat svůj vlastní účet z této obrazovky.", parent=admin_root)
        return

    if messagebox.askyesno("Potvrdit smazání", f"Opravdu chcete smazat uživatele '{selected_user['username']}' a všechny jeho trasy?", parent=admin_root):
        if database.delete_user(user_id_to_delete):
            messagebox.showinfo("Úspěch", f"Uživatel '{selected_user['username']}' byl smazán.", parent=admin_root)
            refresh_user_list() 
        else:
            messagebox.showerror("Chyba", "Nepodařilo se smazat uživatele.", parent=admin_root)


def add_new_user():
    """Allows admin to add a new user (non-admin by default)."""
    username = simpledialog.askstring("Přidat uživatele", "Uživatelské jméno:", parent=admin_root)
    if not username:
        return
    password = simpledialog.askstring("Přidat uživatele", "Heslo:", show='*', parent=admin_root)
    if not password:
        return

    if database.register_user(username, password, is_admin=0): 
        messagebox.showinfo("Úspěch", f"Uživatel '{username}' byl úspěšně přidán.", parent=admin_root)
        refresh_user_list()
    else:
        messagebox.showerror("Chyba", "Nepodařilo se přidat uživatele. Uživatelské jméno už možná existuje.", parent=admin_root)

def show_admin_page(parent_window, username, user_id):
    """
    Sets up the admin page within the given parent_window.
    This function is called from login_screen.py.
    """
    global admin_root, admin_username, admin_user_id, user_tree

    admin_root = parent_window # Use the main_app_window as the admin_root
    admin_username = username
    admin_user_id = user_id

    admin_root.title(f"Admin Panel pro {admin_username}")
    admin_root.geometry("700x500") # Resize for admin panel
    admin_root.deiconify() # Show the window again

    # Clear existing widgets from the parent_window (login screen)
    for widget in admin_root.winfo_children():
        widget.destroy()

    # Create a new frame for the admin content
    admin_frame = tk.Frame(admin_root, bg=BG_COLOR)
    admin_frame.pack(expand=True, fill="both")

    # Title
    tk.Label(admin_frame, text="Správa uživatelů", font=TITLE_FONT, bg=BG_COLOR, fg=FG_COLOR).pack(pady=PADDING)

    # Buttons for actions
    button_frame = tk.Frame(admin_frame, bg=BG_COLOR)
    button_frame.pack(pady=PADDING)

    ttk.Button(button_frame, text="Přidat nového uživatele", command=add_new_user).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Přepnout Admin Status", command=toggle_admin_status).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Smazat uživatele", command=delete_selected_user, style="Red.TButton").pack(side=tk.LEFT, padx=5)

    # Treeview for displaying users
    tree_frame = tk.Frame(admin_frame, bg=BG_COLOR)
    tree_frame.pack(pady=PADDING, padx=PADDING, fill="both", expand=True)

    tree_scroll = ttk.Scrollbar(tree_frame)
    tree_scroll.pack(side="right", fill="y")

    user_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode="browse")
    user_tree.pack(fill="both", expand=True)
    tree_scroll.config(command=user_tree.yview)

    user_tree['columns'] = ("Username", "Is Admin")
    user_tree.column("#0", width=0, stretch=tk.NO) 
    user_tree.column("Username", anchor="w", width=250)
    user_tree.column("Is Admin", anchor="center", width=100)

    user_tree.heading("#0", text="", anchor="w")
    user_tree.heading("Username", text="Uživatelské jméno", anchor="w")
    user_tree.heading("Is Admin", text="Admin", anchor="center")

    # Apply Treeview styling
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", 
                    background="#FFFFFF", 
                    foreground="#333333", 
                    rowheight=25, 
                    fieldbackground="#FFFFFF",
                    font=FONT)
    style.map("Treeview", 
              background=[("selected", "#347083")])
    style.configure("Red.TButton", background="red", foreground="white") 
    style.map("Red.TButton", background=[("active", "#cc0000")])

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
#     # This block would only run if admin_screen.py was executed directly,
#     # but now it's managed by login_screen.py
#     pass