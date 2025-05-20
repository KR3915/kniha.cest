import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import sys
import json
import requests

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
ROUTE_BG_COLOR = "#fffacd"  # Light yellow background for route entries
ROUTE_BORDER_COLOR = "#dda0dd"  # Purple border for route entries
ROUTE_BORDER_WIDTH = 1  # Border width

# Your TomTom API Key - REPLACE WITH YOUR ACTUAL KEY
TOMTOM_API_KEY = "Guh742xz9ZSxx11iki85pe5bvprH9xL9" 

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
    """Prompts the user for route name and destination, then calculates and adds distance automatically."""
    new_name = simpledialog.askstring("Nová trasa", "Jméno trasy:", parent=root)
    if not new_name:
        return  # User cancelled

    new_destination = simpledialog.askstring("Nová trasa", "Cíl:", parent=root)
    if not new_destination:
        return

    # Calculate the distance automatically using TomTom API
    new_distance_km = calculate_tomtom_route_distance_from_prague(new_destination)
    if new_distance_km is None:
        # If calculation fails, do not add the route and inform the user
        messagebox.showerror("Chyba", "Nepodařilo se vypočítat vzdálenost pro zadaný cíl. Zkontrolujte prosím adresu a API klíč.", parent=root)
        return

    # Format the distance for display and storage
    new_distance_str = f"{new_distance_km:.2f} km"

    new_route = {"name": new_name, "destination": new_destination, "distance": new_distance_str}

    user_routes.append(new_route)

    # Update route_names for the dropdown
    global route_names
    route_names = [route["name"] for route in user_routes]
    route_combo['values'] = route_names

    # Find the user and update their routes in the loaded data
    for user_data in login_data["users"]:
        if user_data["username"] == username:
            user_data["trasy"] = user_routes
            break

    save_login_data("login.json", login_data)
    messagebox.showinfo("Úspěch", "Trasa byla přidána.", parent=root)
    update_route_table()  # Update the table after adding a route

def show_page2():
    """Show page 2 (Vybrat trasu) and hide other pages."""
    page1.pack_forget()
    page3.pack_forget()
    page4.pack_forget()
    page2.pack(fill="both", expand=True)

def show_page1():
    """Show page 1 (Dashboard) and hide other pages."""
    page2.pack_forget()
    page3.pack_forget()
    page4.pack_forget()
    page1.pack(fill="both", expand=True)

def show_page3():
    """Show page 3 (Správa tras) and hide other pages."""
    page1.pack_forget()
    page2.pack_forget()
    page4.pack_forget()
    page3.pack(fill="both", expand=True)
    update_route_table()

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

    global route_names
    route_names = [route["name"] for route in user_routes]
    route_combo['values'] = route_names

    for user_data in login_data["users"]:
        if user_data["username"] == username:
            user_data["trasy"] = user_routes
            break

    save_login_data("login.json", login_data)
    update_route_table()

def update_edit_form():
    """Updates the entry fields on the edit route page."""
    route = user_routes[current_route_index]
    name_entry.delete(0, tk.END)
    name_entry.insert(0, route["name"])
    destination_entry.delete(0, tk.END)
    destination_entry.insert(0, route["destination"])
    
    # Distance is now auto-calculated, so this entry field will be updated after saving
    # For initial display, we still show the stored distance
    distance_entry.delete(0, tk.END)
    distance_entry.insert(0, route["distance"])


def save_edited_route():
    """Saves the edited route details, automatically recalculating distance."""
    new_name = name_entry.get()
    new_destination = destination_entry.get() # Get the potentially changed destination

    if not new_name or not new_destination:
        messagebox.showerror("Chyba", "Vyplňte jméno trasy a cíl.", parent=root)
        return

    # AUTOMATICALLY RECALCULATE DISTANCE based on the new_destination
    # We use the same function as for adding a new route, assuming origin is Prague
    recalculated_distance_km = calculate_tomtom_route_distance_from_prague(new_destination)
    if recalculated_distance_km is None:
        messagebox.showerror("Chyba", "Nepodařilo se přepočítat vzdálenost pro zadaný cíl. Zkontrolujte prosím adresu a API klíč.", parent=root)
        return
    
    new_distance_str = f"{recalculated_distance_km:.2f} km"

    # Update the UI field for distance to reflect the new calculated value
    distance_entry.delete(0, tk.END)
    distance_entry.insert(0, new_distance_str)

    update_route(current_route_index, new_name, new_destination, new_distance_str)
    messagebox.showinfo("Úspěch", "Trasa byla upravena.", parent=root)
    show_page3()

def update_route_table():
    """Updates the table to display the user's routes."""
    for widget in route_table_frame.winfo_children():
        widget.destroy()

    headers = ["Název", "Cíl", "Vzdálenost", ""]
    for i, header in enumerate(headers):
        header_label = tk.Label(route_table_frame, text=header, font=FONT, bg=BG_COLOR, fg=FG_COLOR)
        header_label.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")

    for i, route in enumerate(user_routes):
        route_entry_frame = tk.Frame(route_table_frame, bg=ROUTE_BG_COLOR,
                                     highlightbackground=ROUTE_BORDER_COLOR,
                                     highlightthickness=ROUTE_BORDER_WIDTH)
        route_entry_frame.grid(row=i + 1, columnspan=len(headers), sticky="ew", padx=2, pady=2)

        name_label = tk.Label(route_entry_frame, text=route["name"], font=FONT, bg=ROUTE_BG_COLOR, fg=FG_COLOR)
        destination_label = tk.Label(route_entry_frame, text=route["destination"], font=FONT, bg=ROUTE_BG_COLOR, fg=FG_COLOR)
        distance_label = tk.Label(route_entry_frame, text=route["distance"], font=FONT, bg=ROUTE_BG_COLOR, fg=FG_COLOR)
        edit_button = tk.Button(route_entry_frame, text="Upravit",
                                 command=lambda index=i: show_page4(index),
                                 bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG, font=FONT)

        name_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        destination_label.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        distance_label.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        edit_button.grid(row=0, column=3, padx=5, pady=5)

        route_entry_frame.columnconfigure(0, weight=1)
        route_entry_frame.columnconfigure(1, weight=1)
        route_entry_frame.columnconfigure(2, weight=1)
        route_entry_frame.columnconfigure(3, weight=0)

    route_table_frame.columnconfigure(0, weight=1)
    route_table_frame.columnconfigure(1, weight=1)
    route_table_frame.columnconfigure(2, weight=1)
    route_table_frame.columnconfigure(3, weight=0)

# --- TomTom API Functions ---
def geocode_address(address):
    """
    Geocodes an address using TomTom Search API to get its coordinates.
    Returns coordinates as "lat,lon" string or None on failure.
    """
    geocode_url = f"https://api.tomtom.com/search/2/geocode/{requests.utils.quote(address)}.json?key={TOMTOM_API_KEY}"
    try:
        response = requests.get(geocode_url)
        response.raise_for_status()
        data = response.json()
        if data and data.get('results'):
            position = data['results'][0]['position']
            return f"{position['lat']},{position['lon']}"
        else:
            return None
    except requests.exceptions.RequestException:
        return None
    except json.JSONDecodeError:
        return None

def calculate_tomtom_route_distance_from_prague(destination_address):
    """
    Calculates the route distance from Prague to the given destination address.
    Returns the distance in kilometers, or None on failure.
    """
    start_address = "Prague, Czechia" # Fixed starting point for all routes

    start_coords = geocode_address(start_address)
    destination_coords = geocode_address(destination_address)

    if not start_coords or not destination_coords:
        return None

    routing_url = (
        f"https://api.tomtom.com/routing/1/calculateRoute/{start_coords}:{destination_coords}/json"
        f"?key={TOMTOM_API_KEY}"
    )

    try:
        response = requests.get(routing_url)
        response.raise_for_status()
        route_data = response.json()

        if route_data and route_data.get('routes'):
            distance_meters = route_data['routes'][0]['summary']['lengthInMeters']
            distance_km = distance_meters / 1000
            return distance_km
        else:
            return None

    except requests.exceptions.RequestException:
        return None
    except json.JSONDecodeError:
        return None


if __name__ == "__main__":
    username = "Neznámý uživatel"
    current_route_index = -1

    if len(sys.argv) > 1:
        username = sys.argv[1]
        print(f"Uživatelské jméno přihlášeného uživatele: {username}")

    login_data = load_login_data("login.json")
    user_routes = load_routes(login_data, username)
    route_names = [route["name"] for route in user_routes]

    root = tk.Tk()
    root.title(f"Uživatelská obrazovka pro {username}")
    root.geometry("600x600")
    root.configure(bg=BG_COLOR)

    # --- Page 1 (Dashboard) ---
    page1 = tk.Frame(root, bg=BG_COLOR)

    welcome_label = tk.Label(page1, text=f"Vítejte, {username}!", font=TITLE_FONT, bg=BG_COLOR, fg=FG_COLOR)
    welcome_label.pack(pady=PADDING)

    spravovat_trasy_button = tk.Button(page1, text="Spravovat trasy", command=show_page3, padx=BUTTON_PADDING_X, pady=BUTTON_PADDING_Y,
                                     bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG, font=FONT)
    spravovat_trasy_button.pack(pady=PADDING)

    vybrat_trasu_button = tk.Button(page1, text="Vybrat trasu", command=show_page2, padx=BUTTON_PADDING_X, pady=BUTTON_PADDING_Y,
                                  bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG, font=FONT)
    vybrat_trasu_button.pack(pady=PADDING)

    # --- Page 2 (Vybrat trasu) ---
    page2 = tk.Frame(root, bg=BG_COLOR)

    route_label = tk.Label(page2, text="Vyberte trasu:", font=FONT, bg=BG_COLOR, fg=FG_COLOR)
    route_label.pack(pady=PADDING)
    route_combo = ttk.Combobox(page2, values=route_names, state="readonly", font=FONT)
    route_combo.pack(pady=PADDING)
    route_combo.bind("<<ComboboxSelected>>", lambda event: show_route_details())

    details_label = tk.Label(page2, text="Vyberte trasu", font=FONT, bg=BG_COLOR, fg=FG_COLOR)
    details_label.pack(pady=PADDING)

    zpet_na_dashboard_button2 = tk.Button(page2, text="Zpět", command=show_page1, padx=BUTTON_PADDING_X, pady=BUTTON_PADDING_Y,
                                          bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG, font=FONT)
    zpet_na_dashboard_button2.pack(side="bottom", pady=PADDING, fill="x")

    # --- Page 3 (Spravovat trasy) ---
    page3 = tk.Frame(root, bg=BG_COLOR)

    pridat_trasu_button = tk.Button(page3, text="Přidat trasu", command=add_route, padx=BUTTON_PADDING_X, pady=BUTTON_PADDING_Y,
                                     bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG, font=FONT)
    pridat_trasu_button.pack(pady=PADDING)

    route_table_frame = tk.Frame(page3, bg=BG_COLOR)
    route_table_frame.pack(pady=PADDING, fill="both", expand=True)

    zpet_na_dashboard_button3 = tk.Button(page3, text="Zpět", command=show_page1, padx=BUTTON_PADDING_X, pady=BUTTON_PADDING_Y,
                                          bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG, font=FONT)
    zpet_na_dashboard_button3.pack(side="bottom", pady=PADDING, fill="x")

    # --- Page 4 (Edit Route) ---
    page4 = tk.Frame(root, bg=BG_COLOR)

    name_label = tk.Label(page4, text="Název:", font=FONT, bg=BG_COLOR, fg=FG_COLOR)
    name_label.pack(pady=5)
    name_entry = tk.Entry(page4, font=FONT, bg="white", fg=FG_COLOR, relief="solid", bd=1)
    name_entry.pack(pady=5, fill="x", padx=PADDING)

    destination_label = tk.Label(page4, text="Cíl:", font=FONT, bg=BG_COLOR, fg=FG_COLOR)
    destination_label.pack(pady=5)
    destination_entry = tk.Entry(page4, font=FONT, bg="white", fg=FG_COLOR, relief="solid", bd=1)
    destination_entry.pack(pady=5, fill="x", padx=PADDING)

    distance_label = tk.Label(page4, text="Vzdálenost:", font=FONT, bg=BG_COLOR, fg=FG_COLOR)
    distance_label.pack(pady=5)
    distance_entry = tk.Entry(page4, font=FONT, bg="lightgray", fg=FG_COLOR, relief="solid", bd=1, state="readonly") # Changed to readonly
    distance_entry.pack(pady=5, fill="x", padx=PADDING)

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