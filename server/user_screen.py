# user_screen.py
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import requests
import database

# --- Styling Constants (Minimalist Theme) ---
BG_COLOR = "#f0f0f0"  # Light gray background
FG_COLOR = "#333333"  # Dark gray foreground (text)
BUTTON_BG = "#e0e0e0"  # Light gray button background
BUTTON_FG = FG_COLOR
BUTTON_ACTIVE_BG = "#d0d0d0"
FONT = ("Segoe UI", 12)
TITLE_FONT = ("Segoe UI", 16, "bold")
PADDING = 10
BUTTON_PADDING_X = 20
BUTTON_PADDING_Y = 10

# Your TomTom API Key - REPLACE WITH YOUR ACTUAL KEY
TOMTOM_API_KEY = "Guh742xz9ZSxx11iki85pe5bvprH9xL9" # Použijte váš skutečný klíč!

# Global variables specific to the user screen
user_root = None
current_username = "Unknown User"
current_user_id = None
user_routes_tree = None
all_user_routes_cached = [] # To store all fetched route data for filtering/sorting

# Global variables for filter entries
filter_name_entry = None
filter_start_entry = None
filter_destination_entry = None
filter_fuel_var = None

# Global variables for sorting controls
current_sort_column = "name"
current_sort_order = "asc" # Default sort order

# Nová globální proměnná pro uložení callbacku pro návrat na login
_create_login_widgets_callback = None # Bude nastaveno v show_user_page

def show_user_page(parent_window, username, user_id, create_login_widgets_callback_func):
    """
    Zobrazí uživatelský panel.
    :param parent_window: Kořenové okno Tkinteru.
    :param username: Uživatelské jméno přihlášeného uživatele.
    :param user_id: ID přihlášeného uživatele.
    :param create_login_widgets_callback_func: Callback funkce z login_screen pro návrat zpět na login.
    """
    global user_root, current_username, current_user_id, _create_login_widgets_callback, all_user_routes_cached

    user_root = parent_window
    current_username = username
    current_user_id = user_id
    _create_login_widgets_callback = create_login_widgets_callback_func # Uložení callbacku

    user_root.title(f"Uživatelský panel pro {current_username}")
    user_root.geometry("900x750") # Vrátíme šířku na 900, protože bude méně řadicích tlačítek
    user_root.deiconify() # Ensure the window is visible

    for widget in user_root.winfo_children():
        widget.destroy()

    # Reset cached data when user page is shown
    all_user_routes_cached = [] 
    create_user_page_layout()

def create_user_page_layout():
    """Vytvoří rozložení prvků uživatelského panelu."""
    global user_routes_tree, filter_name_entry, filter_start_entry, filter_destination_entry, filter_fuel_var, current_sort_column, current_sort_order

    # Style configuration
    style = ttk.Style(user_root)
    style.theme_use("clam")
    style.configure("TFrame", background=BG_COLOR)
    style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR, font=FONT)
    style.configure("TEntry", font=FONT)
    style.configure("TButton", font=FONT, background=BUTTON_BG, foreground=BUTTON_FG, padding=(BUTTON_PADDING_X, BUTTON_PADDING_Y))
    style.map("TButton", background=[("active", BUTTON_ACTIVE_BG)])
    
    # Specific style for small sort buttons
    style.configure("Sort.TButton", font=("Segoe UI", 10), padding=(5, 2)) # Menší padding
    style.map("Sort.TButton", background=[("active", BUTTON_ACTIVE_BG)])


    style.configure("Treeview", font=FONT, rowheight=25)
    style.configure("Treeview.Heading", font=(FONT[0], FONT[1], "bold"))
    style.map("Treeview", background=[("selected", "#347083")])
    style.configure("TCheckbutton", background=BG_COLOR, foreground=FG_COLOR, font=FONT)
    style.configure("TRadiobutton", background=BG_COLOR, foreground=FG_COLOR, font=FONT)
    style.configure("TCombobox", font=FONT)


    main_frame = ttk.Frame(user_root, padding=PADDING)
    main_frame.pack(fill="both", expand=True)

    # Title
    title_label = ttk.Label(main_frame, text=f"Vítejte, {current_username}! Správa tras", font=TITLE_FONT)
    title_label.pack(pady=(0, PADDING * 2))

    # --- Filtering and Sorting Section ---
    filter_sort_frame = ttk.LabelFrame(main_frame, text="Filtrování a řazení tras", padding=PADDING)
    filter_sort_frame.pack(fill="x", pady=PADDING)

    # Filter entries
    filter_controls_frame = ttk.Frame(filter_sort_frame)
    filter_controls_frame.pack(fill="x", pady=5)
    filter_controls_frame.columnconfigure(1, weight=1) # Make entry columns expand

    ttk.Label(filter_controls_frame, text="Název:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
    filter_name_entry = ttk.Entry(filter_controls_frame)
    filter_name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

    ttk.Label(filter_controls_frame, text="Start:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    filter_start_entry = ttk.Entry(filter_controls_frame)
    filter_start_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

    ttk.Label(filter_controls_frame, text="Cíl:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
    filter_destination_entry = ttk.Entry(filter_controls_frame)
    filter_destination_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

    filter_fuel_var = tk.StringVar(value="Vše") # 'Vše', 'Ano', 'Ne'
    ttk.Radiobutton(filter_controls_frame, text="Po cestě tankovat: Vše", variable=filter_fuel_var, value="Vše").grid(row=0, column=2, padx=10, sticky="w")
    ttk.Radiobutton(filter_controls_frame, text="Po cestě tankovat: Ano", variable=filter_fuel_var, value="Ano").grid(row=1, column=2, padx=10, sticky="w")
    ttk.Radiobutton(filter_controls_frame, text="Po cestě tankovat: Ne", variable=filter_fuel_var, value="Ne").grid(row=2, column=2, padx=10, sticky="w")


    filter_button = ttk.Button(filter_sort_frame, text="Filtrovat", command=apply_filters_and_sort)
    filter_button.pack(pady=5)

    # --- Sorting Buttons (UPDATED IMPLEMENTATION) ---
    sort_buttons_frame = ttk.Frame(filter_sort_frame)
    sort_buttons_frame.pack(fill="x", pady=5)

    # Define only the columns to be sortable
    sortable_columns = {
        "name": "Název",
        "distance": "Vzdálenost"
    }
    
    # Create buttons for each sortable column (Ascending and Descending)
    # Using grid for better control over spacing
    sort_row_index = 0
    col_index = 0
    for col_name, display_name in sortable_columns.items():
        # Frame for each column's sort buttons
        col_button_frame = ttk.Frame(sort_buttons_frame)
        col_button_frame.grid(row=sort_row_index, column=col_index, padx=5, pady=2, sticky="w")
        
        ttk.Label(col_button_frame, text=f"Seřadit podle:{display_name}:").pack(side="left", padx=(0, 5))
        
        ttk.Button(col_button_frame, text="↑", style="Sort.TButton",
                   command=lambda c=col_name: set_sort_and_apply(c, "asc")).pack(side="left", padx=1)
        ttk.Button(col_button_frame, text="↓", style="Sort.TButton",
                   command=lambda c=col_name: set_sort_and_apply(c, "desc")).pack(side="left", padx=1)
        
        col_index += 1
        if col_index >= 2: # Max 2 columns per row for better layout
            col_index = 0
            sort_row_index += 1

    # Ensure the sorting frame columns expand properly
    for i in range(2): # Assuming max 2 columns of sort buttons
        sort_buttons_frame.columnconfigure(i, weight=1)


    filter_name_entry.bind("<KeyRelease>", lambda e: apply_filters_and_sort())
    filter_start_entry.bind("<KeyRelease>", lambda e: apply_filters_and_sort())
    filter_destination_entry.bind("<KeyRelease>", lambda e: apply_filters_and_sort())
    filter_fuel_var.trace_add("write", lambda *args: apply_filters_and_sort())


    # --- Treeview for Routes ---
    routes_frame = ttk.Frame(main_frame)
    routes_frame.pack(fill="both", expand=True, pady=PADDING)

    columns = ("name", "start_location", "destination", "distance", "needs_fuel")
    user_routes_tree = ttk.Treeview(routes_frame, columns=columns, show="headings")
    user_routes_tree.pack(side="left", fill="both", expand=True)

    # Define headings
    user_routes_tree.heading("name", text="Název")
    user_routes_tree.heading("start_location", text="Počáteční místo")
    user_routes_tree.heading("destination", text="Cíl")
    user_routes_tree.heading("distance", text="Vzdálenost")
    user_routes_tree.heading("needs_fuel", text="Potřeba paliva")

    # Column widths
    user_routes_tree.column("name", width=150, stretch=tk.YES)
    user_routes_tree.column("start_location", width=200, stretch=tk.YES)
    user_routes_tree.column("destination", width=200, stretch=tk.YES)
    user_routes_tree.column("distance", width=100, stretch=tk.YES)
    user_routes_tree.column("needs_fuel", width=100, stretch=tk.YES)

    # Scrollbar
    scrollbar = ttk.Scrollbar(routes_frame, orient="vertical", command=user_routes_tree.yview)
    user_routes_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # --- Buttons for Route Management ---
    button_frame = ttk.Frame(main_frame, padding=(0, PADDING))
    button_frame.pack(fill="x", pady=PADDING)

    # Nový vnořený rámeček pro hlavní akční tlačítka (Přidat, Upravit, Smazat)
    action_buttons_frame = ttk.Frame(button_frame)
    action_buttons_frame.pack(side="left", expand=True, fill="x") # Expand tento rámeček

    ttk.Button(action_buttons_frame, text="Přidat trasu", command=add_route_dialog).pack(side="left", padx=5, expand=True)
    ttk.Button(action_buttons_frame, text="Upravit trasu", command=edit_route_dialog).pack(side="left", padx=5, expand=True)
    ttk.Button(action_buttons_frame, text="Smazat trasu", command=delete_route_confirm).pack(side="left", padx=5, expand=True)
    
    # Ostatní tlačítka
    ttk.Button(button_frame, text="Aktualizovat seznam", command=lambda: apply_filters_and_sort(force_fetch=True)).pack(side="left", padx=5, expand=True)
    ttk.Button(button_frame, text="Zpět na přihlášení", command=go_back_to_login).pack(side="right", padx=5) # pack "Zpět" na pravou stranu


    apply_filters_and_sort(force_fetch=True) # Initial load


def fetch_route_distance(start, destination):
    """
    Fetches the distance and travel time from TomTom API.
    Returns (distance_text, needs_fuel_bool) or (None, False) on error.
    """
    if not TOMTOM_API_KEY:
        messagebox.showwarning("API Klíč chybí", "TomTom API klíč není nastaven. Vzdálenost nebude vypočítána.", parent=user_root)
        return None, False

    try:
        # Geocoding start location
        geocode_url_start = f"https://api.tomtom.com/search/2/geocode/{requests.utils.quote(start)}.json?key={TOMTOM_API_KEY}"
        response_start = requests.get(geocode_url_start)
        response_start.raise_for_status()
        data_start = response_start.json()
        if not data_start or not data_start.get('results'):
            messagebox.showwarning("Chyba místa", f"Nelze najít souřadnice pro start: {start}", parent=user_root)
            return None, False
        start_coords = data_start['results'][0]['position']

        # Geocoding destination
        geocode_url_dest = f"https://api.tomtom.com/search/2/geocode/{requests.utils.quote(destination)}.json?key={TOMTOM_API_KEY}"
        response_dest = requests.get(geocode_url_dest)
        response_dest.raise_for_status()
        data_dest = response_dest.json()
        if not data_dest or not data_dest.get('results'):
            messagebox.showwarning("Chyba místa", f"Nelze najít souřadnice pro cíl: {destination}", parent=user_root)
            return None, False
        destination_coords = data_dest['results'][0]['position']

        # Routing
        routing_url = (
            f"https://api.tomtom.com/routing/1/calculateRoute/"
            f"{start_coords['lat']},{start_coords['lon']}:"
            f"{destination_coords['lat']},{destination_coords['lon']}/json"
            f"?key={TOMTOM_API_KEY}"
        )
        response_route = requests.get(routing_url)
        response_route.raise_for_status()
        route_data = response_route.json()

        if route_data and route_data.get('routes'):
            route = route_data['routes'][0]['summary']
            distance_km = route['lengthInMeters'] / 1000
            travel_time_seconds = route['travelTimeInSeconds']
            
            # Simple heuristic for needs_fuel: if distance > 100 km, assume needs fuel
            needs_fuel = distance_km > 100

            return f"{distance_km:.2f} km", needs_fuel
        else:
            messagebox.showwarning("Chyba trasy", "Nelze vypočítat trasu mezi zadanými místy.", parent=user_root)
            return None, False

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Chyba sítě", f"Chyba při komunikaci s TomTom API: {e}", parent=user_root)
        return None, False
    except Exception as e:
        messagebox.showerror("Chyba API", f"Neočekávaná chyba při získávání dat z TomTom API: {e}", parent=user_root)
        return None, False

def add_route_dialog():
    """Zobrazí dialog pro přidání nové trasy."""
    dialog = tk.Toplevel(user_root)
    dialog.title("Přidat novou trasu")
    dialog.transient(user_root) # Dialog bude nad hlavním oknem
    dialog.grab_set() # Zablokuje interakci s hlavním oknem

    dialog.geometry("400x300")
    dialog.resizable(False, False)
    dialog.configure(bg=BG_COLOR)

    dialog_frame = ttk.Frame(dialog, padding=PADDING)
    dialog_frame.pack(fill="both", expand=True)

    labels = ["Název trasy:", "Počáteční místo:", "Cíl:"]
    entries = {}
    for i, text in enumerate(labels):
        ttk.Label(dialog_frame, text=text).grid(row=i, column=0, padx=5, pady=5, sticky="w")
        entry = ttk.Entry(dialog_frame)
        entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
        entries[text.replace(":", "").replace(" ", "_").lower()] = entry # Store by simplified key

    # Configure column to expand
    dialog_frame.grid_columnconfigure(1, weight=1)

    def save_route():
        name = entries["název_trasy"].get().strip()
        start = entries["počáteční_místo"].get().strip()
        destination = entries["cíl"].get().strip()

        if not name or not destination:
            messagebox.showwarning("Upozornění", "Název trasy a cíl jsou povinné.", parent=dialog)
            return

        distance, needs_fuel = fetch_route_distance(start, destination)

        if distance is None:
            # Error already handled by fetch_route_distance
            return

        if database.add_route(current_user_id, name, start, destination, distance, needs_fuel):
            messagebox.showinfo("Úspěch", "Trasa úspěšně přidána.", parent=dialog)
            dialog.destroy()
            apply_filters_and_sort(force_fetch=True) # Refresh list
        else:
            messagebox.showerror("Chyba", "Nepodařilo se přidat trasu. Možná název trasy již existuje.", parent=dialog)

    ttk.Button(dialog_frame, text="Uložit", command=save_route).grid(row=len(labels), column=0, columnspan=2, pady=10)

    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy) # Handle close button
    dialog.wait_window() # Wait until dialog is closed

def edit_route_dialog():
    """Zobrazí dialog pro úpravu vybrané trasy."""
    selected_item = user_routes_tree.selection()
    if not selected_item:
        messagebox.showwarning("Upozornění", "Vyberte prosím trasu k úpravě.", parent=user_root)
        return

    # Get data of the selected item
    item_values = user_routes_tree.item(selected_item, "values")
    # Retrieve the actual route_id from all_user_routes_cached based on the selected item's name
    selected_route_name = item_values[0] # Assuming name is the first column

    selected_route_data = next((route for route in all_user_routes_cached if route['name'] == selected_route_name), None)

    if not selected_route_data:
        messagebox.showerror("Chyba", "Nepodařilo se najít data pro vybranou trasu.", parent=user_root)
        return

    route_id = selected_route_data['id']
    current_name = selected_route_data['name']
    current_start = selected_route_data['start_location']
    current_destination = selected_route_data['destination']
    current_distance = selected_route_data['distance']
    current_needs_fuel = selected_route_data['needs_fuel']

    dialog = tk.Toplevel(user_root)
    dialog.title("Upravit trasu")
    dialog.transient(user_root)
    dialog.grab_set()
    dialog.geometry("400x350")
    dialog.resizable(False, False)
    dialog.configure(bg=BG_COLOR)

    dialog_frame = ttk.Frame(dialog, padding=PADDING)
    dialog_frame.pack(fill="both", expand=True)

    labels = ["Název trasy:", "Počáteční místo:", "Cíl:"]
    entries = {}
    for i, text in enumerate(labels):
        ttk.Label(dialog_frame, text=text).grid(row=i, column=0, padx=5, pady=5, sticky="w")
        entry = ttk.Entry(dialog_frame)
        entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
        entries[text.replace(":", "").replace(" ", "_").lower()] = entry

    entries["název_trasy"].insert(0, current_name)
    entries["počáteční_místo"].insert(0, current_start)
    entries["cíl"].insert(0, current_destination)

    # Checkbutton for needs_fuel
    needs_fuel_var = tk.BooleanVar(value=current_needs_fuel)
    ttk.Checkbutton(dialog_frame, text="Potřeba paliva", variable=needs_fuel_var).grid(row=len(labels), column=0, columnspan=2, padx=5, pady=5, sticky="w")

    dialog_frame.grid_columnconfigure(1, weight=1)

    def save_changes():
        new_name = entries["název_trasy"].get().strip()
        new_start = entries["počáteční_místo"].get().strip()
        new_destination = entries["cíl"].get().strip()
        new_needs_fuel = needs_fuel_var.get()

        if not new_name or not new_destination:
            messagebox.showwarning("Upozornění", "Název trasy a cíl jsou povinné.", parent=dialog)
            return

        # Check if start or destination changed, if so, recalculate distance
        if new_start != current_start or new_destination != current_destination:
            distance, needs_fuel_from_api = fetch_route_distance(new_start, new_destination)
            if distance is None:
                return # Error already shown by fetch_route_distance
            new_distance = distance
            new_needs_fuel = needs_fuel_from_api # Use the API's suggestion
        else:
            new_distance = current_distance # Keep old distance if locations haven't changed

        if database.update_route(route_id, new_name, new_start, new_destination, new_distance, new_needs_fuel):
            messagebox.showinfo("Úspěch", "Trasa úspěšně aktualizována.", parent=dialog)
            dialog.destroy()
            apply_filters_and_sort(force_fetch=True) # Refresh list
        else:
            messagebox.showerror("Chyba", "Nepodařilo se aktualizovat trasu. Možná název trasy již existuje.", parent=dialog)

    ttk.Button(dialog_frame, text="Uložit změny", command=save_changes).grid(row=len(labels) + 1, column=0, columnspan=2, pady=10)

    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
    dialog.wait_window()


def delete_route_confirm():
    """Potvrdí a smaže vybranou trasu."""
    selected_item = user_routes_tree.selection()
    if not selected_item:
        messagebox.showwarning("Upozornění", "Vyberte prosím trasu ke smazání.", parent=user_root)
        return

    selected_route_name = user_routes_tree.item(selected_item, "values")[0]

    response = messagebox.askyesno("Potvrdit smazání", f"Opravdu chcete smazat trasu '{selected_route_name}'?", parent=user_root)
    if response:
        selected_route_data = next((route for route in all_user_routes_cached if route['name'] == selected_route_name), None)
        if selected_route_data:
            route_id = selected_route_data['id']
            if database.delete_route(route_id):
                messagebox.showinfo("Úspěch", "Trasa byla úspěšně smazána.", parent=user_root)
                apply_filters_and_sort(force_fetch=True) # Refresh list
            else:
                messagebox.showerror("Chyba", "Nepodařilo se smazat trasu.", parent=user_root)
        else:
            messagebox.showerror("Chyba", "Nepodařilo se najít ID pro smazání trasy.", parent=user_root)

def set_sort_and_apply(column, order):
    """Nastaví globální proměnné pro řazení a aplikuje filtry a řazení."""
    global current_sort_column, current_sort_order
    current_sort_column = column
    current_sort_order = order
    apply_filters_and_sort()


def apply_filters_and_sort(force_fetch=False):
    """Aplikuje filtry a seřadí trasy, poté aktualizuje Treeview."""
    global all_user_routes_cached, user_routes_tree, current_sort_column, current_sort_order

    if force_fetch:
        all_user_routes_cached = database.get_routes_by_user(current_user_id)

    filtered_routes = all_user_routes_cached

    # Apply filters
    name_filter = filter_name_entry.get().strip().lower()
    start_filter = filter_start_entry.get().strip().lower()
    destination_filter = filter_destination_entry.get().strip().lower()
    fuel_filter = filter_fuel_var.get() # 'Vše', 'Ano', 'Ne'

    if name_filter:
        filtered_routes = [r for r in filtered_routes if name_filter in r['name'].lower()]
    if start_filter:
        filtered_routes = [r for r in filtered_routes if start_filter in r['start_location'].lower()]
    if destination_filter:
        filtered_routes = [r for r in filtered_routes if destination_filter in r['destination'].lower()]

    if fuel_filter == "Ano":
        filtered_routes = [r for r in filtered_routes if r['needs_fuel']]
    elif fuel_filter == "Ne":
        filtered_routes = [r for r in filtered_routes if not r['needs_fuel']]

    # Apply sorting
    sort_col = current_sort_column
    sort_order = current_sort_order == "asc" # True for ascending, False for descending

    # Special handling for numeric sort on 'distance' if needed, otherwise default to string sort
    if sort_col == "distance":
        # Extract numeric part for sorting, assuming "XXX.YY km" format
        filtered_routes.sort(key=lambda x: float(x[sort_col].split(' ')[0]) if x[sort_col] and 'km' in x[sort_col] else 0.0, reverse=not sort_order)
    elif sort_col == "needs_fuel":
         # Sort boolean values (False before True for 'asc')
        filtered_routes.sort(key=lambda x: x[sort_col], reverse=not sort_order)
    else:
        filtered_routes.sort(key=lambda x: str(x.get(sort_col, '')).lower(), reverse=not sort_order)


    # Clear current treeview
    for item in user_routes_tree.get_children():
        user_routes_tree.delete(item)

    # Insert filtered and sorted data
    for route in filtered_routes:
        # Ensure values are in the correct order for the Treeview columns
        user_routes_tree.insert("", "end", values=(
            route.get('name', ''),
            route.get('start_location', ''),
            route.get('destination', ''),
            route.get('distance', ''),
            "Ano" if route.get('needs_fuel', False) else "Ne"
        ))

def go_back_to_login():
    """Destroys current screen content and returns to login using the stored callback."""
    global user_root, _create_login_widgets_callback, all_user_routes_cached 

    # Clear current screen widgets
    for widget in user_root.winfo_children():
        widget.destroy()

    # Reset window size and title
    user_root.geometry("300x200")
    user_root.title("Přihlašovací obrazovka")

    # Clear cached data when logging out
    all_user_routes_cached = []

    # Call the stored callback function to recreate the login UI
    if _create_login_widgets_callback:
        _create_login_widgets_callback() # Call the callback without arguments, as it's lambda: create_login_ui(main_app_window)
    else:
        messagebox.showerror("Chyba", "Nelze se vrátit na přihlašovací obrazovku. Chybí callback.")

    user_root.deiconify() # Ensure window is visible