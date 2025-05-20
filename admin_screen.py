import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import subprocess # Already imported in login screen.py but good to keep if admin_screen starts independently

# --- Constants for Styling (can be imported or defined similarly to user_screen.py) ---
BG_COLOR = "#f0f0f0"
FG_COLOR = "#333333"
BUTTON_BG = "#e0e0e0"
BUTTON_FG = FG_COLOR
BUTTON_ACTIVE_BG = "#d0d0d0"
FONT = ("Segoe UI", 10)
TITLE_FONT = ("Segoe UI", 16, "bold")
PADDING = 10
BUTTON_PADDING_X = 15
BUTTON_PADDING_Y = 8

LOGIN_FILE = "login.json" # Centralize the filename

def load_login_data(file):
    """Loads the entire login data from the JSON file."""
    try:
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        messagebox.showerror("Chyba", f"Soubor '{file}' nebyl nalezen!", parent=admin_window)
        return {"users": []} # Return empty structure if file not found
    except json.JSONDecodeError:
        messagebox.showerror("Chyba", f"Neplatný formát JSON v souboru '{file}'!", parent=admin_window)
        return {"users": []}

def save_login_data(file, data):
    """Saves the modified login data back to the JSON file."""
    try:
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False) # ensure_ascii=False pro češtinu
    except Exception as e:
        messagebox.showerror("Chyba ukládání", f"Chyba při ukládání dat do souboru '{file}': {e}", parent=admin_window)

def refresh_user_list():
    """Clears and repopulates the Treeview with current user data."""
    for i in user_tree.get_children():
        user_tree.delete(i)
    
    data = load_login_data(LOGIN_FILE)
    if data and "users" in data:
        for user in data["users"]:
            username = user.get("username", "N/A")
            is_admin = "Ano" if user.get("admin") == "1" else "Ne"
            # We don't display password for security reasons
            user_tree.insert("", "end", values=(username, is_admin))

def add_user():
    """Prompts for new user details and adds them to login.json."""
    new_username = simpledialog.askstring("Přidat uživatele", "Zadejte nové uživatelské jméno:", parent=admin_window)
    if not new_username:
        return

    new_password = simpledialog.askstring("Přidat uživatele", f"Zadejte heslo pro '{new_username}':", parent=admin_window)
    if not new_password:
        return
    
    is_admin_response = messagebox.askyesno("Přidat uživatele", f"Má být uživatel '{new_username}' administrátor?", parent=admin_window)
    is_admin_str = "1" if is_admin_response else "0"

    data = load_login_data(LOGIN_FILE)
    if not data: # Should not happen if load_login_data returns empty dict
        data = {"users": []}

    # Check if username already exists
    for user in data.get("users", []):
        if user.get("username") == new_username:
            messagebox.showerror("Chyba", "Uživatel s tímto jménem již existuje!", parent=admin_window)
            return

    new_user_data = {
        "username": new_username,
        "password": new_password, # In a real app, this would be hashed!
        "admin": is_admin_str
    }
    data["users"].append(new_user_data)
    save_login_data(LOGIN_FILE, data)
    messagebox.showinfo("Úspěch", f"Uživatel '{new_username}' byl přidán.", parent=admin_window)
    refresh_user_list()

def remove_user():
    """Removes the selected user from login.json."""
    selected_item = user_tree.selection()
    if not selected_item:
        messagebox.showwarning("Upozornění", "Vyberte uživatele k odstranění.", parent=admin_window)
        return

    username_to_remove = user_tree.item(selected_item, "values")[0]

    if username_to_remove == "admin":
        messagebox.showerror("Chyba", "Administrátorský účet 'admin' nelze odstranit!", parent=admin_window)
        return
    
    if messagebox.askyesno("Potvrzení", f"Opravdu chcete odstranit uživatele '{username_to_remove}'?", parent=admin_window):
        data = load_login_data(LOGIN_FILE)
        if not data:
            return

        initial_user_count = len(data.get("users", []))
        data["users"] = [user for user in data.get("users", []) if user.get("username") != username_to_remove]
        
        if len(data["users"]) < initial_user_count:
            save_login_data(LOGIN_FILE, data)
            messagebox.showinfo("Úspěch", f"Uživatel '{username_to_remove}' byl odstraněn.", parent=admin_window)
            refresh_user_list()
        else:
            messagebox.showwarning("Chyba", f"Uživatel '{username_to_remove}' nebyl nalezen.", parent=admin_window)


def show_main_admin_page():
    """Function to display the main admin dashboard."""
    global admin_window
    admin_window = tk.Toplevel() # Use Toplevel for a new window
    admin_window.title("Admin Dashboard")
    admin_window.geometry("800x600")
    admin_window.configure(bg=BG_COLOR)

    # Main frame for content
    content_frame = tk.Frame(admin_window, bg=BG_COLOR)
    content_frame.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)

    # Title
    title_label = tk.Label(content_frame, text="Správa uživatelů", font=TITLE_FONT, bg=BG_COLOR, fg=FG_COLOR)
    title_label.pack(pady=PADDING)

    # User Management Section
    user_management_frame = tk.LabelFrame(content_frame, text="Uživatelé", font=FONT, bg=BG_COLOR, fg=FG_COLOR, padx=PADDING, pady=PADDING)
    user_management_frame.pack(fill="both", expand=True, pady=PADDING)

    # Treeview for displaying users
    global user_tree
    user_tree = ttk.Treeview(user_management_frame, columns=("Username", "Admin"), show="headings", height=10)
    user_tree.heading("Username", text="Uživatelské jméno")
    user_tree.heading("Admin", text="Admin")
    user_tree.column("Username", width=200, anchor="center")
    user_tree.column("Admin", width=100, anchor="center")
    user_tree.pack(fill="both", expand=True)

    # Scrollbar for Treeview
    scrollbar = ttk.Scrollbar(user_management_frame, orient="vertical", command=user_tree.yview)
    user_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")


    # Buttons for user actions
    button_frame = tk.Frame(user_management_frame, bg=BG_COLOR)
    button_frame.pack(pady=PADDING)

    add_user_button = tk.Button(button_frame, text="Přidat uživatele", command=add_user,
                                bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG, font=FONT, padx=BUTTON_PADDING_X, pady=BUTTON_PADDING_Y)
    add_user_button.pack(side="left", padx=5)

    remove_user_button = tk.Button(button_frame, text="Odebrat uživatele", command=remove_user,
                                   bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG, font=FONT, padx=BUTTON_PADDING_X, pady=BUTTON_PADDING_Y)
    remove_user_button.pack(side="left", padx=5)

    # Back button to close admin window
    back_button = tk.Button(admin_window, text="Zpět na přihlášení", command=admin_window.destroy, # Closes the admin window
                            bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG, font=FONT, padx=BUTTON_PADDING_X, pady=BUTTON_PADDING_Y)
    back_button.pack(side="bottom", pady=PADDING)


    refresh_user_list() # Populate the list on startup

# This part is for testing admin_screen.py directly
if __name__ == "__main__":
    # Simulate a main window that would typically call this
    # Or, if running standalone, you'd just call show_main_admin_page()
    root_test = tk.Tk()
    root_test.withdraw() # Hide the root test window
    show_main_admin_page()
    root_test.mainloop()