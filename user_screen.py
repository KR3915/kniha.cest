import tkinter as tk
from tkinter import ttk, simpledialog, messagebox  # Import simpledialog and messagebox
import sys
import json

# --- Styling Constants (Minimalist Theme) ---
BG_COLOR = "#f0f0f0"  # Light gray background
FG_COLOR = "#333333"  # Dark gray foreground (text)
BUTTON_BG = "#e0e0e0"  # Light gray button background
BUTTON_FG = FG_COLOR
BUTTON_ACTIVE_BG = "#d0d0d0"
FONT = ("Segoe UI", 12)  # Clean, modern font
TITLE_FONT = ("Segoe UI", 16, "bold")
PADDING = 10
BUTTON_PADDING_X = 20
BUTTON_PADDING_Y = 10

def load_login_data(file):
    """Loads the entire login data from the JSON file."""
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {file} not found!")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {file}!")
        return {}

def save_login_data(file, data):
    """Saves the modified login data back to the JSON file."""
    try:
        with open(file, 'w') as f:
            json.dump(data, f, indent=2)  # Use indent for readability
    except Exception as e:
        print(f"Error saving data to {file}: {e}")

def load_routes(data, username):
    """Loads routes specific to the given username from the loaded data."""
    for user_data in data.get("users", []):
        if user_data.get("username") == username:
            return user_data.get("trasy", [])  # Return list of routes
    return []  # Return empty list if user or routes not found

def show_route_details():
    """Displays the distance and destination of the selected route."""
    selected_route_name = route_combo.get()
    for route in user_routes:
        if route["name"] == selected_route_name:
            distance = route.get("distance", "N/A")
            destination = route.get("destination", "N/A")
            details_label.config(text=f"Cíl: {destination}, Vzdálenost: {distance}")
            return
    details_label.config(text="Vyberte trasu")

def add_route():
    """Prompts the user for route details and adds it to the user's routes."""
    new_name = simpledialog.askstring("Nová trasa", "Jméno trasy:", parent=root)  # Parent argument
    if not new_name:
        return  # User cancelled

    new_destination = simpledialog.askstring("Nová trasa", "Cíl:", parent=root)
    if not new_destination:
        return

    new_distance = simpledialog.askstring("Nová trasa", "Vzdálenost:", parent=root)
    if not new_distance:
        return

    new_route = {"name": new_name, "destination": new_destination, "distance": new_distance}
    user_routes.append(new_route)  # Add to the in-memory data
    route_names.append(new_name)  # Update dropdown options
    route_combo['values'] = route_names  # Refresh the Combobox

    # Find the user and update their routes in the loaded data
    for user_data in login_data["users"]:
        if user_data["username"] == username:
            user_data["trasy"] = user_routes
            break

    save_login_data("login.json", login_data)  # Save the changes to the file
    messagebox.showinfo("Úspěch", "Trasa byla přidána.", parent=root)  # Parent argument
    update_route_table()  # Update the table after adding a route

def show_page2():
    """Show page 2 (Vybrat trasu) and hide other pages."""
    page1.pack_forget()
    page3.pack_forget()
    page4.pack_forget()
    page2.pack(fill="both", expand=True)  # Fill and expand
    root.update_idletasks()

def show_page1():
    """Show page 1 (Dashboard) and hide other pages."""
    page2.pack_forget()
    page3.pack_forget()
    page4.pack_forget()
    page1.pack(fill="both", expand=True)  # Fill and expand

def show_page3():
    """Show page 3 (Správa tras) and hide other pages."""
    page1.pack_forget()
    page2.pack_forget()
    page4.pack_forget()
    page3.pack(fill="both", expand=True)  # Fill and expand
    update_route_table()  # Update the table when showing the page

def show_page4(route_index):
    """Show page 4 (Edit Route) and hide other pages."""
    global current_route_index
    current_route_index = route_index
    page1.pack_forget()
    page2.pack_forget()
    page3.pack_forget()
    page4.pack(fill="both", expand=True)
    update_edit_form()

def update_route(route_index, new_name, new_destination, new_distance):
    """Updates the route details in the data and saves it."""
    user_routes[route_index]["name"] = new_name
    user_routes[route_index]["destination"] = new_destination
    user_routes[route_index]["distance"] = new_distance

    # Find the user and update their routes in the loaded data
    for user_data in login_data["users"]:
        if user_data["username"] == username:
            user_data["trasy"] = user_routes
            break

    save_login_data("login.json", login_data)
    update_route_table()  # Refresh the route table

def update_edit_form():
    """Updates the entry fields on the edit route page."""
    route = user_routes[current_route_index]
    name_entry.delete(0, tk.END)
    name_entry.insert(0, route["name"])
    destination_entry.delete(0, tk.END)
    destination_entry.insert(0, route["destination"])
    distance_entry.delete(0, tk.END)
    distance_entry.insert(0, route["distance"])

def save_edited_route():
    """Saves the edited route details."""
    new_name = name_entry.get()
    new_destination = destination_entry.get()
    new_distance = distance_entry.get()

    if not new_name or not new_destination or not new_distance:
        messagebox.showerror("Chyba", "Vyplňte všechna pole.", parent=root)
        return

    update_route(current_route_index, new_name, new_destination, new_distance)
    messagebox.showinfo("Úspěch", "Trasa byla upravena.", parent=root)
    show_page3()  # Go back to the route management page

def update_route_table():
    """Updates the table to display the user's routes."""
    # Clear existing table rows
    for widget in route_table_frame.winfo_children():
        widget.destroy()

    # Create table headers
    headers = ["Název", "Cíl", "Vzdálenost", "Upravit"]
    for i, header in enumerate(headers):
        header_label = tk.Label(route_table_frame, text=header, font=FONT, bg=BG_COLOR, fg=FG_COLOR)
        header_label.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")  # Fill cells

    # Populate table with route data
    for i, route in enumerate(user_routes):
        name_label = tk.Label(route_table_frame, text=route["name"], font=FONT, bg=BG_COLOR, fg=FG_COLOR)
        destination_label = tk.Label(route_table_frame, text=route["destination"], font=FONT, bg=BG_COLOR, fg=FG_COLOR)
        distance_label = tk.Label(route_table_frame, text=route["distance"], font=FONT, bg=BG_COLOR, fg=FG_COLOR)
        edit_button = tk.Button(route_table_frame, text="Upravit",
                                 command=lambda index=i: show_page4(index),  # Pass index to command
                                 bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG, font=FONT)

        name_label.grid(row=i + 1, column=0, padx=5, pady=5, sticky="nsew")  # Fill cells
        destination_label.grid(row=i + 1, column=1, padx=5, pady=5, sticky="nsew")
        distance_label.grid(row=i + 1, column=2, padx=5, pady=5, sticky="nsew")
        edit_button.grid(row=i + 1, column=3, padx=5, pady=5)

    # Configure grid weights to make columns resize properly
    for i in range(len(headers)):
        route_table_frame.columnconfigure(i, weight=1)

if __name__ == "__main__":
    username = "Neznámý uživatel"
    if len(sys.argv) > 1:
        username = sys.argv[1]
        print(f"Uživatelské jméno přihlášeného uživatele: {username}")

    # Load the entire login data
    login_data = load_login_data("login.json")
    # Load user-specific routes
    user_routes = load_routes(login_data, username)
    route_names = [route["name"] for route in user_routes]

    # Create the main window
    root = tk.Tk()
    root.title(f"Uživatelská obrazovka pro {username}")
    root.geometry("600x600")  # Increased window height

    # --- Rounded Corners (Platform Dependent - Basic Approximation) ---
    # Tkinter doesn't have built-in rounded corners. This is a simplification.
    # For true rounded corners, you'd need a canvas and draw arcs, which is more complex.
    # We'll simulate it a bit with padding and background colors.

    root.configure(bg=BG_COLOR)  # Set root background

    # Page 1 (Dashboard)
    page1 = tk.Frame(root, bg=BG_COLOR)
    page1.pack(pady=PADDING, padx=PADDING, fill="both", expand=True)  # Fill and expand

    welcome_label = tk.Label(page1, text=f"Vítejte, {username}!", font=TITLE_FONT, bg=BG_COLOR, fg=FG_COLOR)
    welcome_label.pack(pady=PADDING)

    spravovat_trasy_button = tk.Button(page1, text="Spravovat trasy", command=show_page3, padx=BUTTON_PADDING_X, pady=BUTTON_PADDING_Y,
                                     bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG, font=FONT)
    spravovat_trasy_button.pack(pady=PADDING)

    vybrat_trasu_button = tk.Button(page1, text="Vybrat trasu", command=show_page2, padx=BUTTON_PADDING_X, pady=BUTTON_PADDING_Y,
                                  bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG, font=FONT)
    vybrat_trasu_button.pack(pady=PADDING)

    # Page 2 (Vybrat trasu)
    page2 = tk.Frame(root, bg=BG_COLOR)
    page2.pack(pady=PADDING, padx=PADDING, fill="both", expand=True)  # Fill and expand

    # Dropdown for selecting routes
    route_label = tk.Label(page2, text="Vyberte trasu:", font=FONT, bg=BG_COLOR, fg=FG_COLOR)
    route_label.pack(pady=PADDING)
    route_combo = ttk.Combobox(page2, values=route_names, state="readonly", font=FONT)
    route_combo.pack(pady=PADDING)
    route_combo.bind("<<ComboboxSelected>>", lambda event: show_route_details())

    # Label to display route details
    details_label = tk.Label(page2, text="Vyberte trasu", font=FONT, bg=BG_COLOR, fg=FG_COLOR)
    details_label.pack(pady=PADDING)

    zpet_na_dashboard_button2 = tk.Button(page2, text="Zpět", command=show_page1, padx=BUTTON_PADDING_X, pady=BUTTON_PADDING_Y,
                                         bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG, font=FONT)
    zpet_na_dashboard_button2.pack(side="bottom", pady=PADDING, fill="x")  # Fill x

    # Page 3 (Spravovat trasy)
    page3 = tk.Frame(root, bg=BG_COLOR)
    page3.pack(pady=PADDING, padx=PADDING, fill="both", expand=True)  # Fill and expand

    pridat_trasu_button = tk.Button(page3, text="Přidat trasu", command=add_route, padx=BUTTON_PADDING_X, pady=BUTTON_PADDING_Y,
                                    bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG, font=FONT)
    pridat_trasu_button.pack(pady=PADDING)

    # Frame to hold the route table
    route_table_frame = tk.Frame(page3, bg=BG_COLOR)
    route_table_frame.pack(pady=PADDING, fill="both", expand=True)

    zpet_na_dashboard_button3 = tk.Button(page3, text="Zpět", command=show_page1, padx=BUTTON_PADDING_X, pady=BUTTON_PADDING_Y,
                                         bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG, font=FONT)
    zpet_na_dashboard_button3.pack(side="bottom", pady=PADDING, fill="x")  # Fill x

    # Page 4 (Edit Route)
    page4 = tk.Frame(root, bg=BG_COLOR)
    page4.pack(pady=PADDING, padx=PADDING, fill="both", expand=True)

    name_label = tk.Label(page4, text="Název:", font=FONT, bg=BG_COLOR, fg=FG_COLOR)
    name_label.pack(pady=5)
    name_entry = tk.Entry(page4, font=FONT, bg="white", fg=FG_COLOR)
    name_entry.pack(pady=5, fill="x")

    destination_label = tk.Label(page4, text="Cíl:", font=FONT, bg=BG_COLOR, fg=FG_COLOR)
    destination_label.pack(pady=5)
    destination_entry = tk.Entry(page4, font=FONT, bg="white", fg=FG_COLOR)
    destination_entry.pack(pady=5, fill="x")

    distance_label = tk.Label(page4, text="Vzdálenost:", font=FONT, bg=BG_COLOR, fg=FG_COLOR)
    distance_label.pack(pady=5)
    distance_entry = tk.Entry(page4, font=FONT, bg="white", fg=FG_COLOR)
    distance_entry.pack(pady=5, fill="x")

    save_button = tk.Button(page4, text="Uložit", command=save_edited_route, padx=BUTTON_PADDING_X, pady=BUTTON_PADDING_Y,
                             bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG, font=FONT)
    save_button.pack(pady=10)

    zpet_na_spravu_button = tk.Button(page4, text="Zpět na správu tras", command=show_page3, padx=BUTTON_PADDING_X, pady=BUTTON_PADDING_Y,
                                     bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG, font=FONT)
    zpet_na_spravu_button.pack(side="bottom", pady=PADDING, fill="x")

    # Initially show page 1
    show_page1()

    # Run the Tkinter event loop
    root.mainloop()